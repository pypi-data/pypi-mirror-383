#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/24 14:22
# @Author  : 兵
# @email    : 1747193328@qq.com
"""NepTrainKit package configuration."""

from __future__ import annotations
import tempfile

import platform
import sys

import os
import subprocess
import shlex
import pybind11
from pybind11.setup_helpers import Pybind11Extension
from setuptools import  Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
import sysconfig
import shutil
from pathlib import Path

# 获取 pybind11 的 include 路径
pybind11_include = pybind11.get_include()



# 设定编译选项

extra_link_args = [ ]
extra_compile_args=[ ]
# 检查平台并设置相应的 OpenMP 编译标志

if sys.platform == "win32":
    # 对于 Windows 使用 MSVC 编译器时，需要使用 /openmp
    extra_compile_args.append('/openmp' )
    extra_compile_args.append('/O2' )
    extra_compile_args.append('/std:c++11' )



    extra_link_args.append('/openmp')
    extra_link_args.append('/O2' )
    extra_link_args.append('/std:c++11' )


elif sys.platform == "darwin":
    # 对于 macOS 和 Clang 使用 -fopenmp 编译标志
    # Clang 好像不支持openmp 先注释掉
    # extra_compile_args.append('-fopenmp' )
    #
    # extra_link_args.append('-fopenmp')
    # 通过环境变量获取目标架构，默认为 arm64（Apple Silicon）
    target_arch = os.environ.get('ARCHFLAGS', '-arch arm64').split()[-1]
    # extra_compile_args.append(f'-arch {target_arch}')
    # extra_link_args.append(f'-arch {target_arch}')

    extra_compile_args.append('-O3')
    extra_compile_args.append('-std=c++11')


    extra_link_args.append('-O3')
    extra_link_args.append('-std=c++11')

    omp_include = os.getenv("OMP_INCLUDE_PATH", "/opt/homebrew/opt/libomp/include")
    omp_lib = os.getenv("OMP_LIB_PATH", "/opt/homebrew/opt/libomp/lib")
    extra_compile_args.extend(["-Xpreprocessor", "-fopenmp", f"-I{omp_include}"])
    extra_link_args.extend(["-lomp", f"-L{omp_lib}"])

    pass

else:
    # 对于 Linux 和 GCC 使用 -fopenmp 编译标志

    extra_compile_args.append('-fopenmp' )
    extra_compile_args.append('-O3')
    extra_compile_args.append('-std=c++11')


    extra_link_args.append('-fopenmp')
    extra_link_args.append('-O3')
    extra_link_args.append('-std=c++11')


# 定义扩展模块
ext_modules = [
    Extension(
        "NepTrainKit.nep_cpu",  # 模块名
        ["src/nep_cpu/nep_cpu.cpp"],  # 源文件
        include_dirs=[
            pybind11_include,
            # "src/nep_cpu"
        ],
        extra_compile_args=extra_compile_args,  # 编译选项
        extra_link_args=extra_link_args,
        language="c++",  # 指定语言为 C++
    )
]

# ---- CUDA-based nep_gpu extension (built via custom NVCC flow) ----
gpu_sources_cu = [
    "src/nep_gpu/main_nep/dataset.cu",
    "src/nep_gpu/main_nep/nep.cu",
    "src/nep_gpu/main_nep/nep_charge.cu",
    "src/nep_gpu/main_nep/parameters.cu",
    "src/nep_gpu/main_nep/structure.cu",
    "src/nep_gpu/main_nep/tnep.cu",
    # utilities (exclude predict_main.cu, fitness.cu, snes.cu)
    "src/nep_gpu/utilities/cusolver_wrapper.cu",
    "src/nep_gpu/utilities/error.cu",
    "src/nep_gpu/utilities/main_common.cu",
    "src/nep_gpu/utilities/read_file.cu",
]

