from pydantic import ConfigDict, BaseModel


class DefaultBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
