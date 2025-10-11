import numpy as np

from zero.core.layer import Layer
from zero.core.tensor import Parameter
from zero.ops.norm_ops import softmax, LayerNorm
from zero.ops.act_ops import gelu
from zero.ops.math_ops import power
from zero.ops.util_ops import dropout, matmul, reshape, transpose, broadcast_to
from zero.utils.math import xavier_uniform


class MultiHeadAttention(Layer):
    def __init__(self, d_model, num_heads, dropout_rate=0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        assert d_model % num_heads == 0, "d_model必须能被num_heads整除"

        # 线性变换权重
        qkv_gain = 1.0 / np.sqrt(2.0)  # 减小QKV的初始化规模
        self.w_q = Parameter(xavier_uniform((d_model, d_model), gain=qkv_gain))
        self.w_k = Parameter(xavier_uniform((d_model, d_model), gain=qkv_gain))
        self.w_v = Parameter(xavier_uniform((d_model, d_model), gain=qkv_gain))

        self.w_o = Parameter(xavier_uniform((d_model, d_model), gain=1.0))

        self.dropout_rate = dropout_rate

    def forward(self, q, k=None, v=None, mask=None):
        if k is None:
            k = q
        if v is None:
            v = q
        batch_size, seq_len_q, d_model = q.shape
        _, seq_len_k, _ = k.shape
        _, seq_len_v, _ = v.shape
        # 线性变换
        Q = matmul(q, self.w_q)
        K = matmul(k, self.w_k)
        V = matmul(v, self.w_v)
        # 重塑为多头
        Q = reshape(Q, (batch_size, seq_len_q, self.num_heads, self.head_dim))
        K = reshape(K, (batch_size, seq_len_k, self.num_heads, self.head_dim))
        V = reshape(V, (batch_size, seq_len_v, self.num_heads, self.head_dim))
        Q = transpose(Q, (0, 2, 1, 3))
        K = transpose(K, (0, 2, 1, 3))
        V = transpose(V, (0, 2, 1, 3))
        # 计算注意力分数
        attention_scores = matmul(Q, transpose(K, (0, 1, 3, 2))) / power(self.head_dim, 0.5)
        # 应用mask（如果有）
        if mask is not None:
            if mask.ndim == 2:
                # 2D mask: (seq_len_q, seq_len_k) -> 扩展为 (batch_size, num_heads, seq_len_q, seq_len_k)
                mask = mask[np.newaxis, np.newaxis, :, :]
            elif mask.ndim == 3:
                # 3D mask: (batch_size, seq_len_q, seq_len_k) -> 扩展为 (batch_size, num_heads, seq_len_q, seq_len_k)
                mask = mask[:, np.newaxis, :, :]
            elif mask.ndim == 4:
                # 4D mask: (batch_size, num_heads, seq_len_q, seq_len_k) - 已经是正确形状
                pass
            else:
                raise ValueError(f"不支持的mask维度: {mask.ndim}")
            # 将mask广播到与attention_scores相同的形状
            mask = broadcast_to(mask, attention_scores.shape)
            attention_scores = attention_scores + mask * -1e9
        attention_weights = softmax(attention_scores, axis=-1)
        # 应用dropout到注意力权重
        if self.dropout_rate > 0:
            attention_weights = dropout(attention_weights, self.dropout_rate)
        # 应用注意力权重到V
        attention_output = matmul(attention_weights, V)
        # 重塑回原始形状
        attention_output = transpose(attention_output, (0, 2, 1, 3))  # (batch_size, seq_len_q, num_heads, head_dim)
        attention_output = reshape(attention_output, (batch_size, seq_len_q, d_model))  # 合并多头
        # 输出线性变换
        output = matmul(attention_output, self.w_o)
        # 输出dropout
        if self.dropout_rate > 0:
            output = dropout(output, self.dropout_rate)
        return output


class TransformerEncodeLayer(Layer):

    def __init__(self, d_model, hidden_size, num_heads, dropout_rate=0.1):
        super().__init__()
        self.d_model = d_model
        self.hidden_size = hidden_size if hidden_size > d_model else d_model * 4  # 前馈网络隐藏层通常为d_model的4倍
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate

        # 层归一化（Pre-Norm）
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)

        # 多头注意力
        self.self_attention = MultiHeadAttention(d_model, num_heads, dropout_rate)
        # 前馈网络
        w1_std = np.sqrt(2.0 / (d_model + hidden_size))
        self.w1 = Parameter(np.random.normal(0, w1_std, (d_model, hidden_size)))
        self.b1 = Parameter(np.zeros(hidden_size))
        w2_std = 1.0 / np.sqrt(hidden_size)  # 防止输出过大
        self.w2 = Parameter(np.random.normal(0, w2_std, (hidden_size, d_model)))
        self.b2 = Parameter(np.zeros(d_model))
        # 层归一化（Post-Norm）
        # self.norm1 = lambda x: layer_norm(x)
        # self.norm2 = lambda x: layer_norm(x)

    def forward(self, x, mask=None):
        """
        # Post-Norm
        # 第一子层：多头自注意力 + 残差连接 + 层归一化
        attention_output = self.self_attention(x)
        x = self.norm1(x + attention_output)  # 残差连接 + 层归一化
        # 第二子层：前馈网络 + 残差连接 + 层归一化
        ffn_output = np.matmul(x, self.w1) + self.b1
        ffn_output = gelu(ffn_output)
        ffn_output = np.matmul(ffn_output, self.w2) + self.b2
        output = self.norm2(x + ffn_output)  # 残差连接 + 层归一化
        return output
        """
        # Pre-Norm
        # 第一子层：层归一化 + 多头自注意力 + 残差连接 + dropout
        norm_x = self.norm1(x)
        attention_output = self.self_attention(norm_x, norm_x, norm_x, mask)
        x = x + attention_output  # 残差连接
        if self.dropout_rate > 0:
            x = dropout(x, self.dropout_rate)
        # 第二子层：层归一化 + 前馈网络 + 残差连接 + dropout
        norm_x = self.norm2(x)
        ffn_output = matmul(norm_x, self.w1) + self.b1
        ffn_output = gelu(ffn_output)
        ffn_output = matmul(ffn_output, self.w2) + self.b2
        output = x + ffn_output  # 残差连接
        if self.dropout_rate > 0:
            output = dropout(output, self.dropout_rate)
        return output