gpu_include_dirs = [
    pybind11_include,
    "src/nep_gpu",  # so that "utilities/..." resolves
    "src/nep_gpu/main_nep",
]
# ext_modules=[]
ext_modules.append(
    Extension(
        "NepTrainKit.nep_gpu",
        sources=["src/nep_gpu/nep_gpu.cu", "src/nep_gpu/nep_desc.cu", "src/nep_gpu/nep_parameters.cu"] + gpu_sources_cu,
        include_dirs=gpu_include_dirs,
        language="c++",
        extra_link_args=extra_link_args,
        extra_compile_args=extra_compile_args,
    )
)

# 自定义 build_ext 命令，确保兼容性
class BuildExt(build_ext):
    def build_extensions(self):
        # 设置编译器标准为 C++17
        ct = self.compiler.compiler_type
        opts = [ ]
        for ext in self.extensions:
            ext.extra_compile_args = opts + ext.extra_compile_args
        try:
            # 尝试构建扩展模块
            build_ext.build_extensions(self)
        except Exception as e:
            # 捕获编译错误并打印警告
            print(f"WARNING: Failed to build extension module: {e}")
            print("WARNING: Skipping nep_cpu module build. The package will be installed without it.")
            # 清空 ext_modules，跳过扩展模块的构建
            self.ext_modules = []



