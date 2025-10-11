# from docx import Document
from collections import Counter

import numpy as np


def build_vocab(train_texts):
    """
    构造词汇表
    :param train_texts: 训练文本
    使用示例：
    train_texts = [
        "1+1=2",
        "1加1等于2",
        "当我们问1+1等于几时或者1+1=几时，我们一般会回答是2",
        "对于1+1等于几，也有人会直接写为：1+1=?"
    ]
    vocab = build_vocab(train_texts)
    print(vocab)
    reverse_vocab = {_v: _k for _k, _v in vocab.items()}
    print(reverse_vocab)
    """

    """
    Counter用法示例：
    words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
    counter = Counter(words)
    print(counter)  # Counter({'apple': 3, 'banana': 2, 'orange': 1})
    counter = Counter()
    counter.update(['a', 'b', 'a'])  # 添加元素
    print(counter)  # Counter({'a': 2, 'b': 1})
    """
    counter = Counter()
    """
    这里简单粗暴的采用最细粒度的字符级别分词，当然目前现代主流采用的是子词级别，总之：
    最终具体怎么拆，取决于选择的分词算法（BPE, WordPiece, Unigram等）和在训练语料上的统计结果
    """
    for text in train_texts:
        counter.update(list(text))  # counter.update(text)
    """
    <pad>：填充标记
    <sos>：序列开始标记
    <eos>：序列结束标记
    <unk>：未知词标记
    """
    vocab = {'<pad>': 0, '<sos>': 1, '<eos>': 2, '<unk>': 3}  # 特殊标记
    min_freq = 1
    for char, count in counter.items():
        if count >= min_freq:
            vocab[char] = len(vocab)
    return vocab


def create_sequences(inputs, outputs, src_vocab, tgt_vocab, max_length=50):
    src_sequences = []
    tgt_sequences = []

    for inp, out in zip(inputs, outputs):
        # 输入序列：只进行字符到ID的转换，不添加特殊标记
        src_seq = [src_vocab.get(char, src_vocab.get('<unk>', 0)) for char in inp]

        # 输出序列：添加<sos>和<eos>
        tgt_seq = [tgt_vocab.get('<sos>', 1)]  # 开始符
        tgt_seq.extend([tgt_vocab.get(char, tgt_vocab.get('<unk>', 0)) for char in out])
        tgt_seq.append(tgt_vocab.get('<eos>', 2))  # 结束符

        # 填充或截断
        if len(src_seq) < max_length:
            src_seq = src_seq + [0] * (max_length - len(src_seq))
        else:
            src_seq = src_seq[:max_length]

        if len(tgt_seq) < max_length:
            tgt_seq = tgt_seq + [0] * (max_length - len(tgt_seq))
        else:
            tgt_seq = tgt_seq[:max_length]

        src_sequences.append(src_seq)
        tgt_sequences.append(tgt_seq)

    return np.array(src_sequences, dtype=np.int32), np.array(tgt_sequences, dtype=np.int32)


def prepare_training_data(free_texts, qa_pairs):
    """
    准备训练数据，包括问答对和自监督学习数据
    """
    # 1. 处理问答对数据
    train_inputs = []
    train_outputs = []

    for question, answer in qa_pairs:
        train_inputs.append(question)
        train_outputs.append(answer)

    # 2. 处理自由文本（自监督学习）
    # 将文本拆分为输入和输出（前n-1个字符作为输入，后n-1个字符作为输出）
    for text in free_texts:
        if len(text) > 1:
            # 简单分割：前部分作为输入，后部分作为输出
            split_point = max(1, len(text) // 2)
            train_inputs.append(text[:split_point])
            train_outputs.append(text[split_point:])

    return train_inputs, train_outputs


def load_text_data(file_paths):
    """
    从多个文件加载文本数据，如txt、docx等
    """
    all_texts = []
    for file_path in file_paths:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                all_texts.extend(lines)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")
        """
        elif file_path.endswith('.docx'):
            try:
                doc = Document(file_path)
                paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                all_texts.extend(paragraphs)
            except:
                print(f"无法读取Word文档: {file_path}")
        """
    return all_texts
