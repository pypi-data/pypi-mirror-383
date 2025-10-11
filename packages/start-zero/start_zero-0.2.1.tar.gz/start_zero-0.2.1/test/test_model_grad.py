import numpy as np

from zero.core.layer import Layer
from zero.core.model import Model
from zero.core.tensor import Parameter, Tensor
from zero.ops import mean_squared_error, accuracy
from zero.optimizers.sgd import Adam, SGD


class TestLayer(Layer):

    def __init__(self):
        super().__init__()
        self.W = Parameter(np.array([[1.0, 2.0], [3.0, 4.0]]))

    def forward(self, x):
        return x + self.W


class TestModel(Model):

    def __init__(self):
        super().__init__()
        self.layer = TestLayer()

    def forward(self, x):
        return self.layer(x)


def train():
    lr = 0.001
    epoch = 1000
    model = TestModel()
    optimizer = SGD(lr).setup(model)
    x = Tensor(np.array([[4.0, 3.0], [2.0, 1.0]]))
    t = Tensor(np.array([[5.0, 6.0], [7.0, 8.0]]))
    for i in range(epoch):
        x_grad = model(x)
        loss = mean_squared_error(x_grad, t)
        model.clear_tensors()
        loss.backward()
        optimizer.update()
        if i % 10 == 0:
            accuracy_out = round(accuracy(x_grad, t) * 100, 2)
            print("准确率：" + str(accuracy_out) + "%，损失值：" + str(loss))


train()
