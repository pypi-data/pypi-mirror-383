from __future__ import annotations

from uuid import UUID

from pydantic import field_validator, Field
from typing_extensions import Annotated

from ..common.default_base_model import DefaultBaseModel


class AssignmentFunction(DefaultBaseModel):
    pass


class AssignmentConcat(AssignmentFunction):
    concat: list[
        str
        | AssignmentConcat
        | AssignmentJoin
        | AssignmentToken
        | AssignmentUUID5
        | AssignmentGetAttribute
        | AssignmentGetInput
        | AssignmentGetProperty
    ] = Field(min_length=2)


class AssignmentJoin(AssignmentFunction):
    join: list[
        str
        | Annotated[
            list[
                str
                | AssignmentConcat
                | AssignmentJoin
                | AssignmentToken
                | AssignmentUUID5
                | AssignmentGetAttribute
                | AssignmentGetInput
                | AssignmentGetProperty
            ],
            Field(min_length=2),
        ]
    ] = Field(min_length=2, max_length=2)

    @field_validator("join")
    @classmethod
    def check_join(cls, v):
        _list, _delimiter = v
        if not isinstance(_delimiter, str) or isinstance(_list, str):
            raise ValueError('Incorrect "join" implementation')
        return v


class AssignmentToken(AssignmentFunction):
    token: list[
        str
        | int
        | AssignmentConcat
        | AssignmentJoin
        | AssignmentToken
        | AssignmentUUID5
        | AssignmentGetAttribute
        | AssignmentGetInput
        | AssignmentGetProperty
    ] = Field(min_length=3, max_length=3)

    @field_validator("token")
    @classmethod
    def check_token(cls, v):
        if (
            isinstance(v[0], int)
            or not isinstance(v[1], str)
            or not isinstance(v[2], int)
        ):
            raise Exception("Incorrect implementation")
        return v


class AssignmentUUID5(AssignmentFunction):
    uuid5: list[
        str
        | AssignmentConcat
        | AssignmentJoin
        | AssignmentToken
        | AssignmentUUID5
        | AssignmentGetAttribute
        | AssignmentGetInput
        | AssignmentGetProperty
    ] = Field(max_length=2, min_length=2)

    @field_validator("uuid5")
    @classmethod
    def check_uuid5(cls, v):
        _uuid, _name = v
        if not (isinstance(_uuid, str) and isinstance(_name, str)):
            raise ValueError('Incorrect "uuid5" implementation')
        UUID(_uuid)


class AssignmentGetAttribute(AssignmentFunction):
    get_attribute: list[str] = Field(min_length=2, max_length=4)


class AssignmentGetInput(AssignmentFunction):
    get_input: str

    @field_validator("get_input")
    @classmethod
    def check_get_input(cls, v):
        if not isinstance(v, str):
            raise ValueError('Incorrect "get_input" implementation')
        return v


class AssignmentGetProperty(AssignmentFunction):
    get_property: list[str] = Field(min_length=2, max_length=4)


AssignmentConcat.model_rebuild()
AssignmentJoin.model_rebuild()
AssignmentToken.model_rebuild()
AssignmentGetAttribute.model_rebuild()
AssignmentGetInput.model_rebuild()
AssignmentGetProperty.model_rebuild()

AttributePropertyAssignment = (
    AssignmentConcat
    | AssignmentJoin
    | AssignmentToken
    | AssignmentUUID5
    | AssignmentGetAttribute
    | AssignmentGetInput
    | AssignmentGetProperty
)


def property_model(properties: dict[str, any]):
    if isinstance(properties, list):
        return [property_model(v) for v in properties]
    elif not isinstance(properties, dict):
        return properties

    if len(properties) == 1:
        key = list(properties.keys())[0]
        properties = {key: property_model(properties[key])}
        if key == "concat":
            return AssignmentConcat(**properties)
        if key == "join":
            return AssignmentJoin(**properties)
        if key == "token":
            return AssignmentToken(**properties)
        if key == "uuid5":
            return AssignmentUUID5(**properties)
        if key == "get_attribute":
            return AssignmentGetAttribute(**properties)
        if key == "get_input":
            return AssignmentGetInput(**properties)
        if key == "get_property_":
            return AssignmentGetProperty(**properties)
        return properties

    return {k: property_model(v) for k, v in properties.items()}
