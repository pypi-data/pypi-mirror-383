import numpy as np

from .base_op import BaseOp


def sum(x, axis=None, keepdims=False):
    return Sum(axis, keepdims)(x)


def sum_to(x, shape):
    if x.shape == shape:
        return x
    return SumTo(shape)(x)


def broadcast_to(x, shape):
    if x.shape == shape:
        return x
    return BroadcastTo(shape)(x)


def average(x, axis=None, keepdims=False):
    y = sum(x, axis, keepdims)
    count = np.size(x, axis=axis)  # 沿着指定轴的元素个数
    return y / count


def matmul(x0, x1):
    return MatMul()(x0, x1)


def outer(x0, x1):
    return Outer()(x0, x1)


def transpose(x, axes=None):
    return Transpose(axes)(x)


def swap_axes(x, axis1, axis2):
    return SwapAxes(axis1, axis2)(x)


def reshape(x, shape):
    return Reshape(shape)(x)


def get_item(x, slices):
    return GetItem(slices)(x)


def get_item_grad(x, slices, in_shape):
    return GetItemGrad(slices, in_shape)(x)


def clip(x, x_min, x_max):
    return Clip(x_min, x_max)(x)


def max(x, axis=None, keepdims=False):
    return Max(axis, keepdims)(x)


def min(x, axis=None, keepdims=False):
    return Min(axis, keepdims)(x)


def floor(x):
    return Floor()(x)


def accuracy(y, t):
    from zero.core.tensor import Tensor
    _y = y
    _t = t
    if isinstance(_y, Tensor):
        _y = _y.data
    if isinstance(_t, Tensor):
        _t = _t.data
    _y = _y.argmax(axis=1)
    _t = _t.argmax(axis=1)
    return np.sum(_y == _t) / float(_y.shape[0])


"""
# 测试代码
def test_transformer_accuracy():
    # 模拟数据
    batch_size, seq_len, vocab_size = 2, 5, 10
    
    # 创建预测logits
    y = np.random.randn(batch_size, seq_len, vocab_size)
    
    # 创建真实标签（包含padding）
    t = np.array([
        [1, 2, 3, -100, -100],  # 后两个是padding
        [4, 5, 6, 7, -100]      # 最后一个是padding
    ])
    
    # 手动设置一些正确的预测
    y[0, 0, 1] = 10.0  # 位置(0,0)预测为1（正确）
    y[0, 1, 3] = 10.0  # 位置(0,1)预测为3（错误，真实是2）
    
    accuracy = transformer_accuracy(y, t)
    print(f"Accuracy: {accuracy:.4f}")

# 运行测试
test_transformer_accuracy()
"""


def transformer_accuracy(y, t, ignore_index=-100):
    """
    专门处理Transformer输出的准确率计算
    :param y: 模型预测输出(batch_size, seq_len, vocab_size)
    :param t: 真实标签(batch_size, seq_len)
    :param ignore_index: 需要忽略的标签索引（如padding位置）
    """
    from zero.core.tensor import Tensor
    _y = y
    _t = t
    if isinstance(_y, Tensor):
        _y = _y.data
    if isinstance(_t, Tensor):
        _t = _t.data
    # 获取预测结果
    _y = _y.argmax(axis=-1)
    # 创建掩码
    if ignore_index is not None:
        mask = (_t != ignore_index)
    else:
        mask = np.ones_like(t, dtype=bool)
    # 计算准确率
    correct = (_y == _t) & mask
    valid_count = mask.sum()
    # 避免除零错误
    if valid_count == 0:
        return 0.0
    return float(correct.sum() / valid_count)


def dropout(x, dropout_ratio=0.5):
    return Dropout(dropout_ratio)(x)


def gather(x, indices, axis=0):
    return Gather(axis)(x, indices)


