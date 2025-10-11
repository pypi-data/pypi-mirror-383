import numpy as np
from zero.core.tensor import Tensor
from zero.models.transformer import TransformerV1
from zero.utils.vocab import build_vocab, load_text_data, prepare_training_data

""" ############################## 准备词汇表（与训练时相同） ############################## """
# 使用与训练时相同的问答对和文本数据
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

print(f"源词汇表大小: {len(src_vocab)}")
print(f"目标词汇表大小: {len(tgt_vocab)}")
# print("源词汇表样例:", {k: v for k, v in list(src_vocab.items())})
# print("目标词汇表样例:", {k: v for k, v in list(tgt_vocab.items())})


def text_to_sequence(text, vocab, max_len=50):
    tokens = list(text)
    sequence = [vocab.get(token, vocab.get('<unk>', 0)) for token in tokens]
    if len(sequence) < max_len:
        sequence = sequence + [0] * (max_len - len(sequence))
    else:
        sequence = sequence[:max_len]
    return sequence


def sequence_to_text(sequence, vocab):
    """将序列转换为文本"""
    reverse_vocab = {v: k for k, v in vocab.items()}
    tokens = []
    for idx in sequence:
        if idx == 0:  # padding
            continue
        if idx in reverse_vocab:
            token = reverse_vocab[idx]
            if token == '<eos>':  # 结束符
                break
            if token not in ['<pad>', '<sos>']:
                tokens.append(token)
    return ''.join(tokens)


# 方法与训练时一致
def generate_src_mask(src):
    src_np = np.array(src.data)
    mask = (src_np != 0).astype(np.float32)
    mask = mask[:, np.newaxis, np.newaxis, :]
    return Tensor(mask)


# 方法与训练时一致
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


def load_and_setup_model(model_path):
    """加载模型并设置参数"""
    model = TransformerV1(
        src_vocab_size=len(src_vocab),
        tgt_vocab_size=len(tgt_vocab),
        d_model=32,
        num_layers=1,
        num_heads=2,
        hidden_size=64,
        dropout_rate=0.1,
        max_seq_len=50
    )

    # 加载训练好的参数
    model.load_parameters(model_path)
    print(f"模型已从 {model_path} 加载")
    return model


def generate_response(model, question, max_length=20):
    def softmax(x):
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)

    try:
        # 编码输入问题
        src_seq = text_to_sequence(question, src_vocab)
        # print(f"输入序列: {src_seq}")
        src_tensor = Tensor(np.array([src_seq], dtype=np.int32))
        src_mask = generate_src_mask(src_tensor)

        start_token = tgt_vocab.get('<sos>', 1)
        end_token = tgt_vocab.get('<eos>', 2)
        # print(f"开始符: {start_token}, 结束符: {end_token}")

        # 初始化decoder输入 - 只包含开始符
        decoder_input = [start_token]
        # print(f"初始decoder输入: {decoder_input}")

        for i in range(max_length):
            # 创建当前decoder输入（填充到max_length）
            current_seq = decoder_input + [0] * (max_length - len(decoder_input))
            decoder_tensor = Tensor(np.array([current_seq], dtype=np.int32))
            tgt_mask = generate_tgt_mask(decoder_tensor)

            # 前向传播
            output = model(src_tensor, decoder_tensor, src_mask, tgt_mask)

            # 获取最后一个token的预测（当前生成位置）
            last_token_idx = len(decoder_input) - 1
            next_token_logits = output.data[0, last_token_idx, :]
            next_token_probs = softmax(next_token_logits)

            # 关键修改：忽略padding token (0) 和 unknown token
            valid_indices = [idx for idx in range(len(next_token_probs))
                             if idx != 0 and idx != tgt_vocab.get('<unk>', 3)]

            if not valid_indices:
                # print("没有有效的token可预测")
                break

            # 只在有效token中选择
            valid_probs = next_token_probs[valid_indices]
            best_valid_idx = np.argmax(valid_probs)
            next_token = valid_indices[best_valid_idx]

            # print(f"步骤 {i}: 预测token {next_token} ('{sequence_to_text([next_token], tgt_vocab)}'), 概率 {next_token_probs[next_token]:.4f}")

            # 添加到序列中
            decoder_input.append(next_token)

            # 如果遇到结束符则停止
            if next_token == end_token:
                # print("遇到结束符，停止生成")
                break

        # print(f"最终decoder序列: {decoder_input}")

        # 转换回文本
        response_sequence = decoder_input[1:]  # 去掉<sos>
        if response_sequence and response_sequence[-1] == end_token:
            response_sequence = response_sequence[:-1]
        response = sequence_to_text(response_sequence, tgt_vocab)
        # print(f"转换后的回答: '{response}'")
        return response

    except Exception as e:
        print(f"生成过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return ""


def test_specific_questions():
    """测试特定问题"""
    model_path = 'transformer_v1_model.npz'
    try:
        # 加载模型
        model = load_and_setup_model(model_path)
        print("模型加载成功！开始测试...")
        print("-" * 50)

        # 测试问题列表
        test_questions = [
            "6*7=?",
            "100乘以2等于多少？",
            "也有人",
            "系的行星",
            "根号4"
        ]

        for question in test_questions:
            print(f"问题: {question}")
            try:
                response = generate_response(model, question)
                print(f"回答: {response}")
                print("-" * 30)
            except Exception as e:
                print(f"处理问题 '{question}' 时出错: {e}")
                print("-" * 30)

    except Exception as e:
        print(f"测试时出错: {e}")


test_specific_questions()
