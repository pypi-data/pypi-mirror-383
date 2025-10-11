# 深度学习框架 V0.2.1
# 一、安装及使用
1、安装：pip install start-zero   
# 二、未来规划
1、持续优化代码并修正BUG    
2、增加函数、层、模型、优化器    
3、增加GPU支持
# 三、框架说明
1、主要特点   
自动微分、运行时动态图、高阶求导（反向传播的反向传播）、函数、层、模型、优化器   
2、目前支持51个函数，参见[函数列表](https://gitee.com/tank2140896/start-zero/tree/master/zero/ops/__init__.py)   
3、基于谷歌论文《Attention Is All You Need》实现了具有编码器和解码器的Transformer模型，训练调用示例：   
```python
def train():
    lr = 0.001  # 学习率
    epoch = 500  # 迭代次数
    batch_size = 5  # 批量处理
    # 加载模型TransformerV1
    model = TransformerV1(...)
    # 使用GPU加速（如果支持）
    # model.to_gpu()
    # 使用优化器Adam并安装模型
    optimizer = Adam(lr).setup(model)
    for i in range(epoch):
        # 调用模型的正向传播
        x_grad = model(...)
        # 计算损失值
        loss = ...
        # 清空中间梯度
        model.clear_tensors()
        # 反向传播
        loss.backward()
        # 参数更新
        optimizer.update()
        if i % 10 == 0:
            accuracy_out = ...
            print("准确率：" + str(accuracy_out) + "%，损失值：" + str(loss))
    # 保存模型
    model.save_parameters('transformer_v1_model')
```
# 四、发布到PyPI
1、登录[PyPI官网](https://pypi.org)完成账号注册和安全认证   
2、安装插件（如：E:\pyhton\python.exe -m pip install --upgrade pip setuptools wheel和E:\pyhton\python.exe -m pip install twine）   
3、生成压缩包（python setup.py sdist）   
4、上传压缩包（如：E:\pyhton\python.exe -m twine upload dist/*）   
注：完成2FA认证后，username是：__token__，password是：生成的token   
5、安装和卸载（pip install start-zero、pip uninstall start-zero）   
注：指定版本如：pip install start-zero==1.0.0，也可以<或<=等   
