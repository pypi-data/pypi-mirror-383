import numpy as np

from .base_op import BaseOp


def sin(x):
    return Sin()(x)


def cos(x):
    return Cos()(x)


def tan(x):
    return Tan()(x)


def tanh(x):
    return Tanh()(x)


class Sin(BaseOp):
    """
    正弦类
    """

    def forward(self, x):
        """
        正弦的正向传播
        :param x: 待求正弦的值
        """
        return np.sin(x)

    def backward(self, gy):
        """
        正弦的反向传播
        :param gy: 导数值
        :return: 正弦反向传播的值
        """
        x = self.inputs[0]
        return gy * cos(x)


class Cos(BaseOp):
    """
    余弦类
    """

    def forward(self, x):
        """
        余弦的正向传播
        :param x: 待求余弦的值
        """
        return np.cos(x)

    def backward(self, gy):
        """
        余弦的反向传播
        :param gy: 导数值
        :return: 余弦反向传播的值
        """
        x = self.inputs[0]
        return gy * (-sin(x))


class Tan(BaseOp):
    """
    正切类
    """

    def forward(self, x):
        """
        正切的正向传播
        :param x: 待求正切的值
        """
        return np.tan(x)

    def backward(self, gy):
        """
        正切的反向传播
        :param gy: 导数值
        :return: 正切反向传播的值
        """
        x = self.inputs[0]
        return gy * (1 / (cos(x) ** 2))


class Tanh(BaseOp):
    """
    双曲正切类
    """

    def forward(self, x):
        """
        双曲正切的正向传播
        :param x: 待求双曲正切的值
        """
        return np.tanh(x)

    def backward(self, gy):
        """
        双曲正切的反向传播
        :param gy: 导数值
        :return: 双曲正切反向传播的值
        """
        y = self.outputs[0]()  # 弱引用
        # 参见：tanh(x)的导数=1-(tanh(x))^2
        gx = gy * (1 - y * y)
        return gx