class Sum(BaseOp):
    """
    求和
    """

    def __init__(self, axis, keepdims):
        """
        初始化
        :param axis: 要求和的数组的形状
        :param keepdims: 是否保留维度（True：保留维度；False：不保留维度）
        """
        self.axis = axis
        self.keepdims = keepdims
        self.x_shape = None

    def forward(self, x):
        """
        求和的正向传播
        :param x: 待求和的值
        """
        self.x_shape = x.shape
        return x.sum(axis=self.axis, keepdims=self.keepdims)

    def backward(self, gy):
        """
        求和的反向传播
        :param gy: 导数值
        :return: 求和的反向传播的值
        """
        ndim = len(self.x_shape)
        tupled_axis = self.axis
        if self.axis is None:
            tupled_axis = None
        elif not isinstance(self.axis, tuple):
            tupled_axis = (self.axis, )
        # 计算需要reshape的形状
        if not (ndim == 0 or tupled_axis is None or self.keepdims):
            # 计算实际的轴索引（处理负数索引）
            actual_axis = [a if a >= 0 else a + ndim for a in tupled_axis]
            # 构建新的形状，在求和的轴位置插入1
            shape = list(gy.shape)
            for axis in sorted(actual_axis):
                # 确保不重复插入
                if axis < len(shape):
                    shape.insert(axis, 1)
                else:
                    shape.append(1)
        else:
            shape = list(gy.shape)

        # 确保形状长度与原始输入相同
        while len(shape) < ndim:
            shape.append(1)
        while len(shape) > ndim:
            shape.pop()

        # 转换为tuple并reshape
        shape = tuple(shape)
        gy_reshaped = reshape(gy, shape)

        # 广播回原始形状
        gx = broadcast_to(gy_reshaped, self.x_shape)
        return gx


class SumTo(BaseOp):
    """
    合并求和
    """

    def __init__(self, to_shape: tuple):
        """
        初始化
        :param to_shape: 合并求和后的数组形状
        """
        self.to_shape = to_shape  # 合并求和后的数组形状
        self.from_shape = None  # 待合并求和的数组形状

    def forward(self, x):
        """
        合并求和的正向传播
        :param x: 待合并求和的值
        """
        self.from_shape = x.shape  # 待合并求和的数组形状
        ndim = len(self.to_shape)  # 合并求和后的数组长度
        lead = x.ndim - ndim  # 待合并求和的数组长度与合并求和后的数组长度差，如(1, 5, 3, 4)->(1, 1)，则差为2
        lead_axis = tuple(range(lead))  # 创造差值的元祖，如差为2，则差值元祖为：(0, 1)；如果差<=0，则差值元祖为：()
        """
        这是一个用于定位下标的编程技巧，参考：
        temp = ["a", "b", "c", "d"]
        out = tuple([index for index, value in enumerate(temp) if (value == 'a' or value == 'd')])
        print(out)  # (0, 3)
        为什么要筛出value==1？因为只有求和归一的维度才需要合并，比如(4, 4)，只有(1, 4)、(1, 1)、(4, 1)合并求和才有意义
        参考：
        x = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])  # x：(4, 3)
        print(x.sum((0, 1), keepdims=True))  # (1, 1)
        print(x.sum((0, ), keepdims=True))  # (1, 3)
        print(x.sum((1, ), keepdims=True))  # (4, 1)
        # print(x.sum((0, 1, 2), keepdims=True))  # 报错
        # print(x.sum((2, 2), keepdims=True))  # 报错
        对(1, 1)来说，两个值都是1，因此下标0和1都要被选中；对(1, 3)来说，只有下标为0的才会被选中
        """
        axis = tuple([index + lead for index, value in enumerate(self.to_shape) if value == 1])
        """
        (1, 5, 3, 4)->(1, 1)会先扩充为(0, 1, 1, 1)
        (0, 1, 1, 1)其中前2位(0, 1)来自lead_axis，后2位来自axis
        lead_axis+axis的处理参考元祖相加：(1, 2) + (3, 4) = (1, 2, 3, 4)
        转换成(0, 1, 1, 1)后就可以调用numpy.sum函数了，至于为什么要转换成类似(0, 1, 2, 3)形式，感兴趣的可以研究下[numpy.sum]函数说明
        """
        y = x.sum(lead_axis + axis, keepdims=True)
        if lead > 0:
            """
            如(1, 5, 3, 4)->(1, 1)，会先扩充为(0, 1, 1, 1)，但是实际只要(1, 1)，因此需要移除扩充的维度，感兴趣的可以研究下[numpy.squeeze]函数说明
            """
            y = y.squeeze(lead_axis)
        return y

    def backward(self, gy):
        """
        合并求和的反向传播
        :param gy: 导数值
        """
        gx = broadcast_to(gy, self.from_shape)
        return gx


