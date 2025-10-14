import atexit
import pickle
import signal
import sqlite3
import time
from datetime import date, datetime
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace, MethodType
from typing import Type

import pandas as pd
from loguru import logger as log
from pandas import DataFrame
from toomanyconfigs import CWD, TOMLConfig


@property
def row_count(self):
    return len(self)


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


def get_title(self, index):
    return self.at[index, self.title]


def get_subtitle(self, index):
    return self.at[index, self.subtitle]


class Config(TOMLConfig):
    password: str = None


class PickleChangelog:
    def __init__(self, database: 'Database'):
        self.database = database
        self.path = self.database._cwd.file_structure[1]
        self.changelog: dict = {}
        self.fetch()

    def __repr__(self):
        return f"[{self.path.name}]"

    def fetch(self):
        try:
            with open(self.path, 'rb') as f:
                self.changelog = pickle.load(f)
            log.debug(f"{self}: Loaded changelog.")
        except (FileNotFoundError, EOFError):
            log.debug("No existing changelog found or empty file, starting fresh")

    def commit(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.changelog, f)

    def log_change(self, signature: str, table_name: str, change_type: str):
        if not (sig := self.changelog.get(signature)):
            self.changelog[signature] = sig = {}
        if not (tbl := sig.get(table_name)):
            sig[table_name] = tbl = {}
        if not (chg := tbl.get(change_type)):
            tbl[change_type] = chg = 0
        tbl[change_type] = chg + 1


class TableIndex(dict):
    list: list = []

    def __init__(self):
        super().__init__()

