import numpy as np

from zero.core.tensor import Tensor
from zero.models.transformer import TransformerV1
from zero.ops.loss_ops import categorical_cross_entropy
from zero.ops.util_ops import transformer_accuracy
from zero.optimizers.sgd import Adam
from zero.utils.vocab import build_vocab, load_text_data, prepare_training_data, create_sequences

""" ############################## 训练数据 ############################## """
# 固定问答对
qa_pairs = [
    # 数学问题
    ("1+1=?", "2"), ("2+2=?", "4"), ("3+5=?", "8"), ("10-3=?", "7"),
    ("6*7=?", "42"), ("100*2是多少？", "200"), ("81/9=?", "9"), ("100/4=?", "25"),
    ("2的平方是多少？", "4"), ("3的立方是多少？", "27"), ("根号4等于几？", "2"),
    # 常识问题
    ("中国的首都是？", "北京"), ("中国的国旗颜色？", "红色"),
    ("水的化学式是？", "H2O"), ("太阳系的行星数量？", "8"),
    ("Python是什么？", "编程语言"), ("最大的海洋？", "太平洋"),
    # 增加更多变体
    ("一加一等于几？", "2"), ("壹加壹等于多少？", "2"),
    ("100乘以2等于多少？", "200"), ("一百乘二得几？", "200"),
]
# 自由文本
free_texts = [
    "1+1=2",
    "1加1等于2",
    "当我们问1+1等于几时或者1+1=几时，我们一般会回答是2",
    "对于1+1等于几，也有人会直接写为：1+1=?",
    *load_text_data(['test_train_data.txt'])
]
# 文件加载的文本
# free_texts.extend(load_text_data(['test_train_data.txt']))
# 准备训练数据
train_inputs, train_outputs = prepare_training_data(free_texts, qa_pairs)
# 构建词汇表
src_vocab = build_vocab(train_inputs)
tgt_vocab = build_vocab(train_outputs)
"""
reverse_vocab = {v: k for k, v in src_vocab_size.items()}
tgt_vocab_size = build_vocab(train_outputs, qa_pairs)
"""
# 创建序列
src_sequences, tgt_sequences = create_sequences(train_inputs, train_outputs, src_vocab, tgt_vocab)
# 转换为Tensor
inputs_sequences = Tensor(src_sequences)
outputs_sequences = Tensor(tgt_sequences)

print(f"训练样本数量: {len(train_inputs)}")
print(f"输入序列形状: {src_sequences.shape}")
print(f"输出序列形状: {tgt_sequences.shape}")
print(f"源词汇表大小: {len(src_vocab)}")
print(f"目标词汇表大小: {len(tgt_vocab)}")


def get_batch(batch_size, src_data, tgt_data):
    """获取一个批量的数据"""
    if batch_size > len(src_data):
        batch_size = len(src_data)
    indices = np.random.choice(len(src_data), batch_size, replace=False)
    return Tensor(src_data[indices]), Tensor(tgt_data[indices])


def generate_src_mask(src):
    src_np = np.array(src.data)
    mask = (src_np != 0).astype(np.float32)
    mask = mask[:, np.newaxis, np.newaxis, :]
    return Tensor(mask)


def generate_tgt_mask(tgt):
    tgt_np = tgt.data
    batch_size, seq_len = tgt_np.shape
    # 创建因果掩码
    causal_mask = np.triu(np.ones((seq_len, seq_len)), k=1)
    causal_mask = (causal_mask == 0).astype(np.float32)
    causal_mask = causal_mask[np.newaxis, np.newaxis, :, :]
    # 广播到batch_size
    causal_mask = np.broadcast_to(causal_mask, (batch_size, 1, seq_len, seq_len))
    return Tensor(causal_mask)


def train():
    lr = 0.001  # 学习率
    epoch = 500  # 迭代次数
    batch_size = 5  # 批量处理

    # 加载模型
    model = TransformerV1(
        src_vocab_size=len(src_vocab),
        tgt_vocab_size=len(tgt_vocab),
        d_model=32,
        num_layers=1,
        num_heads=2,
        hidden_size=64,
        dropout_rate=0.1,
        max_seq_len=50  # TODO 注意与utils/vocab.py方法的create_sequences的max_length一致，否则会报错，这个也是未来待优化的一个点！！！
    )
    # model.to_gpu()
    # 使用优化器Adam并安装模型
    optimizer = Adam(lr).setup(model)
    for i in range(epoch):
        # x = inputs_sequences
        # t = outputs_sequences
        x, t = get_batch(batch_size, inputs_sequences, outputs_sequences)
        # 准备decoder输入（偏移，去掉最后一个token）
        decoder_input = t[:, :-1]
        # 准备decoder目标（去掉第一个token）
        decoder_target = t[:, 1:]
        # 生成掩码
        src_mask = generate_src_mask(x)  # 需要实现这个函数
        tgt_mask = generate_tgt_mask(decoder_input)  # 需要实现这个函数
        x_grad = model(x, decoder_input, src_mask, tgt_mask)
        loss = categorical_cross_entropy(x_grad, decoder_target)
        # model.clear_tensors(clear_graph=True, clear_grad=False)
        model.clear_tensors()
        loss.backward()
        optimizer.update()
        # model.clear_tensors(clear_graph=False, clear_grad=True)
        if i % 10 == 0:
            accuracy_out = round(transformer_accuracy(x_grad, decoder_target) * 100, 2)
            print("准确率：" + str(accuracy_out) + "%，损失值：" + str(loss))
    model.save_parameters('transformer_v1_model')


# 训练
train()
