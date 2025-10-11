from pydantic import field_validator

from ...common.default_base_model import DefaultBaseModel
from ...properties_attributes_parameters.constraint_clause import ConstraintClause


class PropertiesFilter(DefaultBaseModel):
    properties: list[dict[str, list[ConstraintClause] | ConstraintClause]] | None = None


class NodeFilter(DefaultBaseModel):
    # dict[str, list[ConstraintClause] | ConstraintClause]
    properties: list[dict[str, ConstraintClause]] | None = None
    capabilities: list[dict[str, PropertiesFilter]] | None = None

    # @root_validator
    # # !!! never name this method "validate" !!!
    # def check(cls, values):
    #     properties = values.get('properties')
    #     if properties is not None:
    #         p: dict[str, ConstraintClause]
    #         for p in properties:
    #             if len(p.keys()) != 1:
    #                 raise ValueError(f'Incorrect property : {p}')
    #     return values

    @field_validator("properties")
    def validate_properties(cls, v):
        if v is not None:
            p: dict[str, ConstraintClause]
            for p in v:
                if len(p.keys()) != 1:
                    raise ValueError(f"Incorrect property : {p}")
        return v
