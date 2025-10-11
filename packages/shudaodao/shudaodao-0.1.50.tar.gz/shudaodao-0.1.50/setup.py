#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from pathlib import Path

from setuptools import Extension, find_namespace_packages, setup


def _get_c_extensions() -> list[Extension]:
    """自动发现所有 .c 文件并创建 Extension，使用相对路径"""
    ext_modules = []
    setup_py_dir = Path(__file__).parent  # setup.py 所在目录
    src_dir = setup_py_dir / "src"

    for c_file in src_dir.rglob("*.c"):
        # 计算相对于 setup.py 的路径（例如 "src/shudaodao_core/app/base_app.c"）
        relative_source = c_file.relative_to(setup_py_dir)
        # 模块名：src/shudaodao_core/app/base_app.c → shudaodao_core.app.base_app
        module_name = str(relative_source.with_suffix("")).replace(os.sep, ".")

        compile_args = [] if os.name == 'nt' else [
            "-Wno-unreachable-code-fallthrough",
            "-Wno-unused-function",
            "-Wno-unreachable-code",
        ]

        ext_modules.append(
            Extension(
                name=module_name,
                sources=[str(relative_source)],  # ← 关键：相对路径！
                extra_compile_args=compile_args,
            )
        )
    return ext_modules


setup(
    name="shudaodao",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["*.pyi"],  # 包含所有包中的 .pyi 文件
    },
    ext_modules=_get_c_extensions(),  # ← 直接传 Extension，不 cythonize
    zip_safe=False,
)
