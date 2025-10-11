#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from pathlib import Path
from setuptools import Extension, find_namespace_packages, setup


def _get_c_extensions() -> list[Extension]:
    """自动发现所有 .c 文件并创建 Extension（不经过 Cython）"""
    ext_modules = []
    src_path = Path("src").resolve()

    # 遍历 src 下所有 .c 文件
    for c_file in src_path.rglob("*.c"):
        # 计算模块名：src/shudaodao/core.c → shudaodao.core
        try:
            rel_path = c_file.relative_to(src_path)
            module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")
        except ValueError:
            continue  # 不在 src 下，跳过

        compile_args = [] if os.name == 'nt' else [
            "-Wno-unreachable-code-fallthrough",
            "-Wno-unused-function",
            "-Wno-unreachable-code",
        ]

        ext_modules.append(
            Extension(
                name=module_name,
                sources=[str(c_file)],
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