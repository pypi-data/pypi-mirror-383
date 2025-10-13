# coding: utf-8
import re
from pydantic import Field, BaseModel, model_validator
from typing import Optional, List, Set, Any
import json

type_mapping = {
        'int': 'int',
        'bigint': 'int',
        'smallint': 'int',
        'tinyint': 'int',
        'bit': 'bool',
        'decimal': 'float',
        'numeric': 'float',
        'money': 'float',
        'smallmoney': 'float',
        'float': 'float',
        'real': 'float',
        'date': 'datetime',
        'datetime': 'datetime',
        'datetime2': 'datetime',
        'datetimeoffset': 'datetime',
        'smalldatetime': 'datetime',
        'time': 'datetime.time',
        'binary': 'bytes',
        'varbinary': 'bytes',
        'image': 'bytes',
        'timestamp': 'bytes', 
        'rowversion': 'bytes',  
    }

QUERY_FIELD_TYPES = {
    'str': 'StringQueryField',
    'int': 'NumericQueryField',
    'float': 'NumericQueryField',
    'bool': 'BoolQueryField',
    'datetime': 'DateQueryField',
    'datetime.time': 'DateQueryField',
    'bytes': 'BytesQueryField',  
}

JOIN_CONDITIONAL_FIELD_TYPES = {
    'str': 'JoinStringCondition',
    'int': 'JoinNumericCondition',
    'float': 'JoinNumericCondition',
    'bool': 'JoinBooleanCondition',
    'datetime': 'JoinDateCondition',
    'datetime.time': 'JoinDateCondition',
    'bytes': 'JoinBytesCondition',  
}

class Relation(BaseModel):
    original : bool = True
    table : str 
    column : str 

class SqlTableAuth(BaseModel):
    table : str = ""
    column : str = ""

class TableSettings(BaseModel):
    insert : bool = False
    update : bool = False
    delete : bool = False
    search : bool = True
 
class ForeignKey(BaseModel):
    ref_table: str = ""
    ref_column: str = ""
    on_delete: str = ""
    on_update: str = ""

class AutoColumnDescription(BaseModel):
    nullable: Optional[bool] = None
    type: Optional[str] = None
    identity: Optional[bool] = None
    default: Optional[Any] = None
    primary_key: Optional[bool] = None
    unique: Optional[bool] = None
    foreign_key: Optional[ForeignKey] = None

class ColumnInformation(BaseModel):
    TABLE_CATALOG : str = Field("", description="")
    TABLE_SCHEMA : str = Field("", description="")
    TABLE_NAME : str = Field("", description="")
    COLUMN_NAME : str = Field("", description="")
    DATA_TYPE : str = Field("", description="")
    IS_NULLABLE : str = Field("", description="")
    IS_IDENTITY : str = Field("", description="")
    IS_PRIMARY_KEY : str = Field("", description="")
    IS_UNIQUE : str = Field("", description="")
    CHARACTER_MAXIMUM_LENGTH : Optional[int] = Field(None, description="")
    COLUMN_DESCRIPTION : Optional[str] = Field("", description="")
    AUTO_COLUMN_DESCRIPTION : Optional[AutoColumnDescription] = None

    column_authentication : str = Field("", description="")
    relation : Optional[Relation] = None
    available : bool = True

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data):
        if isinstance(data, dict):
            # Se o campo vier como string JSON, converte para dict e depois para AutoColumnDescription
            if isinstance(data.get("AUTO_COLUMN_DESCRIPTION"), str):
                try:
                    auto_col_dict = json.loads(data["AUTO_COLUMN_DESCRIPTION"])
                    if not auto_col_dict['foreign_key']:
                        auto_col_dict['foreign_key'] = None
                    data["AUTO_COLUMN_DESCRIPTION"] = auto_col_dict
                    description : AutoColumnDescription = AutoColumnDescription(**auto_col_dict)
                    if description.foreign_key:
                        data['relation'] = Relation(table=description.foreign_key.ref_table, column=description.foreign_key.ref_column)

                except json.JSONDecodeError:
                    data["AUTO_COLUMN_DESCRIPTION"] = None
        
        return data
   
class ForeignKey(BaseModel):
    name: str
    column: str
    ref_table: str
    ref_column: str
    on_delete: str
    on_update: str

class UniqueConstraint(BaseModel):
    name: str
    columns: List[str]

class PrimaryKey(BaseModel):
    name: str
    columns: List[str]

