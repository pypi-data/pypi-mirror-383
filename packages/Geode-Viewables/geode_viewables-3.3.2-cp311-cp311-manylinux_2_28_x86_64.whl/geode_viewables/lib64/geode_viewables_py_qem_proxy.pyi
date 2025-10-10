"""
Geode-Viewables Python binding for qem_proxy
"""
from __future__ import annotations
import opengeode.lib64.opengeode_py_mesh
__all__: list[str] = ['ViewablesQEMProxyLibrary', 'simplify']
class ViewablesQEMProxyLibrary:
    @staticmethod
    def initialize() -> None:
        ...
def simplify(arg0: opengeode.lib64.opengeode_py_mesh.TriangulatedSurface3D) -> bool:
    ...
