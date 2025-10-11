from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class RepositoryDefinition(DefaultBaseModel):
    description: str | None = None
    url: str
