"""I/O helpers for Duck+."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from os import PathLike, fspath
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, TypedDict, Unpack, cast, overload

import duckdb

from . import util
from .connect import DuckConnection
from .core import DuckRel
from .table import DuckTable

Pathish = str | PathLike[str]
PathsLike = Pathish | Sequence[Pathish]

ParquetCompression = Literal[
    "auto",
    "none",
    "uncompressed",
    "snappy",
    "gzip",
    "zstd",
    "lz4",
    "brotli",
]
ParquetVersion = Literal["PARQUET_1_0", "PARQUET_2_0"]


class ParquetReadOptions(TypedDict, total=False):
    """Supported keyword arguments for :func:`read_parquet`."""

    binary_as_string: bool
    file_row_number: bool
    filename: bool
    hive_partitioning: bool
    union_by_name: bool
    can_have_nan: bool
    compression: ParquetCompression
    parquet_version: ParquetVersion
    debug_use_openssl: bool
    explicit_cardinality: int


CSVCompression = Literal["auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"]
CSVDecimalSeparator = Literal[",", "."]
CSVQuoting = Literal["all", "minimal", "nonnumeric", "none"]


class CSVReadOptions(TypedDict, total=False):
    """Supported keyword arguments for :func:`read_csv`."""

    delimiter: str
    quote: str | None
    escape: str | None
    nullstr: str | Sequence[str] | None
    sample_size: int
    auto_detect: bool
    ignore_errors: bool
    dateformat: str
    timestampformat: str
    decimal_separator: CSVDecimalSeparator
    columns: Mapping[str, util.DuckDBType]
    all_varchar: bool
    parallel: bool
    allow_quoted_nulls: bool
    null_padding: bool
    normalize_names: bool
    union_by_name: bool
    filename: bool
    hive_partitioning: bool
    hive_types_autocast: bool
    hive_types: Mapping[str, util.DuckDBType]
    files_to_sniff: int
    compression: CSVCompression
    thousands: str


JSONFormat = Literal["auto", "newline_delimited", "unstructured"]
JSONRecords = Literal["auto", "array", "records"]
JSONCompression = Literal["auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"]


class JSONReadOptions(TypedDict, total=False):
    """Supported keyword arguments for :func:`read_json`."""

    columns: Mapping[str, util.DuckDBType]
    sample_size: int
    maximum_depth: int
    records: JSONRecords
    format: JSONFormat
    dateformat: str
    timestampformat: str
    compression: JSONCompression
    maximum_object_size: int
    ignore_errors: bool
    convert_strings_to_integers: bool
    field_appearance_threshold: float
    map_inference_threshold: int
    maximum_sample_files: int
    filename: bool
    hive_partitioning: bool
    union_by_name: bool
    hive_types: Mapping[str, util.DuckDBType]
    hive_types_autocast: bool
    auto_detect: bool


class ParquetWriteOptions(TypedDict, total=False):
    """Supported keyword arguments for :func:`write_parquet`."""

    row_group_size: int
    row_group_size_bytes: int
    partition_by: Sequence[str]
    write_partition_columns: bool
    per_thread_output: bool


class CSVWriteOptions(TypedDict, total=False):
    """Supported keyword arguments for :func:`write_csv`."""

    delimiter: str
    quote: str | None
    escape: str | None
    null_rep: str | None
    date_format: str | None
    timestamp_format: str | None
    quoting: CSVQuoting
    compression: CSVCompression
    per_thread_output: bool
    partition_by: Sequence[str]
    write_partition_columns: bool


@dataclass(slots=True)
class _ValidatedPaths:
    """Container for normalized path inputs."""

    as_list: list[str]
    for_duckdb: str | list[str]


@overload
def _normalize_paths(paths: Pathish) -> _ValidatedPaths:  # pragma: no cover - overload
    ...


@overload
def _normalize_paths(paths: Sequence[Pathish]) -> _ValidatedPaths:  # pragma: no cover - overload
    ...


def _normalize_paths(paths: PathsLike) -> _ValidatedPaths:
    """Return normalized string paths for DuckDB operations."""

    if isinstance(paths, (str, bytes)) or isinstance(paths, PathLike):
        items: list[Pathish] = [paths]
    else:
        if not isinstance(paths, Sequence):
            raise TypeError(
                "Paths must be provided as a path-like object or a sequence of path-like objects; "
                f"received {type(paths).__name__}."
            )
        items = list(paths)
        if not items:
            raise ValueError("At least one path is required for IO operations.")

    normalized: list[str] = []
    for index, item in enumerate(items):
        try:
            rendered = fspath(item)
        except TypeError as exc:  # pragma: no cover - defensive; exercised via TypeError below
            raise TypeError(
                "Paths must implement __fspath__; "
                f"item {index} is of type {type(item).__name__}."
            ) from exc
        if not isinstance(rendered, str):
            raise TypeError(
                "__fspath__ returned a non-string value; "
                f"item {index} produced {type(rendered).__name__}."
            )
        if not rendered:
            raise ValueError(f"Resolved path at position {index} is empty.")
        normalized.append(rendered)

    payload: str | list[str] = normalized[0] if len(normalized) == 1 else normalized
    return _ValidatedPaths(as_list=normalized, for_duckdb=payload)


def _ensure_path(path: Pathish) -> Path:
    """Return *path* as a :class:`Path` instance."""

    if isinstance(path, Path):
        candidate = path
    else:
        try:
            rendered = fspath(path)
        except TypeError as exc:  # pragma: no cover - defensive
            raise TypeError(
                "Path must implement __fspath__; "
                f"received {type(path).__name__}."
            ) from exc
        if not isinstance(rendered, str):
            raise TypeError(
                "__fspath__ returned a non-string value; "
                f"received {type(rendered).__name__}."
            )
        candidate = Path(rendered)
    if not str(candidate):
        raise ValueError("Target path must not be empty.")
    return candidate


def _validate_partition_columns(columns: Sequence[str], *, option: str) -> list[str]:
    validated: list[str] = []
    for index, column in enumerate(columns):
        if not isinstance(column, str):
            raise TypeError(
                f"{option} must contain strings; element {index} has type {type(column).__name__}."
            )
        if not column:
            raise ValueError(f"{option} must not contain empty column names (index {index}).")
        validated.append(column)
    return validated


def _validate_column_types(option: str, mapping: Mapping[str, util.DuckDBType]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in mapping.items():
        if not isinstance(key, str):
            raise TypeError(
                f"Keys in {option} must be strings; received {type(key).__name__}."
            )
        if value not in util.DUCKDB_TYPE_SET:
            raise ValueError(
                f"Unsupported DuckDB type {value!r} provided for column {key!r} in {option}."
            )
        normalized[key] = value
    return normalized


def _validate_csv_common(options: CSVReadOptions) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    delimiter = options.get("delimiter")
    if delimiter is not None:
        if not isinstance(delimiter, str) or not delimiter:
            raise TypeError("delimiter must be provided as a non-empty string when set.")
        normalized["delimiter"] = delimiter

    quote = options.get("quote")
    if quote is not None:
        if quote != "" and (not isinstance(quote, str) or len(quote) != 1):
            raise TypeError("quote must be a single character or an empty string.")
        normalized["quote"] = quote

    escape = options.get("escape")
    if escape is not None:
        if escape != "" and (not isinstance(escape, str) or len(escape) != 1):
            raise TypeError("escape must be a single character or an empty string.")
        normalized["escape"] = escape

    nullstr = options.get("nullstr")
    if nullstr is not None:
        if isinstance(nullstr, (str, bytes)):
            normalized["nullstr"] = str(nullstr)
        elif isinstance(nullstr, Sequence):
            values: list[str] = []
            for index, element in enumerate(nullstr):
                if not isinstance(element, (str, bytes)):
                    raise TypeError(
                        "nullstr sequences must contain strings; "
                        f"element {index} has type {type(element).__name__}."
                    )
                values.append(str(element))
            normalized["nullstr"] = values
        else:
            raise TypeError(
                "nullstr must be a string or a sequence of strings when provided."
            )

    sample_size = options.get("sample_size")
    if sample_size is not None:
        if not isinstance(sample_size, int) or sample_size < 0:
            raise ValueError("sample_size must be a non-negative integer when provided.")
        normalized["sample_size"] = sample_size

    auto_detect = options.get("auto_detect")
    if auto_detect is not None:
        if not isinstance(auto_detect, bool):
            raise TypeError("auto_detect must be a boolean when provided.")
        normalized["auto_detect"] = auto_detect

    ignore_errors = options.get("ignore_errors")
    if ignore_errors is not None:
        if not isinstance(ignore_errors, bool):
            raise TypeError("ignore_errors must be a boolean when provided.")
        normalized["ignore_errors"] = ignore_errors

    dateformat = options.get("dateformat")
    if dateformat is not None:
        if not isinstance(dateformat, str) or not dateformat:
            raise TypeError("dateformat must be a non-empty string when provided.")
        normalized["dateformat"] = dateformat

    timestampformat = options.get("timestampformat")
    if timestampformat is not None:
        if not isinstance(timestampformat, str) or not timestampformat:
            raise TypeError(
                "timestampformat must be a non-empty string when provided."
            )
        normalized["timestampformat"] = timestampformat

    decimal_separator = options.get("decimal_separator")
    if decimal_separator is not None:
        if decimal_separator not in (",", "."):
            raise ValueError("decimal_separator must be ',' or '.' when provided.")
        normalized["decimal_separator"] = decimal_separator

    columns = options.get("columns")
    if columns is not None:
        normalized["columns"] = _validate_column_types("columns", columns)

    all_varchar = options.get("all_varchar")
    if all_varchar is not None:
        if not isinstance(all_varchar, bool):
            raise TypeError("all_varchar must be a boolean when provided.")
        normalized["all_varchar"] = all_varchar

    parallel = options.get("parallel")
    if parallel is not None:
        if not isinstance(parallel, bool):
            raise TypeError("parallel must be a boolean when provided.")
        normalized["parallel"] = parallel

    allow_quoted_nulls = options.get("allow_quoted_nulls")
    if allow_quoted_nulls is not None:
        if not isinstance(allow_quoted_nulls, bool):
            raise TypeError("allow_quoted_nulls must be a boolean when provided.")
        normalized["allow_quoted_nulls"] = allow_quoted_nulls

    null_padding = options.get("null_padding")
    if null_padding is not None:
        if not isinstance(null_padding, bool):
            raise TypeError("null_padding must be a boolean when provided.")
        normalized["null_padding"] = null_padding

    normalize_names = options.get("normalize_names")
    if normalize_names is not None:
        if not isinstance(normalize_names, bool):
            raise TypeError("normalize_names must be a boolean when provided.")
        normalized["normalize_names"] = normalize_names

    union_by_name = options.get("union_by_name")
    if union_by_name is not None:
        if not isinstance(union_by_name, bool):
            raise TypeError("union_by_name must be a boolean when provided.")
        normalized["union_by_name"] = union_by_name

    filename = options.get("filename")
    if filename is not None:
        if not isinstance(filename, bool):
            raise TypeError("filename must be a boolean when provided.")
        normalized["filename"] = filename

    hive_partitioning = options.get("hive_partitioning")
    if hive_partitioning is not None:
        if not isinstance(hive_partitioning, bool):
            raise TypeError("hive_partitioning must be a boolean when provided.")
        normalized["hive_partitioning"] = hive_partitioning

    hive_types_autocast = options.get("hive_types_autocast")
    if hive_types_autocast is not None:
        if not isinstance(hive_types_autocast, bool):
            raise TypeError("hive_types_autocast must be a boolean when provided.")
        normalized["hive_types_autocast"] = hive_types_autocast

    hive_types = options.get("hive_types")
    if hive_types is not None:
        normalized["hive_types"] = _validate_column_types("hive_types", hive_types)

    files_to_sniff = options.get("files_to_sniff")
    if files_to_sniff is not None:
        if not isinstance(files_to_sniff, int) or files_to_sniff < 0:
            raise ValueError("files_to_sniff must be a non-negative integer when provided.")
        normalized["files_to_sniff"] = files_to_sniff

    compression = options.get("compression")
    if compression is not None:
        if compression not in {"auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"}:
            raise ValueError(
                "compression must be one of 'auto', 'none', 'gzip', 'zstd', 'bz2', 'lz4', 'xz', or 'snappy'."
            )
        normalized["compression"] = compression

    thousands = options.get("thousands")
    if thousands is not None:
        if not isinstance(thousands, str) or len(thousands) != 1:
            raise TypeError("thousands must be a single character when provided.")
        normalized["thousands"] = thousands

    return normalized


def _validate_json_options(options: JSONReadOptions) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    columns = options.get("columns")
    if columns is not None:
        normalized["columns"] = _validate_column_types("columns", columns)

    sample_size = options.get("sample_size")
    if sample_size is not None:
        if not isinstance(sample_size, int) or sample_size < 0:
            raise ValueError("sample_size must be a non-negative integer when provided.")
        normalized["sample_size"] = sample_size

    maximum_depth = options.get("maximum_depth")
    if maximum_depth is not None:
        if not isinstance(maximum_depth, int) or maximum_depth < 0:
            raise ValueError("maximum_depth must be a non-negative integer when provided.")
        normalized["maximum_depth"] = maximum_depth

    records = options.get("records")
    if records is not None:
        if records not in {"auto", "array", "records"}:
            raise ValueError("records must be 'auto', 'array', or 'records'.")
        normalized["records"] = records

    format_value = options.get("format")
    if format_value is not None:
        if format_value not in {"auto", "newline_delimited", "unstructured"}:
            raise ValueError(
                "format must be 'auto', 'newline_delimited', or 'unstructured'."
            )
        normalized["format"] = format_value

    dateformat = options.get("dateformat")
    if dateformat is not None:
        if not isinstance(dateformat, str) or not dateformat:
            raise TypeError("dateformat must be a non-empty string when provided.")
        normalized["dateformat"] = dateformat

    timestampformat = options.get("timestampformat")
    if timestampformat is not None:
        if not isinstance(timestampformat, str) or not timestampformat:
            raise TypeError(
                "timestampformat must be a non-empty string when provided."
            )
        normalized["timestampformat"] = timestampformat

    compression = options.get("compression")
    if compression is not None:
        if compression not in {"auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"}:
            raise ValueError(
                "compression must be one of 'auto', 'none', 'gzip', 'zstd', 'bz2', 'lz4', 'xz', or 'snappy'."
            )
        normalized["compression"] = compression

    maximum_object_size = options.get("maximum_object_size")
    if maximum_object_size is not None:
        if not isinstance(maximum_object_size, int) or maximum_object_size < 0:
            raise ValueError(
                "maximum_object_size must be a non-negative integer when provided."
            )
        normalized["maximum_object_size"] = maximum_object_size

    ignore_errors = options.get("ignore_errors")
    if ignore_errors is not None:
        if not isinstance(ignore_errors, bool):
            raise TypeError("ignore_errors must be a boolean when provided.")
        normalized["ignore_errors"] = ignore_errors

    convert_strings_to_integers = options.get("convert_strings_to_integers")
    if convert_strings_to_integers is not None:
        if not isinstance(convert_strings_to_integers, bool):
            raise TypeError(
                "convert_strings_to_integers must be a boolean when provided."
            )
        normalized["convert_strings_to_integers"] = convert_strings_to_integers

    field_appearance_threshold = options.get("field_appearance_threshold")
    if field_appearance_threshold is not None:
        if not isinstance(field_appearance_threshold, (int, float)):
            raise TypeError(
                "field_appearance_threshold must be numeric when provided."
            )
        normalized["field_appearance_threshold"] = float(field_appearance_threshold)

    map_inference_threshold = options.get("map_inference_threshold")
    if map_inference_threshold is not None:
        if not isinstance(map_inference_threshold, int) or map_inference_threshold < 0:
            raise ValueError(
                "map_inference_threshold must be a non-negative integer when provided."
            )
        normalized["map_inference_threshold"] = map_inference_threshold

    maximum_sample_files = options.get("maximum_sample_files")
    if maximum_sample_files is not None:
        if not isinstance(maximum_sample_files, int) or maximum_sample_files < 0:
            raise ValueError(
                "maximum_sample_files must be a non-negative integer when provided."
            )
        normalized["maximum_sample_files"] = maximum_sample_files

    filename = options.get("filename")
    if filename is not None:
        if not isinstance(filename, bool):
            raise TypeError("filename must be a boolean when provided.")
        normalized["filename"] = filename

    hive_partitioning = options.get("hive_partitioning")
    if hive_partitioning is not None:
        if not isinstance(hive_partitioning, bool):
            raise TypeError("hive_partitioning must be a boolean when provided.")
        normalized["hive_partitioning"] = hive_partitioning

    union_by_name = options.get("union_by_name")
    if union_by_name is not None:
        if not isinstance(union_by_name, bool):
            raise TypeError("union_by_name must be a boolean when provided.")
        normalized["union_by_name"] = union_by_name

    hive_types = options.get("hive_types")
    if hive_types is not None:
        normalized["hive_types"] = _validate_column_types("hive_types", hive_types)

    hive_types_autocast = options.get("hive_types_autocast")
    if hive_types_autocast is not None:
        if not isinstance(hive_types_autocast, bool):
            raise TypeError(
                "hive_types_autocast must be a boolean when provided."
            )
        normalized["hive_types_autocast"] = hive_types_autocast

    auto_detect = options.get("auto_detect")
    if auto_detect is not None:
        if not isinstance(auto_detect, bool):
            raise TypeError("auto_detect must be a boolean when provided.")
        normalized["auto_detect"] = auto_detect

    return normalized


def _validate_parquet_read_options(options: ParquetReadOptions) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for key in (
        "binary_as_string",
        "file_row_number",
        "filename",
        "hive_partitioning",
        "union_by_name",
        "can_have_nan",
        "debug_use_openssl",
    ):
        value = options.get(key)
        if value is not None:
            if not isinstance(value, bool):
                raise TypeError(f"{key} must be a boolean when provided.")
            normalized[key] = value

    compression = options.get("compression")
    if compression is not None:
        if compression not in {
            "auto",
            "none",
            "uncompressed",
            "snappy",
            "gzip",
            "zstd",
            "lz4",
            "brotli",
        }:
            raise ValueError(
                "compression must be one of 'auto', 'none', 'uncompressed', 'snappy', 'gzip', 'zstd', 'lz4', or 'brotli'."
            )
        normalized["compression"] = compression

    parquet_version = options.get("parquet_version")
    if parquet_version is not None:
        if parquet_version not in {"PARQUET_1_0", "PARQUET_2_0"}:
            raise ValueError(
                "parquet_version must be 'PARQUET_1_0' or 'PARQUET_2_0' when provided."
            )
        normalized["parquet_version"] = parquet_version

    explicit_cardinality = options.get("explicit_cardinality")
    if explicit_cardinality is not None:
        if not isinstance(explicit_cardinality, int) or explicit_cardinality < 0:
            raise ValueError(
                "explicit_cardinality must be a non-negative integer when provided."
            )
        normalized["explicit_cardinality"] = explicit_cardinality

    return normalized


def _validate_parquet_write_options(options: ParquetWriteOptions) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    row_group_size = options.get("row_group_size")
    if row_group_size is not None:
        if not isinstance(row_group_size, int) or row_group_size <= 0:
            raise ValueError("row_group_size must be a positive integer when provided.")
        normalized["row_group_size"] = row_group_size

    row_group_size_bytes = options.get("row_group_size_bytes")
    if row_group_size_bytes is not None:
        if not isinstance(row_group_size_bytes, int) or row_group_size_bytes <= 0:
            raise ValueError(
                "row_group_size_bytes must be a positive integer when provided."
            )
        normalized["row_group_size_bytes"] = row_group_size_bytes

    partition_by = options.get("partition_by")
    if partition_by is not None:
        normalized["partition_by"] = _validate_partition_columns(partition_by, option="partition_by")

    write_partition_columns = options.get("write_partition_columns")
    if write_partition_columns is not None:
        if not isinstance(write_partition_columns, bool):
            raise TypeError(
                "write_partition_columns must be a boolean when provided."
            )
        normalized["write_partition_columns"] = write_partition_columns

    per_thread_output = options.get("per_thread_output")
    if per_thread_output is not None:
        if not isinstance(per_thread_output, bool):
            raise TypeError(
                "per_thread_output must be a boolean when provided."
            )
        normalized["per_thread_output"] = per_thread_output

    return normalized


def _validate_csv_write_options(options: CSVWriteOptions) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    delimiter = options.get("delimiter")
    if delimiter is not None:
        if not isinstance(delimiter, str) or not delimiter:
            raise TypeError("delimiter must be a non-empty string when provided.")
        normalized["sep"] = delimiter

    quote = options.get("quote")
    if quote is not None:
        if quote != "" and (not isinstance(quote, str) or len(quote) != 1):
            raise TypeError("quote must be a single character or empty string when provided.")
        normalized["quotechar"] = quote

    escape = options.get("escape")
    if escape is not None:
        if escape != "" and (not isinstance(escape, str) or len(escape) != 1):
            raise TypeError("escape must be a single character or empty string when provided.")
        normalized["escapechar"] = escape

    null_rep = options.get("null_rep")
    if null_rep is not None:
        if null_rep != "" and (not isinstance(null_rep, str)):
            raise TypeError("null_rep must be a string when provided.")
        normalized["na_rep"] = null_rep

    date_format = options.get("date_format")
    if date_format is not None:
        if not isinstance(date_format, str) or not date_format:
            raise TypeError("date_format must be a non-empty string when provided.")
        normalized["date_format"] = date_format

    timestamp_format = options.get("timestamp_format")
    if timestamp_format is not None:
        if not isinstance(timestamp_format, str) or not timestamp_format:
            raise TypeError(
                "timestamp_format must be a non-empty string when provided."
            )
        normalized["timestamp_format"] = timestamp_format

    quoting = options.get("quoting")
    if quoting is not None:
        if quoting not in {"all", "minimal", "nonnumeric", "none"}:
            raise ValueError(
                "quoting must be one of 'all', 'minimal', 'nonnumeric', or 'none'."
            )
        normalized["quoting"] = quoting

    compression = options.get("compression")
    if compression is not None:
        if compression not in {"auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"}:
            raise ValueError(
                "compression must be one of 'auto', 'none', 'gzip', 'zstd', 'bz2', 'lz4', 'xz', or 'snappy'."
            )
        normalized["compression"] = compression

    per_thread_output = options.get("per_thread_output")
    if per_thread_output is not None:
        if not isinstance(per_thread_output, bool):
            raise TypeError(
                "per_thread_output must be a boolean when provided."
            )
        normalized["per_thread_output"] = per_thread_output

    partition_by = options.get("partition_by")
    if partition_by is not None:
        normalized["partition_by"] = _validate_partition_columns(partition_by, option="partition_by")

    write_partition_columns = options.get("write_partition_columns")
    if write_partition_columns is not None:
        if not isinstance(write_partition_columns, bool):
            raise TypeError(
                "write_partition_columns must be a boolean when provided."
            )
        normalized["write_partition_columns"] = write_partition_columns

    return normalized


def _execute_duckdb_reader(
    func: Callable[..., duckdb.DuckDBPyRelation],
    description: str,
    payload: str | list[str],
    *,
    options: dict[str, Any],
) -> duckdb.DuckDBPyRelation:
    try:
        return func(payload, **options)
    except duckdb.Error as exc:
        detail = str(exc).strip()
        hint = f" DuckDB error: {detail}" if detail else ""
        raise RuntimeError(
            f"DuckDB failed to {description}; check the provided options and file paths.{hint}"
        ) from exc


def read_parquet(
    conn: DuckConnection,
    paths: PathsLike,
    /,
    **options: Unpack[ParquetReadOptions],
) -> DuckRel:
    """Read Parquet files into a :class:`duckplus.DuckRel`.

    Parameters
    ----------
    conn:
        Connection that will execute the DuckDB read.
    paths:
        A :class:`~pathlib.Path`, ``os.DirEntry`` or any ``__fspath__`` value, or a
        non-empty sequence of such paths.
    ``**options``:
        Keyword arguments forwarded to :meth:`duckdb.DuckDBPyConnection.read_parquet`
        after type validation.

    Supported options
    -----------------
    binary_as_string: bool
        Treat Parquet ``BINARY`` columns as strings.
    file_row_number: bool
        Add a row-number column per file.
    filename: bool
        Add a column containing the originating file name.
    hive_partitioning: bool
        Enable Hive partition discovery for directory inputs.
    union_by_name: bool
        Align schemas by column name when files differ.
    can_have_nan: bool
        Permit ``NaN`` values inside statistics.
    compression: ``Literal["auto", "none", "uncompressed", "snappy", "gzip", "zstd", "lz4", "brotli"]``
        Override the compression codec DuckDB expects in the source file.
    parquet_version: ``Literal["PARQUET_1_0", "PARQUET_2_0"]``
        Force DuckDB to interpret the files as the specified Parquet version.
    debug_use_openssl: bool
        Prefer OpenSSL over the builtin crypto routines.
    explicit_cardinality: int
        Provide an expected row count for planner optimisations.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import connect
    >>> with connect() as conn:
    ...     rel = conn.read_parquet(
    ...         [Path("/data/events/2024-05-01.parquet")],
    ...         union_by_name=True,
    ...         filename=True,
    ...     )
    ...     rel.columns
    ...
    """

    normalized = _normalize_paths(paths)
    read_options = _validate_parquet_read_options(options)
    relation = _execute_duckdb_reader(
        conn.raw.read_parquet, "read Parquet data", normalized.for_duckdb, options=read_options
    )
    return DuckRel(relation)


def read_csv(
    conn: DuckConnection,
    paths: PathsLike,
    /,
    *,
    encoding: str = "utf-8",
    header: bool = True,
    **options: Unpack[CSVReadOptions],
) -> DuckRel:
    """Read CSV files into a :class:`duckplus.DuckRel`.

    Parameters
    ----------
    conn:
        Connection that will execute the DuckDB read.
    paths:
        A :class:`~pathlib.Path`, ``os.DirEntry`` or any ``__fspath__`` value, or a
        non-empty sequence of such paths.
    encoding:
        Text encoding name supplied to DuckDB (defaults to ``"utf-8"``).
    header:
        Either ``True``/``False`` to indicate whether the file includes a header
        row or an integer index for the header line.
    ``**options``:
        Additional keyword arguments validated against DuckDB's CSV reader.

    Supported options
    -----------------
    delimiter: str
        Column delimiter (defaults to ",").
    quote: str | None
        Single-character quote marker or ``None`` to disable quoting.
    escape: str | None
        Escape character used for quoted fields.
    nullstr: str | Sequence[str] | None
        Values interpreted as SQL ``NULL``.
    sample_size: int
        Number of bytes to scan for auto-detection.
    auto_detect: bool
        Enable DuckDB's schema auto-detection.
    ignore_errors: bool
        Skip malformed rows instead of raising.
    dateformat: str
        Format string for DATE columns.
    timestampformat: str
        Format string for TIMESTAMP columns.
    decimal_separator: ``Literal[",", "."]``
        Decimal separator when parsing numeric values.
    columns: Mapping[str, :data:`duckplus.util.DuckDBType`]
        Explicit column type mapping.
    all_varchar: bool
        Force every column to be ``VARCHAR``.
    parallel: bool
        Allow parallel CSV parsing.
    allow_quoted_nulls: bool
        Interpret quoted ``nullstr`` values as ``NULL``.
    null_padding: bool
        Enable null padding for fixed-width values.
    normalize_names: bool
        Request DuckDB to normalise column identifiers.
    union_by_name: bool
        Align schemas by column name when loading multiple files.
    filename: bool
        Add a column containing the originating file name.
    hive_partitioning: bool
        Enable Hive partition discovery for directory inputs.
    hive_types_autocast: bool
        Automatically cast partition values based on Hive metadata.
    hive_types: Mapping[str, :data:`duckplus.util.DuckDBType`]
        Override Hive partition column types.
    files_to_sniff: int
        Limit the number of files inspected for schema inference.
    compression: ``Literal["auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"]``
        Compression codec to expect from the source files.
    thousands: str
        Thousands separator for numeric parsing.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import connect
    >>> with connect() as conn:
    ...     rel = conn.read_csv(
    ...         [Path("/data/customers.csv")],
    ...         delimiter="|",
    ...         dateformat="%Y-%m-%d",
    ...     )
    ...     rel.columns
    ...
    """

    if not isinstance(encoding, str) or not encoding:
        raise TypeError("encoding must be provided as a non-empty string.")

    if not isinstance(header, (bool, int)):
        raise TypeError("header must be a boolean or integer value.")

    normalized = _normalize_paths(paths)
    read_options = _validate_csv_common(options)
    read_options["encoding"] = encoding
    read_options["header"] = header

    relation = _execute_duckdb_reader(
        conn.raw.read_csv, "read CSV data", normalized.for_duckdb, options=read_options
    )
    return DuckRel(relation)


def read_json(
    conn: DuckConnection,
    paths: PathsLike,
    /,
    **options: Unpack[JSONReadOptions],
) -> DuckRel:
    """Read JSON or NDJSON files into a :class:`duckplus.DuckRel`.

    Parameters
    ----------
    conn:
        Connection that will execute the DuckDB read.
    paths:
        A :class:`~pathlib.Path`, ``os.DirEntry`` or any ``__fspath__`` value, or a
        non-empty sequence of such paths.
    ``**options``:
        Keyword arguments forwarded to DuckDB's JSON reader.

    Supported options
    -----------------
    columns: Mapping[str, :data:`duckplus.util.DuckDBType`]
        Explicit column type mapping.
    sample_size: int
        Number of bytes sampled for schema detection.
    maximum_depth: int
        Depth limit for nested objects.
    records: ``Literal["auto", "array", "records"]``
        Interpret the input as a JSON array, individual records, or let DuckDB
        auto-detect.
    format: ``Literal["auto", "newline_delimited", "unstructured"]``
        Choose between JSON, NDJSON, or unstructured log parsing.
    dateformat: str
        Format string for DATE coercion.
    timestampformat: str
        Format string for TIMESTAMP coercion.
    compression: ``Literal["auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"]``
        Compression codec to expect when reading files.
    maximum_object_size: int
        Upper bound on parsed JSON object size.
    ignore_errors: bool
        Skip malformed records instead of raising.
    convert_strings_to_integers: bool
        Attempt integer coercion for numeric-looking strings.
    field_appearance_threshold: float
        Fraction of rows required before creating a struct field.
    map_inference_threshold: int
        Minimum object size before inferring a ``MAP`` type.
    maximum_sample_files: int
        Number of files sampled during auto-detection.
    filename: bool
        Add a column containing the originating file name.
    hive_partitioning: bool
        Enable Hive partition discovery for directory inputs.
    union_by_name: bool
        Align schemas by column name when loading multiple files.
    hive_types: Mapping[str, :data:`duckplus.util.DuckDBType`]
        Override Hive partition column types.
    hive_types_autocast: bool
        Automatically cast partition values based on Hive metadata.
    auto_detect: bool
        Let DuckDB infer data types from the sampled data.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import connect
    >>> with connect() as conn:
    ...     rel = conn.read_json(
    ...         [Path("/data/events.ndjson")],
    ...         format="newline_delimited",
    ...         maximum_depth=3,
    ...     )
    ...     rel.columns
    ...
    """

    normalized = _normalize_paths(paths)
    read_options = _validate_json_options(options)
    relation = _execute_duckdb_reader(
        conn.raw.read_json, "read JSON data", normalized.for_duckdb, options=read_options
    )
    return DuckRel(relation)


def _write_with_temporary(
    relation: duckdb.DuckDBPyRelation,
    target: Path,
    *,
    writer: Any,
    description: str,
    options: dict[str, Any],
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.duckplus_tmp")
    try:
        writer(str(temporary), **options)
        temporary.replace(target)
    except duckdb.Error as exc:
        temporary.unlink(missing_ok=True)
        detail = str(exc).strip()
        hint = f" DuckDB error: {detail}" if detail else ""
        raise RuntimeError(
            f"DuckDB failed to {description}; check the provided options and target path.{hint}"
        ) from exc
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_parquet(
    rel: DuckRel,
    path: Pathish,
    /,
    *,
    compression: ParquetCompression = "zstd",
    **options: Unpack[ParquetWriteOptions],
) -> None:
    """Write a :class:`duckplus.DuckRel` to a Parquet file.

    Parameters
    ----------
    rel:
        Relation to persist.
    path:
        Target file location, converted to :class:`~pathlib.Path`.
    compression:
        Compression codec supplied to DuckDB. Defaults to ``"zstd"``.
    ``**options``:
        Additional DuckDB writer options documented below.

    Supported options
    -----------------
    row_group_size: int
        Number of rows per Parquet row group.
    row_group_size_bytes: int
        Maximum number of bytes per Parquet row group.
    partition_by: Sequence[str]
        Columns used for directory partitioning.
    write_partition_columns: bool
        Persist partition columns in the written files.
    per_thread_output: bool
        Allow DuckDB to emit one file per writer thread.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import connect, write_parquet
    >>> with connect() as conn:
    ...     rel = conn.read_parquet([Path("/data/snapshot.parquet")])
    ...     write_parquet(rel, Path("/exports/snapshot.parquet"), partition_by=["region"])
    ...
    """

    if compression not in {
        "auto",
        "none",
        "uncompressed",
        "snappy",
        "gzip",
        "zstd",
        "lz4",
        "brotli",
    }:
        raise ValueError(
            "compression must be one of 'auto', 'none', 'uncompressed', 'snappy', 'gzip', 'zstd', 'lz4', or 'brotli'."
        )

    target = _ensure_path(path)
    write_options = _validate_parquet_write_options(options)
    write_options["compression"] = compression

    _write_with_temporary(
        rel.relation,
        target,
        writer=rel.relation.write_parquet,
        description="write Parquet data",
        options=write_options,
    )


def write_csv(
    rel: DuckRel,
    path: Pathish,
    /,
    *,
    encoding: str = "utf-8",
    header: bool = True,
    **options: Unpack[CSVWriteOptions],
) -> None:
    """Write a :class:`duckplus.DuckRel` to a CSV file.

    Parameters
    ----------
    rel:
        Relation to persist.
    path:
        Target file location, converted to :class:`~pathlib.Path`.
    encoding:
        Output text encoding (defaults to ``"utf-8"``).
    header:
        Whether DuckDB should emit a header row or the zero-based index of the
        header line.
    ``**options``:
        Additional DuckDB writer options documented below.

    Supported options
    -----------------
    delimiter: str
        Output delimiter (defaults to ",").
    quote: str | None
        Single-character quote marker or ``None`` to disable quoting.
    escape: str | None
        Escape character used for quoted fields.
    null_rep: str | None
        Representation for ``NULL`` values.
    date_format: str | None
        Format string for DATE values.
    timestamp_format: str | None
        Format string for TIMESTAMP values.
    quoting: ``Literal["all", "minimal", "nonnumeric", "none"]``
        Control DuckDB's quoting policy.
    compression: ``Literal["auto", "none", "gzip", "zstd", "bz2", "lz4", "xz", "snappy"]``
        Compression codec applied to the output file.
    per_thread_output: bool
        Allow DuckDB to emit one file per writer thread.
    partition_by: Sequence[str]
        Columns used for directory partitioning.
    write_partition_columns: bool
        Persist partition columns in the written files.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import connect, write_csv
    >>> with connect() as conn:
    ...     rel = conn.read_csv([Path("/data/source.csv")])
    ...     write_csv(rel, Path("/exports/source.csv"), quoting="nonnumeric")
    ...
    """

    if not isinstance(encoding, str) or not encoding:
        raise TypeError("encoding must be provided as a non-empty string.")

    if not isinstance(header, (bool, int)):
        raise TypeError("header must be a boolean or integer value.")

    target = _ensure_path(path)
    write_options = _validate_csv_write_options(options)
    write_options["encoding"] = encoding
    write_options["header"] = header

    _write_with_temporary(
        rel.relation,
        target,
        writer=rel.relation.write_csv,
        description="write CSV data",
        options=write_options,
    )


def append_csv(
    table: DuckTable,
    path: Pathish,
    /,
    *,
    encoding: str = "utf-8",
    header: bool = True,
    **options: Unpack[CSVReadOptions],
) -> None:
    """Append rows from a CSV file into *table*.

    Parameters
    ----------
    table:
        Destination mutable table wrapper.
    path:
        CSV file to read. Accepts the same path types as :func:`read_csv`.
    ``encoding``, ``header``, ``**options``:
        Forwarded to :func:`read_csv`; see its documentation for the complete
        option reference.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import DuckTable, connect
    >>> with connect("warehouse.duckdb") as conn:
    ...     table = DuckTable(conn, "staging.customers")
    ...     table.append_csv(Path("/loads/customers_delta.csv"), delimiter="|")
    ...
    """

    rel = read_csv(
        table._connection,
        path,
        encoding=encoding,
        header=header,
        **options,
    )
    table.append(rel)


def append_parquet(
    table: DuckTable,
    paths: PathsLike,
    /,
    **options: Unpack[ParquetReadOptions],
) -> None:
    """Append rows from Parquet files into *table*.

    Parameters
    ----------
    table:
        Destination mutable table wrapper.
    paths:
        File or directory inputs accepted by :func:`read_parquet`.
    ``**options``:
        Forwarded to :func:`read_parquet`; see its documentation for supported
        arguments.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import DuckTable, connect
    >>> with connect("warehouse.duckdb") as conn:
    ...     table = DuckTable(conn, "analytics.fact_orders")
    ...     table.append_parquet([Path("/loads/fact_orders/*.parquet")], union_by_name=True)
    ...
    """

    rel = read_parquet(table._connection, paths, **options)
    table.append(rel)


def append_ndjson(
    table: DuckTable,
    path: Pathish,
    /,
    **options: Unpack[JSONReadOptions],
) -> None:
    """Append rows from an NDJSON file into *table*.

    Parameters
    ----------
    table:
        Destination mutable table wrapper.
    path:
        NDJSON file to read. Accepts the same path types as :func:`read_json`.
    ``**options``:
        Forwarded to :func:`read_json`. ``format`` defaults to
        ``"newline_delimited"`` when omitted.

    Examples
    --------
    >>> from pathlib import Path
    >>> from duckplus import DuckTable, connect
    >>> with connect("warehouse.duckdb") as conn:
    ...     table = DuckTable(conn, "analytics.fact_events")
    ...     table.append_ndjson(Path("/loads/events.ndjson"), maximum_depth=5)
    ...
    """

    json_options: dict[str, Any] = dict(options)
    json_options.setdefault("format", "newline_delimited")

    rel = read_json(table._connection, path, **cast(JSONReadOptions, json_options))
    table.append(rel)


__all__ = [
    "append_csv",
    "append_parquet",
    "append_ndjson",
    "read_csv",
    "read_json",
    "read_parquet",
    "write_csv",
    "write_parquet",
]
