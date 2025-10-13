# coding: utf-8
from typing import Union
from datetime import datetime, date
from ..models import TableBaseModel, QueryFieldBase, BaseJoinConditionField, SearchTable, JoinSearchTable
import json

class QueryBuilder(object):

    @classmethod
    def build_where_clause(cls, model: TableBaseModel, table_alias: str = "") -> str:
        clause_parts = []

        for field_name, field_value in model:
            
            if field_value is None:
                continue

            # Constrói o nome qualificado com alias, se houver
            qualified_field = f"{table_alias}.{field_name}" if table_alias.strip() else field_name

            if  isinstance(field_value, BaseJoinConditionField):
                continue

            elif isinstance(field_value, QueryFieldBase):
                sql = field_value.to_sql(qualified_field)
                if sql:
                    clause_parts.append(sql)

            else:
                if isinstance(field_value, str):
                    escaped_value = field_value.replace("'", "''")
                    clause_parts.append(f"{qualified_field} = '{escaped_value}'")
                elif isinstance(field_value, bool):
                    clause_parts.append(f"{qualified_field} = {'1' if field_value else '0'}")
                elif isinstance(field_value, datetime):
                    ms = field_value.microsecond // 1000
                    formatted = field_value.strftime(f"%Y-%m-%d %H:%M:%S.{ms:03d}")
                    clause_parts.append(f"{qualified_field} = '{formatted}'")
                elif isinstance(field_value, date):
                    clause_parts.append(f"{qualified_field} = '{field_value.strftime('%Y-%m-%d')}'")
                elif isinstance(field_value, bytes):
                    # Converte os bytes em uma string hexadecimal para SQL (ex: 0x4E6574)
                    hex_value = field_value.hex()
                    clause_parts.append(f"{qualified_field} = 0x{hex_value}")
                elif isinstance(field_value, dict):
                    clause_parts.append(f"{qualified_field} = '{json.dumps(field_value, ensure_ascii=False)}'")
                else:
                    clause_parts.append(f"{qualified_field} = '{str(field_value)}'")
  
        return " AND ".join(clause_parts)
    
    @staticmethod
    def format_sql_value(value):
        if isinstance(value, str):
            value = value.replace("'", "''")
            return f"'{value}'"
        elif isinstance(value, bool):
            return '1' if value else '0'
        elif isinstance(value, datetime):
            ms = value.microsecond // 1000
            formatted = value.strftime(f"%Y-%m-%d %H:%M:%S.{ms:03d}")
            return f"'{formatted}'"
        elif isinstance(value, date):
            return f"'{value.strftime('%Y-%m-%d')}'"
        elif isinstance(value, bytes):
            return f"0x{value.hex()}"
        elif isinstance(value, dict):
            return f"'{json.dumps(value, ensure_ascii=False)}'"
        elif value is None:
            return "NULL"
        else:
            return f"'{str(value)}'"
    
    @staticmethod
    def build_select_fields(search_table: SearchTable, table_alias: str, rename_fields: bool = True) -> str:
        model_fields = search_table.model.model_fields.keys()

        if not rename_fields:
            # Se include estiver presente, listar colunas com alias normal
            if search_table.include:
                fields = [f"{table_alias}.{f}" for f in search_table.include]
            else:
                # Nenhuma regra definida, usar '*'
                return f"{table_alias}.*"
            return ", ".join(fields)

        # Caso rename_fields=True
        if search_table.include:
            fields = search_table.include
        else:
            fields = list(model_fields)

        select_parts = [
            f"{table_alias}.{field} AS {table_alias}{field}" for field in fields
        ]
        return ", ".join(select_parts)

    @classmethod
    def update(cls, model: TableBaseModel, where : Union[str , TableBaseModel]):
        model._reset_defaults()
        update_data = model.model_dump(exclude_none=True)
        if not isinstance(where, str):
            where._reset_defaults()
            for key in where.model_dump(exclude_none=True):
                if key in update_data:
                    update_data.pop(key, None)
            where = cls.build_where_clause(where)

        set_clause = ", ".join(
            f"{key} = {cls.format_sql_value(value)}"
            for key, value in update_data.items()
        )
        sql_query = f"UPDATE {model.TABLE_NAME} SET {set_clause} WHERE {where}"
        return sql_query

    @classmethod
    def insert(cls, model: TableBaseModel, name_column_id = 'Id'):
        model._reset_defaults()
        insert_data = {
            k: int(v) if isinstance(v, bool) else v
            for k, v in model.model_dump(exclude_none=True).items()
        }
        columns = ", ".join(insert_data.keys())
        values = ", ".join(cls.format_sql_value(v) for v in insert_data.values())
        sql_query = f"""
            INSERT INTO {model.TABLE_NAME} ({columns})
            OUTPUT INSERTED.{name_column_id} AS Id
            VALUES ({values})
            """
        return sql_query

    @classmethod
    def select(cls, model: TableBaseModel, additional_sql : str = "" ,select_top : int= None):
        model._reset_defaults()
        top_clause = f"TOP ({select_top}) * " if select_top else "*"
        where_clause = cls.build_where_clause(model)

        sql_query = f"SELECT {top_clause} FROM {model.TABLE_NAME}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        sql_query = f'{sql_query} {additional_sql}'
        return sql_query
    
    @staticmethod
    def build_on_clause(join_model: TableBaseModel, join_alias: str, base_alias: str) -> str:
        clause_parts = []
        for field_name, field_value in join_model:
            if isinstance(field_value, BaseJoinConditionField):
                sql = field_value.to_sql(base_alias, f"{join_alias}.{field_name}")
                if sql:
                    clause_parts.append(sql)
        return " AND ".join(clause_parts)
    
    @classmethod
    def select_with_joins(cls, main_search: SearchTable, joins: list[JoinSearchTable] = [], additional_sql: str = "", select_top: int = None) -> str:
        main_model = main_search.model
        main_model._reset_defaults()
        main_table = main_model.TABLE_NAME
        main_table_alias = main_model.TABLE_ALIAS
        top_clause = f"TOP ({select_top})" if select_top else ""

        # Campos SELECT da tabela principal
        select_fields = cls.build_select_fields(main_search, main_table_alias, False)

        # JOINs
        join_clauses = []
        join_where_clauses : list[str] = []
        for join_search in joins:
            join_model = join_search.model
            join_model._reset_defaults()
            join_table = join_model.TABLE_NAME
            join_table_alias = join_model.TABLE_ALIAS

            join_type = join_search.join_type.upper()
            on_conditions = cls.build_on_clause(join_model, join_table_alias, main_table_alias)

            # Usa o alias no JOIN
            join_clause = (
                f"{join_type} JOIN {join_table} AS {join_table_alias} "
                f"ON {on_conditions}"
            )
            join_clauses.append(join_clause)
            
            # Campos SELECT do JOIN
            select_fields += ", " + cls.build_select_fields(join_search, join_table_alias)

            join_where_clause = cls.build_where_clause(join_model, join_table_alias)
            if join_where_clause.strip():
                join_where_clauses.append(join_where_clause)

        # WHERE principal
        where_clause = cls.build_where_clause(main_model, main_table_alias)
        where_part = f"WHERE {where_clause}" if where_clause else ""
        for join_where_clause in join_where_clauses:
            where_part += f" AND {join_where_clause}"

        # SQL final
        sql_query = (
            f"SELECT {top_clause} {select_fields} "
            f"FROM {main_table} AS {main_table_alias} "
            + " ".join(join_clauses)
            + f" {where_part} {additional_sql}"
        ).strip()

        return sql_query
    
    @classmethod
    def delete(cls, model: TableBaseModel):
        model._reset_defaults()
        where_clause = cls.build_where_clause(model)
        if not where_clause:
            raise ValueError("DELETE operation requires at least one condition.")
        sql_query = f"DELETE FROM {model.TABLE_NAME} WHERE {where_clause}"
        return sql_query

