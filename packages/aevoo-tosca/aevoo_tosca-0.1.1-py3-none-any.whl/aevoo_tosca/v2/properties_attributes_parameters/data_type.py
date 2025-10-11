from __future__ import annotations

from typing import Optional, Dict, get_args, Union, get_origin

from .constraint_clause import ConstraintClause
from .property import PropertyDefinition
from .schema import SchemaDefinition
from ..common import CommonType

try:
    from aevoo_lib.exceptions import IncorrectImplementation, NotImplementedExc
except ModuleNotFoundError as e:
    pass


class DataType(CommonType):
    constraints: Optional[list[ConstraintClause]]
    properties: Optional[Dict[str, PropertyDefinition]]
    key_schema: Optional[SchemaDefinition]
    entry_schema: Optional[SchemaDefinition]


supportedInputTypes = {"string", "integer", "boolean", "password"}


def py_from_tosca_type(tosca_type: str):
    tosca_type = tosca_type.lower()
    # TODO : https://github.com/cython/cython/pull/4897
    # match tosca_type:
    #     case 'boolean':
    #         return bool
    #     case 'integer':
    #         return int
    #     case 'string':
    #         return str
    #     case 'list':
    #         return list
    #     case 'map':
    #         return dict
    if tosca_type == "boolean":
        return bool
    elif tosca_type == "integer":
        return int
    elif tosca_type == "string":
        return str
    elif tosca_type == "password":
        return str
    elif tosca_type == "list":
        return list
    elif tosca_type == "map":
        return dict


def tosca_from_py_type(
    var: str | type, ignore_sub_type: bool = False, _name: str = None
):
    if isinstance(var, str):
        # f = ForwardRef(var, is_argument=False, is_class=True)
        # var = f._evaluate(globals(), locals(), frozenset())
        var = eval(var)

    required = True
    if get_origin(var) is Union:
        _types = get_args(var)
        if type(None) not in _types or len(_types) != 2:
            raise IncorrectImplementation(f"Not supported type : {var}")
        required = False
        var = [i for i in _types if i is not type(None)][0]

    type_: str = var.__name__

    # TODO : https://github.com/cython/cython/pull/4897
    # match type_.lower():
    #     case 'bool':
    #         return 'boolean', None, required
    #     case 'int':
    #         return 'integer', None, required
    #     case 'str':
    #         return 'string', None, required
    #     case 'NoneType':
    #         return 'nil', None, required
    #     case 'list' | 'set':
    #         if ignoreSubType:
    #             return 'list', None, required
    #         _sub_types = get_args(var)
    #         if len(_sub_types) != 1:
    #             raise NotImplementedExc(f'Not supported type: {var}')
    #         _sub_type = toscaFromPyType(_sub_types[0])
    #         return 'list', _sub_type, required
    #     case 'dict':
    #         if ignoreSubType:
    #             return 'list', None, required
    #         k, v = get_args(var)
    #         return 'map', v.__name__, required
    #     case _:
    #         raise NotImplementedExc(f'Not supported type: {var}')

    type_ = type_.lower()
    if type_ == "bool":
        return "boolean", None, required
    elif type_ == "int":
        return "integer", None, required
    elif type_ == "str":
        return "string", None, required
    elif type_ == "NoneType":
        return "nil", None, required
    elif type_ in ("list", "set"):
        if ignore_sub_type:
            return "list", None, required
        _sub_types = get_args(var)
        if len(_sub_types) != 1:
            raise NotImplementedExc(f"Not supported type: {var}")
        _sub_type = tosca_from_py_type(_sub_types[0], _name=_name)
        return "list", _sub_type, required
    elif type_ == "dict":
        if ignore_sub_type:
            return "map", None, required
        k, _sub_type = get_args(var)
        if _sub_type != any:
            _sub_type = tosca_from_py_type(_sub_type.__name__, _name=_name)
        return "map", _sub_type, required
    else:
        raise NotImplementedExc(f"Not supported type: {var} {_name}")


def attr_def_from_py_type(var: str | type, _name: str = None):
    _type, _entry_schema, _required = tosca_from_py_type(var=var, _name=_name)
    _attrDef = {"required": _required, "type": _type}
    if _entry_schema is not None:
        _attrDef["entry_schema"] = _entry_schema_eval_recursive(_entry_schema)
    return _attrDef


def _entry_schema_eval_recursive(_entry_schema):
    _type, _entry_schema, _required = _entry_schema
    _attrDef = {"type": _type}
    if _entry_schema is not None:
        _attrDef["entry_schema"] = _entry_schema_eval_recursive(_entry_schema)
    return _attrDef
