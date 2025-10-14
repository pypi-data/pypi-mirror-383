import os
import re
from concurrent.futures import Future
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Union,
    Type,
    Tuple,
    Callable,
    Set,
    FrozenSet,
)

from dbt.adapters.base.relation import InformationSchema
from dbt.adapters.contracts.connection import AdapterResponse
from dbt.adapters.events.logging import AdapterLogger
from dbt_common.exceptions import DbtRuntimeError, CompilationError
from dbt_common.utils import AttrDict, executor

from typing_extensions import TypeAlias

import agate

from dbt.adapters.base import AdapterConfig, PythonJobHelper
from dbt.adapters.base.impl import catch_as_completed, ConstraintSupport
from dbt.adapters.sql import SQLAdapter
from dbt.adapters.watsonx_spark import (
    SparkConnectionManager,
    SparkRelation,
    SparkColumn,
    SparkCredentials
)
from dbt.adapters.watsonx_spark.python_submissions import (
    JobClusterPythonJobHelper,
    AllPurposeClusterPythonJobHelper,
)
from dbt.adapters.base import BaseRelation
from dbt.adapters.contracts.relation import RelationType, RelationConfig
from dbt_common.clients.agate_helper import DEFAULT_TYPE_TESTER
from dbt_common.contracts.constraints import ConstraintType
from dbt.adapters.base import BaseRelation , available
from dbt.contracts.graph.nodes import ModelConfig
from dbt_common.contracts.config.base import BaseConfig

logger = AdapterLogger("Spark")
packages = ["pyhive.hive", "thrift.transport", "thrift.protocol"]
log_level = os.getenv("DBT_SPARK_LOG_LEVEL", "ERROR")
for package in packages:
    logger.debug(f"Setting {package} logging to {log_level}")
    logger.set_adapter_dependency_log_level(package, log_level)

GET_COLUMNS_IN_RELATION_RAW_MACRO_NAME = "get_columns_in_relation_raw"
LIST_SCHEMAS_MACRO_NAME = "list_schemas"
LIST_RELATIONS_MACRO_NAME = "list_relations_without_caching"
LIST_RELATIONS_SHOW_TABLES_MACRO_NAME = "list_relations_show_tables_without_caching"
DESCRIBE_TABLE_EXTENDED_MACRO_NAME = "describe_table_extended_without_caching"
CREATE_SCHEMA_MACRO_NAME= "create_schema"
CREATE_TABLE_MACRO_NAME= "create_table_as"

KEY_TABLE_OWNER = "Owner"
KEY_TABLE_STATISTICS = "Statistics"

TABLE_OR_VIEW_NOT_FOUND_MESSAGES = (
    "[TABLE_OR_VIEW_NOT_FOUND]",
    "Table or view not found",
    "NoSuchTableException",
)
HEADER_KEYS = ("Type:", "Provider:", "Location:", "Owner:", "Statistics:")

@dataclass
class SparkConfig(AdapterConfig):
    file_format: str = "parquet"
    location_root: Optional[str] = None
    partition_by: Optional[Union[List[str], str]] = None
    clustered_by: Optional[Union[List[str], str]] = None
    buckets: Optional[int] = None
    options: Optional[Dict[str, str]] = None
    merge_update_columns: Optional[str] = None
    catalog: Optional[str] = None


