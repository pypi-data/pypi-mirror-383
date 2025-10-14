from __future__ import annotations

import functools
import io
import json
import linecache
import os
import re
import typing as t
import uuid

import dateutil.parser

from genguardx._internal.util.constants import DataType, URLS
from genguardx._internal.util.networking import api


if t.TYPE_CHECKING:
    import pyspark.sql

    # Our own python dict structure which we use for in-memory python dataframes
    class PythonDataColumn(t.TypedDict):
        type: str
        values: list[t.Any]

    PythonDataFrame = t.Mapping[str, PythonDataColumn]


class classproperty(property):  # noqa: N801
    """
    Create a property that is accessible using the class directly. Similar to classmethods - but for properties.

    Example:
        class Foo:
            _var = 1
            @classproperty
            def var(cls):
                return cls._var

        >>> Foo.var
        1
    """

    def __init__(self, func: t.Callable) -> None:
        self.func = func
        functools.update_wrapper(self, func)

    def __get__(self, obj: t.Any, owner: t.Any) -> t.Any:  # noqa: ANN401 -- Depends on the class
        if owner is None and obj is not None:
            owner = type(obj)
        return self.func(owner)


def ujoin(base: str, url: str) -> str:
    """
    Join a URL part to a given base URL.
    """
    return str(base).rstrip("/") + "/" + str(url).lstrip("/")


def do_exec(
    source_code: str,
    gscope: dict[str, t.Any] | None,
    lscope: dict[str, t.Any] | None = None,
) -> None:
    """
    A generic and better version of `exec()` that registers the code as a tempfile so that tracebacks
    and so on are easily found. This is required to improve error messages shown to users.

    Ref: https://stackoverflow.com/a/50885938/1755083
    """
    filename = f"<tmpfile-{uuid.uuid4()}>"
    code = compile(source_code, filename, "exec")
    if lscope is None:
        lscope = gscope
    # NOTE : linecache should be done before exec otherwise source file will not be accessible during execution.
    linecache.cache[filename] = (
        len(source_code),
        None,
        source_code.splitlines(keepends=True),
        filename,
    )
    exec(code, gscope, lscope)  # noqa: S102


def run_artifact(code: str, *args, scope: dict[str, t.Any] | None = None, funcname: str = "main", **kwargs) -> t.Any:  # noqa: ANN401 -- Depends on the function return type
    """
    Run the given function from the code and pass the provided args/kwargs when running it.

    :param code:     The artifact code to execute.
    :param *args:    The additional arguments to pass to the function when calling it.
    :param scope:    The scope the function should be defined in.
    :param funcname: The name of the function to call in the code.
    :param **kwargs: The additional kwargs to pass to the function when calling it.
    """
    scope = {} if scope is None else scope
    do_exec(code, scope, scope)
    return scope[funcname](*args, **kwargs)


def get_spark() -> pyspark.sql.SparkSession:
    try:
        import findspark

        findspark.init()
        import pyspark
    except ImportError:
        import pyspark

    return pyspark.sql.SparkSession.builder.getOrCreate()


def read_from_datasource(location: str) -> pyspark.sql.DataFrame:
    # NOTE: The below logic is repeated in:
    #        - corridor-api's task_utils.read_from_datasource()
    #        - corridor-python's utils.read_from_datasource()
    #       Ensure any changes here are also done in other places.
    spark = get_spark()
    if location.lower().rstrip("/").endswith(".parquet"):
        data = spark.read.parquet(location)
    elif location.lower().rstrip("/").endswith(".orc"):
        data = spark.read.orc(location)
    elif location.lower().rstrip("/").endswith(".csv"):
        data = spark.read.format("csv").load(location)
    elif location.lower().startswith("hive://"):
        hiveloc = location[len("hive://") :]
        # Hive caches the tables/views. This may cause potential issue if the
        # data-lake is updated with new data for the table.
        # Error: "java.io.FileNotFoundException - It is possible the underlying files have been updated".
        # The reason being we have a long running sparkSession and the cache would be refreshed only when
        # the sparkSession is restarted. So, we refresh the table before reading in order to avoid the error.
        spark.catalog.refreshTable(hiveloc)  # supported in spark 2.0 and above
        data = spark.table(hiveloc)
    elif location.lower().startswith("snowflake://"):
        data = (
            spark.read.format("net.snowflake.spark.snowflake")
            .options(**json.loads(os.environ.get("SNOWFLAKE_OPTIONS", "{}")))
            .option("dbtable", location[len("snowflake://") :])
            .load()
        )
    elif location.lower().startswith("jdbc://"):
        data = (
            spark.read.format("jdbc")
            .options(**json.loads(os.environ.get("JDBC_LAKE_OPTIONS", "{}")))
            .option("dbtable", location[len("jdbc://") :])
            .load()
        )
    else:
        raise NotImplementedError(f'Unable to read from the location: "{location}"')
    return data


def get_model_definition(input_type: str, attachment_id: int) -> io.BytesIO | io.StringIO:
    # Except for types 'python function' and 'lookup' every other file type should be
    # treated as binary file

    out_format, io_func = ("text", io.StringIO) if input_type in ["python function", "lookup"] else ("bin", io.BytesIO)
    return io_func(api.response(ujoin(URLS.ATTACHMENTS_PATH.value, str(attachment_id)), out=out_format))


def str_to_type(val: str, type_: str) -> t.Any:  # noqa: ANN401 -- return type can vary based on the arguments
    if val is None:
        return None
    # FIXME: handle array type
    assert type_ in (t.value for t in DataType), f"Found unknown type: {type_}"
    if type_ == DataType.STRING.value:
        return val
    if type_ == DataType.DATETIME.value:
        return dateutil.parser.parse(val)
    if type_ == DataType.NUMERICAL.value:
        return float(val)
    if type_ == DataType.BOOLEAN.value:
        return bool(val)
    if type_ in (
        DataType.ARRAY_STRING.value,
        DataType.ARRAY_DATETIME.value,
        DataType.ARRAY_NUMERICAL.value,
        DataType.ARRAY_BOOLEAN.value,
    ):
        array_type_mapping = {
            DataType.ARRAY_STRING.value: DataType.STRING.value,
            DataType.ARRAY_DATETIME.value: DataType.DATETIME.value,
            DataType.ARRAY_NUMERICAL.value: DataType.NUMERICAL.value,
            DataType.ARRAY_BOOLEAN.value: DataType.BOOLEAN.value,
        }
        return [str_to_type(v, array_type_mapping[type_]) for v in val]
    raise NotImplementedError(f'Unsure how to handle type "{type_}"')


def ensure_key_exist(data: dict[str, t.Any], keys: t.Iterable[str]) -> None:
    assert set(keys).issubset(data.keys()), f"{', '.join(keys)} are needed"


def camelcase(text: str) -> str:
    """Convert snakecase string into camel case."""
    text = re.sub(r"\w[\s\W]+\w", "", str(text))
    if len(text) == 0:
        return text
    return str(text[0]).lower() + re.sub(r"[\-_\.\s]([a-z])", lambda matched: str(matched.group(1)).upper(), text[1:])


def clean_python_variable_name(variable_name: str) -> str:
    """
    Clean a given string to make it into a valid python variable.

    :param variable_name: Unclean string to use for the variable.
    :return:              The clean valid python variable.
    """
    return re.sub(r"\W|^(?=\d)", "_", variable_name)
