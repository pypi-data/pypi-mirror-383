import os
import weakref
from typing import Any

import numpy as np

from zero.core.tensor import Parameter


class Layer:

    def __init__(self):
        self._params = set()
        self._layers = {}

    """
    正常情况下，如：
    l = Layer()
    l.l1 = 10
    l.l2 = 'a'
    l.l3 = Parameter(np.array(3.56))
    l.l4 = Layer()
    这里通过过滤，只有类型是Parameter或Layer才会被添加
    """
    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, (Parameter, Layer)):
            self._params.add(name)
            if isinstance(value, Layer):
                # 如果是Layer，也存储到_layers字典中便于遍历
                if not hasattr(self, '_layers'):
                    super().__setattr__('_layers', {})
                self._layers[name] = value
        super().__setattr__(name, value)

    def layers(self):
        for name in self._params:
            obj = self.__dict__[name]
            if isinstance(obj, Layer):
                yield obj
                yield from obj.layers()  # 递归获取子层的子层

    def __call__(self, *inputs):
        outputs = self.forward(*inputs)
        if not isinstance(outputs, tuple):
            outputs = (outputs, )
        self.inputs = [weakref.ref(x) for x in inputs]
        self.outputs = [weakref.ref(y) for y in outputs]
        return outputs if len(outputs) > 1 else outputs[0]

    def forward(self, *inputs):
        raise NotImplementedError()

    def params(self):
        for name in self._params:
            obj = self.__dict__[name]
            """
            处理Layer套Layer的情况，最后只会输出Parameter类型
            类似参考：
            new_t = Test()
            new_t.x1 = 'a'
            new_t.x2 = 'b'
            t = Test()
            t.t1 = 'c'
            t.t2 = new_t
            x = t.params()
            print(list(x))  # ['b', 'a', 'c']
            """
            if isinstance(obj, Layer):
                yield from obj.params()
            else:
                yield obj

    def clear_tensors(self):
        """
        def clear_tensors(self, clear_graph=True, clear_grad=False):
            for param in self.params():
                param.clear_tensor(clear_graph, clear_grad)
        """
        for param in self.params():
            param.clear_tensor()

    def _flatten_params(self, params_dict, parent_key=""):
        for name in self._params:
            obj = self.__dict__[name]
            key = parent_key + '/' + name if parent_key else name
            if isinstance(obj, Layer):
                obj._flatten_params(params_dict, key)
            else:
                params_dict[key] = obj

    def _get_name(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def save_parameters(self, path):
        params_dict = {}
        self._flatten_params(params_dict)
        array_dict = {key: param.data for key, param in params_dict.items() if param is not None}
        try:
            np.savez(path, **array_dict)
        except (Exception, KeyboardInterrupt) as e:
            if os.path.exists(path):
                os.remove(path)
            raise e

    def load_parameters(self, path):
        npz = np.load(path)
        params_dict = {}
        self._flatten_params(params_dict)
        for key, param in params_dict.items():
            param.data = npz[key]

    def to_gpu(self):
        from zero.accelerate.cupy import use_gpu
        use_gpu()
        for layer in self.layers():
            layer.to_gpu()

    def to_cpu(self):
        from zero.accelerate.cupy import use_cpu
        use_cpu()
        for layer in self.layers():
            layer.to_cpu()
