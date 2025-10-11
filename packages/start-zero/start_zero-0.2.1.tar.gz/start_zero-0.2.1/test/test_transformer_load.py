import numpy as np


def check_model_basic(file_path):
    try:
        # 加载npz文件
        model_data = np.load(file_path)

        print("=== 模型文件基本信息 ===")
        print(f"文件中的数组数量: {len(model_data.files)}")
        print(f"数组名称: {model_data.files}")

        # 检查每个数组的大小和形状
        total_params = 0
        for key in model_data.files:
            array = model_data[key]
            params_count = np.prod(array.shape)
            total_params += params_count
            print(f"{key}: 形状{array.shape}, 参数数量: {params_count:,}")

        print(f"总参数数量: {total_params:,}")
        return True

    except Exception as e:
        print(f"加载失败: {e}")
        return False


check_model_basic("transformer_v1_model.pkl.npz")