class SparkAdapter(SQLAdapter):
    COLUMN_NAMES = (
        "table_database",
        "table_schema",
        "table_name",
        "table_type",
        "table_comment",
        "table_owner",
        "column_name",
        "column_index",
        "column_type",
        "column_comment",
        "stats:bytes:label",
        "stats:bytes:value",
        "stats:bytes:description",
        "stats:bytes:include",
        "stats:rows:label",
        "stats:rows:value",
        "stats:rows:description",
        "stats:rows:include",
    )
    INFORMATION_COLUMNS_REGEX = re.compile(r"^ \|-- (.*): (.*) \(nullable = (.*)\b", re.MULTILINE)
    INFORMATION_OWNER_REGEX = re.compile(r"^Owner: (.*)$", re.MULTILINE)
    INFORMATION_STATISTICS_REGEX = re.compile(r"^Statistics: (.*)$", re.MULTILINE)

    HUDI_METADATA_COLUMNS = [
        "_hoodie_commit_time",
        "_hoodie_commit_seqno",
        "_hoodie_record_key",
        "_hoodie_partition_path",
        "_hoodie_file_name",
    ]

    CONSTRAINT_SUPPORT = {
        ConstraintType.check: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.not_null: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.unique: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.primary_key: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.foreign_key: ConstraintSupport.NOT_ENFORCED,
    }

    Relation: TypeAlias = SparkRelation
    RelationInfo = Tuple[str, str, str]
    Column: TypeAlias = SparkColumn
    ConnectionManager: TypeAlias = SparkConnectionManager
    AdapterSpecificConfigs: TypeAlias = SparkConfig

    @classmethod
    def date_function(cls) -> str:
        return "current_timestamp()"

    @classmethod
    def convert_text_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "string"

    @classmethod
    def convert_number_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        decimals = agate_table.aggregate(agate.MaxPrecision(col_idx))
        return "double" if decimals else "bigint"

    @classmethod
    def convert_integer_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "bigint"

    @classmethod
    def convert_date_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "date"

    @classmethod
    def convert_time_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "time"

    @classmethod
    def convert_datetime_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "timestamp"

    def quote(self, identifier: str) -> str:
        return "`{}`".format(identifier)

    def _get_relation_information(self, row: agate.Row) -> RelationInfo:
        """relation info was fetched with SHOW TABLES EXTENDED"""
        try:
            
            _schema, name, _, information = row

        except ValueError:
            raise DbtRuntimeError(
                f'Invalid value from "show tables extended ...", got {len(row)} values, expected 4'
            )

        return _schema, name, information

    def _get_relation_information_using_describe(self, row: agate.Row) -> RelationInfo:
        """Relation info fetched using SHOW TABLES and an auxiliary DESCRIBE statement"""
        try:
            _schema, name, _ = row
        except ValueError:
            raise DbtRuntimeError(
                f'Invalid value from "show tables ...", got {len(row)} values, expected 3'
            )

        table_name = f"{_schema}.{name}"
        try:
            table_results = self.execute_macro(
                DESCRIBE_TABLE_EXTENDED_MACRO_NAME, kwargs={"table_name": table_name}
            )
        except DbtRuntimeError as e:
            logger.debug(f"Error while retrieving information about {table_name}: {e.msg}")
            table_results = AttrDict()

        information = ""
        for info_row in table_results:
            info_type, info_value, _ = info_row
            if not info_type.startswith("#"):
                information += f"{info_type}: {info_value}\n"

        return _schema, name, information

    def _build_spark_relation_list(
        self,
        row_list: agate.Table,
        relation_info_func: Callable[[agate.Row], RelationInfo],
    ) -> List[SparkRelation]:
        """Aggregate relations with format metadata included."""
        relations = []
        for row in row_list:
            _schema, name, information = relation_info_func(row)

            rel_type: RelationType = (
                RelationType.View if "Type: VIEW" in information else RelationType.Table
            )
            is_delta: bool = "Provider: delta" in information
            is_hudi: bool = "Provider: hudi" in information
            is_iceberg: bool = "Provider: iceberg" in information

            relation: BaseRelation = self.Relation.create(
                schema=_schema,
                identifier=name,
                type=rel_type,
                information=information,
                is_delta=is_delta,
                is_iceberg=is_iceberg,
                is_hudi=is_hudi,
            )
            relations.append(relation)

        return relations

    def list_relations_without_caching(self, schema_relation: BaseRelation) -> List[BaseRelation]:
        """Distinct Spark compute engines may not support the same SQL featureset. Thus, we must
        try different methods to fetch relation information."""

        kwargs = {"schema_relation": schema_relation}
        try:
            show_table_extended_rows = self.execute_macro(
                LIST_RELATIONS_MACRO_NAME, kwargs=kwargs
            )
            rels = self._build_spark_relation_list(
                row_list=show_table_extended_rows,
                relation_info_func=self._get_relation_information,
            )
            if "." in schema_relation.schema:
                rels = [r.incorporate(path={"schema": schema_relation.schema}) for r in rels]
            return rels
        except DbtRuntimeError as e:
            errmsg = getattr(e, "msg", "").lower()
            if f"database '{schema_relation}' not found" in errmsg:
                return []
            # Iceberg compute engine behavior: show table
            if (
                "show table extended is not supported for v2 tables" in errmsg
                or 'invalid value from "show tables extended' in errmsg
                or "failed to list all tables under namespace" in errmsg
                or ("show table extended" in errmsg and "not supported" in errmsg)
                ):
                # this happens with spark-iceberg with v2 iceberg tables
                # https://issues.apache.org/jira/browse/SPARK-33393
                try:
                    # Iceberg behavior: 3-row result of relations obtained
                    show_table_rows = self.execute_macro(
                        LIST_RELATIONS_SHOW_TABLES_MACRO_NAME, kwargs=kwargs
                    )
                    rels = self._build_spark_relation_list(
                        row_list=show_table_rows,
                        relation_info_func=self._get_relation_information_using_describe,
                    )
                    if "." in schema_relation.schema:
                        rels = [r.incorporate(path={"schema": schema_relation.schema}) for r in rels]
                    return rels
                except DbtRuntimeError as e:
                    description = "Error while retrieving information about"
                    logger.debug(f"{description} {schema_relation}: {e.msg}")
                    return []
            else:
                logger.debug(
                    f"Error while retrieving information about {schema_relation}: {errmsg}"
                )
                return []

    def get_relation(self, database: str, schema: str, identifier: str) -> Optional[BaseRelation]:
        if not self.Relation.get_default_include_policy().database:
            database = None  # type: ignore

        return super().get_relation(database, schema, identifier)

    def parse_describe_extended(
        self, relation: BaseRelation, raw_rows: AttrDict
    ) -> List[SparkColumn]:
        # Convert the Row to a dict
        dict_rows = [dict(zip(row._keys, row._values)) for row in raw_rows]
        # Find the separator between the rows and the metadata provided
        # by the DESCRIBE TABLE EXTENDED statement
        pos = self.find_table_information_separator(dict_rows)

        # Remove rows that start with a hash, they are comments
        rows = [row for row in raw_rows[0:pos] if not row["col_name"].startswith("#")]
        metadata = {col["col_name"]: col["data_type"] for col in raw_rows[pos + 1 :]}

        raw_table_stats = metadata.get(KEY_TABLE_STATISTICS)
        table_stats = SparkColumn.convert_table_stats(raw_table_stats)
        return [
            SparkColumn(
                table_database=None,
                table_schema=relation.schema,
                table_name=relation.name,
                table_type=relation.type,
                table_owner=str(metadata.get(KEY_TABLE_OWNER)),
                table_stats=table_stats,
                column=column["col_name"],
                column_index=idx,
                dtype=column["data_type"],
            )
            for idx, column in enumerate(rows)
        ]

    @staticmethod
    def find_table_information_separator(rows: List[dict]) -> int:
        pos = 0
        for row in rows:
            if not row["col_name"] or row["col_name"].startswith("#"):
                break
            pos += 1
        return pos

    def get_columns_in_relation(self, relation: BaseRelation) -> List[SparkColumn]:
        columns = []
        try:
            rows: AttrDict = self.execute_macro(
                GET_COLUMNS_IN_RELATION_RAW_MACRO_NAME, kwargs={"relation": relation}
            )
            columns = self.parse_describe_extended(relation, rows)
        except DbtRuntimeError as e:
            # spark would throw error when table doesn't exist, where other
            # CDW would just return and empty list, normalizing the behavior here
            errmsg = getattr(e, "msg", "")
            found_msgs = (msg in errmsg for msg in TABLE_OR_VIEW_NOT_FOUND_MESSAGES)
            if any(found_msgs):
                pass
            else:
                raise e

        # strip hudi metadata columns.
        columns = [x for x in columns if x.name not in self.HUDI_METADATA_COLUMNS]
        return columns

    def create_schema(self, relation: SparkRelation) -> None:
        relation = relation.without_identifier()
        kwargs = {
            "relation": relation
        }
        self.execute_macro(CREATE_SCHEMA_MACRO_NAME, kwargs=kwargs)
        self.commit_if_has_connection()

    @available.parse_none
    def set_location_root(self, relation: SparkRelation , config: SparkConfig) -> str:
        profile_cred: SparkCredentials = self.connections.get_thread_connection().credentials
        profile_location_root = self.validate_location(profile_cred.location_root)
        model_location_root = self.validate_location(config.get("location_root"))

        if model_location_root is not None: #Model location root 
            relation.set_location(model_location_root)
            return model_location_root

        if profile_location_root is not None: #Profile location root
            relation.set_location(profile_location_root)
            return profile_location_root
        
        if self.ConnectionManager.get_location_from_api(profile_cred) is not None:
            location_root,file_format = self.get_location_format_api(profile_cred,config)
            relation.set_location(location_root)
            return location_root
        return None
    
    def get_location_format_api(self, profile_cred: SparkCredentials , config: SparkConfig):
        catalog = self.set_catalog(config)
        bucket, file_format = self.ConnectionManager.get_location_from_api(profile_cred)
        location_root = self.build_location(bucket, catalog, profile_cred.schema)
        return location_root,file_format

    def validate_location(self, location_root: str) -> str:
        if location_root is not None and location_root != "":
            regex = re.compile("^'.*'$")
            if (self.check_regex(regex, location_root)):
                return location_root
            return f"'{location_root}'"
        return None

    def build_location(self, bucket: str, catalog: str, schema: str) -> None:
        if bucket is not None and catalog is not None and schema is not None:
            if '.' in schema:
                schema = schema.split('.')[1]
            location_root = f"'s3a://{bucket}/{catalog}/{schema}'"
            return location_root
        return None

    def check_regex(self, regex: any, string: str) -> bool:
        if re.match(regex, string):
            return True
        return False
    
    @available.parse_none
    def set_configuration(self, config: SparkConfig) -> None:
        profile_cred: SparkCredentials = self.connections.get_thread_connection().credentials
        configuration: ModelConfig = config.__dict__['model'].config
        location_root,file_format = self.get_location_format_api(profile_cred,config)
        configuration.__setitem__("location_root",location_root.replace("'", ""))
        if configuration.get("file_format") is None:  configuration.__setitem__("file_format",file_format)
        if configuration.get("catalog") is None:  configuration.__setitem__("catalog",self.set_catalog(config))
        config.__dict__['model'].config = configuration
        return config

    @available.parse_none
    def set_catalog(self, config: SparkConfig) -> str:
        cred: SparkCredentials = self.connections.get_thread_connection().credentials
        if config.get("catalog") is not None and config.get("catalog") != "":
            return config.get("catalog")

        if cred.catalog is not None and cred.catalog != "":
            return cred.catalog
        return ''

    def parse_columns_from_information(self, relation: BaseRelation) -> List[SparkColumn]:
        if hasattr(relation, "information"):
            information = relation.information or ""
        else:
            information = ""
        owner_match = re.findall(self.INFORMATION_OWNER_REGEX, information)
        owner = owner_match[0] if owner_match else None
        matches = re.finditer(self.INFORMATION_COLUMNS_REGEX, information)
        columns = []
        stats_match = re.findall(self.INFORMATION_STATISTICS_REGEX, information)
        raw_table_stats = stats_match[0] if stats_match else None
        table_stats = SparkColumn.convert_table_stats(raw_table_stats)
        for match_num, match in enumerate(matches):
            column_name, column_type, nullable = match.groups()
            column = SparkColumn(
                table_database=None,
                table_schema=relation.schema,
                table_name=relation.table,
                table_type=relation.type,
                column_index=match_num,
                table_owner=owner,
                column=column_name,
                dtype=column_type,
                table_stats=table_stats,
            )
            columns.append(column)
        return columns

    def _get_columns_for_catalog(self, relation: BaseRelation) -> Iterable[Dict[str, Any]]:
        columns = self.parse_columns_from_information(relation)

        for column in columns:
            # convert SparkColumns into catalog dicts
            as_dict = column.to_column_dict()
            as_dict["column_name"] = as_dict.pop("column", None)
            as_dict["column_type"] = as_dict.pop("dtype")
            as_dict["table_database"] = None
            yield as_dict

    def get_catalog(
        self,
        relation_configs: Iterable[RelationConfig],
        used_schemas: FrozenSet[Tuple[str, str]],
    ) -> Tuple[agate.Table, List[Exception]]:
        schema_map = self._get_catalog_schemas(relation_configs)
        if len(schema_map) > 1:
            raise CompilationError(
                f"Expected only one database in get_catalog, found " f"{list(schema_map)}"
            )

        with executor(self.config) as tpe:
            futures: List[Future[agate.Table]] = []
            for info, schemas in schema_map.items():
                for schema in schemas:
                    futures.append(
                        tpe.submit_connected(
                            self,
                            schema,
                            self._get_one_catalog,
                            info,
                            [schema],
                            relation_configs,
                        )
                    )
            catalogs, exceptions = catch_as_completed(futures)
        return catalogs, exceptions

    def _get_one_catalog(
        self,
        information_schema: InformationSchema,
        schemas: Set[str],
        used_schemas: FrozenSet[Tuple[str, str]],
    ) -> agate.Table:
        if len(schemas) != 1:
            raise CompilationError(
                f"Expected only one schema in spark _get_one_catalog, found " f"{schemas}"
            )

        database = information_schema.database
        schema = list(schemas)[0]

        columns: List[Dict[str, Any]] = []
        for relation in self.list_relations(database, schema):
            logger.debug("Getting table schema for relation {}", str(relation))
            columns.extend(self._get_columns_for_catalog(relation))
        return agate.Table.from_object(columns, column_types=DEFAULT_TYPE_TESTER)

    def check_schema_exists(self, database: str, schema: str) -> bool:
        results = self.execute_macro(LIST_SCHEMAS_MACRO_NAME, kwargs={"database": database})

        exists = True if schema in [row[0] for row in results] else False
        return exists

    def to_agate_table(self,rows_list):
        fixed = []
        for db, name, is_temp, info in rows_list:
            # drop catalog if present: "catalog.schema" -> "schema"
            schema = db.split(".", 1)[-1]
            fixed.append([schema, name, bool(is_temp), self.normalize_information(info)])
        return agate.Table(
            fixed,
            column_names=["database", "tableName", "isTemporary", "information"]
        )
    
    def normalize_information(self,info: str) -> str:
        """Move header keys out of the schema block; keep proper EXTENDED shape."""
        lines = [ln.strip() for ln in info.splitlines() if ln.strip()]
        header, schema_lines = [], []
        in_schema = False

        for ln in lines:
            if ln.startswith("Schema:"):
                in_schema = True
                continue
            if in_schema:
                # Lines like "|-- col: type (nullable = true)"
                m = re.match(r"^\|--\s+(.*)$", ln)
                if m:
                    raw = m.group(1)
                    if any(raw.startswith(k) for k in HEADER_KEYS):
                        # turn "|-- Type: MANAGED (nullable = true)" -> "Type: MANAGED"
                        k, v = raw.split(":", 1)
                        header.append(f"{k.strip()}: {v.split('(nullable',1)[0].strip()}")
                    else:
                        schema_lines.append(f" |-- {raw}")
                continue
            # Some DESCRIBE variants list header lines before "Schema:"
            if any(ln.startswith(k) for k in HEADER_KEYS):
                header.append(ln)

        # Compose canonical blob
        return "\n".join(header + ["Schema: root"] + schema_lines)
    

    def get_rows_different_sql(
        self,
        relation_a: BaseRelation,
        relation_b: BaseRelation,
        column_names: Optional[List[str]] = None,
        except_operator: str = "EXCEPT",
    ) -> str:
        """Generate SQL for a query that returns a single row with two
        columns: the number of rows that are different between the two
        relations and the number of mismatched rows.
        """
        # This method only really exists for test reasons.
        names: List[str]
        if column_names is None:
            columns = self.get_columns_in_relation(relation_a)
            names = sorted((self.quote(c.name) for c in columns))
        else:
            names = sorted((self.quote(n) for n in column_names))
        columns_csv = ", ".join(names)

        sql = COLUMNS_EQUAL_SQL.format(
            columns=columns_csv,
            relation_a=str(relation_a),
            relation_b=str(relation_b),
        )

        return sql

    # This is for use in the test suite
    # Spark doesn't have 'commit' and 'rollback', so this override
    # doesn't include those commands.
    def run_sql_for_tests(self, sql, fetch, conn):  # type: ignore
        cursor = conn.handle.cursor()
        try:
            cursor.execute(sql)
            if fetch == "one":
                if hasattr(cursor, "fetchone"):
                    return cursor.fetchone()
                else:
                    # AttributeError: 'PyhiveConnectionWrapper' object has no attribute 'fetchone'
                    return cursor.fetchall()[0]
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return
        except BaseException as e:
            print(sql)
            print(e)
            raise
        finally:
            conn.transaction_open = False

    def generate_python_submission_response(self, submission_result: Any) -> AdapterResponse:
        return self.connections.get_response(None)

    @property
    def default_python_submission_method(self) -> str:
        return "all_purpose_cluster"

    @property
    def python_submission_helpers(self) -> Dict[str, Type[PythonJobHelper]]:
        return {
            "job_cluster": JobClusterPythonJobHelper,
            "all_purpose_cluster": AllPurposeClusterPythonJobHelper,
        }

    def standardize_grants_dict(self, grants_table: agate.Table) -> dict:
        grants_dict: Dict[str, List[str]] = {}
        for row in grants_table:
            grantee = row["Principal"]
            privilege = row["ActionType"]
            object_type = row["ObjectType"]

            # we only want to consider grants on this object
            # (view or table both appear as 'TABLE')
            # and we don't want to consider the OWN privilege
            if object_type == "TABLE" and privilege != "OWN":
                if privilege in grants_dict.keys():
                    grants_dict[privilege].append(grantee)
                else:
                    grants_dict.update({privilege: [grantee]})
        return grants_dict

    def debug_query(self) -> None:
        """Override for DebugTask method"""
        self.execute("select 1 as id")


# spark does something interesting with joins when both tables have the same
# static values for the join condition and complains that the join condition is
# "trivial". Which is true, though it seems like an unreasonable cause for
# failure! It also doesn't like the `from foo, bar` syntax as opposed to
# `from foo cross join bar`.
COLUMNS_EQUAL_SQL = """
with diff_count as (
    SELECT
        1 as id,
        COUNT(*) as num_missing FROM (
            (SELECT {columns} FROM {relation_a} EXCEPT
             SELECT {columns} FROM {relation_b})
             UNION ALL
            (SELECT {columns} FROM {relation_b} EXCEPT
             SELECT {columns} FROM {relation_a})
        ) as a
), table_a as (
    SELECT COUNT(*) as num_rows FROM {relation_a}
), table_b as (
    SELECT COUNT(*) as num_rows FROM {relation_b}
), row_count_diff as (
    select
        1 as id,
        table_a.num_rows - table_b.num_rows as difference
    from table_a
    cross join table_b
)
select
    row_count_diff.difference as row_count_difference,
    diff_count.num_missing as num_mismatched
from row_count_diff
cross join diff_count
""".strip()