class AutoTableDescription(BaseModel):
    columns: int
    identity: List[str]
    primary_keys: Optional[PrimaryKey]
    unique_constraints: List[UniqueConstraint]
    foreign_keys: List[ForeignKey]
   
class TableInformation(BaseModel):
    TABLE_CATALOG : str = Field("", description="")
    TABLE_SCHEMA : str = Field("", description="")
    TABLE_NAME : str = Field("", description="")
    AUTO_TABLE_DESCRIPTION : AutoTableDescription = Field(..., description="")
    TABLE_DESCRIPTION : Optional[str] = Field("", description="")
    settings : TableSettings = TableSettings()
    available : bool = True

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data):
        if isinstance(data, dict):
            if isinstance(data.get("AUTO_TABLE_DESCRIPTION"), str):
                data["AUTO_TABLE_DESCRIPTION"] = json.loads(data["AUTO_TABLE_DESCRIPTION"])
        return data

class SqlTable(TableInformation):
    COLUMNS : list[ColumnInformation] = []

class InformationSchemaRoutines(BaseModel):
    ORDINAL_POSITION: int | None = None
    PARAMETER_NAME: str = ""
    DATA_TYPE: str = ""

class SqlStored(BaseModel):
    SPECIFIC_CATALOG: str
    SPECIFIC_SCHEMA: str
    SPECIFIC_NAME: str
    PROCEDURE_DEFINITION: str
    PARAMETERS: list[InformationSchemaRoutines] = []

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data):
        if isinstance(data, dict):
            if isinstance(data.get("PARAMETERS"), str):
                try:
                    data["PARAMETERS"] = json.loads(data["PARAMETERS"])
                except Exception:
                    data["PARAMETERS"] = []
        return data
    
def create_database_description(tables: List[TableInformation]) -> str:
    lines = []
    for table in tables:
        auto = table.AUTO_TABLE_DESCRIPTION
        lines.append(f"\n[Tabela: {table.TABLE_NAME}]")

        # Chave primária
        if auto.primary_keys:
            pk_cols = ", ".join(auto.primary_keys.columns or [])
            lines.append(f"- PK: {pk_cols}")

        # Restrições únicas
        if auto.unique_constraints:
            for uc in auto.unique_constraints:
                cols = ", ".join(uc.columns or [])
                lines.append(f"- UNIQUE ({uc.name}): {cols}")

        # Chaves estrangeiras
        if auto.foreign_keys:
            for fk in auto.foreign_keys:
                lines.append(
                    f"- FK: {fk.column} → {fk.ref_table}.{fk.ref_column} "
                    f"[ON DELETE {fk.on_delete}, ON UPDATE {fk.on_update}]"
                )

        # Colunas identidade
        if auto.identity:
            identity_cols = ", ".join(auto.identity)
            lines.append(f"- Identity: {identity_cols}")

    return "\n".join(lines)

def create_table_description(table_info: TableInformation) -> str:
    parts = []

    # Identity columns
    identity = table_info.AUTO_TABLE_DESCRIPTION.identity or []
    if identity:
        identity_cols = ", ".join(identity)
        parts.append(f"Identity columns: {identity_cols}")

    # Primary key
    pk = table_info.AUTO_TABLE_DESCRIPTION.primary_keys
    if pk:
        pk_cols = ", ".join(pk.columns or [])
        parts.append(f"Primary key ({pk.name}: {pk_cols})" if pk_cols else f"Primary key ({pk.name})")

    # Unique constraints
    unique_list = table_info.AUTO_TABLE_DESCRIPTION.unique_constraints or []
    for uc in unique_list:
        cols = ", ".join(uc.columns or [])
        parts.append(f"Unique constraint ({uc.name}: {cols})" if cols else f"Unique constraint ({uc.name})")

    # Foreign keys
    # for fk in table_info.AUTO_TABLE_DESCRIPTION.foreign_keys or []:
    #     ref = f"{fk.ref_table}.{fk.ref_column}"
    #     action = f"ON DELETE {fk.on_delete}, ON UPDATE {fk.on_update}"
    #     parts.append(f"Foreign key ({fk.column} → {ref}) [{action}]")

    # Final assembly
    auto_summary = "; ".join(parts)

    if table_info.TABLE_DESCRIPTION and table_info.TABLE_DESCRIPTION.strip():
        return f"{table_info.TABLE_DESCRIPTION.strip()} — [{auto_summary}]"
    else:
        return f"[{auto_summary}]"
    
