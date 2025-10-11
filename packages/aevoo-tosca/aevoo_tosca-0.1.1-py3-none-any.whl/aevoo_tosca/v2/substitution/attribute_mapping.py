from pydantic import Field

from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class AttributeMapping(DefaultBaseModel):
    mapping: list[str] | None = Field(min_length=1, max_length=1)
