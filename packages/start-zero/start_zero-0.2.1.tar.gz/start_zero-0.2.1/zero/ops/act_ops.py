import numpy as np

from .base_op import BaseOp
from .math_ops import power
from .tri_ops import tanh


def step(x):
    """
    无需反向传播，或者说反向传播对它没有意义
    在深度学习训练中，应该使用可微的激活函数（如relu、sigmoid等）替代step函数。step函数只在模型推理阶段或特定情况下使用
    """
    y = x > 0
    return y.astype(int)


def sigmoid(x):
    return Sigmoid()(x)


def relu(x):
    return ReLU()(x)


def gelu(x):
    return GeLU()(x)


def leaky_relu(x, slope=0.2):
    return LeakyReLU(slope)(x)


class Sigmoid(BaseOp):
    """
    sigmoid函数
    """

    def forward(self, x):
        """
        sigmoid的正向传播
        :param x: 参数x
        :return: sigmoid函数的计算结果
        """
        # y = 1 / (1 + xp.exp(-x))
        y = np.tanh(x * 0.5) * 0.5 + 0.5  # 更好的实现方式
        return y

    def backward(self, gy):
        """
        sigmoid的反向传播
        :param gy: 导数值
        :return: sigmoid函数的的反向传播的值
        """
        y = self.outputs[0]()
        # 为什么sigmoid(y1)的导数反而是(1-y2)*y2？因为sigmoid(y1)的导数等于sigmoid(y1)*(1-sigmoid(y1))，而y2=sigmoid(y1)，所以替换后就是(1-y2)*y2
        gx = gy * y * (1 - y)
        return gx


class ReLU(BaseOp):
    """
    ReLU
    """

    def forward(self, x):
        """
        ReLU的正向传播
        :param x: 参数x
        :return: ReLU函数的计算结果
        """
        y = np.maximum(x, 0.0)
        return y

    def backward(self, gy):
        """
        ReLU的反向传播
        :param gy: 导数值
        :return: ReLU函数的的反向传播的值
        """
        x, = self.inputs
        mask = x.data > 0
        # mask：True=1、False=0
        gx = gy * mask
        return gx


class GeLU(BaseOp):
    """
    GeLU
    基于高斯分布的近似实现
    """

    def forward(self, x):
        """
        GeLU的正向传播
        :param x: 参数x
        :return: GeLU函数的计算结果
        """
        y = 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x ** 3)))
        return y

    def backward(self, gy):
        """
        GeLU的反向传播
        :param gy: 导数值
        :return: GeLU函数的的反向传播的值
        """
        x, = self.inputs
        sqrt_2_over_pi = power(2 / np.pi, 0.5)
        inner = sqrt_2_over_pi * (x.data + 0.044715 * x.data ** 3)
        tanh_inner = tanh(inner)
        dy_dx = 0.5 * (1 + tanh_inner) + 0.5 * x.data * (1 - tanh_inner ** 2) * sqrt_2_over_pi * (1 + 3 * 0.044715 * x.data ** 2)
        gx = gy * dy_dx
        return gx


class LeakyReLU(BaseOp):
    """
    leaky_relu
    """

    def __init__(self, slope):
        """
        初始化
        :param slope: 参数slope
        """
        self.slope = slope

    def forward(self, x):
        """
        leaky_relu的正向传播
        :param x: 参数x
        :return: leaky_relu函数的计算结果
        """
        y = x.copy()
        y[x <= 0] *= self.slope
        return y

    def backward(self, gy):
        """
        leaky_relu的反向传播
        :param gy: 导数值
        :return: leaky_relu函数的的反向传播的值
        """
        x, = self.inputs
        mask = (x.data > 0).astype(gy.dtype)
        mask[mask <= 0] = self.slope
        gx = gy * mask
        return gx
