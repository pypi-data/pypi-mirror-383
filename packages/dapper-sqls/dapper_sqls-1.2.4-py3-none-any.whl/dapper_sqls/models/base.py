from pydantic import BaseModel, ConfigDict, PrivateAttr, Field, create_model
from abc import ABC, abstractmethod
from typing import Set, Any, ClassVar, get_origin, get_args, Union, Optional, Literal, get_type_hints, List
from ..utils import get_dict_args
from dataclasses import asdict
import copy
import datetime

QUERY_FIELD_TYPES = {
    'StringQueryField',
    'NumericQueryField',
    'BoolQueryField',
    'DateQueryField',
    'BytesQueryField',
    'JoinStringCondition',
    'JoinNumericCondition',
    'JoinBooleanCondition',
    'JoinDateCondition',
    'JoinBytesCondition',  
}

def convert_datetime_date_to_str(annotation):
    """Convert datetime/date or their unions with str to just str."""
    if annotation in (datetime.datetime, datetime.date):
        return str
    origin_inner = get_origin(annotation)
    args_inner = get_args(annotation)
    if origin_inner is Union:
        set_args = set(args_inner)
        if str in set_args and (datetime.datetime in set_args or datetime.date in set_args):
            return str
    return annotation

def remove_query_field_types(annotation):
    """
    Remove os tipos de QueryField (como StringQueryField) de uma Union ou substitui diretamente
    """
    origin = get_origin(annotation)
    args = get_args(annotation)

    def is_query_field(arg):
        return getattr(arg, '__name__', '') in QUERY_FIELD_TYPES

    if origin is Union:
        new_args = tuple(arg for arg in args if not is_query_field(arg))
        if len(new_args) == 1:
            return new_args[0]
        return Union[new_args]
    elif is_query_field(annotation):
        return str  # fallback para str caso algum passe isolado
    return annotation

