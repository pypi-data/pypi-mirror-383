from zipfile import ZipFile

import io
import logging
import re
import yaml
from dataclasses import dataclass, field
from uuid import uuid4

from aevoo_tosca.csar.dependency_injector import CSARDependencyInjector

logger = logging.getLogger("aevoo.console")


# from aevoo_lib.utils.filetype import is_zip


# TODO remove (tests)
def is_zip(buf):
    return (
        len(buf) > 3
        and buf[0] == 0x50
        and buf[1] == 0x4B
        and (buf[2] == 0x3 or buf[2] == 0x5 or buf[2] == 0x7)
        and (buf[3] == 0x4 or buf[3] == 0x6 or buf[3] == 0x8)
    )


yaml_ext_re = re.compile(r".+\.ya*ml$")

TOSCA_META = "TOSCA-Metadata/TOSCA.meta"


@dataclass(eq=False, repr=False, slots=True, weakref_slot=True)
class TOSCAmeta:
    version: str
    cid: str = None
    ephemeral: bool = False
    Entry_Definitions: str = None
    Created_By: str = None
    Other_Definitions: str = None


@dataclass(eq=False, repr=False, slots=True, weakref_slot=True)
class CSAR:
    data: bytes | None = None
    entry_definitions: bytes = None
    meta: TOSCAmeta = None
    templates: list[str] = field(default_factory=list)
    _dirs: set[str] = None
    _python_interfaces: CSARDependencyInjector = None
    _root: str = None
    _zf: ZipFile = None

    # def is_csar(cls, content: bytes):
    #     if content is None:
    #         return False
    #     try:
    #         with urllib.request.urlopen(content) as response:
    #             csar_raw = response.read()
    #             return is_zip(csar_raw)
    #     except urllib.error.URLError as e:
    #         return False
    #     except UnicodeDecodeError as e:
    #         return False

    def file_read(self, path: str, decode: bool = True) -> str | bytes:
        content = self._read(self._path(path))
        if decode is True:
            content = content.decode()
        return content

    def file_exist(self, path: str) -> bool:
        if path is None:
            return False
        _path = self._path(path)
        return len([f for f in self._zf.filelist if f.filename == _path]) == 1

    def python_module_get(self, node: str):
        if self._python_interfaces is None:
            _uuid = "i_" + str(uuid4()).replace("-", "_")
            logger.debug(f"Import module {node} => {_uuid}")
            self._python_interfaces = CSARDependencyInjector(
                module_name=_uuid, node_name=node, csar=self
            )
        try:
            return __import__(self._python_interfaces.module_name), None
        except ModuleNotFoundError as e:
            _f_list = "\n".join([f.filename for f in self._zf.filelist])
            _msg = f"Error loading interface '{node}' in CSAR '{self}' : \n {_f_list}"
            logger.exception(e.msg)
            return None, _msg

    def _read(self, path: str) -> bytes:
        return self._zf.read(path)

    def _path(self, path: str):
        if self._root is None or path.startswith(self._root):
            return path
        return f"{self._root}/{path}"

    def _zip_inv(self):
        self._zf = ZipFile(io.BytesIO(self.data))
        _tosca_meta_exist = False
        _roots = set()
        _dirs = set()
        for data in self._zf.filelist:
            _fullname = data.filename
            _path = _fullname.split("/")
            if len(_path) > 1:
                _roots.add(_path[0])
                if _path[-1] == "":
                    _dirs.add(_fullname)
            if _fullname == TOSCA_META:
                _tosca_meta_exist = True
            elif yaml_ext_re.match(_fullname):
                self.templates.append(_fullname)
        if len(_roots) == 1:
            self._root = _roots.pop()
        self._dirs = _dirs
        return _tosca_meta_exist

    def __post_init__(self):
        if not is_zip(self.data):
            raise Exception("Only zip format supported")

        _tosca_meta_exist = self._zip_inv()

        if len(self.templates) == 0:
            raise Exception("Templates not found")

        _version = None
        if _tosca_meta_exist:
            _meta: dict = yaml.safe_load(self._read(TOSCA_META))
            _ephemeral = _meta.get("ephemeral") or False
            _version = _meta.get("CSAR-Version")
            self.meta = TOSCAmeta(
                ephemeral=_ephemeral,
                version=_version,
                Created_By=_meta.get("Created-By"),
                Entry_Definitions=_meta.get("Entry-Definitions"),
                Other_Definitions=_meta.get("Other-Definitions"),
            )
            _path = self.meta.Entry_Definitions
            if _path is None:
                raise Exception("Invalid TOSCA meta (Entry-Definitions missing )")
        else:
            if len(self.templates) != 1:
                raise Exception(
                    "Entry-Definitions not defined (more than 1 template exist)"
                )
            _path = self.templates[0]

        self.entry_definitions = self._read(_path)
        _template = yaml.safe_load(self.entry_definitions)
        _meta = _template.get("metadata")
        if _meta is None:
            raise Exception("Metadata missing")
        _author = _meta.get("template_author")
        _cid = _meta.get("template_name")
        _ephemeral = _meta.get("ephemeral") or False
        _version = _meta.get("template_version")

        if _tosca_meta_exist:
            if (
                None not in (self.meta.version, _version)
                and self.meta.version != _version
            ):
                raise Exception("Versions in metadata and template mismatch")
            if self.meta.version is None:
                self.meta.version = _version
            self.meta.cid = _cid
        else:
            self.meta = TOSCAmeta(
                cid=_cid, ephemeral=_ephemeral, version=_version, Created_By=_author
            )

        if _version is None:
            raise Exception("Version missing")

    def __repr__(self):
        return f"{self.meta.cid}@{self.meta.version}/{self._root}"
