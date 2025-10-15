# Copyright (C) 2017-2019 Matthieu Ancellin
# See LICENSE file at <https://github.com/mancellin/capytaine>


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'capytaine.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-capytaine-2.3.1')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-capytaine-2.3.1')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

from .__about__ import (
    __title__, __description__, __version__, __author__, __uri__, __license__
)

from capytaine.meshes.geometry import Axis, Plane, xOz_Plane, yOz_Plane, xOy_Plane
from capytaine.meshes.meshes import Mesh
from capytaine.meshes.collections import CollectionOfMeshes
from capytaine.meshes.symmetric import ReflectionSymmetricMesh, TranslationalSymmetricMesh, AxialSymmetricMesh
from capytaine.meshes.predefined.cylinders import mesh_disk, mesh_horizontal_cylinder, mesh_vertical_cylinder
from capytaine.meshes.predefined.spheres import mesh_sphere
from capytaine.meshes.predefined.rectangles import mesh_rectangle, mesh_parallelepiped

from capytaine.bodies.bodies import FloatingBody
from capytaine.bodies.dofs import rigid_body_dofs

from capytaine.bodies.predefined.spheres import Sphere
from capytaine.bodies.predefined.cylinders import VerticalCylinder, HorizontalCylinder, Disk
from capytaine.bodies.predefined.rectangles import Rectangle, RectangularParallelepiped, OpenRectangularParallelepiped

from capytaine.bem.problems_and_results import RadiationProblem, DiffractionProblem
from capytaine.bem.solver import BEMSolver
from capytaine.bem.engines import BasicMatrixEngine, HierarchicalToeplitzMatrixEngine, HierarchicalPrecondMatrixEngine
from capytaine.green_functions.delhommeau import Delhommeau, XieDelhommeau
from capytaine.green_functions.hams import LiangWuNoblesseGF, FinGreen3D, HAMS_GF

from capytaine.post_pro.free_surfaces import FreeSurface

from capytaine.io.mesh_loaders import load_mesh
from capytaine.io.xarray import assemble_dataframe, assemble_dataset, assemble_matrices, export_dataset

from capytaine.ui.rich import set_logging

set_logging(level="WARNING")