class TransformerDecodeLayer(Layer):
    def __init__(self, d_model, hidden_size, num_heads, dropout_rate=0.1):
        super().__init__()
        self.d_model = d_model
        self.hidden_size = hidden_size if hidden_size > d_model else d_model * 4
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate

        # 层归一化（Pre-Norm）
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.norm3 = LayerNorm(d_model)

        # 掩码多头自注意力（第一个注意力层）
        self.masked_self_attention = MultiHeadAttention(d_model, num_heads, dropout_rate)

        # 编码器-解码器注意力（第二个注意力层）
        self.encoder_decoder_attention = MultiHeadAttention(d_model, num_heads, dropout_rate)

        # 前馈网络
        w1_std = np.sqrt(2.0 / (d_model + hidden_size))
        self.w1 = Parameter(np.random.normal(0, w1_std, (d_model, hidden_size)))
        self.b1 = Parameter(np.zeros(hidden_size))
        w2_std = 1.0 / np.sqrt(hidden_size)
        self.w2 = Parameter(np.random.normal(0, w2_std, (hidden_size, d_model)))
        self.b2 = Parameter(np.zeros(d_model))

    def forward(self, x, encoder_output, self_attention_mask=None, encoder_attention_mask=None):
        """
        x: 解码器输入 (batch_size, tgt_seq_len, d_model)
        encoder_output: 编码器输出 (batch_size, src_seq_len, d_model)
        self_attention_mask: 自注意力掩码（用于防止看到未来信息）
        encoder_attention_mask: 编码器-解码器注意力掩码
        """
        # 第一子层：掩码多头自注意力 + 残差连接
        norm_x = self.norm1(x)
        self_attention_output = self.masked_self_attention(norm_x, norm_x, norm_x, self_attention_mask)
        x = x + self_attention_output  # 残差连接
        if self.dropout_rate > 0:
            x = dropout(x, self.dropout_rate)
        # 第二子层：编码器-解码器注意力 + 残差连接
        norm_x = self.norm2(x)
        encoder_attention_output = self.encoder_decoder_attention(norm_x, encoder_output, encoder_output, encoder_attention_mask)
        x = x + encoder_attention_output  # 残差连接
        if self.dropout_rate > 0:
            x = dropout(x, self.dropout_rate)
        # 第三子层：前馈网络 + 残差连接
        norm_x = self.norm3(x)
        ffn_output = matmul(norm_x, self.w1) + self.b1
        ffn_output = gelu(ffn_output)
        ffn_output = matmul(ffn_output, self.w2) + self.b2
        output = x + ffn_output  # 残差连接
        if self.dropout_rate > 0:
            output = dropout(output, self.dropout_rate)
        return output
