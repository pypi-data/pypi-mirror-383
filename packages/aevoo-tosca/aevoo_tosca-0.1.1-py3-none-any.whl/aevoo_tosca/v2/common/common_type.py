from typing import Optional, Dict

from aevoo_tosca.v2.common.default_base_model import DefaultBaseModel


class CommonType(DefaultBaseModel):
    derived_from: Optional[str]
    version: Optional[str]
    metadata: Optional[Dict[str, str]]
    description: Optional[str]
