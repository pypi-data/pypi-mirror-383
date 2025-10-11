import numpy as np

from .base_op import BaseOp
from .util_ops import sum_to, matmul


def linear(x, W, b=None):
    return Linear()(x, W, b)


class Linear(BaseOp):
    """
    线性回归：x*W+b
    """

    def forward(self, x, W, b):
        """
        线性变换的正向传播
        :param x: 参数x
        :param W: 权重W
        :param b: 偏置b
        :return: 线性回归的计算结果
        """
        y = np.matmul(x, W)
        if b is not None:
            y += b
        return y

    def backward(self, gy):
        """
        线性变换的反向传播
        :param gy: 导数值
        :return: 线性回归的反向传播的值
        """
        x, W, b = self.inputs
        gb = None if b.data is None else sum_to(gy, b.shape)
        gx = matmul(gy, W.T)
        gW = matmul(x.T, gy)
        return gx, gW, gb
