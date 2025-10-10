from setuptools import setup, Extension
from Cython.Build import cythonize
import platform

system = platform.system()
machine = platform.machine()

is_arm64 = machine in ("arm64", "aarch64")
is_x86_64 = machine == "x86_64"

if system == "Windows":  # Windows（MSVC）
    extra_compile_args = [
        "/O2",  # 最高优化级别
        "/Ot",  # 优先速度优化
        "/arch:AVX2",  # 启用AVX2指令集（根据CPU支持调整）
        "/GL",
    ]
    extra_link_args = ["/LTCG"]
else:
    if is_arm64:
        extra_compile_args = [
            "-O3",  # 激进优化
            # "-march=native",  # 针对本地CPU优化
            "-fvectorize",
            "-fslp-vectorize",
            "-ffast-math",  # 快速数学运算
            "-funroll-loops",  # 循环展开
            "-flto=thin",
        ]
        extra_link_args = ["-flto=thin"]  # 链接器通常无需额外参数，特殊场景可加（如-lm链接数学库）
    else:
        extra_compile_args = [
            "-O3",  # 激进优化
            # "-march=native",  # 针对本地CPU优化
            "-ftree-vectorize",
            "-ftree-slp-vectorize",
            "-ffast-math",  # 快速数学运算
            "-funroll-loops",  # 循环展开
            "-flto",
            "-march=x86-64-v2",
        ]

        extra_link_args = ["-flto"]  # 链接器通常无需额外参数，特殊场景可加（如-lm链接数学库）


ext_modules = [
    Extension(
        name="bencode._bencodec",  # 生成的模块名
        sources=["bencode/_bencode.py"],  # 你的Cython源码文件
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="bencode.cy",
    packages=["bencode"],
    # ext_modules =cythonize("bencode.py")
    ext_modules=cythonize(ext_modules, annotate=True, language_level="3str"),  # annotate生成优化分析报告
)
