# coding: utf-8
import aioodbc, asyncio
from typing import overload
from datetime import datetime
from abc import ABC, abstractmethod
from ..models import ConnectionStringData, Result, UnavailableServiceException, BaseUpdate, SearchTable, JoinSearchTable
from .._types import T, ExecType
from ..builders import QueryBuilder, StoredBuilder
from ..utils import Utils
import pyodbc

class AsyncBaseExecutor(ABC):
    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        self._connectionStringData = connectionStringData
        self._cursor = None
        self._connection = None
        self._connection_error : Exception = None
        self._wait_timeout = wait_timeout 
        self._attempts = attempts 
        self._sql_version = sql_version
        self._api_environment = api_environment

    async def __aenter__(self):
        cs_data = self._connectionStringData
        for n in range(self._attempts):
            odbc_version = f'ODBC Driver {self._sql_version} for SQL Server' 
            if not self._sql_version:
                drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
                if not drivers:
                    raise RuntimeError("Nenhum driver ODBC do SQL Server encontrado. Instale o ODBC Driver 17 ou 18.")
                odbc_version = drivers[-1]
            try:
                connection_string = f'DRIVER={{{odbc_version}}};SERVER={cs_data.server};DATABASE={cs_data.database};UID={cs_data.username};PWD={cs_data.password}'
                self._connection = await aioodbc.connect(dsn=connection_string)
                self._cursor = await self._connection.cursor()

            except Exception as e:
                self._connection_error = e
                print(e)
                print(f'Erro na conexão com a base de dados, nova tentativa em {self._wait_timeout}s')
                await asyncio.sleep(self._wait_timeout)

        return self

    async def __aexit__(self, *args):
        if self._cursor:
            await self._cursor.close()
        if self._connection:
            await self._connection.close()

    @property
    def connectionStringData(self):
        return self._connectionStringData

    @property
    def api_environment(self):
        return self._api_environment

    @property
    def sql_version(self):
        return self._sql_version

    @property
    async def cursor(self):
        if not self._cursor:
            if self._connection:
                self._cursor = await self._connection.cursor()
        return self._cursor

    @property
    def connection(self):
        if self._connection:
            return self._connection

    @property
    def attempts(self):
        return self._attempts

    @attempts.setter
    def attempts(self, value):
        if isinstance(value, int):
            self._attempts = value
        else:
            raise ValueError("O número de tentativas deve ser um número inteiro.")

    @property
    def wait_timeout(self):
        return self._wait_timeout

    @wait_timeout.setter
    def wait_timeout(self, value):
        if isinstance(value, int):
            self._wait_timeout = value
        else:
            raise ValueError("O tempo de espera deve ser um número inteiro.")

    @abstractmethod
    async def _exec_(self, connection, operation_sql, exec_type):
        pass

class AsyncQueryUpdate(BaseUpdate):
    def __init__(self, executor : AsyncBaseExecutor, model : T):
        super().__init__(executor, model)

    @overload
    async def where(self, model : T)  -> Result.Send:
            pass

    @overload
    async def where(self, query : str)  -> Result.Send:
        pass

    async def where(self, *args) -> Result.Send:
        query = QueryBuilder.update(self._set_data, *args)
        return await self.executor._exec_(self.executor.connection , query, ExecType.send)