def create_column_description(column_desc: Optional[str], auto_desc: Optional[AutoColumnDescription]) -> str:
    if auto_desc is None:
        return column_desc or ""

    parts = []

    # Nullable
    if auto_desc.nullable is False:
        parts.append("Required")
    elif auto_desc.nullable is True:
        parts.append("Optional")

    # Type
    if auto_desc.type:
        parts.append(f"Type: {auto_desc.type}")

    # Identity (Auto Increment)
    if auto_desc.identity:
        parts.append("Identity (auto increment)")

    # Default value
    if auto_desc.default is not None and str(auto_desc.default).lower() != 'null':
        parts.append(f"Default: {auto_desc.default}")

    # Primary key
    if auto_desc.primary_key:
        parts.append("Primary key")

    # Unique
    if auto_desc.unique:
        parts.append("Unique")

    # Foreign key
    # if auto_desc.foreign_key:
    #     fk = auto_desc.foreign_key
    #     details = []
    #     if fk.ref_table and fk.ref_column:
    #         details.append(f"{fk.ref_table}.{fk.ref_column}")
    #     if fk.on_delete:
    #         details.append(f"ON DELETE {fk.on_delete}")
    #     if fk.on_update:
    #         details.append(f"ON UPDATE {fk.on_update}")
    #     fk_info = " | ".join(details) if details else "Foreign key"
    #     parts.append(f"Foreign key → {fk_info}")

    auto_summary = "; ".join(parts)

    if column_desc:
        return f"{column_desc.strip()} — [{auto_summary}]"
    else:
        return f"[{auto_summary}]"

def create_field(data: ColumnInformation, all_optional=True):
    sql_data_type = data.DATA_TYPE.lower()
    python_type = type_mapping.get(sql_data_type, 'str')

    field_args = [
        f'description="{create_column_description(data.COLUMN_DESCRIPTION, data.AUTO_COLUMN_DESCRIPTION)}"'
    ]

    # Define QueryField type adicional
    query_field_type = QUERY_FIELD_TYPES.get(python_type)

    join_conditional_field_type = JOIN_CONDITIONAL_FIELD_TYPES.get(python_type)

    # Combina os tipos
    if python_type in ['datetime', 'datetime.time']:
        annotated_type = f'Union[{python_type}, str]'
    else:
        annotated_type = python_type

    if query_field_type:
        annotated_type = f'Union[{annotated_type}, {query_field_type}, {join_conditional_field_type}]'

    if data.IS_NULLABLE == "YES" or all_optional:
        annotated_type = f'Optional[{annotated_type}]'
        field_def = f'Field(None, {", ".join(field_args)})' if field_args else 'Field(None)'
    else:
        field_def = f'Field(..., {", ".join(field_args)})' if field_args else 'Field(...)'

    return f'{data.COLUMN_NAME}: {annotated_type} = {field_def}'

def create_arg(
    data: ColumnInformation,
    default_type: str = None,
    default_value: str = "None",
    with_query_field: bool = False
):
    sql_data_type = data.DATA_TYPE.lower()
    python_type = default_type or type_mapping.get(sql_data_type, 'str')

    # Define o tipo base
    if python_type in ['datetime', 'datetime.time']:
        annotated_type = f'Union[{python_type}, str]'
    else:
        annotated_type = python_type

    # Adiciona o QueryField, se for solicitado
    if with_query_field:
        query_field_type = QUERY_FIELD_TYPES.get(python_type)
        join_conditional_field_type = JOIN_CONDITIONAL_FIELD_TYPES.get(python_type)
        if query_field_type:
            annotated_type = f'Union[{annotated_type}, {query_field_type}, {join_conditional_field_type}]'

    return f'{data.COLUMN_NAME}: {annotated_type} = {default_value}'

