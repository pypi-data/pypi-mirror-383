import weakref

from zero.core.tensor import Tensor, to_tensor


class BaseOp:
    """
    所有算子的父类（基类）
    """

    def __call__(self, *inputs):
        self.inputs = [to_tensor(each) for each in inputs]  # 函数的输入值（对输入值进行类型转换处理）
        xs = [each.data for each in self.inputs]
        ys = self.forward(*xs)  # 前向传播的计算值
        ys = (ys, ) if not isinstance(ys, tuple) else ys  # 例如[1,2,3]+[1,2,3]=[2,4,6]，[2,4,6]应将其当做一个值而不是一个列表包含三个值
        outputs = [Tensor(each) for each in ys]  # 前向传播的计算值需要再将其封装为Tensor对象

        # if Config.ENABLE_BACKPROP:  # 只有需要进行反向传播时才会进行处理
        generation = max([each.generation for each in self.inputs])
        for each in outputs:
            each.creator = self
            each.generation = generation + 1
        """
        关于弱引用：
        import weakref
        x = {1, 2, 3, 4}
        y = weakref.ref(x)
        print(x, type(x), y(), type(y))  # {1, 2, 3, 4} <class 'set'> {1, 2, 3, 4} <class 'weakref.ReferenceType'>
        x = {5, 6, 7, 8}
        print(x, type(x), y(), type(y))  # {8, 5, 6, 7} <class 'set'> None <class 'weakref.ReferenceType'>
        当x被新值覆盖后，y对x的引用就不存在了，如果不用弱引用：
        x = {1, 2, 3, 4}
        y = x
        print(x, type(x), y, type(y))  # {1, 2, 3, 4} <class 'set'> {1, 2, 3, 4} <class 'set'>
        x = {5, 6, 7, 8}
        print(x, type(x), y, type(y))  # {8, 5, 6, 7} <class 'set'> {1, 2, 3, 4} <class 'set'>
        当x被新值覆盖后，y对x的引用依然存在
        再来看个例子：
        import weakref
        class A:
            def __init__(self, x):
                self.x = x
        a = A(10)
        print(a)  # <__main__.A object at 0x0000022389614C10>
        b = weakref.ref(a)
        print(b, b().x)  # <weakref at 0x0000022389932160; to 'A' at 0x0000022389614C10> 10
        b().x = None
        print(a, a.x, b, b().x)  # <__main__.A object at 0x0000022389614C10> None <weakref at 0x0000022389932160; to 'A' at 0x0000022389614C10> None
        """
        self.outputs = [weakref.ref(output) for output in outputs]  # 保存输出信息（弱引用）

        # print('输入：', self.inputs, '参与运算的函数名称：', self.__class__.__name__, '输出：', outputs)
        return outputs if len(outputs) > 1 else outputs[0]  # 函数的输出值

    def forward(self, *xs):
        """
        正向传播
        """
        raise NotImplementedError()

    def backward(self, *gys):
        """
        反向传播
        """
        raise NotImplementedError()
