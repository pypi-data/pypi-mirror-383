from pydantic import Field, ConfigDict

from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class CapabilityMapping(DefaultBaseModel):
    model_config = ConfigDict(extra="forbid")

    mapping: list[str] | None = Field(min_length=2, max_length=2)
    # value: Optional # Deprecated
