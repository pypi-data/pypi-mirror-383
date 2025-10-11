#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from pathlib import Path

from setuptools import Extension, find_namespace_packages, setup


def _get_c_extensions() -> list[Extension]:
    """扫描 src/ 下所有 .c 文件，返回 Extension 列表（使用相对路径）"""
    setup_py_dir = Path(__file__).parent.resolve()  # setup.py 所在目录（项目根）
    src_dir = setup_py_dir / "src"

    ext_modules = []

    for c_file in src_dir.rglob("*.c"):
        # 确保 c_file 在 src_dir 下
        try:
            rel_to_src = c_file.relative_to(src_dir)  # e.g., shudaodao_core/app/base_app.c
        except ValueError:
            continue  # 不在 src 下，跳过

        # 模块名：shudaodao_core.app.base_app
        module_name = str(rel_to_src.with_suffix("")).replace(os.sep, ".")

        # 源文件路径：相对于 setup.py 的路径 → "src/shudaodao_core/app/base_app.c"
        source_path = str(c_file.relative_to(setup_py_dir))

        # 安全检查：禁止绝对路径
        if os.path.isabs(source_path):
            raise RuntimeError(f"Absolute path detected: {source_path}")

        compile_args = [] if os.name == 'nt' else [
            "-Wno-unreachable-code-fallthrough",
            "-Wno-unused-function",
            "-Wno-unreachable-code",
        ]

        ext_modules.append(
            Extension(
                name=module_name,
                sources=[source_path],  # ← 必须是 "src/xxx.c"，不是绝对路径！
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
