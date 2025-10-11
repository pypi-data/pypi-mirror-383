import numpy as np

from .base_op import BaseOp
from .act_ops import sigmoid
from .exp_log_ops import ln, exp
from .util_ops import clip
from .norm_ops import softmax


def mean_squared_error(x0, x1):
    """
    简单实现：
    x0, x1 = Tensor(x0), Tensor(x1)
    diff = x0 - x1
    y = sum(diff ** 2) / len(diff)
    return y
    """
    return MeanSquaredError()(x0, x1)


def softmax_cross_entropy(x, t):
    """
    简单实现
    x, t = Tensor(x), Tensor(t)
    N = x.shape[0]
    p = softmax(x)
    p = clip(p, 1e-15, 1.0)  # 避免log(0)
    log_p = log(p)
    tlog_p = log_p[np.arange(N), t.data]
    y = -1 * sum(tlog_p) / N
    return y
    """
    return SoftmaxCrossEntropy()(x, t)


def sigmoid_cross_entropy(x, t):
    if x.ndim != t.ndim:
        t = t.reshape(*x.shape)
    from zero.core.tensor import Tensor
    x, t = (x if isinstance(x, Tensor) else Tensor(x)), (t if isinstance(t, Tensor) else Tensor(t))
    N = len(x)
    p = sigmoid(x)
    p = clip(p, 1e-15, 1.0)
    tlog_p = t * ln(p) + (1 - t) * ln(1 - p)
    y = -1 * sum(tlog_p) / N
    return y


def binary_cross_entropy(x, t):
    if x.ndim != t.ndim:
        t = t.reshape(*x.shape)
    N = len(t)
    p = clip(x, 1e-15, 0.999)
    tlog_p = t * ln(p) + (1 - t) * ln(1 - p)
    y = -1 * sum(tlog_p) / N
    return y


def categorical_cross_entropy(x, t):
    return CategoricalCrossEntropy()(x, t)


class MeanSquaredError(BaseOp):
    """
    mean_squared_error
    """

    def forward(self, x0, x1):
        """
        mean_squared_error的正向传播
        :param x0: 参数x0
        :param x1: 参数x1
        :return: mean_squared_error函数的计算结果
        """
        diff = x0 - x1
        y = (diff ** 2).sum() / len(diff)
        return y

    def backward(self, gy):
        """
        mean_squared_error的反向传播
        :param gy: 导数值
        :return: mean_squared_error函数的的反向传播的值
        """
        x0, x1 = self.inputs
        diff = x0 - x1
        gx0 = gy * diff * (2. / len(diff))
        gx1 = -gx0
        return gx0, gx1


class SoftmaxCrossEntropy(BaseOp):
    """
    softmax_cross_entropy
    """

    def forward(self, x, t):
        """
        softmax_cross_entropy的正向传播
        :param x: 参数x
        :param t: 参数t
        :return: softmax_cross_entropy函数的计算结果
        """
        N = x.shape[0]
        log_z = x.max(axis=1, keepdims=True)
        y = x - log_z
        y = np.exp(y)
        s = y.sum(axis=1, keepdims=True)
        s = np.log(s)
        log_z = log_z + s
        log_p = x - log_z
        log_p = log_p[np.arange(N), t.ravel()]
        y = -log_p.sum() / np.float32(N)
        return y

    def backward(self, gy):
        """
        softmax_cross_entropy的反向传播
        :param gy: 导数值
        :return: softmax_cross_entropy函数的的反向传播的值
        """
        x, t = self.inputs
        N, CLS_NUM = x.shape
        gy *= 1 / N
        y = softmax(x)
        t_onehot = np.eye(CLS_NUM, dtype=t.dtype)[t.data]
        y = (y - t_onehot) * gy
        return y


class CategoricalCrossEntropy(BaseOp):

    def __init__(self, ignore_index=-100):
        self.ignore_index = ignore_index

    def forward(self, x, t):
        """
        predictions: (batch_size, seq_len, vocab_size) 或 (batch_size, vocab_size)
        targets: (batch_size, seq_len) 或 (batch_size,)
        """
        if x.ndim == 2:
            batch_size, vocab_size = x.shape
            seq_len = 1
            x_flat = x
            t_flat = t.flatten()
        else:
            batch_size, seq_len, vocab_size = x.shape
            x_flat = x.reshape(-1, vocab_size)
            t_flat = t.reshape(-1)
        # 数值稳定的log_softmax
        max_vals = x_flat.max(axis=1, keepdims=True)
        x_shifted = x_flat - max_vals
        log_sum_exp = np.log(np.exp(x_shifted).sum(axis=1, keepdims=True) + 1e-12)
        log_probs = x_shifted - log_sum_exp
        # 计算NLL损失
        nll_loss = -log_probs[np.arange(len(t_flat)), t_flat]
        # 应用忽略索引掩码
        if self.ignore_index is not None:
            mask = (t_flat != self.ignore_index).astype(np.float32)
        else:
            mask = np.ones_like(t_flat, dtype=np.float32)
        loss = (nll_loss * mask).sum() / (mask.sum() + 1e-8)
        return loss

    def backward(self, gy):
        """
        反向传播
        upstream_grad: 上游梯度，通常为1.0
        """
        x, t = self.inputs
        # 处理不同维度的输入
        if x.data.ndim == 2:
            batch_size, vocab_size = x.data.shape
            seq_len = 1
            x_flat = x.data
            t_flat = t.data.flatten()
        else:
            batch_size, seq_len, vocab_size = x.data.shape
            x_flat = x.data.reshape(-1, vocab_size)
            t_flat = t.data.reshape(-1)
        # 计算softmax
        from .util_ops import max, sum
        max_vals = max(x_flat, axis=1, keepdims=True)
        from .exp_log_ops import exp
        exp_vals = exp(x_flat - max_vals)
        softmax_vals = exp_vals / (sum(exp_vals, axis=1, keepdims=True) + 1e-12)
        # 创建one-hot编码
        t_onehot = np.eye(vocab_size)[t_flat]
        # 梯度计算
        grad = (softmax_vals - t_onehot) * gy
        from .util_ops import reshape
        # 应用忽略索引掩码
        if self.ignore_index is not None:
            mask = (t_flat != self.ignore_index).astype(np.float32)
            grad = grad * reshape(mask, (-1, 1))
        # 恢复原始形状
        if x.data.ndim == 2:
            grad = reshape(grad, (batch_size, vocab_size))
        else:
            grad = reshape(grad, (batch_size, seq_len, vocab_size))
        return grad