def get_parameters_with_defaults(stored_procedure):
    # Regular expression to capture parameters and their default values
    pattern = r"@(\w+)\s+\w+(?:\(\d+\))?\s*(?:=\s*(NULL|'[^']*'|\"[^\"]*\"|\d+))?"
    
    # Dictionary to hold parameters and their default values
    params_with_defaults = {}

    # Extract the parameter section of the stored procedure
    param_section_match = re.search(r'\(\s*(.*?)\s*\)\s*AS', stored_procedure, re.S | re.I)
    if not param_section_match:
        return params_with_defaults  # Return an empty dictionary if no parameters found

    param_section = param_section_match.group(1)

    # Find all parameter definitions in the extracted section
    matches = re.findall(pattern, param_section, re.IGNORECASE)

    for match in matches:
        param_name = match[0]  # Parameter name
        default_value = match[1] if match[1] else False  # Default value or None if not present

        # Validate the default value to be a string or an integer
        if default_value != False:
            # Check if it's a string (enclosed in quotes)
            if default_value.startswith(("'", '"')) and default_value.endswith(("'", '"')):
                # Remove quotes for the final value
                default_value = default_value
            # Check if it's an integer
            elif default_value.isdigit():
                default_value = int(default_value)
            else:
                # If it's not a valid string or integer, set to None
                default_value = None

        # Add to dictionary
        params_with_defaults[param_name] = default_value

    return params_with_defaults

def create_queue_update(fields_args_str : str):
    return f'''def queue_update(self, *, {fields_args_str}):
        super().queue_update(**locals())
'''

def create_set_ignored_fields(fields_args_str : str):
    return f'''@classmethod
    def set_ignored_fields(cls, *, {fields_args_str}):
        super().set_ignored_fields(**locals())
'''

def create_params_routine(data : InformationSchemaRoutines, defaults_values : dict[str, str | int | None]):
    sql_data_type = data.DATA_TYPE.lower()  
    python_type = type_mapping.get(sql_data_type)
    if python_type is None:
        python_type = 'str'
    name = data.PARAMETER_NAME.replace('@', '')
    default_value = defaults_values.get(name)
    if default_value == False:
        if python_type != 'str' and python_type != 'bool':
            return f'{name} : Union[{python_type}, str]'
        return f'{name} : {python_type}'
    else:
        if python_type != 'str' and python_type != 'bool':
            return f'{name} : Union[{python_type}, str] = {default_value}'
        return f'{name} : {python_type} = {default_value}'

