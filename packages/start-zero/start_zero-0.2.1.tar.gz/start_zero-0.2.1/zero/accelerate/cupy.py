import numpy as np

cupy_available = False
gpu_flag = False
try:
    """
    Windows下安装cupy支持GPU运算：   
    1、N卡支持下载：
    参考地址A：https://developer.nvidia.com/cuda-downloads
    参考地址B：https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html
    参考地址C：https://developer.nvidia.com/cuda-toolkit-archive
    2、pip安装：
    参考命令：pip install cupy-cuda12x
    """
    import cupy as cp
    cupy_available = True
except ModuleNotFoundError:
    pass


def use_gpu():
    global gpu_flag
    if cupy_available:
        gpu_flag = True


def use_cpu():
    global gpu_flag
    gpu_flag = False


def cp_np():
    return cp if gpu_flag else np


def cp_to_np(cp_data):
    return cp.asnumpy(cp_data)


def np_to_cp(np_data):
    return cp.asarray(np_data)
