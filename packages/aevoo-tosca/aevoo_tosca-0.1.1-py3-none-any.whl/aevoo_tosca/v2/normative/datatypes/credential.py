from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class Credential(DefaultBaseModel):
    protocol: str | None
    token_type: str
    token: str
    keys: dict[str, str] | None
    user: str | None
