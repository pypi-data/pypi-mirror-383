from .math_ops import add, sub, mul, div, power, neg, mod
from .util_ops import sum, sum_to, broadcast_to, average, matmul, outer, transpose, swap_axes, reshape, get_item
from .util_ops import get_item_grad, clip, max, min, floor, accuracy, transformer_accuracy, dropout, gather
from .linear_ops import linear
from .tri_ops import sin, cos, tan, tanh
from .exp_log_ops import exp, lg, ln
from .act_ops import step, sigmoid, relu, gelu, leaky_relu
from .norm_ops import softmax, log_softmax, layer_norm, batch_norm
from .loss_ops import mean_squared_error, softmax_cross_entropy, sigmoid_cross_entropy, binary_cross_entropy, categorical_cross_entropy
from .compare_ops import gt, ge, lt, le

"""
基于numpy，关于矩阵的乘法，这里简单说明下，假设有两个矩阵A和B
1、A*B                       =>逐元素相乘，又称之为阿达马积
2、np.dot(A,B)/A.dot(B)      =>矩阵相乘，二维矩阵处理，一般兼容旧代码
3、np.matmul(A,B)            =>多维矩阵处理（优先）
4、A@B                       =>Python3.5+推荐使用
"""

__all__ = [
    # ------------------------------ 数学操作 ------------------------------
    'add',                          # 加（+）
    'sub',                          # 减（-）
    'mul',                          # 乘（*）
    'div',                          # 除（/）
    'power',                        # 幂（**）
    'neg',                          # 负数（-）
    'mod',                          # 取模（%）
    # ------------------------------ 工具操作 ------------------------------
    'sum',                          # 求和
    'sum_to',                       # 合并求和
    'broadcast_to',                 # 广播
    'average',                      # 平均数
    'matmul',                       # 矩阵乘法（matmul或者@）
    'outer',                        # 外积
    'transpose',                    # 矩阵转置（比.T更加灵活，都是视图操作，不改变底层数据，只是改变了数据的索引方式）
    'swap_axes',                     # 轴交换
    'reshape',                      # 矩阵重构（重塑矩阵形态）
    'get_item',                     # 切片
    'get_item_grad',                # 切片（梯度）
    'clip',                         # 上下界限定
    'max',                          # 最大值
    'min',                          # 最小值
    'floor',                        # 向下取整（使用STE的标准实现）
    'accuracy',                     # 准确度（一般情况下适用）
    'transformer_accuracy',         # 准确度（Transformer专用）
    'dropout',                      # 随机丢弃
    'gather',                       # 从输入张量中按照索引收集元素
    # ------------------------------ 线性操作 ------------------------------
    'linear',                       # 线性变换
    # ------------------------------ 三角函数操作 ------------------------------
    'sin',                          # 正弦
    'cos',                          # 余弦
    'tan',                          # 正切
    'tanh',                         # 双曲正切
    # ------------------------------ 指数对数操作 ------------------------------
    'exp',                          # e为底的指数
    'lg',                           # 10为底的对数
    'ln',                           # e为底的对数
    # ------------------------------ 激活函数操作 ------------------------------
    'step',                         # step函数
    'sigmoid',                      # sigmoid函数
    'relu',                         # relu函数
    'gelu',                         # gelu函数
    'leaky_relu',                   # leaky_relu函数
    # ------------------------------ 归一化函数操作 ------------------------------
    'softmax',                      # softmax函数
    'log_softmax',                  # log_softmax函数
    'layer_norm',                   # layer_norm函数
    'batch_norm',                   # batch_norm函数
    # ------------------------------ 损失函数操作 ------------------------------
    'mean_squared_error',           # 均方误差
    'softmax_cross_entropy',        # 交叉熵损失
    'sigmoid_cross_entropy',        # 交叉熵损失
    'binary_cross_entropy',         # 二元交叉熵
    'categorical_cross_entropy',    # 多分类交叉熵
    # ------------------------------ 比较操作 ------------------------------
    'gt',                           # 大于
    'ge',                           # 大于等于
    'lt',                           # 小于
    'le',                           # 小于等于
]
