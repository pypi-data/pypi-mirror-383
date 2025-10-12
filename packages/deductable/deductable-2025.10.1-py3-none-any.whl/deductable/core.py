from typing import Callable, List, Optional, Union, get_origin, get_args
import inspect
from contextvars import ContextVar
import re

import duckdb
from _duckdb._func import FunctionNullHandling
from duckdb.sqltypes import DuckDBPyType
from loguru import logger
import pandas as pd


def return_is_optional(return_annotation) -> bool:
    origin = get_origin(return_annotation)
    args = get_args(return_annotation)

    # Optional[T] is implemented as Union[T, NoneType]
    if origin is Union and type(None) in args:
        return True

    return False

# Context object to expose current id to column functions
_current_id: ContextVar[Optional[int]] = ContextVar("_current_id", default=None)

class DeductableContext:
    """Context helper to get the current row id inside a column function."""
    @staticmethod
    def get_id() -> Optional[int]:
        return _current_id.get()


class Deductable:
    def __init__(self,
                 con: duckdb.DuckDBPyConnection,
                 table_name: str, ):
        """
        con: DuckDB connection
        table_name: table to manage
        """
        self.con = con
        self.name = table_name

        # registry: list of tuples (func, eager, overwrite)
        # overwrite retained as optional control (defaults False)
        self._registry: List[Callable] = []

        # create table if not exists, ensure id column
        self._ensure_table()

    def _ensure_table(self):
        """
        Ensure the table exists with a clean id column.
        Uses a SEQUENCE to auto-increment the primary key.
        Raises an exception if the table exists but id is missing.
        """
        # Check if table exists
        tables = [r[0] for r in self.con.execute("SHOW TABLES").fetchall()]
        if self.name not in tables:
            raise ValueError(f"no table named {self.name}")
            # Table exists: verify id column exists
        cols = self.columns
        if "id" not in cols:
            raise RuntimeError(
                f"Table '{self.name}' exists but is missing the required 'id' column. "
                "Deductible expects a table with an 'id' primary key."
            )

    @property
    def columns(self) -> List[str]:
        return [r[1] for r in self.con.execute(f"PRAGMA table_info({self.name})").fetchall()]

    @property
    def row_count(self) -> int:
        return int(self.con.execute(f"SELECT COUNT(*) FROM {self.name}").fetchone()[0])

    def column(self, func: Optional[Callable] = None, ):

        def _register(fn: Callable):
            # basic validation
            if not callable(fn):
                raise TypeError("Column target must be callable")
            if inspect.isgeneratorfunction(fn):
                raise TypeError("Column functions must be normal functions that return a value (not generators).")

            sig = inspect.signature(fn)
            fn_return_type = sig.return_annotation
            fn_rt_op = return_is_optional(fn_return_type)
            params = sig.parameters

            try:
                # creates function in duckdb
                self.con.create_function(
                    fn.__name__,
                    fn,
                    [DuckDBPyType(p_type.annotation) for p_name, p_type in params.items()],
                    DuckDBPyType(fn_return_type),
                    null_handling=FunctionNullHandling.SPECIAL if fn_rt_op else FunctionNullHandling.DEFAULT
                )
            except RuntimeError:
                raise TypeError(f"Unsupported return type: {fn_return_type}")
            logger.info(f"Created function '{fn.__name__}'")

            # register
            self._registry.append(fn)
            logger.debug(f"Registered function '{fn.__name__}' ")
            try:
                # Reflects Optional
                null_or_not = "NULL" if fn_rt_op else ""
                query = f"""
                ALTER TABLE {self.name} 
                ADD COLUMN IF NOT EXISTS {fn.__name__} {DuckDBPyType(fn_return_type)} {null_or_not}"""
                logger.info(f"Creating column: {query}")
                self.con.execute(query)

            except RuntimeError as rex:
                raise rex
            else:
                logger.info(f"Created column '{fn.__name__}'")

            return fn

        if func is not None:
            return _register(func)
        return _register



    def _apply_function(self, fn: Callable, overwrite: bool) -> None:
        """
        Apply any column function (root or dependent) row by row.
        - Iterates over existing rows from DuckDB as a generator.
        - Creates new rows until the function returns None.
        - auto_commit_each_row only wraps commit().
        """
        colname = fn.__name__
        params = list(inspect.signature(fn).parameters.keys())
        # with self.con.begin() as transaction:

        # Validate dependencies
        existing_cols = self.columns
        missing = [p for p in params if p not in existing_cols]
        if missing:
            raise ValueError(f"Function '{colname}' depends on missing columns: {missing}")

        # Generator over existing rows
        sql_cols = ", ".join(params)
        update_query = f"UPDATE {self.name} SET {colname} = {colname}({sql_cols})"
        # Apply function to existing rows

        try:
            logger.info(f"executing {update_query!r}...")
            self.con.execute(update_query)
        except duckdb.InvalidInputException:
            logger.warning(f"Could not update column, rolling back")


    def materialize(self) -> None:
        """
        Execute all registered columns (eager columns have been already applied).
        Registered order is respected. Dependencies are NOT automatically resolved;
        if a function depends on a column not yet created or populated, a clear error is raised.
        """
        logger.info(f"Materializing Deductable'{self.name}'")
        for fn in self._registry:
            logger.info(f"Applying column '{fn.__name__}' ")
            self._apply_function(fn, False)
        logger.info(f"Materialization complete for '{self.name}'")
        return None

    def df(self) -> pd.DataFrame:
        """Return full table as pandas DataFrame"""
        return self.con.execute(f"SELECT * FROM {self.name} ORDER BY id").df()
