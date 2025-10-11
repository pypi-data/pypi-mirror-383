from .base_op import BaseOp


def gt(x0, x1):
    return Gt()(x0, x1)


def ge(x0, x1):
    return Ge()(x0, x1)


def lt(x0, x1):
    return Lt()(x0, x1)


def le(x0, x1):
    return Le()(x0, x1)


class Gt(BaseOp):
    """
    大于类
    """

    def forward(self, x0, x1):
        """
        大于的正向传播
        :param x0: 需要比较的一个值
        :param x1: 需要比较的另一个值
        """
        return x0 > x1

    def backward(self, gy):
        """
        大于的反向传播
        :param gy: 导数值
        """
        gx0, gx1 = 0, 0
        return gx0, gx1


class Ge(BaseOp):
    """
    大于等于类
    """

    def forward(self, x0, x1):
        """
        大于等于的正向传播
        :param x0: 需要比较的一个值
        :param x1: 需要比较的另一个值
        """
        return x0 >= x1

    def backward(self, gy):
        """
        大于等于的反向传播
        :param gy: 导数值
        """
        gx0, gx1 = 0, 0
        return gx0, gx1


class Lt(BaseOp):
    """
    小于类
    """

    def forward(self, x0, x1):
        """
        小于的正向传播
        :param x0: 需要比较的一个值
        :param x1: 需要比较的另一个值
        """
        return x0 < x1

    def backward(self, gy):
        """
        小于的反向传播
        :param gy: 导数值
        """
        gx0, gx1 = 0, 0
        return gx0, gx1


class Le(BaseOp):
    """
    小于等于类
    """

    def forward(self, x0, x1):
        """
        小于等于的正向传播
        :param x0: 需要比较的一个值
        :param x1: 需要比较的另一个值
        """
        return x0 <= x1

    def backward(self, gy):
        """
        小于等于的反向传播
        :param gy: 导数值
        """
        gx0, gx1 = 0, 0
        return gx0, gx1
