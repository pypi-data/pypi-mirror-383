from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aevoo_lib.workspace.mapping.ws.instance import Nodes

nid_valid = r".+-\d+$"
nid_re = re.compile(nid_valid)


def occurrences_get(parent: Nodes, cid: str = None, return_cid: bool = False):
    cid = topo_cid(cid)
    _nodes = {
        n.num: n
        for n in parent.components.values()
        if n.cid == cid or n.cid == nid(cid, n.num)
    }
    if return_cid is True:
        return {n.cid for n in _nodes.values()}
    return _nodes


def nid(cid: str, num: int, _initial_: bool = True):
    if num == 1 or _initial_:
        return f"{cid}-{format(num, '02d')}"
    else:
        return cid


def occurrence(cid: str):
    try:
        return int(cid.split("-")[-1]) if nid_re.match(cid) is not None else 1
    except ValueError as e:
        return 1


def topo_cid(cid: str):
    return "-".join(cid.split("-")[:-1]) if nid_re.match(cid) is not None else cid