class BroadcastTo(BaseOp):
    """
    矩阵广播
    """

    def __init__(self, to_shape: tuple):
        """
        初始化
        :param to_shape: 广播后的数组形状
        """
        self.to_shape = to_shape
        self.from_shape = None

    def forward(self, x):
        """
        广播的正向传播
        :param x: 待合并求和的值
        """
        self.from_shape = x.shape
        """
        参考：
        import numpy as np
        from numpy import broadcast_to
        x = np.array([[1, 2]])
        y = broadcast_to(x, (4, 2))
        print(y)
        # [[1 2]
        #  [1 2]
        #  [1 2]
        #  [1 2]]
        """
        y = np.broadcast_to(x, self.to_shape)
        return y

    def backward(self, gy):
        """
        广播的反向传播
        :param gy: 导数值
        """
        gx = sum_to(gy, self.from_shape)
        return gx


class MatMul(BaseOp):
    """
    矩阵相乘
    """

    def forward(self, x0, x1):
        """
        矩阵相乘的正向传播
        :param x0: 一个乘数
        :param x1: 另一个乘数
        """
        return np.matmul(x0, x1)

    def backward(self, gy):
        """
        矩阵相乘的反向传播
        :param gy: 导数值
        :return: 矩阵相乘的反向传播的值
        """
        x0, x1 = self.inputs

        # 对x0的梯度: gy @ x1^T
        # 对x1的梯度: x0^T @ gy

        # 处理不同维度的情况
        if x0.ndim == 2 and x1.ndim == 2:
            # 标准2D矩阵乘法
            gx0 = matmul(gy, transpose(x1))
            gx1 = matmul(transpose(x0), gy)
        else:
            # 对于高维情况，只转置最后两个维度
            gx0 = matmul(gy, swap_axes(x1, -1, -2))
            gx1 = matmul(swap_axes(x0, -1, -2), gy)

        return gx0, gx1


class Outer(BaseOp):
    """外积运算"""

    def forward(self, x0, x1):
        # 外积: 如果 x0 形状 (m,), x1 形状 (n,)，结果形状 (m, n)
        return np.outer(x0, x1)

    def backward(self, gy):
        x0, x1 = self.inputs
        # 外积的梯度:
        # 对 x0 的梯度 = gy 与 x1 的点积（沿着 x1 的维度求和）
        # 对 x1 的梯度 = gy 与 x0 的点积（沿着 x0 的维度求和）
        gx0 = matmul(gy, x1)  # 或者sum(gy * x1, axis=1)
        gx1 = matmul(gy.T, x0)  # 或者sum(gy.T * x0, axis=1)
        return gx0, gx1


class Transpose(BaseOp):
    """
    矩阵转置
    """

    def __init__(self, axes=None):
        """
        初始化
        :param axes: 轴
        """
        self.axes = axes

    def forward(self, x):
        """
        矩阵转置的正向传播
        :param x: 所要转置的矩阵
        """
        return np.transpose(x, axes=self.axes)

    def backward(self, gy):
        """
        矩阵转置的反向传播
        :param gy: 导数值
        :return: 矩阵转置的反向传播的值
        """
        if self.axes is None:
            return transpose(gy)
        inv_axes = tuple(np.argsort(self.axes))
        return transpose(gy, inv_axes)


