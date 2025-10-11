import logging
import time
from copy import copy
from typing import Dict, List, Tuple

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit
from sws_api_client import Tags
from sws_api_client.tags import BaseDisseminatedTagTable, TableLayer, TableType

from .constants import DatasetTables, IcebergDatabases, IcebergTables
from .SWSPostgresSparkReader import SWSPostgresSparkReader
from .utils import get_or_create_tag, save_cache_csv


class SWSBronzeIcebergSparkHelper:
    def __init__(
        self,
        spark: SparkSession,
        bucket: str,
        tag_name: str,
        dataset_id: str,
        sws_postgres_spark_reader: SWSPostgresSparkReader,
        iceberg_tables: IcebergTables,
        domain_code: str,
        dataset_details: dict = None,
        dataset_tables: DatasetTables = None,
    ) -> None:
        self.spark: SparkSession = spark
        self.dataset_details: dict = dataset_details
        self.bucket: str = bucket
        self.tag_name: str = tag_name
        self.dataset_id: str = dataset_id
        self.sws_postgres_spark_reader = sws_postgres_spark_reader
        self.dataset_tables: DatasetTables = dataset_tables
        self.iceberg_tables: IcebergTables = iceberg_tables
        self.domain_code = domain_code

        if dataset_details is not None:
            (
                self.dim_columns_w_time,
                self.dim_columns,
                self.time_column,
                self.flag_columns,
            ) = self._get_dim_time_flag_columns()

            # ----------------
            # Get the codelist -> type mapping (e.g. geographicAreaM49 -> area )
            # ----------------

            self.dim_col_to_id_mapping: Dict[str, str] = (
                self._get_column_names_to_idmappings("dimension")
            )
            self.flag_col_to_id_mapping: Dict[str, str] = (
                self._get_column_names_to_idmappings("flag")
            )

            self.codelist_type_mapping = (
                self.sws_postgres_spark_reader.get_codelist_type_mapping(
                    self.domain_code,
                    dimension_flag_columns=self.dim_columns_w_time + self.flag_columns,
                )
            )

            # I suppose to have only 1 element column in each dataset
            self.element_column = next(
                dimension_column
                for dimension_column in self.dim_columns_w_time
                # Select the value where the type of the column is "element"
                if self.codelist_type_mapping[dimension_column] == "element"
            )

        if dataset_tables is not None:
            self.raw_data, self.raw_reference_data, self.raw_operational_data = (
                self.sws_postgres_spark_reader.import_data_reference_data_operational_data(
                    self.dataset_tables
                )
            )

            (
                self.df_observation,
                self.df_obs_coord,
                self.df_metadata,
                self.df_meta_elem,
            ) = self.raw_data

            (
                self.df_flag_method,
                self.df_flag_obs_status,
                self.df_metadata_type,
                self.df_meta_elem_type,
                self.df_language,
                self.df_unit_of_measure,
                self.dfs_dimension,
            ) = self.raw_reference_data

            self.df_user = self.raw_operational_data

    def _get_dim_time_flag_columns(self) -> Tuple[List[str], List[str], str, List[str]]:
        """Extract the dimension columns with time, without time, the time column and the flag columns names."""
        dim_columns_w_time = [
            dimension["id"] for dimension in self.dataset_details["dimensions"]
        ]
        time_column = next(
            dimension["id"]
            for dimension in self.dataset_details["dimensions"]
            if dimension["codelist"]["type"] == "time"
        )
        dim_columns = copy(dim_columns_w_time)
        dim_columns.remove(time_column)

        flag_columns = [flag["id"] for flag in self.dataset_details["flags"]]

        return dim_columns_w_time, dim_columns, time_column, flag_columns

    def _get_column_names_to_idmappings(self, col_type: str) -> Dict[str, str]:
        """Create a mapping from column names to dimension/flag ids."""
        return {
            dimension[f"{col_type}Column"]: dimension["id"]
            for dimension in self.dataset_details[f"{col_type}s"]
        }

    def _convert_dim_start_end_date_to_data(self) -> List[DataFrame]:
        """Prepare the dimension DataFrames for joining by adding the validity date time range."""

        dfs_dimension = [
            df_dimension.select(
                "id",
                "code",
                F.to_date(F.coalesce("start_date", lit(None))).alias(
                    f"{dimension_column}_start_date"
                ),
                F.to_date(F.coalesce("end_date", lit(None))).alias(
                    f"{dimension_column}_end_date"
                ),
            )
            for dimension_column, df_dimension in zip(
                self.dim_columns_w_time, self.dfs_dimension
            )
        ]

        for dimension_column, df_dimension in zip(
            self.dim_columns_w_time, dfs_dimension
        ):
            logging.debug("dimension_column")
            logging.debug(dimension_column)
            logging.debug("df_dimension.columns")
            logging.debug(df_dimension.columns)

        return dfs_dimension

    def _prepare_element_uom(self) -> DataFrame:
        """Prepare the element and unit of measure join."""

        # Get the element DataFrame
        df_element = next(
            df_dimension
            for dimension_column, df_dimension in zip(
                self.dim_columns_w_time, self.dfs_dimension
            )
            if dimension_column == self.element_column
        )

        # Join the element and the unit_of_measure
        df_element_uom = (
            df_element.alias("e")
            .join(
                self.df_unit_of_measure.alias("u"),
                col("e.unit_of_measure") == col("u.id"),
            )
            .select(
                col("e.code").alias("element_code"),
                col("u.code").alias("unit_of_measure"),
                col("u.symbol").alias("unit_of_measure_symbol"),
                col("u.base_unit").alias("unit_of_measure_base_unit"),
                col("u.multiplier").alias("unit_of_measure_multiplier"),
            )
        )

        return df_element_uom

    def _gen_denormalized_observation(self) -> DataFrame:
        """Original query upon which the below computation is based

        select o.id,
            o.value,
            u.email,
            o.created_on,
            o.replaced_on, // To remove (always null)
            o.version,
            o.flag_obs_status,
            o.flag_method,
            d0.code as "geographic_area_m49",
            d1.code as "element_fao",
            d2.code as "item_cpc ",
            d3.code as "time_series_years",
            ...
        from <dataset_id>.observation o
            join operational_data.user u ON u.id = o.created_by
            left join <dataset_id>.observation_coordinate as oc on oc.id = o.observation_coordinates
            left join reference_data.dim_geographic_area_m49 d0 on d0.id = oc.dim_geographic_area_m49
            left join reference_data.dim_element_fao d1 on d1.id = oc.dim_element_fao
            left join reference_data.dim_item_cpc d2 on d2.id = oc.dim_item_cpc
            left join reference_data.dim_time_series_years d3 on d3.id = oc.dim_time_series_years
        where o.replaced_on is null,
        """

        # ----------------
        # Prepare dataframes for the joins
        # ----------------

        df_observation = self.df_observation.withColumnsRenamed(
            self.flag_col_to_id_mapping
        )

        df_obs_coord = self.df_obs_coord.withColumnsRenamed(
            self.dim_col_to_id_mapping
        ).drop("approved_observation", "num_version")

        logging.debug("df_observation.columns")
        logging.debug(df_observation.columns)
        logging.debug("df_obs_coord.columns")
        logging.debug(df_obs_coord.columns)

        # Get the element DataFrame separately to join with the unit of measure DataFrame
        df_element_uom = self._prepare_element_uom()

        dfs_dimension_w_validity = self._convert_dim_start_end_date_to_data()

        # ----------------
        # Generate denormalized observation table
        # ----------------

        logging.info("obs_denorm start")

        # Join observations with user and observation coordinate
        df_intermediate = (
            # Keep only the latest version of an observation
            df_observation.where(col("replaced_on").isNull())
            .alias("o")
            # Join the user with the observation
            .join(
                F.broadcast(self.df_user).alias("u"),
                col("o.created_by") == col("u.id"),
            )
            .select("o.*", "u.email")
            .alias("o")
            .join(
                df_obs_coord.withColumnRenamed("id", "join_id").alias("oc"),
                col("o.observation_coordinates") == col("oc.join_id"),
                "left",
            )
            .drop("join_id")
        )

        # Join all the dimension codelists
        for dimension_column, df_dimension in zip(
            self.dim_columns_w_time, dfs_dimension_w_validity
        ):
            df_intermediate = (
                df_intermediate.alias("o")
                .join(
                    F.broadcast(df_dimension.withColumnRenamed("id", "join_id")).alias(
                        "d"
                    ),
                    col(f"{dimension_column}") == col("d.join_id"),
                )
                .drop(f"{dimension_column}", "join_id")
                .withColumnRenamed("code", dimension_column)
            )

        df_intermediate = (
            df_intermediate.alias("d")
            .join(
                F.broadcast(df_element_uom).alias("e"),
                col(f"d.{self.element_column}") == col("e.element_code"),
                "left",
            )
            .drop("element_code")
        )

        df_obs_denorm = df_intermediate

        return df_obs_denorm

    def _gen_denormalized_metadata(self) -> DataFrame:
        """Original query upon which the below computation is based

        select m.observation as observation_id,
            mt.code as type,
            met.code as element_type,
            l.country_code as language,
            me.value
        from <dataset_id>.metadata_element me
            left join <dataset_id>.metadata m on m.id = me.metadata
            left join reference_data.metadata_element_type met on met.id = me.metadata_element_type
            left join reference_data.metadata_type mt on mt.id = m.metadata_type
            left join reference_data.language l on l.id = m.language
        """

        # ----------------
        # Generate denormalized observation table
        # ----------------

        logging.info("meta_denorm start")

        df_meta_denorm = (
            self.df_meta_elem.select("metadata", "metadata_element_type", "value")
            .alias("me")
            .join(
                self.df_metadata.alias("m"), col("me.metadata") == col("m.id"), "left"
            )
            .select("me.*", "m.id", "m.observation", "m.metadata_type", "m.language")
            .alias("md")
            .join(
                self.df_meta_elem_type.alias("met"),
                col("md.metadata_element_type") == col("met.id"),
                "left",
            )
            .select("md.*", col("met.code").alias("element_type"))
            .alias("md")
            .join(
                self.df_metadata_type.alias("mt"),
                col("md.metadata_type") == col("mt.id"),
                "left",
            )
            .select("md.*", col("mt.code").alias("type"))
            .withColumnRenamed("language", "join_language")
            .alias("md")
            .join(
                self.df_language.alias("l"),
                col("md.join_language") == col("l.id"),
                "left",
            )
            .select("md.*", col("l.country_code").alias("language"))
            .select(
                col("observation").alias("observation_id"),
                "type",
                "element_type",
                "language",
                "value",
            )
        )

        logging.info("meta_denorm write")

        return df_meta_denorm

    def _gen_grouped_metadata(self) -> DataFrame:
        return (
            self._gen_denormalized_metadata()
            .select(
                col("observation_id"),
                F.create_map(
                    lit("type"),
                    col("type"),
                    lit("element_type"),
                    col("element_type"),
                    lit("language"),
                    col("language"),
                    lit("value"),
                    col("value"),
                ).alias("metadata"),
            )
            .groupby("observation_id")
            .agg(F.collect_list("metadata").alias("metadata"))
        )

    def _gen_bronze_data(self) -> DataFrame:
        return (
            self._gen_denormalized_observation()
            .alias("o")
            .join(
                self._gen_grouped_metadata().alias("m"),
                col("o.id") == col("m.observation_id"),
                "left",
            )
            .drop("m.observation_id")
        )

    # TODO decouple data generation and data writing
    def write_bronze_data_to_iceberg_and_csv(self) -> DataFrame:
        self.df_bronze = self._gen_bronze_data()

        self.df_bronze.writeTo(self.iceberg_tables.BRONZE.iceberg_id).createOrReplace()

        logging.info(f"Bronze table written to {self.iceberg_tables.BRONZE.iceberg_id}")

        self.spark.sql(
            f"ALTER TABLE {self.iceberg_tables.BRONZE.iceberg_id} CREATE TAG `{self.tag_name}`"
        )

        logging.info(f"bronze tag '{self.tag_name}' created")

        df_bronze = self.df_bronze.withColumn(
            "metadata", F.to_json(col("metadata"))
        ).coalesce(1)

        save_cache_csv(
            df=df_bronze,
            bucket=self.bucket,
            prefix=self.iceberg_tables.BRONZE.csv_prefix,
            tag_name=self.tag_name,
        )

        return df_bronze

    def write_bronze_sws_dissemination_tag(self, tags: Tags):
        # Get or create a new tag
        tag = get_or_create_tag(tags, self.dataset_id, self.tag_name, self.tag_name)
        logging.debug(f"Tag: {tag}")

        new_iceberg_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_bronze_iceberg",
            name=f"{self.domain_code} bronze Iceberg",
            description="Bronze table containing all the raw data imported from the SWS and denormalized",
            layer=TableLayer.BRONZE,
            private=True,
            debug=True,
            type=TableType.ICEBERG,
            database=IcebergDatabases.BRONZE_DATABASE,
            table=self.iceberg_tables.BRONZE.table,
            path=self.iceberg_tables.BRONZE.path,
            structure={"columns": self.df_bronze.schema.jsonValue()["fields"]},
            pinned_columns=[*self.dim_columns_w_time, "value", *self.flag_columns],
        )
        tag = tags.add_dissemination_table(
            self.dataset_id, self.tag_name, new_iceberg_table
        )
        logging.debug(f"Tag with Added Iceberg Table: {tag}")

        new_csv_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_bronze_csv",
            name=f"{self.domain_code} bronze csv",
            description="Bronze table containing all the raw data imported from the SWS and denormalized cached in csv",
            layer=TableLayer.BRONZE,
            private=True,
            debug=True,
            type=TableType.CSV,
            path=self.iceberg_tables.BRONZE.csv_path,
            structure={"columns": self.df_bronze.schema.jsonValue()["fields"]},
        )
        tag = tags.add_dissemination_table(
            self.dataset_id, self.tag_name, new_csv_table
        )
        logging.debug(f"Tag with Added csv Table: {tag}")

        logging.info("Bronze Dissemination tags successfully written")

    def write_bronze_disseminated_tag_data_to_iceberg_and_csv(
        self, dimensions: Dict[str, List[str]]
    ) -> DataFrame:

        self.disseminated_tag_df = self.df_bronze

        if isinstance(dimensions, dict):
            for dimension_name, codes in dimensions.items():
                logging.info(f"dimension_name: {dimension_name}")
                logging.info(f"codes: {codes}")
                if len(codes) != 0:
                    self.disseminated_tag_df = self.disseminated_tag_df.filter(
                        col(dimension_name).isin(codes)
                    )

        self.disseminated_tag_df.writeTo(
            self.iceberg_tables.BRONZE_DISS_TAG.iceberg_id
        ).createOrReplace()

        logging.info(
            f"Bronze disseminated tag table written to {self.iceberg_tables.BRONZE_DISS_TAG.iceberg_id}"
        )

        self.spark.sql(
            f"ALTER TABLE {self.iceberg_tables.BRONZE_DISS_TAG.iceberg_id} CREATE TAG `{self.tag_name}`"
        )

        disseminated_tag_df = self.disseminated_tag_df.withColumn(
            "metadata", F.to_json(col("metadata"))
        ).coalesce(1)

        save_cache_csv(
            df=disseminated_tag_df,
            bucket=self.bucket,
            prefix=f"{self.iceberg_tables.BRONZE_DISS_TAG.csv_prefix}",
            tag_name=self.tag_name,
        )

        return disseminated_tag_df

    def write_bronze_sws_filtered_disseminated_tag(self, tags: Tags):
        # Get or create a new tag
        tag = get_or_create_tag(tags, self.dataset_id, self.tag_name, self.tag_name)
        logging.debug(f"Tag: {tag}")

        new_iceberg_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_bronze_disseminated_tag_iceberg",
            name=f"{self.domain_code} bronze disseminated tag Iceberg",
            description="Bronze table containing the raw data imported from the SWS, denormalized and filtered per dimension",
            layer=TableLayer.BRONZE,
            private=True,
            type=TableType.ICEBERG,
            database=IcebergDatabases.BRONZE_DATABASE,
            table=self.iceberg_tables.BRONZE_DISS_TAG.table,
            path=self.iceberg_tables.BRONZE_DISS_TAG.path,
            structure={
                "columns": self.disseminated_tag_df.schema.jsonValue()["fields"]
            },
            pinned_columns=[*self.dim_columns_w_time, "value", *self.flag_columns],
        )
        tag = tags.add_dissemination_table(
            self.dataset_id, self.tag_name, new_iceberg_table
        )
        logging.debug(f"Tag with Added Iceberg Table: {tag}")

        new_csv_table = BaseDisseminatedTagTable(
            id=f"{self.domain_code.lower()}_bronze_disseminated_tag_csv",
            name=f"{self.domain_code} bronze disseminated tag csv",
            description="Bronze table containing the raw data imported from the SWS, denormalized and filtered per dimension cached in csv",
            layer=TableLayer.BRONZE,
            private=True,
            type=TableType.CSV,
            # TODO Correct the path in the origin library
            path=self.iceberg_tables.BRONZE_DISS_TAG.csv_path,
            structure={
                "columns": self.disseminated_tag_df.schema.jsonValue()["fields"]
            },
        )
        tag = tags.add_dissemination_table(
            self.dataset_id, self.tag_name, new_csv_table
        )

        logging.debug(f"Tag with Added csv Table: {tag}")

        logging.info("Bronze Disseminated tag with selection successfully written")
