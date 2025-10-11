import numpy as np

from .base_op import BaseOp
from .exp_log_ops import exp
from .util_ops import sum
from .math_ops import power


def softmax(x, axis=1):
    """
    简单实现：
    x = as_variable(x)
    y = exp(x)
    sum_y = sum(y, axis=axis, keepdims=True)
    return y / sum_y
    """
    return Softmax(axis)(x)


def log_softmax(x, axis=1):
    return LogSoftmax(axis)(x)


def layer_norm(x, axis=1):
    return LayerNorm(axis)(x)


def batch_norm(x, gamma, beta, mean, var, decay=0.9, eps=2e-5):
    return BatchNorm(mean, var, decay, eps)(x, gamma, beta)


class Softmax(BaseOp):
    """
    softmax归一化概率函数
    """

    def __init__(self, axis=1):
        """
        初始化
        :param axis: 参数axis
        """
        self.axis = axis

    def forward(self, x):
        """
        softmax的正向传播
        :param x: 参数x
        :return: Softmax函数的计算结果
        """
        y = x - x.max(axis=self.axis, keepdims=True)
        y = np.exp(y)
        y /= np.sum(y, axis=self.axis, keepdims=True)
        return y

    def backward(self, gy):
        """
        softmax的反向传播
        :param gy: 导数值
        :return: softmax函数的的反向传播的值
        """
        y = self.outputs[0]()
        gx = y * gy
        sum_dx = sum(gx, axis=self.axis, keepdims=True)
        gx -= y * sum_dx
        return gx


class LogSoftmax(BaseOp):
    """
    log_softmax归一化概率函数
    """

    def __init__(self, axis=1):
        """
        初始化
        :param axis: 参数axis
        """
        self.axis = axis

    def forward(self, x):
        """
        log_softmax的正向传播
        :param x: 参数x
        :return: log_softmax函数的计算结果
        """
        m = x.max(axis=self.axis, keepdims=True)
        y = x - m
        y = np.exp(y)
        s = np.sum(y, axis=self.axis, keepdims=True)
        s = np.log(s)
        m = m + s
        y = x - m
        return y

    def backward(self, gy):
        """
        log_softmax的反向传播
        :param gy: 导数值
        :return: log_softmax函数的的反向传播的值
        """
        y = self.outputs[0]()
        gx = gy - exp(y) * sum(gy, axis=self.axis, keepdims=True)
        return gx


class LayerNorm(BaseOp):
    """
    层归一化函数（包含可学习的缩放和平移参数）
    """

    def __init__(self, normalized_shape, eps=1e-6):
        """
        初始化层归一化
        :param normalized_shape: 归一化的特征维度
        :param eps: 数值稳定性参数
        """
        self.mean = None
        self.variance = None
        self.x_hat = None

        self.normalized_shape = normalized_shape
        self.eps = eps

        # 可学习的参数
        self.gamma = np.ones(normalized_shape)  # 缩放参数
        self.beta = np.zeros(normalized_shape)  # 平移参数

        # 参数的梯度
        self.gamma_grad = np.zeros_like(self.gamma)
        self.beta_grad = np.zeros_like(self.beta)

    def forward(self, x):
        """
        层归一化的正向传播
        :param x: 输入张量
        :return: 归一化结果
        """
        # 计算均值和方差
        mean = np.mean(x, axis=-1, keepdims=True)
        variance = np.var(x, axis=-1, keepdims=True)
        # 归一化
        x_hat = (x - mean) / np.sqrt(variance + self.eps)
        # 缩放和平移
        y = self.gamma * x_hat + self.beta
        # 保存中间结果用于反向传播
        self.mean = mean
        self.variance = variance
        self.x_hat = x_hat

        return y

    def backward(self, gy):
        """
        层归一化的反向传播
        :param gy: 上一层的梯度
        :return: 输入x的梯度
        """
        x = self.inputs[0]
        N = x.shape[-1]  # 特征维度大小
        # 计算beta和gamma的梯度
        self.beta_grad = sum(gy, axis=tuple(range(gy.ndim - 1)))
        self.gamma_grad = sum(gy * self.x_hat, axis=tuple(range(gy.ndim - 1)))
        # 计算dx_hat的梯度
        std = power(self.variance + self.eps, -0.5)
        dx_hat = gy * self.gamma
        # 计算方差梯度
        d_var = sum(dx_hat * (x - self.mean) * (-0.5) / (std ** 3), axis=-1, keepdims=True)
        # 计算均值梯度
        d_mean = sum(dx_hat * (-1 / std), axis=-1, keepdims=True) + d_var * sum(-2 * (x - self.mean), axis=-1, keepdims=True) / N
        # 计算x的梯度
        gx = dx_hat / std + d_var * 2 * (x - self.mean) / N + d_mean / N
        return gx


class BatchNorm(BaseOp):
    """
    batch_norm
    """

    def __init__(self, mean, var, decay, eps):
        """
        初始化
        :param mean: 参数mean
        :param var: 参数var
        :param decay: 参数decay
        :param eps: 参数eps
        """
        self.avg_mean = mean
        self.avg_var = var
        self.decay = decay
        self.eps = eps
        self.inv_std = None

    def forward(self, x, gamma, beta):
        """
        batch_norm的正向传播
        :param x: 参数x
        :param gamma: 参数gamma
        :param beta: 参数beta
        :return: batch_norm函数的计算结果
        """
        assert x.ndim == 2 or x.ndim == 4

        x_ndim = x.ndim
        if x_ndim == 4:
            N, C, H, W = x.shape
            # (N, C, H, W) -> (N * H * W, C)
            x = x.transpose(0, 2, 3, 1).reshape(-1, C)

        """
        inv_std = 1 / xp.sqrt(self.avg_var + self.eps)
        xc = (x - self.avg_mean) * inv_std
        """
        mean = x.mean(axis=0)
        var = x.var(axis=0)
        inv_std = 1 / np.sqrt(var + self.eps)
        xc = (x - mean) * inv_std

        m = x.size // gamma.size
        s = m - 1. if m - 1. > 1. else 1.
        adjust = m / s  # unbiased estimation
        self.avg_mean *= self.decay
        self.avg_mean += (1 - self.decay) * mean
        self.avg_var *= self.decay
        self.avg_var += (1 - self.decay) * adjust * var
        self.inv_std = inv_std

        y = gamma * xc + beta

        if x_ndim == 4:
            # (N * H * W, C) -> (N, C, H, W)
            y = y.reshape(N, H, W, C).transpose(0, 3, 1, 2)
        return y

    def backward(self, gy):
        """
        batch_norm的反向传播
        :param gy: 导数值
        :return: batch_norm函数的的反向传播的值
        """
        gy_ndim = gy.ndim
        if gy_ndim == 4:
            N, C, H, W = gy.shape
            gy = gy.transpose(0, 2, 3, 1).reshape(-1, C)

        x, gamma, beta = self.inputs
        batch_size = len(gy)

        if x.ndim == 4:
            N, C, H, W = x.shape
            x = x.transpose(0, 2, 3, 1).reshape(-1, C)
        mean = sum(x, axis=0) / batch_size
        xc = (x - mean) * self.inv_std

        gbeta = sum(gy, axis=0)
        ggamma = sum(xc * gy, axis=0)
        gx = gy - gbeta / batch_size - xc * ggamma / batch_size
        gx *= gamma * self.inv_std

        if gy_ndim == 4:
            gx = gx.reshape(N, H, W, C).transpose(0, 3, 1, 2)
        return gx, ggamma, gbeta
