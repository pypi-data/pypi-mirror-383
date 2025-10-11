from __future__ import annotations

import re
from copy import copy
from pydantic import Field, model_validator
from typing import Any

from .common.default_base_model import DefaultBaseModel
from .nodes_relationships.node import NodeTemplate
from .nodes_relationships.relationship import RelationshipTemplate
from .occurrence import nid_re, nid_valid
from .properties_attributes_parameters.data_type import tosca_from_py_type
from .properties_attributes_parameters.parameter import (
    ParameterDefinition,
    InputDefinition,
    OutputDefinition,
)
from .substitution.substitution_mapping import SubstitutionMapping
from ..constants import CHAR_ALLOWED as CA

try:
    from aevoo_lib.exceptions import IncorrectImplementation
except ModuleNotFoundError as e:
    pass

CHAR_ALLOWED = CA - {"-"}
component_name_valid = r"[A-Za-z-._\d]+"
component_name_regex = re.compile(component_name_valid)

instance_name_valid = r"[A-Za-z][A-Za-z-_\d]+"
instance_name_regex = re.compile(instance_name_valid)


class TopologyTemplate(DefaultBaseModel):
    description: str | None = None
    inputs: dict[str, InputDefinition] = Field(default_factory=dict)
    node_templates: dict[str, NodeTemplate]
    relationship_templates: dict[str, RelationshipTemplate] = Field(
        default_factory=dict
    )
    groups: dict[str, Any] | None = None
    policies: list[Any] | None = None
    outputs: dict[str, OutputDefinition] = Field(default_factory=dict)
    substitution_mappings: SubstitutionMapping | None = None

    # workflows: Optional[dict[str, ImperativeWorkflowDefinition]]

    @model_validator(mode="after")
    # !!! never name this method "validate" !!!
    def check(self):
        for k, i in self.inputs.items():
            if i.required is None:
                i.required = i.default is None and not k.startswith("__secret__")

        if self.node_templates is None:
            raise ValueError("node_templates mandatory")
        node_templates: set[str] = set(self.node_templates.keys())
        relationship_templates: set[str] = set(self.relationship_templates.keys())
        _intersection = node_templates.intersection(relationship_templates)
        if _intersection:
            raise ValueError(f"Duplicate names : {_intersection}")
        _chars = set()
        for k in relationship_templates.union(node_templates):
            _chars = _chars.union(set(k))
        if not set(_chars) <= CHAR_ALLOWED:
            raise ValueError(f"Characters allowed in keys : CHAR_ALLOWED")

        _errors = []
        for n in node_templates.union(relationship_templates):
            if not component_name_regex.fullmatch(n):
                _errors.append(n)
            if nid_re.match(n):
                _errors.append(n)

        if _errors:
            raise ValueError(
                f"Invalid name : {_errors} (regex : {component_name_valid}, re forbidden : {nid_valid})"
            )

        sm: SubstitutionMapping = self.substitution_mappings
        if sm:
            sf = sm.substitution_filter
            if sf and sf.properties and self.inputs:
                sf_p = {list(p.keys())[0] for p in sf.properties}
                _intersection = sf_p.intersection({i for i in self.inputs})
                if _intersection:
                    raise ValueError(
                        f"Collision between inputs and substitution_filter properties : {_intersection}"
                    )
        return self

    def input_default(self, name):
        _input: ParameterDefinition = self.inputs.get(name)
        if _input is None:
            raise IncorrectImplementation(f"No input -{name}- in topology")
        return _input.default

    def input_validator(
        self, replace: bool, strict: bool, inputs: dict, secrets: set[str]
    ) -> tuple[bool, list[str]]:  # TODO : type
        # sm_filter_inputs = self.substitution_filter_inputs()
        # inputs_copy = {k: copy(v) for k, v in inputs.items() if k not in sm_filter_inputs}
        ask = (
            inputs and set(k for k, v in inputs.items() if v not in (None, "")) or set()
        )

        _extra = ask - set(self.inputs.keys())
        _missing = set()
        _none_value = set()
        _read_only = set()
        _invalid_value = set()
        _invalid_type_value = set()

        need = {k for k, v in self.inputs.items() if v.required is not False}
        # TODO s/strict/replace/ ?
        if strict:
            for missing in need - ask:
                default = self.input_default(missing)
                if missing not in secrets and default in (None, ""):
                    _missing.add(missing)
        inputs_copy = copy(inputs)
        for key, value in inputs_copy.items():
            _input = self.inputs.get(key)
            if _input is None:
                continue
            # TODO do
            if (key == "name" or _input.read_only) and replace:
                _read_only.add(key)
            if key == "name" and not instance_name_regex.fullmatch(value):
                _invalid_value.add(key)
            type_ = _input.type
            if type_ == "password":
                type_ = "string"

            if type_ == "integer":
                try:
                    inputs[key] = int(value)
                except ValueError:
                    _invalid_type_value.add(key)
            # TODO: entry_schema
            else:
                if type_ != tosca_from_py_type(type(value), True, _name=key)[0]:
                    _result = tosca_from_py_type(type(value), True, _name=key)[0]
                    _invalid_type_value.add(
                        f"{key} (get: {_result}, expected: {type_})"
                    )

        errors = []
        if len(_extra) > 0:
            errors.append(f"Extra: {_extra}")
        if len(_missing) > 0:
            errors.append(f"Missing: {_missing}")
        if len(_none_value) > 0:
            errors.append(f"None value: {_none_value}")
        if len(_read_only) > 0:
            errors.append(f"Read only: {_read_only}")
        if len(_invalid_value) > 0:
            errors.append(f"Invalid value: {_invalid_value}")
        if len(_invalid_type_value) > 0:
            errors.append(f"Invalid type: {_invalid_type_value}")
        if len(errors) > 0:
            return False, errors
        return True, []

    # def substitution_filter_inputs(self):
    #     sm = self.substitution_mappings
    #     if sm and sm.substitution_filter and sm.substitution_filter.properties:
    #         return [list(p.keys())[0] for p in sm.substitution_filter.properties]