class BuildExtNVCC(build_ext):
    """NVCC-enabled build_ext.
    CPU extensions build normally; for NepTrainKit.nep_gpu, .cu files
    are compiled with nvcc and linked against CUDA libs.
    """
    def _cuda_paths(self):
        cuda_env = os.environ.get("CUDA_PATH") or os.environ.get("CUDA_HOME")
        if cuda_env:
            cuda_root = Path(cuda_env)
            cuda_bin = cuda_root / "bin"
            nvcc_path = cuda_bin / ("nvcc.exe" if os.name == 'nt' else "nvcc")
            include = cuda_root / "include"
            lib64 = (cuda_root / "lib" / "x64") if os.name == 'nt' else (cuda_root / "lib64")
            nvcc_cmd = nvcc_path if nvcc_path.exists() else shutil.which("nvcc")
            if isinstance(nvcc_cmd, str):
                nvcc_cmd = Path(nvcc_cmd)
            return (nvcc_cmd, include, lib64)
        nvcc_cmd = shutil.which("nvcc")
        return (Path(nvcc_cmd) if nvcc_cmd else None, None, None)

    def build_extension(self, ext):
        if ext.name != "NepTrainKit.nep_gpu":
            return super().build_extension(ext)

        nvcc, cuda_include, cuda_lib = self._cuda_paths()
        if not nvcc:
            print("WARNING: nvcc not found; skipping NepTrainKit.nep_gpu build.")
            return

        cu_srcs = [s for s in ext.sources if s.endswith('.cu')]
        cpp_srcs = [s for s in ext.sources if not s.endswith('.cu')]

        objects = []
        if cpp_srcs:
            objects += self.compiler.compile(
                cpp_srcs,
                output_dir=self.build_temp,
                include_dirs=ext.include_dirs,
                extra_postargs=ext.extra_compile_args,
                depends=ext.depends)

        nvcc_flags = ["-O3", "-std=c++14"]
        # Target GPU architecture(s)
        # Accept either:
        #  - NEP_GPU_GENCODE="arch=compute_80,code=sm_80"
        #  - NEP_GPU_GENCODE="-gencode arch=compute_60,code=sm_60 -gencode arch=compute_80,code=sm_80"
        # If unset, default to sm_60.
        gencode_env = os.environ.get("NEP_GPU_GENCODE", "").strip()
        if gencode_env:
            parts = shlex.split(gencode_env)
            if any(p == "-gencode" for p in parts):
                i = 0
                while i < len(parts):
                    if parts[i] == "-gencode" and i + 1 < len(parts):
                        nvcc_flags += ["-gencode", parts[i + 1]]
                        i += 2
                    else:
                        i += 1
            else:
                nvcc_flags += ["-gencode", gencode_env]
        else:
            nvcc_flags += ["-gencode", "arch=compute_60,code=sm_60"]

            nvcc_flags += ["-gencode", "arch=compute_75,code=sm_75"]
            nvcc_flags += ["-gencode", "arch=compute_80,code=sm_80"]
            nvcc_flags += ["-gencode", "arch=compute_86,code=sm_86"]
            nvcc_flags += ["-gencode", "arch=compute_89,code=sm_89"]
            nvcc_flags += ["-gencode", "arch=compute_90,code=sm_90"]


        # Optional: silence warnings for older architectures on newer toolchains
        if os.environ.get("NEP_GPU_SILENCE_DEPRECATED", "1") == "1":
            nvcc_flags += ["-Wno-deprecated-gpu-targets"]
        # Optional stronger CUDA error checks
        # if os.environ.get("NEP_GPU_STRONG_DEBUG"):
        #     nvcc_flags += ["-DSTRONG_DEBUG"]
        if os.name == 'nt':
            # Enable OpenMP (SIMD) and typical MSVC flags for host compilation
            nvcc_flags += ["-Xcompiler", "/openmp:experimental,/MD,/O2,/EHsc"]
        else:
            # PIC for shared lib, enable OpenMP on host compiler
            nvcc_flags += ["-Xcompiler", "-fPIC", "-Xcompiler", "-fopenmp"]

        incs = []
        for inc in (ext.include_dirs or []):
            incs += ["-I", str(inc)]
        if cuda_include:
            incs += ["-I", str(cuda_include)]

        # Add Python.h include dirs for NVCC (pybind11 needs it)
        try:
            paths = sysconfig.get_paths()
            py_inc = paths.get("include")
            plat_inc = paths.get("platinclude")
            if py_inc:
                incs += ["-I", py_inc]
            if plat_inc and plat_inc != py_inc:
                incs += ["-I", plat_inc]
        except Exception:
            pass

        # Enable verbose debug prints via env var
        # if os.environ.get("NEP_GPU_DEBUG"):
        #     nvcc_flags += ["-DNEP_GPU_DEBUG"]

        Path(self.build_temp).mkdir(parents=True, exist_ok=True)

        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        for src in cu_srcs:
            src_path = Path(src)
            obj_path = build_temp / (src_path.stem + (".obj" if os.name == 'nt' else ".o"))
            cmd = [str(nvcc), "-c", str(src_path), "-o", str(obj_path)] + nvcc_flags + incs
            try:
                subprocess.check_call(cmd)
            except Exception as e:
                print(f"WARNING: NVCC failed on {src}: {e}")
                return
            objects.append(str(obj_path))

        lib_dirs = []
        if cuda_lib:
            lib_dirs.append(str(cuda_lib))
        libs = ["cudart", "cublas", "cusolver", "curand"]





        output_path = self.get_ext_fullpath(ext.name)
        try:
            self.compiler.link_shared_object(
                objects,
                output_path,
                libraries=libs,
                library_dirs=lib_dirs,
                extra_postargs=ext.extra_link_args,
                target_lang='c++')
        except Exception as e:
            print(f"WARNING: Linking nep_gpu failed: {e}")
            return
    def build_extensions(self):
        # If nvcc is unavailable, drop the GPU extension so copy stage won't fail
        try:
            nvcc, _, _ = self._cuda_paths()
        except Exception:
            nvcc = None
        if not nvcc:
            print("WARNING: nvcc not found; skipping NepTrainKit.nep_gpu build.")
            self.extensions = [e for e in self.extensions if e.name != "NepTrainKit.nep_gpu"]
        return super().build_extensions()
setup(
    author="Chen Cheng bing",
cmdclass={'build_ext': BuildExtNVCC},
    # include_dirs=[np.get_include()],
ext_modules=ext_modules,
zip_safe=False,
)
