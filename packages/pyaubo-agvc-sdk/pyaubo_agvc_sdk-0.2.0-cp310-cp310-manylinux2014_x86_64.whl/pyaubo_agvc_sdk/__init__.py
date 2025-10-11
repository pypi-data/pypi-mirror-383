import os
import sys
import ctypes

def _load_agvc_sdk():
    """跨平台加载 AGVC SDK 动态库，确保加载成功后再导入扩展模块"""
    # 1. 确定动态库路径（包内目录）
    _pkg_dir = os.path.dirname(__file__)
    _so_name = "libagvc_sdk.so"
    _so_path = os.path.join(_pkg_dir, _so_name)
    
    if not os.path.exists(_so_path):
        raise ImportError(
            f"AGVC SDK 动态库不存在：{_so_path}\n"
            f"请确保编译时动态库已生成并复制到包目录"
        )
    
    # 2. 跨平台加载逻辑
    try:
        if sys.platform == "win32":
            # Windows：用 WinDLL 加载（适配 stdcall 调用约定，避免函数调用错误）
            ctypes.WinDLL(_so_path)
        else:
            # Linux：用 CDLL + RTLD_GLOBAL（确保扩展模块能找到 SDK 中的符号）
            ctypes.CDLL(_so_path, mode=ctypes.RTLD_GLOBAL)
        print(f"成功加载 AGVC SDK：{_so_path}")
    except Exception as e:
        raise ImportError(f"加载 AGVC SDK 失败：{str(e)}") from e

# 先加载动态库，再导入扩展模块（避免扩展模块找不到 SDK 符号）
_load_agvc_sdk()

# 导入 pybind11 生成的 C++ 扩展模块
from . import pyaubo_agvc_sdk as _ext_module

# 将扩展模块的公开符号暴露到包顶层（方便用户直接使用）
__all__ = [name for name in dir(_ext_module) if not name.startswith("_")]
for name in __all__:
    globals()[name] = getattr(_ext_module, name)

# 清理内部引用，避免用户误操作
del _ext_module, os, sys, ctypes, _load_agvc_sdk