def create_content_orm(class_name : str, fields_args_str : str):

    return f'''# coding: utf-8

from datetime import datetime
from typing import overload, Union
from dapper_sqls import Dapper
from dapper_sqls.dapper.dapper import Stored, Query
from dapper_sqls.dapper.executors import BaseExecutor, StoredUpdate, QueryUpdate
from dapper_sqls.utils import get_dict_args
from dapper_sqls.models import ConnectionStringData, Result
from .model import {class_name}

      
class BaseExecutorORM(BaseExecutor):
    def __init__(self, executor : Query | Stored , connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        BaseExecutor.__init__(self, connectionStringData, attempts, wait_timeout, sql_version, api_environment)
        self._executor = executor

    @property
    def executor(self):
        return self._executor

    def count(self, additional_sql : str = "", *, {fields_args_str}):
        return self.executor.count(self, {class_name}(**get_dict_args(locals(), ['additional_sql'])), additional_sql)

    def fetchone(self, additional_sql : str = "", *, {fields_args_str}) -> Result.FetchoneModel[{class_name}]:
        return self.executor.fetchone(self, {class_name}(**get_dict_args(locals(), ['additional_sql'])), additional_sql)

    def fetchall(self, additional_sql : str = "", select_top : int = None, *, {fields_args_str}) -> Result.FetchallModel[{class_name}]:
        return self.executor.fetchall(self, {class_name}(**get_dict_args(locals(), ['additional_sql', 'select_top'])), additional_sql, select_top)

    def delete(self, *, {fields_args_str}) -> Result.Send:
        return self.executor.delete(self, {class_name}(**get_dict_args(locals())))
    
    def insert(self, *, {fields_args_str}) -> Result.Insert:
        return self.executor.insert(self, {class_name}(**get_dict_args(locals())))

    def _exec_(self, *args):
        return self.executor._exec_(self, *args)

class QueryUpdate{class_name}ORM(object):
        def __init__(self, executor, model : {class_name}):
            self._set_data = model
            self._executor = executor

        @property
        def set_data(self):
            return self._set_data

        @property
        def executor(self):
            return self._executor

        @overload
        def where(self, query : str = None, *, {fields_args_str}) -> Result.Send:
            pass

        def where(self, *args, **kwargs) -> Result.Send:
            query = kwargs.get('query')
            if query:
                return QueryUpdate(self._executor, self.set_data).where(query)
            return QueryUpdate(self._executor, self.set_data).where({class_name}(**kwargs))

class Query{class_name}ORM(BaseExecutorORM):
    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        BaseExecutorORM.__init__(self, Query, connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    def update(self, *, {fields_args_str}):
            return QueryUpdate{class_name}ORM(self, {class_name}(**get_dict_args(locals())))

class StoredUpdate{class_name}ORM(object):
    def __init__(self, executor, model : {class_name}):
        self._set_data = model
        self._executor = executor

    @property
    def set_data(self):
        return self._set_data

    @property
    def executor(self):
        return self._executor

    def where(self, *, {fields_args_str}) -> Result.Send:
        return StoredUpdate(self._executor, self.set_data).where({class_name}(**get_dict_args(locals())))

class Stored{class_name}ORM(BaseExecutorORM):
    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        BaseExecutorORM.__init__(self, Stored, connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    def update(self, {fields_args_str}):
        return StoredUpdate{class_name}ORM(self, {class_name}(**get_dict_args(locals())))

class {class_name}ORM(object):

    def __init__(self, dapper : Dapper):
          self._dapper = dapper

    @property
    def dapper(self):
        return self._dapper

    def query(self, attempts : int = None, wait_timeout : int = None):
            attempts = attempts if attempts else self.dapper.config.default_attempts
            wait_timeout = wait_timeout if wait_timeout else self.dapper.config.default_wait_timeout
            return Query{class_name}ORM(self.dapper.config.connectionStringDataQuery.get(), attempts, wait_timeout, self.dapper.config.sql_version, self.dapper.config.api_environment)

    def stored(self, attempts : int = None, wait_timeout : int = None):
        attempts = attempts if attempts else self.dapper.config.default_attempts
        wait_timeout = wait_timeout if wait_timeout else self.dapper.config.default_wait_timeout
        return Stored{class_name}ORM(self.dapper.config.connectionStringDataStored.get() , attempts, wait_timeout, self.dapper.config.sql_version, self.dapper.config.api_environment)
            
    @overload
    @staticmethod
    def load(dict_data : dict) -> {class_name}:
        pass

    @overload
    @staticmethod
    def load(list_dict_data : list[dict]) -> list[{class_name}]:
        pass

    @overload
    @staticmethod
    def load(fetchone : Result.Fetchone) -> {class_name}:
        pass

    @overload
    @staticmethod
    def load(fetchall : Result.Fetchall) -> list[{class_name}]:
        pass

    @staticmethod
    def load(*args):
        data = args[0]
        if isinstance(data, dict) or isinstance(data, Result.Fetchone):
            if isinstance(data, Result.Fetchone):
                data = data.dict
            if all(value is None for value in data.values()):
                return {class_name}()

            return {class_name}(**data)

        if isinstance(data, Result.Fetchall):
                data = data.list_dict

        return [{class_name}(**d) for d in data]
            '''

