import numpy as np

from zero.core.layer import Layer
from zero.core.tensor import Parameter
from zero.ops.util_ops import gather, reshape


class NumpyEmbedding(Layer):
    """
    使用numpy实现的嵌入层Embedding
    """

    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        limit = np.sqrt(1.0 / embedding_dim)
        embedding_matrix = np.random.uniform(-limit, limit, (vocab_size, embedding_dim))
        self.embedding_matrix = Parameter(embedding_matrix)  # 使用Parameter包装

    def __call__(self, indices):
        """根据索引获取对应的嵌入向量"""
        if isinstance(indices, (list, tuple)):
            indices = np.array(indices)
        # 处理多维索引（如batch处理）
        if indices.ndim > 1:
            original_shape = indices.shape
            indices = indices.reshape(-1)
            result = gather(self.embedding_matrix, indices)
            new_shape = original_shape + (self.embedding_dim,)
            return reshape(result, new_shape)
        else:
            return gather(self.embedding_matrix, indices)

    def forward(self, indices):
        """与__call__相同，为了与PyTorch接口保持一致"""
        return self.__call__(indices)

    def __getitem__(self, index):
        """支持直接索引访问"""
        return self.embedding_matrix[index]

    def get_weights(self):
        """获取嵌入矩阵"""
        return self.embedding_matrix.data.copy()

    def set_weights(self, weights):
        """设置嵌入矩阵"""
        assert weights.shape == (self.vocab_size, self.embedding_dim)
        self.embedding_matrix.data = weights.copy()
