from typing import Union, List, Literal, Any, Optional
from pydantic import BaseModel, Field, create_model
from datetime import datetime, date
from abc import ABC, abstractmethod

class QueryFieldBase(BaseModel, ABC):

    class Config:
        extra = "forbid"

    prefix: Optional[str] = Field(
        default=..., 
        description="Optional prefix to be prepended to the SQL condition (e.g., for parentheses or NOT)"
    )
    suffix: Optional[str] = Field(
        default=..., 
        description="Optional suffix to be appended to the SQL condition (e.g., for closing parentheses)"
    )
    
    def quote(self, val):
        if isinstance(val, str):
            val = val.replace("'", "''")
            return f"'{val}'"
        elif isinstance(val, bool):
            return '1' if val else '0'
        elif isinstance(val, datetime):
            ms = val.microsecond // 1000
            formatted = val.strftime(f"%Y-%m-%d %H:%M:%S.{ms:03d}")
            return f"'{formatted}'"
        elif isinstance(val, date):
            return f"'{val.strftime('%Y-%m-%d')}'"
        return str(val)

    def format_sql(self, field_name: str, value_expr: str, operator: str) -> str:
        prefix = self.prefix if isinstance(self.prefix, str) else ""
        suffix = self.suffix if isinstance(self.suffix, str) else ""
        return f"{prefix}{field_name} {operator} {value_expr}{suffix}"
    
    @abstractmethod
    def to_sql(self, field_name: str):
        ...
    

class StringQueryField(QueryFieldBase):
    value: Union[str, List[str]] = Field(
        default=...,
        description="The value or list of values to compare against the string column"
    )
    operator: Literal['=', '!=', 'LIKE', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for comparison"
    )

    case_insensitive: bool = Field(
        default=..., 
        description="Whether to apply case-insensitive matching (uses UPPER() on field and value)"
    )

    def apply_like_pattern(self, v: str) -> str:
        if self.operator == 'LIKE':
            return f"%{v}%"
        return v

    def to_sql(self, field_name: str) -> str:
        field_expr = f"UPPER({field_name})" if self.case_insensitive else field_name

        if isinstance(self.value, list):
            values = [self.apply_like_pattern(v) for v in self.value]
            values = [v.upper() if self.case_insensitive else v for v in values]
            value_expr = "(" + ", ".join(self.quote(v) for v in values) + ")"
        else:
            val = self.apply_like_pattern(self.value)
            val = val.upper() if self.case_insensitive else val
            value_expr = self.quote(val)

        return self.format_sql(field_expr, value_expr, self.operator)
    
class NumericQueryField(QueryFieldBase):
    value: Union[int, float, List[Union[int, float]]] = Field(
        default=...,
        description="The numeric value or list of values to compare against the column"
    )
    operator: Literal['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for numeric comparison"
    )

    def to_sql(self, field_name: str) -> str:
        if isinstance(self.value, list):
            value_expr = "(" + ", ".join(str(v) for v in self.value) + ")"
        else:
            value_expr = str(self.value)

        return self.format_sql(field_name, value_expr, self.operator)
    
class BoolQueryField(QueryFieldBase):
    value: bool = Field(
        default=...,
        description="Boolean value to compare against the column"
    )
    operator: Literal['=', '!='] = Field(
        default=...,
        description="SQL operator used for boolean comparison"
    )

    def to_sql(self, field_name: str) -> str:
        value_expr = '1' if self.value else '0'
        return self.format_sql(field_name, value_expr, self.operator)
    

class DateQueryField(QueryFieldBase):
    value:Union[str, datetime, date] = Field(
        default=...,
        description="Date or datetime value to compare (can also be a string in ISO format)"
    )
    operator: Literal['=', '!=', '>', '<', '>=', '<='] = Field(
        default=...,
        description="SQL operator used for date/time comparison"
    )

    def to_sql(self, field_name: str) -> str:
        if isinstance(self.value, str):
            value_expr = f"'{self.value}'"
        else:
            value_expr = self.quote(self.value)
        return self.format_sql(field_name, value_expr, self.operator)
    

class BytesQueryField(QueryFieldBase):
    value: Union[bytes, List[bytes]] = Field(
        default=...,
        description="The bytes value or list of byte values to compare against the column"
    )
    operator: Literal['=', '!=', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for byte comparison"
    )

    def to_sql(self, field_name: str) -> str:
        def format_byte(b: bytes) -> str:
            return "0x" + b.hex()  # SQL Server format

        if isinstance(self.value, list):
            value_expr = "(" + ", ".join(format_byte(v) for v in self.value) + ")"
        else:
            value_expr = format_byte(self.value)

        return self.format_sql(field_name, value_expr, self.operator)
    
class BaseJoinConditionField(BaseModel):
    class Config:
        extra = "forbid"
        
    join_table_column: str = Field(
        ...,
        description="Join table column"
    )
    operator: Literal['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN', 'LIKE'] = Field(
        default=...,
        description="SQL operator used for join condition"
    )

    def to_sql(self, alias_table : str, field_name: str) -> str:
        right = f"{alias_table}.{self.join_table_column}"
        return f"{field_name} {self.operator} {right}"
    
    @classmethod
    def with_join_table_column_type(cls, join_table_column_type: Any):
        new_model = create_model(
            cls.__name__,
            __base__=cls,
            join_table_column=(
                join_table_column_type,
                Field(
                    ...,
                    description=cls.model_fields['join_table_column'].description
                )
            ),
        )
        return new_model

class JoinNumericCondition(BaseJoinConditionField):
    operator: Literal['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for numeric comparison"
    )

class JoinNumericCondition(BaseJoinConditionField):
    operator: Literal['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for numeric comparison in a join condition"
    )

class JoinStringCondition(BaseJoinConditionField):
    operator: Literal['=', '!=', 'LIKE', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for string comparison in a join condition"
    )

class JoinBooleanCondition(BaseJoinConditionField):
    operator: Literal['=', '!='] = Field(
        default=...,
        description="SQL operator used for boolean comparison in a join condition"
    )

class JoinDateCondition(BaseJoinConditionField):
    operator: Literal['=', '!=', '>', '<', '>=', '<='] = Field(
        default=...,
        description="SQL operator used for date/time comparison in a join condition"
    )

class JoinBytesCondition(BaseJoinConditionField):
    operator: Literal['=', '!=', 'IN', 'NOT IN'] = Field(
        default=...,
        description="SQL operator used for byte comparison in a join condition"
    )