class AsyncQuery(AsyncBaseExecutor):

    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        super().__init__(connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    @overload
    async def count(self, query : str) -> Result.Count:
        pass

    @overload
    async def count(self, model : T, additional_sql : str = "", select_top : int = None) -> Result.Count:
        pass

    async def count(self, *args, **kwargs) -> T | Result.Count:
        args = Utils.args_query(*args, **kwargs)
        if args.model:
            args.query = QueryBuilder.select(args.model, args.additional_sql, args.select_top)

        count_query = f"""
        SELECT COUNT(*) AS Count FROM (
            {args.query}
        ) AS count_subquery
        """

        result : Result.Fetchone = await self._exec_(self._connection, count_query, ExecType.fetchone)
        if result.success:
            return Result.Count(count_query, result.dict.get('Count', 0), result.status_code, result.error)
        return Result.Count(count_query, 0, result.status_code, result.error)

    @overload
    async def fetchone(self, query : str) -> Result.Fetchone:
        pass

    @overload
    async def fetchone(self, model : T, additional_sql : str = "") -> Result.FetchoneModel[T]:
        pass
          
    async def fetchone(self, *args, **kwargs) -> Result.FetchoneModel[T] | Result.Fetchone:
        args = Utils.args_query(*args, **kwargs)
        if args.model:
            args.query = QueryBuilder.select(args.model, args.additional_sql, args.select_top)
        
        result = await self._exec_(self._connection, args.query, ExecType.fetchone)
        if args.model:
            model_instance = args.model.__class__(**result.dict) if result.success else args.model.__class__()
            return Result.FetchoneModel(model_instance, result)
        return result
    
    async def fetchone_with_joins(self, main_search: SearchTable, joins: list[JoinSearchTable] = [], additional_sql: str = "", select_top: int = None) -> Result.Fetchone:
        query = QueryBuilder.select_with_joins(main_search, joins, additional_sql, select_top)
        result = await self._exec_(self._connection, query, ExecType.fetchone)
        result._organize_joined_tables(joins)
        return result

    @overload
    async def fetchall(self, query : str) -> Result.Fetchall:
        pass

    @overload
    async def fetchall(self, model : T, additional_sql : str = "", select_top : int = None) -> Result.FetchallModel[T]:
        pass

    async def fetchall(self, *args, **kwargs) -> Result.FetchallModel[T] | Result.Fetchall:
        args = Utils.args_query(*args, **kwargs)
        if args.model:
            args.query = QueryBuilder.select(args.model, args.additional_sql, args.select_top)

        result = await self._exec_(self._connection, args.query, ExecType.fetchall)
        if args.model:
            models = [args.model.__class__(**r) for r in result.list_dict] if result.success else []
            return Result.FetchallModel(models, result)
        return result
    
    async def fetchall_with_joins(self, main_search: SearchTable, joins: list[JoinSearchTable] = [], additional_sql: str = "", select_top: int = None) -> Result.Fetchall:
        query = QueryBuilder.select_with_joins(main_search, joins, additional_sql, select_top)
        result = await self._exec_(self._connection, query, ExecType.fetchall)
        result._organize_joined_tables(joins)
        return result

    async def execute(self, query : str) -> Result.Send:
            return await self._exec_(self._connection, query, ExecType.send)

    async def delete(self, model: T) -> Result.Send:
        query = QueryBuilder.delete(model)
        return await self._exec_(self._connection, query, ExecType.send)

    def update(self, model: T):
        return AsyncQueryUpdate(self, model)

    async def insert(self, model: T, name_column_id = 'Id') -> Result.Insert:
        insert_data = model.model_dump()
        if name_column_id not in insert_data:
            name_column_id = next(iter(insert_data.keys())) 

        query = QueryBuilder.insert(model, name_column_id)
        result : Result.Fetchone = await self._exec_(self._connection, query, ExecType.fetchone)
        if result.success:
            return Result.Insert(query, result.dict.get('Id', 0), result.status_code, result.error)
        return Result.Insert(query, 0, result.status_code, result.error)
    
    async def _exec_(self, connection, query_sql : str, exec_type : ExecType):
 
        if not self._cursor:
            if self._api_environment:
                raise UnavailableServiceException()

            if exec_type == ExecType.fetchone:
                return Result.Fetchone(query_sql, None, None, self._connection_error)
            elif exec_type == ExecType.fetchall:
                return Result.Fetchall(query_sql, None, None, self._connection_error)
            elif exec_type == ExecType.send:
                return Result.Send(query_sql, False, self._connection_error)

        try:
            # executar
            response = await self._cursor.execute(query_sql)

            # ober resultado se nessesario
            if exec_type == ExecType.fetchone:
                result = Result.Fetchone(query_sql, self._cursor, await response.fetchone())

            elif exec_type == ExecType.fetchall:
                result = Result.Fetchall(query_sql, self._cursor, await response.fetchall())
            elif exec_type == ExecType.send:
                result = Result.Send(query_sql, True)

            # fazer o commit 
            await connection.commit()

        except Exception as ex:
            if exec_type == ExecType.fetchone:
                return Result.Fetchone(query_sql, None, None, ex)
            elif exec_type == ExecType.fetchall:
                return Result.Fetchall(query_sql, None, None, ex)
            elif exec_type == ExecType.send:
                return Result.Send(query_sql, False, ex)

        # retorna o resultado
        return result


class AsyncStoredUpdate(BaseUpdate):
    def __init__(self, executor : AsyncBaseExecutor, model : T):
        super().__init__(executor, model)

    async def where(self, data : T)  -> Result.Send:
        query, params = StoredBuilder.update(self._set_data, data)
        return await self.executor._exec_(self.executor.connection, (query,  *params), ExecType.send)


class AsyncStored(AsyncBaseExecutor):

    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int,sql_version : int | None,  api_environment : bool):
        super().__init__(connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    @overload
    async def count(self, query : str) -> Result.Count:
        pass

    @overload
    async def count(self, model : T, additional_sql : str = "", select_top : int = None) -> Result.Count:
        pass

    async def count(self, *args, **kwargs) -> T | Result.Count:
        args = Utils.args_query(*args, **kwargs)
        if args.model:
            args.query = StoredBuilder.select(args.model, args.additional_sql, args.select_top)

        count_query = f"""
        SELECT COUNT(*) AS Count FROM (
            {args.query}
        ) AS count_subquery
        """

        result : Result.Fetchone = await self._exec_(self._connection, count_query, ExecType.fetchone)
        if result.success:
            return Result.Count(count_query, result.dict.get('Count', 0), result.status_code, result.error)
        return Result.Count(count_query, 0, result.status_code, result.error)

    @overload
    async def fetchone(self, query : str, params : list | tuple) -> Result.Fetchone:
        pass

    @overload
    async def fetchone(self, query : str, *params : int | str | datetime) -> Result.Fetchone:
        pass

    @overload
    async def fetchone(self, model : T, additional_sql : str = "") -> Result.FetchoneModel[T]:
        pass

    async def fetchone(self, *args, **kwargs) -> Result.FetchoneModel[T] | Result.Fetchone:
        args = Utils.args_stored(*args, **kwargs)
        if args.model:
            args.query, args.params = StoredBuilder.select(args.model, args.additional_sql, args.select_top)

        result : Result.Fetchone = await self._exec_(self._connection, (args.query, *args.params), ExecType.fetchone)
        if args.model:
            model_instance = args.model.__class__(**result.dict) if result.success else args.model.__class__()
            return Result.FetchoneModel(model_instance, result)
        return result

    @overload
    async def fetchall(self, query : str, params : list | tuple) -> Result.Fetchall:
        pass

    @overload
    async def fetchall(self, query : str, *params : int | str | datetime) -> Result.Fetchall:
        pass

    @overload
    async def fetchall(self, model : T, additional_sql : str = "", select_top : int = None) -> Result.FetchallModel[T]:
        pass

    async def fetchall(self, *args, **kwargs) -> Result.FetchallModel[T] | Result.Fetchall:
        args = Utils.args_stored(*args, **kwargs)
        if args.model:
            args.query, args.params = StoredBuilder.select(args.model, args.additional_sql, args.select_top)

        result : Result.Fetchall = await self._exec_(self._connection, (args.query, *args.params), ExecType.fetchall)
        if args.model:
            models = [args.model.__class__(**r) for r in result.list_dict] if result.success else []
            return Result.FetchallModel(models, result)
        return result

    @overload
    async def execute(self, query : str, *params : str | int) -> Result.Send:
        pass

    @overload
    async def execute(self, query : str, params : list | tuple) -> Result.Send:
        pass

    async def execute(self, *args) -> Result.Send:
        query = args[0]
        params = args[1:]
        if len(params) == 1 and isinstance(params[0], (list, tuple)):
            params = params[0]
        return await self._exec_(self._connection, (query, *params), ExecType.send)

    async def delete(self, model: T) -> Result.Send:
        query, params = StoredBuilder.delete(model)
        return await self._exec_(self._connection, (query,  *params), ExecType.send)

    def update(self, model: T):
        return AsyncStoredUpdate(self, model)

    async def insert(self, model: T, name_column_id = 'Id') -> Result.Insert:
        insert_data = model.model_dump()
        if name_column_id not in insert_data:
            name_column_id = next(iter(insert_data.keys()))

        query, params = StoredBuilder.insert(model, name_column_id)
        stored_procedure = (query,  *params)
        result : Result.Fetchone = await self._exec_(self._connection, stored_procedure, ExecType.fetchone)
        if result.success:
            return Result.Insert(stored_procedure, result.dict.get('Id', 0), result.status_code, result.error)
        return Result.Insert(stored_procedure, 0, result.status_code, result.error)
    
    async def _exec_(self, connection , stored_procedure : tuple, exec_type : ExecType):
 
        if not self._cursor:
            if self._api_environment:
                raise UnavailableServiceException()

            if exec_type == ExecType.fetchone:
                return Result.Fetchone(stored_procedure, None, None, self._connection_error)
            elif exec_type == ExecType.fetchall:
                return Result.Fetchall(stored_procedure, None, None, self._connection_error)
            elif exec_type == ExecType.send:
                return Result.Send(stored_procedure, False, self._connection_error)

        try:
            # executar
            response = await self._cursor.execute(*stored_procedure)

            # ober resultado se nessesario
            if exec_type == ExecType.fetchone:
                result = Result.Fetchone(stored_procedure, self._cursor, await response.fetchone())
            elif exec_type == ExecType.fetchall:
                result = Result.Fetchall(stored_procedure, self._cursor, await response.fetchall())
            elif exec_type == ExecType.send:
                result = Result.Send(stored_procedure, True)

            # fazer o commit 
            await connection.commit()
            
        except Exception as ex:
            if exec_type == ExecType.fetchone:
                return Result.Fetchone(stored_procedure, None, None, ex)
            elif exec_type == ExecType.fetchall:
                return Result.Fetchall(stored_procedure, None, None, ex)
            elif exec_type == ExecType.send:
                return Result.Send(stored_procedure, False, ex)

        # retorna o resultado
        return result




