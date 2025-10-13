# coding: utf-8
from functools import wraps
from dataclasses import dataclass
from typing import Any, Callable, TypeVar
from enum import Enum

T = TypeVar("T")

# Tipos de erro padronizados
class SqliteErrorType(Enum):
    UNIQUE_VIOLATION = "Unique violation"
    FOREIGN_KEY_VIOLATION = "Foreign key violation"
    CHECK_CONSTRAINT_VIOLATION = "Check constraint violation"
    PERMISSION_DENIED = "Permission denied"
    SYNTAX_ERROR = "Syntax error"
    TIMEOUT = "Timeout"
    CONNECTION_ERROR = "Connection error"
    UNKNOWN = "Unknown"

# Classificador específico para SQLite
def classify_sqlite_error(message: str) -> SqliteErrorType:
    msg = message.lower()

    if "unique constraint failed" in msg:
        return SqliteErrorType.UNIQUE_VIOLATION
    if "foreign key constraint failed" in msg:
        return SqliteErrorType.FOREIGN_KEY_VIOLATION
    if "check constraint failed" in msg:
        return SqliteErrorType.CHECK_CONSTRAINT_VIOLATION
    if "permission denied" in msg:
        return SqliteErrorType.PERMISSION_DENIED
    if "syntax error" in msg or ("near" in msg and "syntax error" in msg):
        return SqliteErrorType.SYNTAX_ERROR
    if "database is locked" in msg or "timeout" in msg:
        return SqliteErrorType.TIMEOUT
    if any(kw in msg for kw in [
        "unable to open database file",
        "disk i/o error",
        "not a database",
        "file is encrypted",
        "file is not a database"
    ]):
        return SqliteErrorType.CONNECTION_ERROR

    return SqliteErrorType.UNKNOWN

# Classe Error
class Error:
    def __init__(self, exception: Exception = None):
        self.message = str(exception) if isinstance(exception, Exception) else ""
        self.type = classify_sqlite_error(self.message) if self.message.strip() else None

# Classe de retorno do decorador
@dataclass
class OperationResult:
    success: bool
    error: Error | None
    result: Any = None

# Decorador
def safe_sqlite_operation(func: Callable[..., T]) -> Callable[..., OperationResult]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> OperationResult:
        try:
            result = func(*args, **kwargs)
            return OperationResult(success=True, error=None, result=result)
        except Exception as e:
            return OperationResult(success=False, error=Error(e), result=None)
    return wrapper