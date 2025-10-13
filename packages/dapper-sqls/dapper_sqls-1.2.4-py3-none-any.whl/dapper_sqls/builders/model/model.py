# coding: utf-8

from itertools import groupby
import os
from .utils import (create_content_orm, TableInformation, ColumnInformation, InformationSchemaRoutines, create_field, create_content_async_orm,
                    create_params_routine, get_parameters_with_defaults, create_queue_update, create_table_description, create_arg,
                    SqlTable, SqlStored)
from ...models import TableBaseModel

class TableBuilderData:
    def __init__(self, table_schema : str, table_name : str, class_name : str, model : str, orm : str | None, async_orm : str | None):
        self.table_schema = table_schema
        self.table_name = table_name
        self.class_name = class_name
        self.model = model
        self.orm = orm
        self.async_orm = async_orm

class RoutineBuilderData:
    def __init__(self, table_schema : str, stp_name : str, content_stp : str, content_async_stp : str):
        self.table_schema = table_schema
        self.stp_name = stp_name
        self.content_stp = content_stp
        self.content_async_stp = content_async_stp

class BuilderData(object):
    def __init__(self, table_catalog : str):
        self.table_catalog = table_catalog
        self.talbes : list[TableBuilderData] = []
        self.routines : list[RoutineBuilderData] = []