class Reshape(BaseOp):
    """
    重塑形状
    """

    def __init__(self, shape):
        """
        初始化
        :param shape: 所要重塑的形状
        """
        self.shape = shape

    def forward(self, x):
        """
        重塑形状的正向传播
        :param x: 所要转置的矩阵
        """
        y = np.reshape(x, self.shape)
        return y

    def backward(self, gy):
        """
        重塑形状的反向传播
        :param gy: 导数值
        :return: 重塑形状的反向传播的值
        """
        x0_shape = self.inputs[0].shape
        return reshape(gy, x0_shape)


class GetItem(BaseOp):

    def __init__(self, slices):
        self.slices = slices

    def forward(self, x):
        if not isinstance(self.slices, tuple):
            slices_tuple = (self.slices,)
        else:
            slices_tuple = self.slices
        filtered_slices = []
        dim_count = 0
        for s in slices_tuple:
            if dim_count >= x.ndim:
                # 如果已经达到数组维度，跳过后续切片
                break
            if s is None:
                # None会插入新维度，我们跳过它或者根据需求处理
                continue
            filtered_slices.append(s)
            dim_count += 1
        # 如果过滤后切片不足，用slice(None)补齐
        while len(filtered_slices) < x.ndim:
            filtered_slices.append(slice(None))
        # 只取前x.ndim个切片
        filtered_slices = filtered_slices[:x.ndim]
        y = x[tuple(filtered_slices)]
        return y

    def backward(self, gy):
        x = self.inputs[0]
        f = GetItemGrad(self.slices, x.shape)
        return f(gy)


class GetItemGrad(BaseOp):

    def __init__(self, slices, in_shape):
        self.slices = slices
        self.in_shape = in_shape

    def forward(self, gy):
        gx = np.zeros(self.in_shape, dtype=gy.dtype)
        # GPU：xp.scatter_add(gx, self.slices, gy)
        np.add.at(gx, self.slices, gy)
        return gx

    def backward(self, ggx):
        return get_item(ggx, self.slices)


class Clip(BaseOp):
    """
    clip函数
    """

    def __init__(self, x_min, x_max):
        """
        初始化
        :param x_min: 最小值
        :param x_max: 最大值
        """
        self.x_min = x_min
        self.x_max = x_max

    def forward(self, x):
        """
        clip的正向传播
        :param x: 参数x
        :return: clip函数的计算结果
        """
        y = np.clip(x, self.x_min, self.x_max)
        return y

    def backward(self, gy):
        """
        clip的反向传播
        :param gy: 导数值
        :return: clip函数的的反向传播的值
        """
        x = self.inputs[0]
        mask = (x.data >= self.x_min) * (x.data <= self.x_max)
        gx = gy * mask
        return gx


class Max(BaseOp):
    """
    max
    """

    def __init__(self, axis=None, keepdims=False):
        """
        初始化
        :param axis: 参数axis
        :param keepdims: 参数keepdims
        """
        self.axis = axis
        self.keepdims = keepdims

    def forward(self, x):
        """
        max的正向传播
        :param x: 参数x
        :return: max函数的计算结果
        """
        y = x.max(axis=self.axis, keepdims=self.keepdims)
        return y

    def backward(self, gy):
        """
        max的反向传播
        例如：
        [
            [1, 2, 3],
            [2, 2, 3],
            [1, 1, 1]
        ]
        结果为：
        [
            [0 0 1]
            [0 0 1]
            [0 0 0]
        ]
        :param gy: 导数值
        :return: max函数的的反向传播的值
        """
        x = self.inputs[0]
        y = self.outputs[0]()  # 弱引用

        if self.axis is None:
            axis = range(x.ndim)
        elif isinstance(self.axis, int):
            axis = (self.axis,)
        else:
            axis = self.axis
        shape = [s if ax not in axis else 1 for ax, s in enumerate(x.shape)]

        gy = reshape(gy, shape)
        y = reshape(y, shape)
        cond = (x.data == y.data)
        gy = broadcast_to(gy, cond.shape)
        return gy * cond


