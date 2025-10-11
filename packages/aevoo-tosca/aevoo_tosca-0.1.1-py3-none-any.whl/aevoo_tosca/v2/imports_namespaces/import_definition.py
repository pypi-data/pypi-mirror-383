from __future__ import annotations

from pydantic import model_validator

from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class ImportDefinition(DefaultBaseModel):
    url: str | None = None
    profile: str | None = None
    repository: str | None = None
    namespace: str | None = None

    @model_validator(mode="after")
    def check(self):
        if self.profile is not None:
            raise Exception("Profile not implemented")
        return self