def is_optional(annotation):
    """Check if an annotation is Optional[...] or Union[..., None]."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    return origin is Union and type(None) in args

def remove_optional(annotation):
    """Remove NoneType from Union[...]"""
    args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
    if len(args) == 1:
        return args[0]
    return Union[args]

def make_optional(annotation):
    """Make an annotation optional if not already."""
    if is_optional(annotation):
        return annotation
    return Optional[annotation]

class SensitiveFields(object):

    _sensitive_fields : Set[str] = set()

    @classmethod
    def set(cls, new_sensitive_filds : Set[str]):
        cls._sensitive_fields = new_sensitive_filds

    @classmethod
    def get(cls):
        return cls._sensitive_fields
    

class TableBaseModel(BaseModel, ABC): 
    class Config(ConfigDict):
        from_attributes = True

    TABLE_NAME: ClassVar[str] 

    TABLE_ALIAS: ClassVar[str] 

    DESCRIPTION : ClassVar[str] 
    
    IDENTITIES : ClassVar[Set[str]]

    PRIMARY_KEYs : ClassVar[Set[str]]

    OPTIONAL_FIELDS : ClassVar[Set[str]]

    MAX_LENGTH_FIELDS: ClassVar[dict[str, int]] = {}

    _explicit_fields:  Set[str] = PrivateAttr(default_factory=set)
    _pending_updates: dict[str, Any] = PrivateAttr(default_factory=dict)
    _initial_values: dict[str, Any] = PrivateAttr(default_factory=dict)
   

    def __init__(self, **data):
        sensitive = SensitiveFields.get()
        filtered_data = {k: v for k, v in data.items() if k not in sensitive}
        
        super().__init__(**filtered_data)
        self._explicit_fields = set(filtered_data.keys())
        self._initial_values = copy.deepcopy(self.model_dump())
    
    def _reset_defaults(self):
        for field_name, model_field in self.model_fields.items():
            if field_name not in self._explicit_fields:
                setattr(self, field_name, None)

    def reset_to_initial_values(self):
        for key, value in self._initial_values.items():
            setattr(self, key, copy.deepcopy(value))
        self.clear_updates()

    def equals(self, other: "TableBaseModel") -> bool:
        return self.model_dump() == other.model_dump()

    def clear_updates(self):
        self._pending_updates.clear()

    def has_updates(self) -> bool:
        for key, new_value in self._pending_updates.items():
            if key in self.model_fields:
                current_value = getattr(self, key, None)

            if isinstance(current_value, BaseModel) and isinstance(new_value, BaseModel):
                if current_value.model_dump() != new_value.model_dump():
                    return True
                
            elif hasattr(current_value, "__dataclass_fields__") and hasattr(new_value, "__dataclass_fields__"):
                if asdict(current_value) != asdict(new_value):
                    return True

            elif hasattr(current_value, "__dict__") and hasattr(new_value, "__dict__"):
                if vars(current_value) != vars(new_value):
                    return True

            elif new_value != current_value:
                return True
        return False

    @staticmethod
    def queue_update(self : 'TableBaseModel', **fields):
        fields = get_dict_args(fields)
        for key, value in fields.items():
            if value != None and key in self.model_fields:
                self._pending_updates[key] = value

    def apply_updates(self):
        for key, value in self._pending_updates.items():
            if key in self.model_fields:
                setattr(self, key, value)
        self.clear_updates()

    def alter_model_class(self, remove_fields: tuple[str] = (), mode: Literal['all_optional', 'all_required', 'original'] = 'all_optional', query_field = False):
        fields = {}
        
        for field_name, field in self.model_fields.items():
            if field_name in remove_fields:
                continue

            ann = convert_datetime_date_to_str(field.annotation)
            if not query_field:
                ann = remove_query_field_types(ann)

            max_length = None
            if mode in ('all_required', 'original'):
                max_length = self.MAX_LENGTH_FIELDS.get(field_name)
                if isinstance(max_length, int) and max_length < 1:
                    max_length = None

            default = field.default

            if mode == 'all_optional':
                ann = make_optional(ann)
                default = None

            elif mode == 'all_required':
                if is_optional(ann):
                    ann = remove_optional(ann)
                default = ...

            elif mode == 'original':
                if field_name in self.OPTIONAL_FIELDS:
                    ann = make_optional(ann)
                    default = None
                else:
                    if is_optional(ann):
                        ann = remove_optional(ann)
                    default = ...

            fields[field_name] = (ann, Field(default=default, description=field.description, max_length=max_length))

        new_model_class = create_model(
            self.__name__,
            __config__=ConfigDict(extra='forbid'),
            **fields
        )
        return new_model_class
    
    @classmethod
    def get_field_type_names(cls) -> dict[str, set[str]]:
        result = {}
        type_hints = get_type_hints(cls, include_extras=True)

        for field_name, hint in type_hints.items():
            if field_name.startswith('_') or get_origin(hint) is ClassVar:
                continue

            args = get_args(hint)
            if not args:
                args = (hint,)

            types = {
                t.__name__ if hasattr(t, '__name__') else t._name if hasattr(t, '_name') else str(t)
                for t in args
                if t is not type(None)  
            }

            result[field_name] = types

        return result
    
class SearchTable(BaseModel):
    model: TableBaseModel
    include: Optional[List[str]] = Field(default_factory=list)

    def model_dump_log(self):
        model = self.model.model_dump(exclude_none=True, mode="json")
        return {'model': model, 'include': self.include}

class JoinSearchTable(SearchTable):
    join_type: Literal["INNER", "LEFT", "RIGHT", "FULL"] = "LEFT"

    def model_dump_log(self,):
        model = self.model.model_dump(exclude_none=True, mode="json")
        return {'table': self.model.__class__.__name__, 'model': model, 'include': self.include, 'type': self.join_type}
    
class BaseUpdate(ABC):

    def __init__(self, executor , model):
        self._set_data = model
        self._executor = executor

    @property
    def set_data(self):
        return self._set_data

    @property
    def executor(self):
        return self._executor

    @abstractmethod
    def where(self, *args):
        pass



