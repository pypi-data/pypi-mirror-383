from zero.core.model import Model
from zero.ops.act_ops import sigmoid
from zero.layers.linear import LinearLayer

LINEAR_LAYER_PREFIX = 'l'  # 前缀


class MLP(Model):
    """
    多层感知器
    """

    def __init__(self, out_sizes: tuple, activation=sigmoid):
        super().__init__()
        self.activation = activation
        self.layers = []

        for (index, item) in enumerate(out_sizes):
            layer = LinearLayer(item)
            setattr(self, LINEAR_LAYER_PREFIX + str(index), layer)
            self.layers.append(layer)

    def forward(self, x):
        # 当x是一维度数组时（如(784, )）将其转为二维数组（如(1, 784)）
        if x.ndim == 1:
            x = x.reshape((1, -1))
        # 假设数组为：[1, 2, 3, 4, 5]，这里去除最后一个外的所有，即：[1, 2, 3, 4]
        for ls in self.layers[:-1]:
            linear = ls(x)  # 仿射
            x = self.activation(linear)  # 激活
        # 返回最后一个，即：[5]
        return self.layers[-1](x)  # 仿射
