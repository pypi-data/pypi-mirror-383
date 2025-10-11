try:
    import urllib.request
except ImportError:
    raise ImportError('You should use Python 3.x')
import os.path
import gzip
import pickle
import os
import numpy as np

from zero.ops.loss_ops import mean_squared_error
from zero.ops.util_ops import accuracy
from zero.ops.act_ops import relu
from zero.models.mlp import MLP
from zero.optimizers.sgd import MomentumSGD


url_base = 'https://ossci-datasets.s3.amazonaws.com/mnist/'
key_file = {
    'train_img': 'train-images-idx3-ubyte.gz',
    'train_label': 'train-labels-idx1-ubyte.gz',
    'test_img': 't10k-images-idx3-ubyte.gz',
    'test_label': 't10k-labels-idx1-ubyte.gz'
}
dataset_dir = os.path.dirname(os.path.abspath(__file__))
save_file = dataset_dir + "/mnist.pkl"

train_num = 60000
test_num = 10000
img_dim = (1, 28, 28)
img_size = 784


def _download(file_name):
    file_path = dataset_dir + "/" + file_name

    if os.path.exists(file_path):
        return

    print("Downloading " + file_name + " ... ")
    urllib.request.urlretrieve(url_base + file_name, file_path)
    print("Done")


def download_mnist():
    for v in key_file.values():
        _download(v)


def _load_label(file_name):
    file_path = dataset_dir + "/" + file_name

    print("Converting " + file_name + " to NumPy Array ...")
    with gzip.open(file_path, 'rb') as f:
        labels = np.frombuffer(f.read(), np.uint8, offset=8)
    print("Done")

    return labels


def _load_img(file_name):
    file_path = dataset_dir + "/" + file_name

    print("Converting " + file_name + " to NumPy Array ...")
    with gzip.open(file_path, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8, offset=16)
    data = data.reshape(-1, img_size)
    print("Done")

    return data


def _convert_numpy():
    dataset = {
        'train_img': _load_img(key_file['train_img']),
        'train_label': _load_label(key_file['train_label']),
        'test_img': _load_img(key_file['test_img']),
        'test_label': _load_label(key_file['test_label'])
    }
    return dataset


def init_mnist():
    download_mnist()
    dataset = _convert_numpy()
    print("Creating pickle file ...")
    with open(save_file, 'wb') as f:
        pickle.dump(dataset, f, -1)
    print("Done!")


def _change_one_hot_label(X):
    T = np.zeros((X.size, 10))
    for idx, row in enumerate(T):
        row[X[idx]] = 1

    return T


def load_mnist(normalize=True, flatten=True, one_hot_label=False):
    """读入MNIST数据集

    Parameters
    ----------
    normalize : 将图像的像素值正规化为0.0~1.0，False就是0~255
    one_hot_label :
        one_hot_label为True的情况下，标签作为one-hot数组返回
        one-hot数组是指[0,0,1,0,0,0,0,0,0,0]这样的数组
    flatten : 是否将图像展开为一维数组

    Returns
    -------
    (训练图像, 训练标签), (测试图像, 测试标签)
    """
    if not os.path.exists(save_file):
        init_mnist()

    with open(save_file, 'rb') as f:
        dataset = pickle.load(f)

    if normalize:
        for key in ('train_img', 'test_img'):
            dataset[key] = dataset[key].astype(np.float32)
            dataset[key] /= 255.0

    if one_hot_label:
        dataset['train_label'] = _change_one_hot_label(dataset['train_label'])
        dataset['test_label'] = _change_one_hot_label(dataset['test_label'])

    if not flatten:
        for key in ('train_img', 'test_img'):
            dataset[key] = dataset[key].reshape(-1, 1, 28, 28)

    return (dataset['train_img'], dataset['train_label']), (dataset['test_img'], dataset['test_label'])


def train():
    lr = 0.1  # 学习率
    epoch = 10000  # 迭代次数
    batch_size = 100  # 批量处理
    load_or_save_file = 'mnist_mlp.npz'

    # 加载模型MLP（多层感知器）并使用线性整流激活函数（relu）
    model = MLP((200, 100, 10), activation=relu)
    # 使用优化器MomentumSGD并安装模型
    optimizer = MomentumSGD(lr).setup(model)

    if os.path.exists(load_or_save_file):
        model.load_parameters(load_or_save_file)

    (x_train, t_train), (x_test, t_test) = load_mnist(normalize=True, flatten=True, one_hot_label=True)  # 加载训练集
    for i in range(epoch):
        # 从0-len(x_train)间随机选择batch_size个数字（可能重复）
        random_choice_index = np.random.choice(len(x_train), batch_size)
        x = x_train[random_choice_index]  # 100行784列
        t = t_train[random_choice_index]  # 100行784列

        if os.path.exists(load_or_save_file):
            x_grad = model(x)
            loss = mean_squared_error(t, x_grad)
            model.clear_tensors()
            if i % 1000 == 0:
                accuracy_out = round(accuracy(x_grad, t) * 100, 2)
                print("准确率：" + str(accuracy_out) + "%，损失值：" + str(loss))
        else:
            x_grad = model(x)
            loss = mean_squared_error(t, x_grad)
            model.clear_tensors()

            loss.backward()
            optimizer.update()
            if i % 1000 == 0:
                accuracy_out = round(accuracy(x_grad, t) * 100, 2)
                print("准确率：" + str(accuracy_out) + "%，损失值：" + str(loss))

    model.save_parameters(load_or_save_file)


# 训练测试
train()
