from typing import TypeVar
from enum import Enum

SQL_NULL = "SQL_NULL"
T = TypeVar('T')

class ExecType(Enum):
    count = "count"
    send = "send"
    fetchone = "fetchone"
    fetchall = "fetchall"

class SqlErrorType(str, Enum):
    UNIQUE_VIOLATION = "UniqueConstraintViolation"
    FOREIGN_KEY_VIOLATION = "ForeignKeyViolation"
    CHECK_CONSTRAINT_VIOLATION = "CheckConstraintViolation"
    PERMISSION_DENIED = "PermissionDenied"
    SYNTAX_ERROR = "SyntaxError"
    TIMEOUT = "Timeout"
    CONNECTION_ERROR = "SqlConnectionError"
    UNKNOWN = "UnknownError"

SQL_ERROR_HTTP_CODES = {
    SqlErrorType.UNIQUE_VIOLATION: 409,             # Conflict
    SqlErrorType.FOREIGN_KEY_VIOLATION: 409,        # Conflict
    SqlErrorType.CHECK_CONSTRAINT_VIOLATION: 400,   # Bad Request
    SqlErrorType.PERMISSION_DENIED: 403,            # Forbidden
    SqlErrorType.SYNTAX_ERROR: 400,                 # Bad Request
    SqlErrorType.TIMEOUT: 504,                      # Gateway Timeout
    SqlErrorType.CONNECTION_ERROR: 503,             # Service Unavailable
    SqlErrorType.UNKNOWN: 500                       # Internal Server Error
}


    



