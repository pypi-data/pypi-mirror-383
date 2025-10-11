import numpy as np


def cos_similarity_norm2(vector1, vector2):
    """
    余弦相似度（采用范数2）
    为什么采用余弦相似度？因为两个向量重叠（即100%相似），那么他们的角度就是0度，而sin0度为0，cos0度为1；sin90度为1，cos90度为0。一般认为值越大（越接近1，100%=1）相似度越高
    示例1：
    vector1 = np.array([[1, 2], [3, 4], [5, 6]]) # 3行2列。可以理解为有3组数据，每组数据有2个特征点
    vector2 = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 0]]) # 5行2列。可以理解为有5组数据，每组数据有2个特征点
    cos_similarity_norm2(vector1, vector2.T) # 得出的是3组数据与5组数据的分别匹配度，值越大表示越相似
    示例2：
    vector1 = np.random.rand(1, 512)
    vector2 = np.random.rand(1, 512)
    cos_similarity_norm2(vector1, vector2.T)
    关于转置的参考：线性代数的行列式性质1为：行列式与其转置行列式的值相等
    """
    # 点积
    dot_product = np.dot(vector1, vector2)
    # 范数（这里采用的是向量的2范数，即向量的各元素的平方之和再开平方根）
    norm_1 = np.linalg.norm(vector1)
    norm_2 = np.linalg.norm(vector2)
    # 余弦相似度（值越大表示越相似）
    cos_similarity = dot_product / (norm_1 * norm_2)
    return cos_similarity


def xavier_uniform(shape, gain=1.0):
    """
    bound = gain * np.sqrt(6.0 / (shape[0] + shape[1]))
    return np.random.uniform(-bound, bound, shape)
    """
    # 缩放版的Xavier初始化，适合Transformer
    fan_in, fan_out = shape[0], shape[1]
    scale = gain * np.sqrt(6.0 / (fan_in + fan_out))
    return np.random.uniform(-scale, scale, shape)