class Database:
    def __init__(
            self,
            db_name=None,
    ):
        try:
            _ = self._tables
        except KeyError:
            pass
        if db_name is None: db_name = "my_database"
        if not isinstance(db_name, str): raise RuntimeError
        self._name = db_name
        db = f"{self._name}.db"
        backups = "backups"
        self._cwd = CWD({
            f"{self._name}": {
                db: None,
                "changes.pkl": None,
                "config.toml": None,
                backups: {}
            }
        })
        self._path: Path = self._cwd.file_structure[0]
        self._backups: Path = self._cwd.cwd / self._name / backups
        self._default_columns = ["created_at", "created_by", "modified_at", "modified_by"] #TODO: Add default column support in schema class declaration
        self._unique_keys = {}

        # initialize schema
        for item in self.__annotations__.items():
            a, t = item
            if a.startswith("_"): continue
            if hasattr(self, a): continue
            df, unique_keys = empty_dataframe_from_type(t, self._default_columns)
            df.insert(0, 'created_at', pd.Series(dtype='str'))
            df.insert(1, 'created_by', pd.Series(dtype='str'))
            df.insert(2, 'modified_at', pd.Series(dtype='str'))
            df.insert(3, 'modified_by', pd.Series(dtype='str'))
            setattr(self, a, df)
            self._unique_keys[a] = unique_keys

        self._fetch()
        _ = self._pkl

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        log.debug(f"Received signal {signum}, committing database")
        self._commit()
        self._pkl.commit()
        exit(0)

    def __repr__(self):
        return f"[{self._name}.db]"

    @cached_property
    def _pkl(self) -> PickleChangelog:
        return PickleChangelog(self)

    @cached_property
    def _analytics(self):
        metadata = {}
        for item in self._tables.list:
            metadata["row_count"] = len(item)
            metadata["column_count"] = len(item.columns)
            bytes_value = int(item.memory_usage(deep=False).sum())
            metadata["size_bytes"] = bytes_value
            metadata["size_kilobytes"] = round(bytes_value / 1024, 2)
            metadata["size_megabytes"] = round(bytes_value / (1024 ** 2), 2)
            metadata["size_gigabytes"] = round(bytes_value / (1024 ** 3), 6)

        return SimpleNamespace(
            **metadata, as_dict=metadata
        )

    @property
    def _tables(self) -> TableIndex:
        index = TableIndex()  # table index is a subclass of dict with a list attribute
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name.startswith("_"): continue
            index[attr_name] = getattr(self, attr_name, None)
            if index[attr_name] is None: raise KeyError
        if index == {}: raise RuntimeError("Cannot initialize a database with no _tables!")
        for item in index.keys():
            index.list.append(getattr(self, item))
        return index

    def _get_table(self, table_name: str):
        """Get a table with NaN values properly handled based on type annotations"""
        table = getattr(self, table_name)
        table_class_name = table_name.capitalize()
        for attr_name, attr_type in self.__annotations__.items():
            if attr_name == table_name:
                type_annotations = attr_type.__annotations__
                break
        else: raise Exception(f"Unable to find type annotations for {table_class_name}")

        for col, expected_type in type_annotations.items():
            if col in table.columns:
                if expected_type == bool:
                    table[col] = table[col].fillna(False).astype(bool)
                elif expected_type == int:
                    table[col] = table[col].fillna(0).astype('int64')
                elif expected_type == float:
                    table[col] = table[col].fillna(0.0).astype('float64')
                elif expected_type == str:
                    table[col] = table[col].fillna('').astype('object')
        return table

    def _backup(self):
        today = date.today()
        folder = self._backups / str(today)

        if not any(self._backups.glob(f"{today}*")):
            log.warning(f"{self}: Backup not found for today! Creating...")
            folder.mkdir(exist_ok=True)
            if folder.exists():
                log.success(f"{self}: Successfully created backup folder at {folder}")
            else:
                raise FileNotFoundError

            for table_name, table_df in self._tables.items():
                backup_path = folder / f"{table_name}.parquet"
                table_df.to_parquet(backup_path)

    def _fetch(self):
        with sqlite3.connect(self._path) as conn:
            successes = 0
            for table_name in self._tables.keys():
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    try:
                        setattr(df, "title", df.columns[4])
                        setattr(df, "get_title", MethodType(get_title, df))
                    except IndexError:
                        pass
                    try:
                        setattr(df, "subtitle", df.columns[5])
                        setattr(df, "get_subtitle", MethodType(get_subtitle, df))
                    except IndexError:
                        pass

                    setattr(self, table_name, df)
                    successes = successes + 1
                    log.debug(f"{self}: Read {table_name} from database")
                except pd.errors.DatabaseError:
                    log.debug(f"{self}: Table {table_name} doesn't exist, keeping empty DataFrame")

            if successes == 0:
                log.warning(f"{self}: No _tables were successfully registered. "
                            f"This probably means the database is empty. Attempting to write...")
                self._commit()
            else:
                log.success(f"{self}: Successfully loaded {successes} _tables from {self._path}")

    def _commit(self):
        self._backup()
        with sqlite3.connect(self._path) as conn:
            for table_name, table_df in self._tables.items():
                df_copy = table_df.copy()
                for col in df_copy.columns:
                    if df_copy[col].dtype == 'datetime64[ns]' or 'datetime' in str(df_copy[col].dtype):
                        df_copy[col] = pd.to_datetime(df_copy[col]).astype('datetime64[ns]').astype(object)

                df_copy.to_sql(table_name, conn, if_exists='replace', index=False)
                log.debug(f"{self}: Wrote {table_name} to database")

    def create(self, table_name: str, signature: str = "system", **kwargs) -> pd.DataFrame:
        """
        Create a new record in the specified table with automatic NaN handling and type enforcement.

        Enforces unique key constraints and automatically sets audit columns (created_at, created_by,
        modified_at, modified_by). If a record with the same unique key already exists, performs
        an update instead of creating a duplicate.

        Args:
            table_name: Name of the table to insert into (must match class annotation)
            signature: User/system identifier for audit trail (default: "system")
            **kwargs: Column values to insert. Complex objects (dict, list) are JSON serialized.

        Returns:
            pd.DataFrame: The updated table with the new record added

        Raises:
            Exception: If table doesn't exist or required fields are missing

        Use Cases:
            # Create a new lead
            db.create("leads", "user123", name="John Doe", email="john@example.com", active=True)

            # Create with auto-generated ID
            db.create("leads", signature="sales_team", name="Jane Smith", priority_level="high")

            # Complex data gets serialized automatically
            db.create("leads", "admin", name="Corp Lead", metadata={"source": "website", "tags": ["vip"]})
        """
        start_time = time.time()
        try:
            table = self._get_table(table_name)
            unique_keys = self._unique_keys[table_name]

            log.debug(f"Creating in {table_name}, unique_keys: {unique_keys}")
            log.debug(f"kwargs: {kwargs}")
            log.debug(f"table type: {type(table)}")

            if unique_keys:
                for key in unique_keys:
                    log.debug(f"Checking unique key: {key}")
                    if key in kwargs and not table.empty and kwargs[key] in table[key].values:
                        log.debug(f"Found existing record with {key}={kwargs[key]}, updating instead")
                        return self.update(table_name, kwargs, signature, **{key: kwargs[key]})

            new_idx = len(table)
            log.debug(f"Adding new row at index: {new_idx}")

            # Set audit columns
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            table.loc[new_idx, 'created_at'] = now_str
            table.loc[new_idx, 'created_by'] = signature
            table.loc[new_idx, 'modified_at'] = now_str
            table.loc[new_idx, 'modified_by'] = signature

            for col, value in kwargs.items():
                log.debug(f"Setting {col} = {value} (type: {type(value)})")

                # Serialize complex objects
                if isinstance(value, (dict, list)):
                    import json
                    value = json.dumps(value)
                    log.debug(f"Serialized {col} to JSON string")

                table.loc[new_idx, col] = value

            self._pkl.log_change(signature, table_name, "create")
            elapsed = time.time() - start_time
            log.debug(f"Created row in {table_name}: {kwargs} (took {elapsed:.4f}s)")
            return table
        except Exception as e:
            log.error(f"Exception in create method: {e}")
            import traceback
            log.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def read(self, table_name: str, **conditions) -> pd.DataFrame:
        """
        Read records from the specified table with automatic NaN cleaning and type enforcement.

        Returns all records if no conditions specified, otherwise filters by exact matches
        on the provided column values. All returned data has NaN values properly handled
        based on column types (bool columns get False, int/float get 0, str get empty string).

        Args:
            table_name: Name of the table to read from
            **conditions: Column=value pairs to filter by (AND logic)

        Returns:
            pd.DataFrame: Filtered records with NaN values cleaned according to type annotations

        Use Cases:
            # Get all leads
            all_leads = db.read("leads")

            # Get leads assigned to specific user
            user_leads = db.read("leads", assigned_to="john_doe")

            # Get high priority active leads
            urgent_leads = db.read("leads", priority_level="high", active=True)

            # Find specific lead by email
            lead = db.read("leads", email="customer@company.com")
        """
        start_time = time.time()
        try:
            table = self._get_table(table_name)

            if not conditions:
                elapsed = time.time() - start_time
                log.debug(f"Read all {len(table)} rows from {table_name} (took {elapsed:.4f}s)")
                return table

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            result = table[mask]
            elapsed = time.time() - start_time
            log.debug(f"Read {len(result)} rows from {table_name} (took {elapsed:.4f}s)")
            return result
        except Exception:
            raise

    def update(self, table_name: str, updates: dict, signature: str = "system", **conditions) -> pd.DataFrame:
        """
        Update existing records in the specified table with automatic audit trail.

        Updates all records matching the condition criteria. Automatically sets modified_at
        and modified_by columns for audit tracking. The updated table is saved back to
        the database instance.

        Args:
            table_name: Name of the table to update
            updates: Dictionary of column=new_value pairs to apply
            signature: User/system identifier for audit trail (default: "system")
            **conditions: Column=value pairs to identify records to update (AND logic)

        Returns:
            pd.DataFrame: The updated table with changes applied

        Raises:
            Exception: If table doesn't exist or update fails

        Use Cases:
            # Update lead status by ID
            db.update("leads", {"status": "closed"}, "sales_rep", id="lead_123")

            # Bulk update all leads assigned to user
            db.update("leads", {"priority_level": "low"}, "manager", assigned_to="former_employee")

            # Update multiple fields at once
            updates = {"status": "qualified", "probability": 75, "notes": "Ready for proposal"}
            db.update("leads", updates, "sales_team", email="prospect@company.com")
        """
        start_time = time.time()
        try:
            table = self._get_table(table_name)

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            # Set audit columns
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            table.loc[mask, 'modified_at'] = now_str
            table.loc[mask, 'modified_by'] = signature

            for col, value in updates.items():
                table.loc[mask, col] = value

            setattr(self, table_name, table)
            updated_count = mask.sum()
            self._pkl.log_change(signature, table_name, "update")
            elapsed = time.time() - start_time
            log.debug(f"Updated {updated_count} rows in {table_name} by {signature} (took {elapsed:.4f}s)")
            return table
        except Exception:
            raise

    def delete(self, table_name: str, signature: str = "system", **conditions) -> pd.DataFrame:
        """
        Delete records from the specified table based on condition criteria.

        Permanently removes all records matching the specified conditions. The operation
        is logged for audit purposes. Use with caution as deletions cannot be undone.

        Args:
            table_name: Name of the table to delete from
            signature: User/system identifier for audit trail (default: "system")
            **conditions: Column=value pairs to identify records to delete (AND logic)

        Returns:
            pd.DataFrame: The updated table with specified records removed

        Raises:
            Exception: If table doesn't exist or delete operation fails

        Use Cases:
            # Delete specific lead by ID
            db.delete("leads", "admin", id="lead_to_remove")

            # Delete all inactive leads older than a certain date
            db.delete("leads", "cleanup_job", active=False, created_by="old_system")

            # Delete test data
            db.delete("leads", "developer", name="Test Lead")

            # Bulk delete by criteria
            db.delete("leads", "data_admin", status="spam", priority_level="low")
        """
        start_time = time.time()
        try:
            table = self._get_table(table_name)

            mask = pd.Series([True] * len(table))
            for col, value in conditions.items():
                mask &= (table[col] == value)

            result = table[~mask].reset_index(drop=True)
            setattr(self, table_name, result)
            deleted_count = len(table) - len(result)
            self._pkl.log_change(signature, table_name, "delete")
            elapsed = time.time() - start_time
            log.debug(f"Deleted {deleted_count} rows from {table_name} by {signature} (took {elapsed:.4f}s)")
            return result
        except Exception:
            raise


Database.c = Database.create
Database.r = Database.read
Database.u = Database.update
Database.d = Database.delete