class Min(Max):
    """
    min
    """

    def forward(self, x):
        """
        min的正向传播
        :param x: 参数x
        :return: min函数的计算结果
        """
        y = x.min(axis=self.axis, keepdims=self.keepdims)
        return y

    """
    min的反向传播
    例如：
    [
        [1, 2, 3],
        [2, 2, 3],
        [1, 1, 1]
    ]
    结果为：
    [
        [1 0 0]
        [0 0 0]
        [1 1 1]
    ]
    """


class Floor(BaseOp):
    """
    向下取整类
    """

    def forward(self, x):
        """
        向下取整的正向传播
        :param x: 参数x
        """
        return np.floor(x)

    def backward(self, gy):
        """
        向下取整的反向传播
        :param gy: 导数值
        """

        """
        注意：这里使用了STE的标准实现，从数学角度看，floor的导数应该是0或未定义，但STE“欺骗”了反向传播
        零梯度（数学正确但可能没用）：
        x = self.inputs[0]
        return np.zeros_like(self.x)
        """
        return gy


class Gather(BaseOp):
    """
    Gather操作类 - 简洁版本
    """

    def __init__(self, axis=0):
        self.axis = axis
        self.x_shape = None
        self.indices_shape = None

    def forward(self, x, indices):
        """
        Gather的正向传播
        """
        self.x_shape = x.shape
        self.indices_shape = indices.shape
        indices = indices.astype(np.int32)

        # 使用numpy.take实现gather，更简洁
        return np.take(x, indices, axis=self.axis)

    def backward(self, gy):
        """
        Gather的反向传播
        """
        x, indices = self.inputs

        indices = indices.astype(np.int32)

        # 初始化输入梯度
        gx = np.zeros_like(x)

        # 使用numpy的add.at进行scatter操作
        # 构建用于scatter的索引
        slices = [slice(None)] * x.ndim
        slices[self.axis] = indices

        # 在对应位置添加梯度
        np.add.at(gx, tuple(slices), gy)

        # 索引的梯度为0
        g_indices = np.zeros_like(indices, dtype=np.float32)

        return gx, g_indices


class SwapAxes(BaseOp):
    """交换轴"""

    def __init__(self, axis1, axis2):
        super().__init__()
        self.axis1 = axis1
        self.axis2 = axis2

    def forward(self, x):
        return np.swapaxes(x, self.axis1, self.axis2)

    def backward(self, gy):
        # 交换轴的梯度就是再交换回来
        return swap_axes(gy, self.axis1, self.axis2)


class Dropout(BaseOp):
    """
    Dropout层
    """

    def __init__(self, dropout_rate=0.1):
        """
        初始化Dropout层
        :param dropout_rate: 丢弃率
        """
        self.dropout_rate = dropout_rate
        self.mask = None
        self.training = True  # 训练模式标志

    def set_training(self, training):
        """设置训练/推理模式"""
        self.training = training

    def forward(self, x):
        """
        Dropout正向传播
        :param x: 输入张量
        :return: 输出张量
        """
        if not self.training or self.dropout_rate == 0:
            return x
        # 生成mask，按照dropout_rate随机置0
        self.mask = np.random.binomial(1, 1 - self.dropout_rate, size=x.shape)
        output = x * self.mask / (1 - self.dropout_rate)  # 缩放保持期望值不变
        return output

    def backward(self, grad):
        """
        Dropout反向传播
        :param grad: 上游梯度
        :return: 下游梯度
        """
        if not self.training or self.dropout_rate == 0:
            return grad
        return grad * self.mask / (1 - self.dropout_rate)
