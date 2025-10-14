from __future__ import annotations

import os
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", "13.0")


def gather_include_dirs() -> list[str]:
    import torch
    import nanobind

    includes = []
    try:
        from torch.utils.cpp_extension import include_paths
    except ImportError:
        torch_dir = Path(torch.__file__).resolve().parent
        includes.append(str(torch_dir / "include"))
        includes.append(str(torch_dir / "include" / "torch" / "csrc" / "api" / "include"))
    else:
        includes.extend(include_paths())

    nb_root = Path(nanobind.__file__).resolve().parent
    includes.append(str(nb_root / "include"))
    includes.append(str(nb_root / "ext" / "robin_map" / "include"))
    return includes


def gather_extra_sources() -> list[str]:
    import nanobind

    nb_root = Path(nanobind.__file__).resolve().parent
    nb_combined = nb_root / "src" / "nb_combined.cpp"
    if nb_combined.exists():
        return [str(nb_combined)]
    return []


class TorchBuildExt(build_ext):
    def build_extensions(self) -> None:
        include_dirs = gather_include_dirs()
        extra_sources = gather_extra_sources()
        compiler = self.compiler
        if ".mm" not in compiler.src_extensions:
            compiler.src_extensions.append(".mm")
        compiler.language_map[".mm"] = "objc++"
        for ext in self.extensions:
            ext.include_dirs.extend(include_dirs)
            ext.sources.extend(extra_sources)
        super().build_extensions()


def make_extension() -> Extension:
    return Extension(
        "chamfer_ext",
        sources=[
            "chamfer/src/metal_bridge.mm",
            "chamfer/src/kd_tree.cpp",
        ],
        extra_compile_args=["-std=c++20", "-fobjc-arc", "-fvisibility=hidden"],
        extra_link_args=["-framework", "Metal", "-framework", "Foundation"],
        language="c++",
    )


IS_BUILDING_SDIST = "sdist" in sys.argv
extensions = [] if IS_BUILDING_SDIST else [make_extension()]

setup(
    cmdclass={"build_ext": TorchBuildExt},
    ext_modules=extensions,
)
