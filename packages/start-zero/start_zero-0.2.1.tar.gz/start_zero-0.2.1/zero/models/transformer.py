import numpy as np

from zero.core.model import Model
from zero.core.tensor import Parameter
from zero.layers.ted import TransformerEncodeLayer, TransformerDecodeLayer
from zero.layers.ne import NumpyEmbedding
from zero.ops.norm_ops import LayerNorm
from zero.ops.util_ops import Dropout, matmul, reshape
from zero.ops.math_ops import power
from zero.utils.math import xavier_uniform
# from zero.utils.perf import timeit


class TransformerV1(Model):
    """
    Transformer原始模型
    """

    def __init__(self, src_vocab_size, tgt_vocab_size, d_model, num_layers, num_heads, hidden_size, dropout_rate=0.1, max_seq_len=100):
        """
        初始化方法
        :param src_vocab_size: 源语言词汇表大小
        :param tgt_vocab_size: 目标语言词汇表大小
        :param d_model: 每个词（或字符或token）被表示成的向量的长度
        :param num_layers: 堆叠层数（原论文《Attention Is All You Need》使用6层（4-8层为资源有限时的合理选择））
        :param num_heads: 多头数
        :param hidden_size: 前馈网络的隐藏层维度
        :param dropout_rate: 丢弃率
        :param max_seq_len: 最大序列长度（整个对话上下文的最大容量）
        """
        assert d_model % num_heads == 0, f"d_model({d_model})必须能被num_heads({num_heads})整除"
        assert 0 <= dropout_rate < 1, "dropout_rate必须在[0, 1)范围内"
        assert num_layers > 0, "num_layers必须大于0"
        assert max_seq_len > 0, f"max_seq_len必须大于0，当前为{max_seq_len}"
        super().__init__()
        self.vocab_size = src_vocab_size
        self.tgt_vocab_size = tgt_vocab_size
        self.d_model = d_model
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.hidden_size = hidden_size
        self.dropout_rate = dropout_rate

        self.src_embedding = NumpyEmbedding(src_vocab_size, d_model)
        self.tgt_embedding = NumpyEmbedding(tgt_vocab_size, d_model)

        # 位置编码
        pe_array = create_positional_encoding(max_seq_len, d_model)
        self.positional_encoding = Parameter(pe_array)

        # 添加嵌入dropout
        self.embed_dropout = Dropout(dropout_rate) if dropout_rate > 0 else None

        # 编码器层
        for i in range(num_layers):
            layer = TransformerEncodeLayer(d_model, hidden_size, num_heads, dropout_rate)
            self.__setattr__(f"encoder_layers_{i}", layer)

        # 解码器层
        for i in range(num_layers):
            layer = TransformerDecodeLayer(d_model, hidden_size, num_heads, dropout_rate)
            self.__setattr__(f"decoder_layers_{i}", layer)

        # 输出层归一化
        self.encoder_norm = LayerNorm(d_model)
        self.decoder_norm = LayerNorm(d_model)

        # 输出线性层（将d_model映射到目标词汇表大小）
        self.output_projection = Parameter(xavier_uniform((d_model, tgt_vocab_size), gain=np.sqrt(1.0)))
        self.output_bias = Parameter(np.zeros(tgt_vocab_size))

    def encode(self, src_tokens, src_mask=None):
        batch_size, src_seq_len = src_tokens.shape
        # 源语言词嵌入并缩放
        x = self.src_embedding(src_tokens) * power(self.d_model, 0.5)
        # 添加位置编码
        pe = self.positional_encoding[:src_seq_len, :]  # (src_seq_len, d_model)
        pe = reshape(pe, (1, src_seq_len, self.d_model))  # (1, src_seq_len, d_model)
        x = x + pe  # 自动广播到(batch_size, src_seq_len, d_model)
        # 应用嵌入dropout
        x = self.embed_dropout(x)
        # 编码器层
        for i in range(self.num_layers):
            layer = self.__getattribute__(f"encoder_layers_{i}")
            x = layer(x, src_mask)
        encoder_output = self.encoder_norm(x)
        return encoder_output

    def decode(self, tgt_tokens, encoder_output, encoder_mask=None, tgt_mask=None):
        batch_size, tgt_seq_len = tgt_tokens.shape
        # 目标语言词嵌入并缩放
        x = self.tgt_embedding(tgt_tokens) * power(self.d_model, 0.5)
        # 添加位置编码
        pe = self.positional_encoding[:tgt_seq_len, :]  # (tgt_seq_len, d_model)
        pe = reshape(pe, (1, tgt_seq_len, self.d_model))  # (1, tgt_seq_len, d_model)
        x = x + pe  # 自动广播到(batch_size, tgt_seq_len, d_model)
        # 应用嵌入dropout
        x = self.embed_dropout(x)
        # 解码器层
        for i in range(self.num_layers):
            layer = self.__getattribute__(f"decoder_layers_{i}")
            x = layer(x, encoder_output, tgt_mask, encoder_mask)
        decoder_output = self.decoder_norm(x)
        return decoder_output

    # @timeit
    def forward(self, src_tokens, tgt_tokens, src_mask=None, tgt_mask=None):
        # 编码器
        encoder_output = self.encode(src_tokens, src_mask)
        # 解码器
        decoder_output = self.decode(tgt_tokens, encoder_output, src_mask, tgt_mask)
        # 输出投影到目标词汇表
        logits = matmul(decoder_output, self.output_projection) + self.output_bias
        return logits

    # @timeit
    def generate(self, src_tokens, src_mask=None, max_length=50, start_token=1, end_token=2):
        batch_size = src_tokens.shape[0]
        # 编码源序列
        encoder_output = self.encode(src_tokens, src_mask)
        # 初始化目标序列（开始符号）
        tgt_tokens = np.full((batch_size, 1), start_token, dtype=np.int32)
        for step in range(max_length):
            # 创建目标序列的因果掩码
            tgt_seq_len = tgt_tokens.shape[1]
            tgt_mask = create_causal_mask(tgt_seq_len)
            # 解码
            decoder_output = self.decode(tgt_tokens, encoder_output, src_mask, tgt_mask)
            logits = matmul(decoder_output[:, -1, :], self.output_projection) + self.output_bias
            # 贪婪选择下一个token
            next_tokens = np.argmax(logits, axis=-1).reshape(batch_size, 1)
            # 添加到目标序列
            tgt_tokens = np.concatenate([tgt_tokens, next_tokens], axis=1)
            # 检查是否所有序列都生成了结束符号
            if np.all(next_tokens == end_token):
                break
            if step % 10 == 0:
                import gc
                gc.collect()
        return tgt_tokens


def create_positional_encoding(max_len, d_model):
    position = np.arange(max_len)[:, np.newaxis]
    div_term = np.exp(np.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))
    pe = np.zeros((max_len, d_model))
    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term)
    return pe


def create_causal_mask(seq_len):
    mask = np.triu(np.ones((seq_len, seq_len)) * -1e9, k=1)
    return mask
