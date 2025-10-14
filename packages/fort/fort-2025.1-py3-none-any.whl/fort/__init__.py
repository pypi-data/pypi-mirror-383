import warnings

try:
    from .postgres import PostgresDatabase as PostgresDatabase
except ModuleNotFoundError:
    warnings.warn("PostgresDatabase will not be available", ImportWarning)

from .sqlite import SQLiteDatabase as SQLiteDatabase
