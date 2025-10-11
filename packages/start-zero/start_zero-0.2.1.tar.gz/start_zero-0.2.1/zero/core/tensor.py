import numpy as np
from zero.ds.queue import PriorityQueue


class Tensor:
    """
    张量（Tensor）是一个多维数组，它是标量、向量、矩阵的高维扩展，是一个数据容器，张量是矩阵向任意维度的推广
    """

    def __add__(self, other):
        from zero.ops import add
        return add(self, other)

    def __radd__(self, other):
        from zero.ops import add
        return add(self, other)

    def __sub__(self, other):
        from zero.ops import sub
        return sub(self, other)

    def __rsub__(self, other):
        from zero.ops import sub
        return sub(self, other)

    def __mul__(self, other):
        from zero.ops import mul
        return mul(self, other)

    def __rmul__(self, other):
        from zero.ops import mul
        return mul(self, other)

    def __truediv__(self, other):
        from zero.ops import div
        return div(self, other)

    def __rtruediv__(self, other):
        from zero.ops import div
        return div(self, other)

    def __pow__(self, other):
        from zero.ops import power
        return power(self, other)

    def __neg__(self):
        from zero.ops import neg
        return neg(self)

    def __mod__(self, other):
        from zero.ops import mod
        return mod(self, other)

    def __rmod__(self, other):
        from zero.ops import mod
        return mod(self, other)

    def __matmul__(self, other):
        from zero.ops import matmul
        return matmul(self, other)

    def __rmatmul__(self, other):
        from zero.ops import matmul
        return matmul(self, other)

    def __gt__(self, other):
        from zero.ops import gt
        return gt(self, other)

    def __ge__(self, other):
        from zero.ops import ge
        return ge(self, other)

    def __lt__(self, other):
        from zero.ops import lt
        return lt(self, other)

    def __le__(self, other):
        from zero.ops import le
        return le(self, other)

    def __len__(self):
        return len(self.data)

    def __repr__(self) -> str:
        return 'Tensor(None)' if self.data is None else 'Tensor(' + str(self.data) + ')'

    def __getitem__(self, indices):
        from zero.ops.util_ops import get_item
        return get_item(self, indices)

    def __array__(self, dtype=None, copy=None):
        """
        这里主要解决的是盒子嵌套问题及性能
        所谓盒子嵌套问题是指：
        比如有一个变量如x，输出类型为<class 'numpy.ndarray'>，乍一看是numpy类型，
        但是假设这个矩阵形态是(3,2)，然后输出会发现每个元素其实都是Tensor类型
        """
        """
        if dtype is None:
            return self.data
        else:
            return self.data.astype(dtype)
        """
        if dtype is None:
            if copy:
                return self.data.copy()
            else:
                return self.data
        else:
            if copy:
                return self.data.astype(dtype, copy=True)
            else:
                return self.data.astype(dtype, copy=False)

    @property
    def shape(self):
        """ 数据的形态，如一个3行4列的二维矩阵，它的形态是：(3, 4) """
        return self.data.shape

    @property
    def size(self):
        """
        矩阵总元素个数，如A=(3,2,4)，则size=3*2*4=24
        """
        return self.data.size

    @property
    def ndim(self):
        """
        维度，如(3,8,5)，则维度为3
        """
        return self.data.ndim

    @property
    def dtype(self):
        """
        数据类型，如np.random.randn(3, 2, 1)的数据类型为：float64
        """
        return self.data.dtype

    @DeprecationWarning
    @property
    def T(self):
        from zero.ops.util_ops import transpose
        return transpose(self)

    @DeprecationWarning
    def transpose(self, *axes):
        if not isinstance(axes, tuple):
            axes = (axes,)
        from zero.ops.util_ops import transpose
        return transpose(self, axes)

    def reshape(self, *shape):
        if not isinstance(shape, tuple):
            shape = (shape,)
        from zero.ops.util_ops import reshape
        return reshape(self, shape)

    def astype(self, dtype, order='K', casting='unsafe', copy=True):
        new_data = self.data.astype(
            dtype=dtype,
            order=order,
            casting=casting,
            copy=copy
        )
        new_tensor = Tensor(new_data)
        return new_tensor

    def clear_tensor(self, clear_graph=True, clear_grad=False):
        """
        def clear_tensor(self, clear_graph=True, clear_grad=False):
            # clear_graph: 是否清理计算图（creator, generation）
            # clear_grad: 是否清理梯度（设置为None）
            if clear_graph:
                self.creator = None
                self.generation = 0
            if clear_grad:
                self.grad = None
            elif self.grad is not None:
                self.grad.data.fill(0)
        """
        self.grad = None
        self.creator = None
        self.generation = 0

    def unchain(self):
        self.creator = None

    def unchain_backward(self):
        if self.creator is not None:
            funcs = [self.creator]
            while funcs:
                f = funcs.pop()
                for x in f.inputs:
                    if x.creator is not None:
                        funcs.append(x.creator)
                        x.unchain()

    def __init__(self, data, name=None):
        self.data = data  # 正向传播时的变量值
        self.grad = None  # 反向传播时的导数值
        self.creator = None  # 与变量关联的函数，即f(x)与x关联的函数f
        self.generation = 0  # 表示函数属于哪一代，主要用于反向传播时确定复杂计算图的计算顺序
        self.name = name  # 张量名称

    def backward(self):
        """
        反向传播的主要目的是为了更新梯度
        """
        if self.grad is None:
            self.grad = Tensor(np.ones_like(self.data))

        priorityQueue = PriorityQueue()
        priorityQueue.push(self.creator, self.generation)
        visited_outputs = set()

        while priorityQueue.len() != 0:
            pop_creator = priorityQueue.pop()
            xs, ys = pop_creator.inputs, pop_creator.outputs

            # 安全获取梯度
            gys = []
            for y_ref in ys:
                y = y_ref()
                if y is not None:
                    gys.append(y.grad)
                    visited_outputs.add(y)
                else:
                    gys.append(None)

            # 检查梯度是否完整
            if not any(g is None for g in gys):
                gxs = pop_creator.backward(*gys)
                if not isinstance(gxs, tuple):
                    gxs = (gxs,)

                for x, gx in zip(xs, gxs):
                    if x.grad is None:
                        x.grad = gx
                    else:
                        x.grad += gx  # 使用原地操作累积梯度

                    if x.creator is not None:
                        priorityQueue.push(x.creator, x.generation)

        # 统一清理中间梯度
        for y in visited_outputs:
            if y != self:  # 不清理最终输出的梯度
                y.grad = None


