# coding: utf-8
from typing import Generic, Any
from .._types import SqlErrorType, SQL_ERROR_HTTP_CODES, T
from .base import SensitiveFields
import json
from collections import defaultdict
import sqlparse

def result_dict(cursor, result):
    return dict(
            zip(
                [column[0] for column in cursor.description],
                result
            )
            )

def classify_error(message: str) -> SqlErrorType:
    msg = message.lower()

    if "unique key constraint" in msg or "duplicate key" in msg:
        return SqlErrorType.UNIQUE_VIOLATION
    if "foreign key constraint" in msg:
        return SqlErrorType.FOREIGN_KEY_VIOLATION
    if "check constraint" in msg:
        return SqlErrorType.CHECK_CONSTRAINT_VIOLATION
    if "permission denied" in msg or "permission violation" in msg:
        return SqlErrorType.PERMISSION_DENIED
    if "syntax error" in msg:
        return SqlErrorType.SYNTAX_ERROR
    if "timeout" in msg:
        return SqlErrorType.TIMEOUT
    if any(kw in msg for kw in [
        "could not connect", 
        "connection failed", 
        "server not found",
        "network-related", 
        "login failed", 
        "connection timeout", 
        "transport-level error", 
        "communication link failure"
    ]):
        return SqlErrorType.CONNECTION_ERROR
    
    return SqlErrorType.UNKNOWN

class Error(object):
    def __init__(self, exception: Exception = None):
        self.message =  str(exception) if isinstance(exception, Exception) else ""
        self.type = classify_error(self.message)

def format_sql(query: str) -> str:
    formatted_query = sqlparse.format(
        query,
        reindent=True,       
        keyword_case='upper', 
        identifier_case=None,
        strip_comments=False,
        use_space_around_operators=True
    )
    return formatted_query

class BaseResult(object):
    def __init__(self, query : str | tuple):
        if isinstance(query, tuple):
            q_str, *params = query
            stored_procedure = {
                "query": format_sql(q_str),
                "params": [list(p) if isinstance(p, tuple) else p for p in params]
            }
            self._query = json.dumps(stored_procedure)
        else:
            self._query = format_sql(query)

    @property
    def query(self):
        return self._query