def create_content_async_orm(class_name : str, fields_args_str : str):

    return f'''# coding: utf-8

from datetime import datetime
from typing import overload, Union
from dapper_sqls import AsyncDapper
from dapper_sqls.async_dapper.async_dapper import AsyncStored, AsyncQuery
from dapper_sqls.async_dapper.async_executors import AsyncBaseExecutor, AsyncQueryUpdate, AsyncStoredUpdate
from dapper_sqls.utils import get_dict_args
from dapper_sqls.models import ConnectionStringData, Result
from .model import {class_name}


class AsyncBaseExecutorORM(AsyncBaseExecutor):
    def __init__(self, executor : AsyncQuery | AsyncStored , connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        AsyncBaseExecutor.__init__(self, connectionStringData, attempts, wait_timeout, sql_version, api_environment)
        self._executor = executor

    @property
    def executor(self):
        return self._executor

    async def count(self, additional_sql : str = "", *, {fields_args_str}):
        return await self.executor.count(self, {class_name}(**get_dict_args(locals(), ['additional_sql'])), additional_sql)

    async def fetchone(self, additional_sql : str = "", *, {fields_args_str}) -> Result.FetchoneModel[{class_name}]:
        return await self.executor.fetchone(self, {class_name}(**get_dict_args(locals(), ['additional_sql'])), additional_sql)

    async def fetchall(self, additional_sql : str = "", select_top : int = None, *, {fields_args_str}) -> Result.FetchallModel[{class_name}]:
        return await self.executor.fetchall(self, {class_name}(**get_dict_args(locals(), ['additional_sql', 'select_top'])), additional_sql, select_top)

    async def delete(self, *, {fields_args_str}) -> Result.Send:
        return await self.executor.delete(self, {class_name}(**get_dict_args(locals())))
    
    async def insert(self, *, {fields_args_str}) -> Result.Insert:
        return await self.executor.insert(self, {class_name}(**get_dict_args(locals())))

    async def _exec_(self, *args):
        return await self.executor._exec_(self, *args)

class AsyncQueryUpdate{class_name}ORM(object):
    def __init__(self, executor, model : {class_name}):
        self._set_data = model
        self._executor = executor

    @property
    def set_data(self):
        return self._set_data

    @property
    def executor(self):
        return self._executor

    @overload
    async def where(self, query : str = None, *, {fields_args_str}) -> Result.Send:
        pass
        
    async def where(self, *args, **kwargs) -> Result.Send:
        query = kwargs.get('query')
        if query:
            return await AsyncQueryUpdate(self._executor, self.set_data).where(query)
        return await AsyncQueryUpdate(self._executor, self.set_data).where({class_name}(**kwargs))

class AsyncQuery{class_name}ORM(AsyncBaseExecutorORM):
    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        AsyncBaseExecutorORM.__init__(self, AsyncQuery, connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    def update(self, *, {fields_args_str}):
        return AsyncQueryUpdate{class_name}ORM(self, {class_name}(**get_dict_args(locals())))

class AsyncStoredUpdate{class_name}ORM(object):
    def __init__(self, executor, model : {class_name}):
        self._set_data = model
        self._executor = executor

    @property
    def set_data(self):
        return self._set_data

    @property
    def executor(self):
        return self._executor

    async def where(self, *, {fields_args_str}) -> Result.Send:
        return await AsyncStoredUpdate(self._executor, self.set_data).where({class_name}(**get_dict_args(locals())))

class AsyncStored{class_name}ORM(AsyncBaseExecutorORM):
    def __init__(self, connectionStringData : ConnectionStringData, attempts : int, wait_timeout : int, sql_version : int | None, api_environment : bool):
        AsyncBaseExecutorORM.__init__(self, AsyncStored, connectionStringData, attempts, wait_timeout, sql_version, api_environment)

    def update(self, {fields_args_str}):
        return AsyncStoredUpdate{class_name}ORM(self, {class_name}(**get_dict_args(locals())))

class Async{class_name}ORM(object):

    def __init__(self, async_dapper : AsyncDapper):
          self._async_dapper = async_dapper

    @property
    def async_dapper(self):
        return self._async_dapper

    async def query(self, attempts : int = None, wait_timeout : int = None):
            attempts = attempts if attempts else self.async_dapper.config.default_attempts
            wait_timeout = wait_timeout if wait_timeout else self.async_dapper.config.default_wait_timeout
            return AsyncQuery{class_name}ORM(self.async_dapper.config.connectionStringDataQuery.get(), attempts, wait_timeout, self.async_dapper.config.sql_version, self.async_dapper.config.api_environment)

    async def stored(self, attempts : int = None, wait_timeout : int = None):
        attempts = attempts if attempts else self.async_dapper.config.default_attempts
        wait_timeout = wait_timeout if wait_timeout else self.async_dapper.config.default_wait_timeout
        return AsyncStored{class_name}ORM(self.async_dapper.config.connectionStringDataStored.get() , attempts, wait_timeout, self.async_dapper.config.sql_version, self.async_dapper.config.api_environment)
    
    @overload
    @staticmethod
    def load(dict_data : dict) -> {class_name}:
        pass

    @overload
    @staticmethod
    def load(list_dict_data : list[dict]) -> list[{class_name}]:
        pass

    @overload
    @staticmethod
    def load(fetchone : Result.Fetchone) -> {class_name}:
        pass

    @overload
    @staticmethod
    def load(fetchall : Result.Fetchall) -> list[{class_name}]:
        pass

    @staticmethod
    def load(*args):
        data = args[0]
        if isinstance(data, dict) or isinstance(data, Result.Fetchone):
            if isinstance(data, Result.Fetchone):
                data = data.dict
            if all(value is None for value in data.values()):
                return {class_name}()

            return {class_name}(**data)

        if isinstance(data, Result.Fetchall):
                data = data.list_dict

        return [{class_name}(**d) for d in data]
    '''