class ModelBuilder(object):

    class TableOptions(object):
        def __init__(self, table_name : str, *, create_orm=True, ignore_table=False):
            self.table_name = table_name
            self.create_orm = create_orm
            self.ignore_table = ignore_table

    class RoutineOptions(object):
        def __init__(self, routine_name : str, ignore_routine=False):
            self.routine_name = routine_name
            self.ignore_routine = ignore_routine

    def __init__(self, dapper):
        self._dapper = dapper

        self.query_columns = """
            SELECT 
                c.TABLE_CATALOG, 
                c.TABLE_SCHEMA, 
                c.TABLE_NAME, 
                c.COLUMN_NAME, 
                c.DATA_TYPE, 
                c.CHARACTER_MAXIMUM_LENGTH,
                c.IS_NULLABLE,

                -- Coluna separada: IS_IDENTITY
                CASE 
                    WHEN COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') = 1 
                        THEN 'YES' 
                    ELSE 'NO' 
                END AS IS_IDENTITY,

                CASE 
                    WHEN i.is_primary_key = 1 THEN 'YES'
                    ELSE 'NO'
                END AS IS_PRIMARY_KEY,

                CASE 
                    WHEN i.is_unique = 1 THEN 'YES'
                    ELSE 'NO'
                END AS IS_UNIQUE,

                -- Auto_Description como string JSON
                CONCAT(
                '{',
                    '"type": "', 
                        c.DATA_TYPE COLLATE SQL_Latin1_General_CP1_CI_AS,
                        CASE 
                            WHEN c.CHARACTER_MAXIMUM_LENGTH IS NOT NULL 
                                THEN CONCAT('(', 
                                    CASE 
                                        WHEN c.CHARACTER_MAXIMUM_LENGTH = -1 
                                            THEN 'MAX' 
                                        ELSE CAST(c.CHARACTER_MAXIMUM_LENGTH AS VARCHAR) 
                                    END, 
                                ')')
                            ELSE ''
                        END, 
                    '", ',
                    '"nullable": ', CASE WHEN c.IS_NULLABLE = 'YES' THEN 'true' ELSE 'false' END, ', ',
                    '"identity": ', CASE WHEN COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'IsIdentity') = 1 THEN 'true' ELSE 'false' END, ', ',
                    '"default": ', 
                        CASE 
                            WHEN dc.definition IS NOT NULL 
                                THEN '"' + REPLACE(REPLACE(dc.definition, '"', '\"'), '''', '''') + '"' 
                            ELSE 'null' 
                        END, ', ',
                    '"primary_key": ', CASE WHEN i.is_primary_key = 1 THEN 'true' ELSE 'false' END, ', ',
                    '"unique": ', CASE WHEN i.is_unique = 1 THEN 'true' ELSE 'false' END, ', ',
                    '"foreign_key": ',
                        CASE 
                            WHEN fk_constraint.object_id IS NOT NULL THEN CONCAT(
                                '{',
                                    '"name": "', fk_constraint.name COLLATE SQL_Latin1_General_CP1_CI_AS, '", ',
                                    '"ref_table": "', ref_schema.name COLLATE SQL_Latin1_General_CP1_CI_AS, '.', ref_table.name COLLATE SQL_Latin1_General_CP1_CI_AS, '", ',
                                    '"ref_column": "', ref_column.name COLLATE SQL_Latin1_General_CP1_CI_AS, '", ',
                                    '"on_delete": "', fk_constraint.delete_referential_action_desc COLLATE SQL_Latin1_General_CP1_CI_AS, '", ',
                                    '"on_update": "', fk_constraint.update_referential_action_desc COLLATE SQL_Latin1_General_CP1_CI_AS, '"',
                                '}'
                            )
                            ELSE 'false'
                        END,
                '}'
            ) AS AUTO_COLUMN_DESCRIPTION,

                col_ep.value AS COLUMN_DESCRIPTION

            FROM 
                INFORMATION_SCHEMA.COLUMNS c
            JOIN 
                (SELECT TABLE_NAME, TABLE_SCHEMA, TABLE_CATALOG FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE') t
                ON c.TABLE_NAME = t.TABLE_NAME AND c.TABLE_SCHEMA = t.TABLE_SCHEMA

            LEFT JOIN 
                sys.columns sc 
                ON sc.object_id = OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME) 
                AND sc.name = c.COLUMN_NAME

            LEFT JOIN 
                sys.default_constraints dc 
                ON dc.parent_object_id = sc.object_id 
                AND dc.parent_column_id = sc.column_id

            LEFT JOIN 
                sys.extended_properties col_ep 
                ON OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME) = col_ep.major_id 
                AND COLUMNPROPERTY(OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME), c.COLUMN_NAME, 'ColumnId') = col_ep.minor_id
                AND col_ep.name = 'MS_Description'

            LEFT JOIN 
                sys.index_columns ic 
                ON ic.object_id = sc.object_id AND ic.column_id = sc.column_id

            LEFT JOIN 
                sys.indexes i 
                ON i.object_id = ic.object_id AND i.index_id = ic.index_id

            LEFT JOIN 
                sys.foreign_key_columns fkc 
                ON fkc.parent_object_id = sc.object_id AND fkc.parent_column_id = sc.column_id

            LEFT JOIN 
                sys.foreign_keys fk_constraint 
                ON fk_constraint.object_id = fkc.constraint_object_id

            LEFT JOIN 
                sys.tables ref_table 
                ON ref_table.object_id = fkc.referenced_object_id

            LEFT JOIN 
                sys.schemas ref_schema 
                ON ref_schema.schema_id = ref_table.schema_id

            LEFT JOIN 
                sys.columns ref_column 
                ON ref_column.column_id = fkc.referenced_column_id AND ref_column.object_id = ref_table.object_id
        """

        self.query_tables = """
            WITH
            col_data AS (
                SELECT 
                    c.object_id,
                    COUNT(*) AS column_count,
                    STRING_AGG('"' + c.name + '"' COLLATE DATABASE_DEFAULT, ',' ) 
                        WITHIN GROUP (ORDER BY c.column_id) AS identity_list
                FROM sys.columns c
                WHERE c.is_identity = 1
                GROUP BY c.object_id
            ),
            pk_data AS (
                SELECT 
                    i.object_id,
                    CONCAT(
                        '{',
                            '"name":"', i.name COLLATE DATABASE_DEFAULT, '",',
                            '"columns":[', STRING_AGG('"' + c.name + '"' COLLATE DATABASE_DEFAULT, ',') 
                                WITHIN GROUP (ORDER BY ic.key_ordinal), ']',
                        '}'
                    ) AS pk_json
                FROM sys.indexes i
                JOIN sys.index_columns ic 
                    ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                JOIN sys.columns c 
                    ON c.object_id = ic.object_id AND c.column_id = ic.column_id
                WHERE i.is_primary_key = 1
                GROUP BY i.object_id, i.name
            ),
            UniqueIndexColumns AS (
                SELECT 
                    i.object_id,
                    i.name COLLATE DATABASE_DEFAULT AS index_name,
                    c.name COLLATE DATABASE_DEFAULT AS column_name,
                    ic.key_ordinal
                FROM sys.indexes i
                JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                JOIN sys.columns c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
                WHERE i.is_unique = 1 AND i.is_primary_key = 0
            ),
            UniqueColumnsByIndex AS (
                SELECT
                    object_id,
                    index_name,
                    STRING_AGG('"' + column_name + '"' COLLATE DATABASE_DEFAULT, ',') 
                        WITHIN GROUP (ORDER BY key_ordinal) AS columns_json
                FROM UniqueIndexColumns
                GROUP BY object_id, index_name
            ),
            UniqueConstraintsJSON AS (
                SELECT 
                    object_id,
                    '[' + STRING_AGG(
                        CONCAT(
                            '{',
                                '"name":"', index_name, '",',
                                '"columns":[', columns_json, ']',
                            '}'
                        ) COLLATE DATABASE_DEFAULT, ','
                    ) + ']' AS unique_json
                FROM UniqueColumnsByIndex
                GROUP BY object_id
            ),
            ForeignKeysJSON AS (
                SELECT 
                    fkc.parent_object_id,
                    '[' + STRING_AGG(
                        CONCAT(
                            '{',
                                '"name":"', fk.name COLLATE DATABASE_DEFAULT, '",',
                                '"column":"', parent_col.name COLLATE DATABASE_DEFAULT, '",',
                                '"ref_table":"', ref_schema.name COLLATE DATABASE_DEFAULT, '.', ref_table.name COLLATE DATABASE_DEFAULT, '",',
                                '"ref_column":"', ref_col.name COLLATE DATABASE_DEFAULT, '",',
                                '"on_delete":"', fk.delete_referential_action_desc COLLATE DATABASE_DEFAULT, '",',
                                '"on_update":"', fk.update_referential_action_desc COLLATE DATABASE_DEFAULT, '"',
                            '}'
                        ) COLLATE DATABASE_DEFAULT, ','
                    ) + ']' AS foreign_keys_json
                FROM sys.foreign_keys fk
                JOIN sys.foreign_key_columns fkc 
                    ON fk.object_id = fkc.constraint_object_id
                JOIN sys.columns parent_col 
                    ON parent_col.object_id = fkc.parent_object_id 
                    AND parent_col.column_id = fkc.parent_column_id
                JOIN sys.tables ref_table 
                    ON ref_table.object_id = fkc.referenced_object_id
                JOIN sys.columns ref_col 
                    ON ref_col.object_id = fkc.referenced_object_id 
                    AND ref_col.column_id = fkc.referenced_column_id
                JOIN sys.schemas ref_schema 
                    ON ref_schema.schema_id = ref_table.schema_id
                GROUP BY fkc.parent_object_id
            )

            SELECT 
                t.TABLE_CATALOG,
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                tbl_ep.value AS TABLE_DESCRIPTION,
                CONCAT(
                    '{',
                        '"columns": ', ISNULL(col_count.column_count, 0), ', ',
                        '"identity": [', ISNULL(col_count.identity_list, ''), '], ',
                        '"primary_keys": ', ISNULL(pk.pk_json, 'null'), ', ',
                        '"unique_constraints": ', ISNULL(uc.unique_json, '[]'), ', ',
                        '"foreign_keys": ', ISNULL(fk.foreign_keys_json, '[]'),
                    '}'
                ) AS AUTO_TABLE_DESCRIPTION
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN sys.extended_properties tbl_ep 
                ON tbl_ep.major_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
                AND tbl_ep.minor_id = 0
                AND tbl_ep.name = 'MS_Description'
            LEFT JOIN col_data col_count
                ON col_count.object_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
            LEFT JOIN pk_data pk
                ON pk.object_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
            LEFT JOIN UniqueConstraintsJSON uc
                ON uc.object_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
            LEFT JOIN ForeignKeysJSON fk
                ON fk.parent_object_id = OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME)
            WHERE t.TABLE_TYPE = 'BASE TABLE';
        """

        self.query_routines = f"""
            SELECT  
                r.SPECIFIC_CATALOG,
                r.SPECIFIC_SCHEMA,
                r.SPECIFIC_NAME,
                sm.definition AS PROCEDURE_DEFINITION,
                (
                    SELECT 
                        p.ORDINAL_POSITION,
                        p.PARAMETER_NAME,
                        p.DATA_TYPE
                    FROM INFORMATION_SCHEMA.PARAMETERS p
                    WHERE p.SPECIFIC_NAME = r.SPECIFIC_NAME
                    ORDER BY p.ORDINAL_POSITION
                    FOR JSON PATH
                ) AS PARAMETERS
            FROM INFORMATION_SCHEMA.ROUTINES r
            JOIN sys.sql_modules sm 
                ON OBJECT_NAME(sm.object_id) = r.SPECIFIC_NAME
            WHERE r.ROUTINE_TYPE = 'PROCEDURE'
            ORDER BY r.SPECIFIC_NAME;
        """

    @property
    def dapper(self):
        return self._dapper
    
    def get_tables_data(self):
        with self.dapper.query() as db:
            information_schema_tables = db.fetchall(self.query_tables)
            if not information_schema_tables.success:
                return False
            information_schema_tables : list[TableInformation] = self.dapper.load(TableInformation, information_schema_tables)
         
        data : dict[str, TableInformation] = {}
        for table in information_schema_tables:
            if not table.TABLE_NAME.startswith('__'):
                key = f"{table.TABLE_CATALOG}{table.TABLE_SCHEMA}{table.TABLE_NAME}"
                data[key] = table
        return data

    def get_columns_data(self):
        with self.dapper.query() as db:
            information_schema_tables = db.fetchall(self.query_columns)
            if not information_schema_tables.success:
                return False

            information_schema_tables = self.dapper.load(ColumnInformation, information_schema_tables)
            information_schema_tables = [table for table in information_schema_tables if not table.TABLE_NAME.startswith('__')]

        # ✅ Remover colunas duplicadas com base em (TABLE_NAME, COLUMN_NAME)
        unique_columns = {}
        for col in information_schema_tables:
            key = (col.TABLE_NAME, col.COLUMN_NAME)
            if key not in unique_columns:
                unique_columns[key] = col
        information_schema_tables = list(unique_columns.values())

        # Agrupamento por tabela
        information_schema_tables.sort(key=lambda x: x.TABLE_NAME)
        grouped_data = groupby(information_schema_tables, lambda x: x.TABLE_NAME)
        grouped_list: list[list[ColumnInformation]] = [[obj for obj in group] for _, group in grouped_data]

        if not grouped_list:
            return False
        return grouped_list

    def get_routines_data(self) -> list[SqlStored]:
        with self.dapper.query() as db:
            rows = db.fetchall(self.query_routines)
            if not rows.success:
                return []
        return self.dapper.load(SqlStored, rows)
    
    def get_models_db(self, tables : dict[str, SqlTable]):
        models : list[TableBaseModel] = []
        for table in tables.values():
            if not table.available:
                continue
            models.append(self.get_model_db(table))
        return models

    def get_model_db(self, table : SqlTable):
            
        from datetime import datetime
        from pydantic import Field
        from typing import Union, Optional, ClassVar, Set
        from dapper_sqls import (TableBaseModel, StringQueryField, NumericQueryField, BoolQueryField, DateQueryField, BytesQueryField,
                            JoinNumericCondition, JoinStringCondition, JoinBooleanCondition, JoinDateCondition, JoinBytesCondition)

        
        table_description = create_table_description(table)

        table_name = table.TABLE_NAME
        class_name = table_name 
        schema = table.TABLE_SCHEMA

        fields = [create_field(row) for row in table.COLUMNS if row.available]
        fields_str = "\n    ".join(fields)

        identities = {d.COLUMN_NAME for d in table.COLUMNS if d.IS_IDENTITY == "YES" and d.available}

        primary_keys = {d.COLUMN_NAME for d in table.COLUMNS if d.IS_PRIMARY_KEY == "YES" and d.available}

        optional_fields = {d.COLUMN_NAME for d in table.COLUMNS if d.IS_NULLABLE == "YES" and d.available}

        max_length_fields = {
            d.COLUMN_NAME: d.CHARACTER_MAXIMUM_LENGTH
            for d in table.COLUMNS
            if d.CHARACTER_MAXIMUM_LENGTH is not None and d.CHARACTER_MAXIMUM_LENGTH > 0 and d.available
        }

        table_alias = table_name.lower()

        content_model = f'''# coding: utf-8
class {class_name}(TableBaseModel):
    TABLE_NAME: ClassVar[str] = '[{schema}].[{table_name}]'

    TABLE_ALIAS: ClassVar[str] = '{table_alias}'
    
    DESCRIPTION : ClassVar[str] = '{table_description}'
    
    IDENTITIES : ClassVar[Set[str]] = {identities}

    PRIMARY_KEYs : ClassVar[Set[str]] = {primary_keys}

    OPTIONAL_FIELDS : ClassVar[Set[str]] = {optional_fields}   

    MAX_LENGTH_FIELDS: ClassVar[dict[str, int]] = {max_length_fields}
    
    {fields_str}
            '''
        local_vars = {}
        exec(content_model, {
            "TableBaseModel": TableBaseModel,
            "StringQueryField": StringQueryField,
            "NumericQueryField": NumericQueryField,
            "BoolQueryField": BoolQueryField,
            "DateQueryField": DateQueryField,
            "BytesQueryField": BytesQueryField,
            "JoinNumericCondition": JoinNumericCondition,
            "JoinStringCondition": JoinStringCondition,
            "JoinBooleanCondition": JoinBooleanCondition,
            "JoinDateCondition": JoinDateCondition,
            "JoinBytesCondition": JoinBytesCondition,
            "datetime": datetime,
            "Field": Field,
            "Union": Union,
            "Optional": Optional,
            "ClassVar": ClassVar,
            "Set": Set
        }, local_vars)
        return local_vars[class_name]

    def create_model_db(self, dir_path : str, create_orm = True, create_stp = True, *, table_catalog : str | list[str] | tuple[str] = "all",
                          table_schema : str | list[str] | tuple[str] = "all",
                          tables_options : list[TableOptions] = [], routines_oprions : list[RoutineOptions] = []):

        dict_tables_options = {}
        if tables_options:
            dict_tables_options = {options.table_name : options for options in tables_options}
            create_orm = False
            for options in tables_options:
                if options.create_orm:
                    create_orm = True
                    break

        dict_routines_options = {options.routine_name : options for options in routines_oprions}
        if routines_oprions:
            create_stp = False
            for options in routines_oprions:
                if not options.ignore_routine:
                    create_stp = True
                    break

        information_db = self.get_columns_data()
        information_routines = []
        if create_stp:
            information_routines = self.get_routines_data()
        if not information_db:
            return False
        
        table_data = self.get_tables_data()

        table_catalog = [table_catalog] if isinstance(table_catalog, str) and table_catalog != "all" else table_catalog
        table_schema = [table_schema] if isinstance(table_schema, str) and table_schema != "all" else table_schema
       
        builder_data : dict[str, BuilderData] = {}
        import_init_db = ""
        for data in information_db:

            if table_catalog != "all":
                if data[0].TABLE_CATALOG not in table_catalog :
                    continue

            if table_schema != "all":
                if data[0].TABLE_SCHEMA not in table_schema :
                    continue

            table_options = dict_tables_options.get(data[0].TABLE_NAME)
            if table_options:
                if table_options.ignore_table:
                    continue
            
            table_description = ""
            key_table = f"{data[0].TABLE_CATALOG}{data[0].TABLE_SCHEMA}{data[0].TABLE_NAME}"
            table_info = table_data.get(key_table)
            if table_info:
                table_description = create_table_description(table_info)

            table_name = data[0].TABLE_NAME
            class_name = table_name #table_name.replace("TBL_", "")
            schema = data[0].TABLE_SCHEMA

            fields = [create_field(row) for row in data]
            fields_str = "\n    ".join(fields)

            # original_fields = [create_field(row, False) for row in data]
            # original_fields_str = "\n        ".join(original_fields)

            fields_args = [create_arg(row) for row in data]
            fields_args_str = ", ".join(fields_args)

            identities = {d.COLUMN_NAME for d in data if d.IS_IDENTITY == "YES"}

            primary_keys = {d.COLUMN_NAME for d in data if d.IS_PRIMARY_KEY == "YES"}

            optional_fields = {d.COLUMN_NAME for d in data if d.IS_NULLABLE == "YES"}

            max_length_fields = {
                d.COLUMN_NAME: d.CHARACTER_MAXIMUM_LENGTH
                for d in data
                if d.CHARACTER_MAXIMUM_LENGTH is not None and d.CHARACTER_MAXIMUM_LENGTH > 0
            }

            table_alias = table_name.lower()
            
            content_model = f'''# coding: utf-8

from dapper_sqls import (TableBaseModel, StringQueryField, NumericQueryField, BoolQueryField, DateQueryField, BytesQueryField,
                        JoinNumericCondition, JoinStringCondition, JoinBooleanCondition, JoinDateCondition, JoinBytesCondition)
from datetime import datetime
from pydantic import Field
from typing import Union, Optional, ClassVar, Set

class {class_name}(TableBaseModel):
    TABLE_NAME: ClassVar[str] = '[{schema}].[{table_name}]'

    TABLE_ALIAS: ClassVar[str] = '{table_alias}'
    
    DESCRIPTION : ClassVar[str] = '{table_description}'
    
    IDENTITIES : ClassVar[Set[str]] = {identities}

    PRIMARY_KEYs : ClassVar[Set[str]] = {primary_keys}

    OPTIONAL_FIELDS : ClassVar[Set[str]] = {optional_fields}   

    MAX_LENGTH_FIELDS: ClassVar[dict[str, int]] = {max_length_fields}
    
    {fields_str}
    
    {create_queue_update(fields_args_str)}
\n
            '''
            
            table_create_orm = create_orm
            if table_options:
                    table_create_orm = table_options.create_orm

            content_orm = create_content_orm(class_name, fields_args_str) if table_create_orm else None
            content_async_orm = create_content_async_orm(class_name, fields_args_str) if table_create_orm else None

            catalog = data[0].TABLE_CATALOG
            if catalog not in builder_data:
                builder_data[catalog] = BuilderData(catalog)

            table_builder_data = TableBuilderData(schema, table_name, class_name, content_model, content_orm, content_async_orm)
            builder_data[catalog].talbes.append(table_builder_data)
      
        for data in information_routines:

            if table_catalog != "all":
                if data.SPECIFIC_CATALOG not in table_catalog :
                    continue

            if table_schema != "all":
                if data.SPECIFIC_SCHEMA not in table_schema :
                    continue

            routine_oprions = dict_routines_options.get(data.SPECIFIC_NAME)
            if routine_oprions:
                if routine_oprions.ignore_routine:
                    continue
            
            defaults_values = get_parameters_with_defaults(data.PROCEDURE_DEFINITION)
            params_routine = [create_params_routine(row, defaults_values) for row in data]
            params_routine_str = ", ".join(params_routine)

            stp_name = data.SPECIFIC_NAME.replace('STP_', '')
            content_routine = f'''
    def {stp_name}(self, *, {params_routine_str}):
        return StpBuilder(self.dapper, '[{data.SPECIFIC_SCHEMA}].[{data.SPECIFIC_NAME}]',locals())'''

            content_async_routine = f'''
    def {stp_name}(self, *, {params_routine_str}):
        return AsyncStpBuilder(self.async_dapper, '[{data.SPECIFIC_SCHEMA}].[{data.SPECIFIC_NAME}]', locals())'''
            
            catalog = data.SPECIFIC_CATALOG
            if catalog not in builder_data:
                builder_data[catalog] = BuilderData(catalog)

            builder_data[catalog].routines.append(RoutineBuilderData(data.SPECIFIC_SCHEMA, data.SPECIFIC_NAME, content_routine, content_async_routine))

        for catalog, data in builder_data.items():
            import_init_db += f"from .{catalog} import {catalog}\n"
  
            dir_catalog = os.path.join(dir_path, catalog)
            schema_data_tables : dict[str, list[TableBuilderData]] = {}
            for table in data.talbes:
                if table.table_schema not in schema_data_tables:
                    schema_data_tables[table.table_schema] = []

                dir_schema = os.path.join(dir_catalog, table.table_schema)
                dir_table = os.path.join(dir_schema, table.table_name)

                if not os.path.exists(dir_table):
                    os.makedirs(dir_table)

                table_options = dict_tables_options.get(table.table_name)

                table_create_orm = create_orm
                if table_options:
                    table_create_orm = table_options.create_orm

                if table_create_orm:
                    with open(os.path.join(dir_table ,'orm.py'), 'w', encoding='utf-8') as file:
                        file.write(''.join(table.orm))

                    with open(os.path.join(dir_table ,'async_orm.py'), 'w', encoding='utf-8') as file:
                        file.write(''.join(table.async_orm))

                with open(os.path.join(dir_table ,f'__init__.py'), 'w', encoding='utf-8') as file:
                    if table_create_orm:
                        file.write(f'from .orm import {table.class_name}ORM\nfrom .async_orm import Async{table.class_name}ORM\nfrom .model import {table.class_name}')
                    else:
                        file.write(f'from .model import {table.class_name}')

                with open(os.path.join(dir_table ,'model.py'), 'w', encoding='utf-8') as file:
                    file.write(''.join(table.model))

                
                schema_data_tables[table.table_schema].append(table)

            schema_data_routine : dict[str, list[RoutineBuilderData]] = {}
            content_file_routine = '''# coding: utf-8
from dapper_sqls import StpBuilder
from dapper_sqls import Dapper
from datetime import datetime
from typing import Union

class stp(object):

    def __init__(self, dapper : Dapper):
        self._dapper = dapper

    @property
    def dapper(self):
        return self._dapper
            '''

            content_file_async_rounine = '''# coding: utf-8
from dapper_sqls import AsyncStpBuilder
from dapper_sqls import AsyncDapper
from datetime import datetime
from typing import Union

class async_stp(object):

    def __init__(self, async_dapper : AsyncDapper):
        self._async_dapper = async_dapper

    @property
    def async_dapper(self):
        return self._async_dapper
            '''

            for routine in data.routines:
                if routine.table_schema not in schema_data_routine:
                    schema_data_routine[routine.table_schema] = []

                dir_schema = os.path.join(dir_catalog, routine.table_schema)
                if not os.path.exists(dir_schema):
                    os.makedirs(dir_schema)

                content_file_routine += f'{routine.content_stp}\n' 
                content_file_async_rounine += f'{routine.content_async_stp}\n' 

            if data.routines:
                dir_schema = os.path.join(dir_catalog, data.routines[0].table_schema)
                with open(os.path.join(dir_schema ,'routines.py'), 'w', encoding='utf-8') as file:
                     file.write(''.join(content_file_routine))
                with open(os.path.join(dir_schema ,'async_routines.py'), 'w', encoding='utf-8') as file:
                     file.write(''.join(content_file_async_rounine))

            import_init_catalog = ""
            class_init_catalog = f'''class {catalog}(object):\n'''
         
            for schema, data in schema_data_tables.items():
                import_init_catalog += f"from .{schema} import schema_{schema}\n"
                class_init_catalog += f"\n    class {schema}(schema_{schema}):\n        ...\n"
                import_init_schema = ""
                class_init_schema = ""
                class_models_schema = "    class models(object):\n"
                class_orm_schema = "    class orm(object):\n        def __init__(self, dapper : Dapper):\n"
                class_async_orm_schema = "    class async_orm(object):\n        def __init__(self, async_dapper : AsyncDapper):\n"
                for table in data:

                    table_options = dict_tables_options.get(table.table_name)
                    table_create_orm = create_orm
                    if table_options:
                        table_create_orm = table_options.create_orm

                    dir_schema = os.path.join(dir_catalog, schema)
                    class_models_schema += f"\n        class {table.class_name}({table.class_name}):\n            ...\n"
                    if table_create_orm:
                        class_orm_schema += f"            self.{table.class_name} = {table.class_name}ORM(dapper)\n"
                        class_async_orm_schema += f"            self.{table.class_name} = Async{table.class_name}ORM(async_dapper)\n"
                        import_init_schema += f"from .{table.table_name} import {table.class_name}, {table.class_name}ORM, Async{table.class_name}ORM\n"
                        class_init_schema += f"\n    class {table.class_name}ORM({table.class_name}ORM):\n        ...\n"
                        class_init_schema += f"\n    class Async{table.class_name}ORM(Async{table.class_name}ORM):\n        ...\n"
                    else:
                        import_init_schema += f"from .{table.table_name} import {table.class_name}\n"

                if information_routines :
                    import_init_schema += "from .routines import stp\nfrom .async_routines import async_stp\n"

                class_stp = "\n    class stp(stp):\n        ...\n" if information_routines else ""
                class_async_stp = "\n    class async_stp(async_stp):\n        ...\n" if information_routines else ""
                
                class_schema = f"class schema_{schema}(object):\n"
                if create_orm:
                    class_init_schema = f"{class_schema}{class_stp}{class_async_stp}\n{class_models_schema}\n{class_orm_schema}\n{class_async_orm_schema}\n{class_init_schema}"
                    content_init_schema = f"{import_init_schema}\nfrom dapper_sqls import Dapper, AsyncDapper\n\n{class_init_schema}"
                else:
                    class_init_schema = f"{class_schema}{class_stp}{class_async_stp}\n{class_models_schema}"
                    content_init_schema = f"{import_init_schema}\n\n{class_init_schema}"

                with open(os.path.join(dir_schema ,f'__init__.py'), 'w', encoding='utf-8') as file:
                    file.write(''.join(content_init_schema))

            content_init_catalog = f"{import_init_catalog}\n\n{class_init_catalog}"
            with open(os.path.join(dir_catalog ,f'__init__.py'), 'w', encoding='utf-8') as file:
                    file.write(''.join(content_init_catalog))

        if builder_data:
            #with open(os.path.join(dir_path ,f'__init__.py'), 'w', encoding='utf-8') as file:
            #        file.write(''.join(import_init_db))

            return True