class Parameter(Tensor):
    """
    Parameter参数类与Tensor拥有相同的能力，只是对象名称不一样
    """
    pass


def is_tensor(obj):
    """
    判断对象是不是Tensor对象
    :param obj: 要判断的对象
    :return: True：是Tensor对象；False：不是Tensor对象
    """
    return isinstance(obj, Tensor)


def is_parameter(obj):
    """
    判断对象是不是Parameter对象
    :param obj: 要判断的对象
    :return: True：是Parameter对象；False：不是Parameter对象
    """
    return isinstance(obj, Parameter)


def to_tensor(obj):
    """
    将对象转化为Tensor对象
    :param obj: 要转化的对象
    :return: 转化后的对象
    """

    # 1.判断是否是Tensor对象
    """
    绝对不能写为类似如下形式：
    if is_tensor(obj):
        obj = obj.data
    因为这样重新赋值会破坏原obj的属性
    """
    if not is_tensor(obj):
        obj = Tensor(obj)
    # 2.使用np.array转化
    obj.data = np.array(obj.data)
    # 3.如果ndim等于0，则将其转为一维数组
    if obj.data.ndim == 0:
        obj.data = obj.data.reshape(1)
    return obj


def clear_tensors(*tensors):
    for tensor in tensors:
        tensor.clear_tensor()
