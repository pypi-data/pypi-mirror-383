from __future__ import annotations

import sys

import importlib.abc
from importlib.machinery import ModuleSpec
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aevoo_tosca.csar.context import CSAR


class ZipDIFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if self._loader.provides(fullname):
            return ModuleSpec(fullname, self._loader)

    def __init__(self, loader):
        self._loader = loader


class ZipDILoader(importlib.abc.Loader):
    def provides(self, fullname: str) -> bool:
        return fullname.split(".")[0] == self.module_name

    def create_module(self, spec: ModuleSpec):
        _mod = self._modules.get(spec.name)
        if _mod is not None:
            return _mod
        # return types.ModuleType(spec.name)
        pass

    def exec_module(self, module):
        _name = module.__name__
        _mod = self._modules.get(_name)
        if _mod is not None:
            return

        self._modules[_name] = module
        _path = f"interfaces/{self.node_name}"
        if _name != self.module_name:
            _path += _name.replace(self.module_name, "").replace(".", "/")
            raise NotImplementedError("Only one file for now")
        compiled = self.get_code(_path)
        exec(compiled, module.__dict__)

    def get_code(self, path: str):
        if not self._csar.file_exist(path):
            path += "/__init__.py"
            if not self._csar.file_exist(path):
                raise ImportError(f"Path {path} not found ")
        return compile(
            self._csar.file_read(path, decode=False),
            path,
            "exec",
            dont_inherit=True,
        )

    def __init__(self, module_name: str, node_name: str, csar: CSAR):
        self._csar = csar
        self._modules = {}
        self.module_name = module_name
        self.node_name = node_name


class CSARDependencyInjector:
    def __init__(self, module_name: str, node_name: str, csar: CSAR):
        self.module_name = module_name
        self._loader = ZipDILoader(module_name, node_name, csar)
        sys.meta_path.append(ZipDIFinder(self._loader))
