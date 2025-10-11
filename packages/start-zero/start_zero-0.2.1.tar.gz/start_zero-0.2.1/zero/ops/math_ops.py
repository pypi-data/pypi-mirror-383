import numpy as np

from .base_op import BaseOp
from .util_ops import sum_to, floor


def add(x0, x1):
    return Add()(x0, x1)


def sub(x0, x1):
    return Sub()(x0, x1)


def mul(x0, x1):
    return Mul()(x0, x1)


def div(x0, x1):
    return Div()(x0, x1)


def power(x, c):
    return Power(c)(x)


def neg(x):
    return Neg()(x)


def mod(x0, x1):
    return Mod()(x0, x1)


class Add(BaseOp):
    """
    加法类
    """

    def __init__(self):
        """
        初始化
        """
        self.x0_shape = None
        self.x1_shape = None

    def forward(self, x0, x1):
        """
        加法的正向传播
        :param x0: 加法的一个值
        :param x1: 加法的另一个值
        :return: 一个值与另一个值相加的结果
        """
        self.x0_shape = x0.shape
        self.x1_shape = x1.shape
        return x0 + x1

    def backward(self, gy):
        """
        加法的反向传播
        :param gy: 导数值
        :return: 加法反向传播的值
        """
        gx0, gx1 = gy, gy  # 即：1 * gy, 1 * gy
        """
        为了处理如数组(2,3)反向传播更新梯度为(3,)之类的情况
        这里可能会有个疑问，为什么不是(1,3)呢？因为(1,3)实际是一个二维矩阵了，而(3,)则是一个以为矩阵
        举例：
        [1 2 3]    => (3,)
        [[1 2 3]]  => (1,3)
        """
        # if self.x0_shape != self.x1_shape:
        if gx0.shape != self.x0_shape:
            gx0 = sum_to(gx0, self.x0_shape)
        if gx1.shape != self.x1_shape:
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1


class Sub(BaseOp):
    """
    减法类
    """

    def __init__(self):
        self.x0_shape = None
        self.x1_shape = None

    def forward(self, x0, x1):
        """
        减法的正向传播
        :param x0: 被减数
        :param x1: 减数
        """
        self.x0_shape = x0.shape
        self.x1_shape = x1.shape
        return x0 - x1

    def backward(self, gy):
        """
        减法的反向传播
        :param gy: 导数值
        """
        gx0, gx1 = gy, -gy
        """
        为了处理如数组(2,3)反向传播更新梯度为(3,)之类的情况
        这里可能会有个疑问，为什么不是(1,3)呢？因为(1,3)实际是一个二维矩阵了，而(3,)则是一个以为矩阵
        举例：
        [1 2 3]    => (3,)
        [[1 2 3]]  => (1,3)
        """
        # if self.x0_shape != self.x1_shape:
        if gx0.shape != self.x0_shape:
            gx0 = sum_to(gx0, self.x0_shape)
        if gx1.shape != self.x1_shape:
            gx1 = sum_to(gx1, self.x1_shape)
        return gx0, gx1


class Mul(BaseOp):
    """
    乘法类
    """

    def forward(self, x0, x1):
        """
        乘法的正向传播
        请特别注意：x0*x1表示逐元素相乘，又称之为阿达马积
        x = np.array([[1, 2, 3], [4, 5, 6]])
        y = np.array([[9, 8, 7], [5, 5, 4]])
        print(x * y)
        结果为：
        [[ 9 16 21]
        [20 25 24]]
        而还有一种叫点乘
        x = np.array([[1, 2, 3], [4, 5, 6]])
        y = np.array([[1, 2], [3, 4], [5, 6]])
        print(np.dot(x, y))
        结果为：
        [[22 28]
        [49 64]]
        :param x0: 一个乘数
        :param x1: 另一个乘数
        """
        return x0 * x1

    def backward(self, gy):
        """
        乘法的反向传播
        :param gy: 导数值
        :return: 乘法反向传播的值
        """
        x0, x1 = self.inputs
        gx0, gx1 = gy * x1, gy * x0
        """
        为了处理如数组(2,3)反向传播更新梯度为(3,)之类的情况
        这里可能会有个疑问，为什么不是(1,3)呢？因为(1,3)实际是一个二维矩阵了，而(3,)则是一个以为矩阵
        举例：
        [1 2 3]    => (3,)
        [[1 2 3]]  => (1,3)
        """
        # if x0.shape != x1.shape:
        if gx0.shape != x0.shape:
            gx0 = sum_to(gx0, x0)
        if gx1.shape != x1.shape:
            gx1 = sum_to(gx1, x1.shape)
        return gx0, gx1


class Div(BaseOp):
    """
    除法类
    """

    def forward(self, x0, x1):
        """
        除法的正向传播
        :param x0: 被除数
        :param x1: 除数
        """
        return x0 / x1

    def backward(self, gy):
        """
        除法的反向传播
        :param gy: 导数值
        """
        x0, x1 = self.inputs
        gx0, gx1 = gy / x1, gy * (-x0 / x1 ** 2)
        # if x0.shape != x1.shape:
        if gx0.shape != x0.shape:
            gx0 = sum_to(gx0, x0)
        if gx1.shape != x1.shape:
            gx1 = sum_to(gx1, x1.shape)
        return gx0, gx1


class Power(BaseOp):
    """
    幂类
    """

    def __init__(self, c):
        """
        初始化
        :param c: 常数
        """
        self.c = c

    def forward(self, x):
        """
        幂的正向传播
        :param x: 底数
        """
        """
        异常处理：Integers to negative integer powers are not allowed
        当幂值为负数时，需要将底数变为浮点型
        """
        if np.issubdtype(x.dtype, np.integer) and self.c < 0:
            x = np.array(x, dtype=np.float32)
        return x ** self.c

    def backward(self, gy):
        """
        幂的反向传播
        :param gy: 导数值
        :return: 幂反向传播的值
        """
        x = self.inputs[0]
        c = self.c
        gx = c * (x ** (c - 1)) * gy
        return gx


class Neg(BaseOp):
    """
    负数类
    """

    def forward(self, x):
        """
        负数的正向传播
        :param x: 需要变负的数
        """
        return -x

    def backward(self, gy):
        """
        负数的反向传播
        :param gy: 导数值
        """
        return -gy


class Mod(BaseOp):
    """
    模类
    """

    def forward(self, x0, x1):
        """
        模的正向传播
        :param x0: 被取模数
        :param x1: 模数
        """
        return x0 % x1

    def backward(self, gy):
        """
        模的反向传播
        :param gy: 导数值
        """
        """
        另一种实现：
        from zero.core import Tensor
        x0, x1 = self.inputs
        gx0 = gy  # gy * 1
        gx1 = gy * Tensor(-np.floor(x0.data / x1.data))
        return gx0, gx1
        """
        x0, x1 = self.inputs
        gx0 = gy  # gy * 1
        gx1 = gy * (-floor(x0 / x1))
        return gx0, gx1
