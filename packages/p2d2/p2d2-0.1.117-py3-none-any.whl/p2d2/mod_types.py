from typing import Type
from loguru import logger as log
import pandas as pd
from pandas import DataFrame
import sqlite3

def python_to_dtype(python_type: type[str | int | float | bool | dict | list]) -> str:
    type_mapping = {
        str: 'object',
        int: 'int64',
        float: 'float64',
        bool: 'bool',
        dict: 'object',
        list: 'object',
    }
    return type_mapping.get(python_type, 'object')


def dtype_to_sql_type(dtype: str) -> str:
    mapping = {
        'int64': 'INTEGER',
        'float64': 'REAL',
        'bool': 'INTEGER',
        'object': 'TEXT',
    }
    return mapping.get(dtype, 'TEXT')


def python_to_sql_type(python_type: type[str | int | float | bool | dict | list]) -> str:
    dtype = python_to_dtype(python_type)
    return dtype_to_sql_type(dtype)


def migrate_table_schema(self, table_name: str, table_type: Type, comparison: dict):
    from . import Database
    self: Database
    if not isinstance(self, Database):
        raise TypeError("This method must be called on a Database instance")

    log.info(f"{self}: Starting schema migration for table '{table_name}'")

    if comparison["only_in_df1"]:
        log.info(f"{self}: Adding {len(comparison['only_in_df1'])} new columns to '{table_name}' DataFrame")

        table_df = getattr(self, table_name)
        type_annotations = table_type.__annotations__

        for col in comparison["only_in_df1"]:
            if col in type_annotations:
                python_type = type_annotations[col]
                dtype = python_to_dtype(python_type)
                table_df[col] = pd.Series(dtype=dtype)
                log.success(f"{self}: Added column '{col}' ({dtype}) to DataFrame '{table_name}'")
            else:
                table_df[col] = pd.Series(dtype='object')
                log.warning(f"{self}: Column '{col}' not found in type annotations, defaulting to 'object'")

        setattr(self, table_name, table_df)

    if comparison["only_in_df2"]:
        log.warning(
            f"{self}: Table '{table_name}' has {len(comparison['only_in_df2'])} columns not in schema: {comparison['only_in_df2']}")
        log.warning(f"{self}: These columns exist in the database but not in your schema definition")
        log.warning(f"{self}: Options: 1) Add them to schema, 2) Manually drop them, 3) Ignore if legacy data")

    log.info(f"{self}: Committing schema changes to database...")
    self._commit()
    log.success(f"{self}: Schema migration completed for table '{table_name}'")

def empty_dataframe_from_type(typ: Type, defvals: list = None) -> tuple[DataFrame, list]:
    log.debug(f"Creating empty DataFrame for type: {typ.__name__}")

    a = typ.__annotations__
    log.debug(f"Found {len(a)} annotated fields: {list(a.keys())}")

    if not defvals:
        defvals = ["id", "created_on", "created_by", "modified_on", "modified_by"]
    log.debug(f"Using default columns: {defvals}")

    # Check for conflicts with default columns
    conflicts = []
    for col in a:
        for name in defvals:
            if col == name:
                conflicts.append(col)

    if conflicts:
        log.error(f"Column conflicts detected: {conflicts}")
        raise KeyError(f"Your database class cannot contain default values: {defvals}")

    log.debug("No column conflicts found")

    # Map Python types to pandas dtypes
    type_mapping = {
        str: 'object',
        int: 'int64',
        float: 'float64',
        bool: 'bool',
        dict: 'object',  # Store as JSON strings
        list: 'object',  # Store as JSON strings
    }

    log.debug("Mapping Python types to pandas dtypes:")

    # Create DataFrame with mapped types
    pandas_types = {}
    for col, python_type in a.items():
        mapped_type = type_mapping.get(python_type, 'object')
        pandas_types[col] = mapped_type
        log.debug(f"  {col}: {python_type.__name__} -> {mapped_type}")

        if python_type not in type_mapping:
            log.warning(f"Unknown type {python_type.__name__} for column {col}, using 'object'")

    log.debug(f"Final pandas dtypes: {pandas_types}")

    try:
        df = pd.DataFrame(columns=list(a.keys())).astype(pandas_types)
        log.success(f"Successfully created DataFrame with shape {df.shape} and columns: {list(df.columns)}")
    except Exception as e:
        log.error(f"Failed to create DataFrame with types {pandas_types}: {e}")
        log.warning("Falling back to default 'object' dtype for all columns")
        df = pd.DataFrame(columns=list(a.keys()))

    # Set up uniqueness constraints
    unique_keys = getattr(typ, '_unique_keys', [])
    if unique_keys:
        log.debug(f"Found unique keys for {typ.__name__}: {unique_keys}")
    else:
        log.debug(f"No unique keys specified for {typ.__name__}")

    log.debug(f"Returning DataFrame with {len(df.columns)} columns and {len(unique_keys)} unique keys")
    return df, unique_keys