class Result(object):

    class Count(BaseResult):
        def __init__(self, query : str | tuple, result : int | str, status_code : int, error: Error):
            super().__init__(query)
            self._count = result
            self._status_code = status_code
            self._success = bool(status_code == 200)
            self._error = error

        def model_dump(self):
            if self.success:
                return {'status_code': self.status_code, 'count': self.count}
            else:
                return {'status_code': self.status_code, 'message': self.error.message}
            
        @property
        def count(self):
            return self._count

        @property
        def status_code(self):
            return self._status_code

        @property
        def success(self):
            return self._success
        
        @property
        def error(self):
            return self._error
    
    class Fetchone(BaseResult):

        def __init__(self, query: str | tuple, cursor, result, exception: Exception = None):
            super().__init__(query)
            self._error = Error(exception)
            self._list = []
            self._dict: dict[str, Any] = {}

            if cursor is not None:
                self._status_code = 200
                self._success = True
                if result:
                    sensitive_fields = SensitiveFields.get()
                    columns = [column[0] for column in cursor.description]
                    raw_dict = dict(zip(columns, result))

                    # Exclui campos sensíveis 
                    self._dict = {
                        k: v for k, v in raw_dict.items()
                        if k not in sensitive_fields 
                    }
                    # Lista só com valores que não sejam None
                    self._list = [v for v in result if v is not None]
            else:
                self._status_code = SQL_ERROR_HTTP_CODES.get(self._error.type, 500)
                self._success = False

        def _organize_joined_tables(self, joins: list):
            alias_to_table_name = {
                join.model.TABLE_ALIAS: join.model.__class__.__name__ for join in joins
            }

            if not self._dict:
                return

            alias_data = defaultdict(dict)
            cleaned_alias_data : dict[str, dict] = {}
            keys_to_remove = []

            for key, value in self._dict.items():
        
                for alias_table, table_name in alias_to_table_name.items():
                    if alias_table in key:
                        column_name = key.replace(alias_table, '')
                        alias_data[table_name][column_name] = value
                        keys_to_remove.append(key)
                        break

            if alias_data:
                for table_name, cols in alias_data.items():
                    if all(v is None for v in cols.values()):
                        cleaned_alias_data[table_name] = {}
                    else:
                        cleaned_alias_data[table_name] = {
                            k: v for k, v in cols.items() if v is not None
                        }

            for key in keys_to_remove:
                self._dict.pop(key, None)

            if cleaned_alias_data:
                self._dict['joined_tables'] = {
                    t: {k: v for k, v in cols.items() if v}
                    for t, cols in cleaned_alias_data.items()
                }

            if self._list:
                columns = [col for col in self._dict.keys() if col]
                self._list = [self._dict[col] for col in columns if self._dict[col] is not None]

        def model_dump(self, *, include: set[str] = None):
            if not self.success:
                return {
                    'status_code': self.status_code,
                    'message': self.error.message
                }

            result_dict = {k: v for k, v in self._dict.items() if v is not None}

            if include is not None:
                include = set(include)
                result_dict = {
                    k: v for k, v in result_dict.items()
                    if k in include or k == 'joined_tables'
                }

            return {
                'status_code': self.status_code,
                'data': result_dict
            }

        @property
        def status_code(self):
            return self._status_code

        @property
        def list(self):
            return self._list

        @property
        def dict(self):
            return {k: v for k, v in self._dict.items() if v is not None}

        @property
        def success(self):
            return self._success
        
        @property
        def error(self):
            return self._error

    class FetchoneModel(Generic[T]):
        def __init__(self, model_instance: T, fetchone_result: 'Result.Fetchone'):
            self._model = model_instance
            self._fetchone = fetchone_result

        @property
        def query(self):
            return self._fetchone.query

        @property
        def model(self) -> T:
            return self._model

        @property
        def success(self):
            return self._fetchone.success

        @property
        def dict(self):
            return self._fetchone.dict

        @property
        def list(self):
            return self._fetchone.list

        @property
        def status_code(self):
            return self._fetchone.status_code

        @property
        def error(self):
            return self._fetchone.error

        def model_dump(self, *, include: set[str] = None):
            return self._fetchone.model_dump(include=include)

    class Fetchall(BaseResult):
        def __init__(self, query: str | tuple, cursor, result, exception: Exception = None):
            super().__init__(query)
            self._error = Error(exception)
            self._list_dict: list[dict[str, Any]] = []

            if cursor is not None:
                self._status_code = 200
                self._success = True
                if result:
                    sensitive_fields = SensitiveFields.get()
                    columns = [column[0] for column in cursor.description]

                    for r in result:
                        raw_dict = dict(zip(columns, r))
                        # remove campos sensíveis 
                        clean_dict = {
                            k: v for k, v in raw_dict.items()
                            if k not in sensitive_fields 
                        }
                        self._list_dict.append(clean_dict)
            else:
                self._status_code = SQL_ERROR_HTTP_CODES.get(self._error.type, 500)
                self._success = False

        def _organize_joined_tables(self, joins: list):
            alias_to_table_name = {
                join.model.TABLE_ALIAS: join.model.__class__.__name__ for join in joins
            }

            for item in self._list_dict:
                alias_data = defaultdict(dict)
                cleaned_alias_data : dict[str, dict] = {}
                keys_to_remove = []

                for key, value in item.items():
                    for alias_table, table_name in alias_to_table_name.items():
                        if alias_table in key:
                            column_name = key.replace(alias_table, '')
                            alias_data[table_name][column_name] = value
                            keys_to_remove.append(key)
                            break

                if alias_data:
                    for table_name, cols in alias_data.items():
                        if all(v is None for v in cols.values()):
                            cleaned_alias_data[table_name] = {}
                        else:
                            cleaned_alias_data[table_name] = {
                                k: v for k, v in cols.items() if v is not None
                            }

                for key in keys_to_remove:
                    item.pop(key, None)

                if cleaned_alias_data:
                    # filtra None também dentro de joined_tables
                    item['joined_tables'] = {
                        t: {k: v for k, v in cols.items()}
                        for t, cols in cleaned_alias_data.items()
                    }

        def model_dump(self, *, include: set[str] = None):
            if not self.success:
                return {
                    'status_code': self.status_code,
                    'message': self.error.message
                }

            # remove valores None de todos os dicts
            data = [
                {k: v for k, v in d.items() if v is not None}
                for d in self._list_dict
            ]

            if include is not None:
                include = set(include)
                data = [
                    {k: v for k, v in d.items() if k in include or k == 'joined_tables'}
                    for d in data
                ]

            return {
                'status_code': self.status_code,
                'data': data
            }
        
        @property
        def status_code(self):
            return self._status_code

        @property
        def list_dict(self):
            return [
                {k: v for k, v in d.items() if v is not None}
                for d in self._list_dict
            ]

        @property
        def success(self):
            return self._success
        
        @property
        def error(self):
            return self._error
        
    class FetchallModel(Generic[T]):
        def __init__(self, model_list: list[T], fetchall_result: 'Result.Fetchall'):
            self._models = model_list
            self._fetchall = fetchall_result

        @property
        def query(self):
            return self._fetchall.query

        @property
        def models(self) -> list[T]:
            return self._models

        @property
        def success(self):
            return self._fetchall.success

        @property
        def list_dict(self):
            return self._fetchall.list_dict

        @property
        def status_code(self):
            return self._fetchall.status_code

        @property
        def error(self):
            return self._fetchall.error

        def model_dump(self, *, include: set[str] = None):
            include = set(include)
            return self._fetchall.model_dump(include=include)

    class Insert(BaseResult):
        def __init__(self, query : str | tuple, result : int | str, status_code : int, error: Error):
            super().__init__(query)
            self._id = result
            self._status_code = status_code
            self._success = bool(status_code == 200)
            self._error = error

        def model_dump(self):
            if self.success:
                return {'status_code': self.status_code, 'id': self.id}
            else:
                return {'status_code': self.status_code, 'message': self.error.message}

        @property
        def id(self):
            return self._id

        @property
        def status_code(self):
            return self._status_code

        @property
        def success(self):
            return self._success
        
        @property
        def error(self):
            return self._error

    class Send(BaseResult):
        def __init__(self, query : str | tuple, result : bool, exception: Exception = None):
            super().__init__(query)
            self._error = Error(exception)
            self._status_code = 200 if result else SQL_ERROR_HTTP_CODES.get(self._error.type, 500)
            self._success = result

        def model_dump(self):
            if self.success:
                return {'status_code': self.status_code}
            else:
                return {'status_code': self.status_code, 'message': self.error.message}
            
        @property
        def status_code(self):
            return self._status_code

        @property
        def success(self):
            return self._success
        
        @property
        def error(self):
            return self._error



