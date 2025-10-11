import numpy as np

from zero.core.tensor import Tensor, clear_tensors
from zero.ops import add, sub, mul, div, power, neg, mod

print("------------------------------ add ------------------------------")
x1_add = Tensor(np.array([1, 2, 3]))
x2_add = Tensor(np.array([[1, 2, 3], [4, 5, 6]]))
y_add = add(x1_add, x2_add)
print(y_add)  # Tensor([[2 4 6] [5 7 9]])
y_add.backward()
print(x1_add.grad)  # Tensor([2 2 2])
print(x2_add.grad)  # Tensor([[1 1 1] [1 1 1]])

clear_tensors(x1_add, x2_add)

y_add = x1_add + x2_add
print(y_add)  # Tensor([[2 4 6] [5 7 9]])
y_add.backward()
print(x1_add.grad)  # Tensor([2 2 2])
print(x2_add.grad)  # Tensor([[1 1 1] [1 1 1]])
print("------------------------------ sub ------------------------------")
x1_sub = Tensor(np.array([[1, 2, 3], [4, 5, 6]]))
x2_sub = Tensor(np.array([1, 1, 1]))
y_sub = sub(x1_sub, x2_sub)
print(y_sub)  # Tensor([[0 1 2] [3 4 5]])
y_sub.backward()
print(x1_sub.grad)  # Tensor([[1 1 1] [1 1 1]])
print(x2_sub.grad, x2_sub.grad.shape)  # Tensor([-2 -2 -2])  (3,)

clear_tensors(x1_sub, x2_sub)

y_sub = x1_sub - x2_sub
print(y_sub)  # Tensor([[0 1 2] [3 4 5]])
y_sub.backward()
print(x1_sub.grad)  # Tensor([[1 1 1] [1 1 1]])
print(x2_sub.grad, x2_sub.grad.shape)  # Tensor([-2 -2 -2])  (3,)
print("------------------------------ mul ------------------------------")
x1_mul = Tensor(np.array([[1, 2, 3], [4, 5, 6]]))
x2_mul = Tensor(np.array([5, 1, 2]))
y_mul = mul(x1_mul, x2_mul)
print(y_mul)  # Tensor([[ 5  2  6] [20 15  6]])
y_mul.backward()
print(x1_mul.grad)  # Tensor([[5 1 2] [5 1 2]])
print(x2_mul.grad)  # Tensor([5 7 9]])

clear_tensors(x1_mul, x2_mul)

y_mul = x1_mul * x2_mul
print(y_mul)  # Tensor([[ 5  2  6] [20 15  6]])
y_mul.backward()
print(x1_mul.grad)  # Tensor([[5 1 2] [5 1 2]])
print(x2_mul.grad)  # Tensor([5 7 9]])
print("------------------------------ div ------------------------------")
x1_div = Tensor(np.array([[9, 8, 10], [12, 24, 8]]))
x2_div = Tensor(np.array([3, 4, 2]))
y_div = div(x1_div, x2_div)
print(y_div)  # Tensor([[3. 2. 5.] [4. 6. 4.]])
y_div.backward()
print(x1_div.grad)  # Tensor([[0.33333333 0.25 0.5] [0.33333333 0.25 0.5]])
print(x2_div.grad)  # Tensor([-2.33333333 -2. -4.5])

clear_tensors(x1_div, x2_div)

y_div = x1_div / x2_div
print(y_div)  # Tensor([[3. 2. 5.] [4. 6. 4.]])
y_div.backward()
print(x1_div.grad)  # Tensor([[0.33333333 0.25 0.5] [0.33333333 0.25 0.5]])
print(x2_div.grad)  # Tensor([-2.33333333 -2. -4.5])
print("------------------------------ power ------------------------------")
x_power = Tensor(np.array([3, 1, 2]))
y_power = power(x_power, 2)
print(y_power)  # Tensor([ 9 1 4])
y_power.backward()
print(x_power.grad)  # Tensor([6 2 4])

clear_tensors(x_power)

y_power = x_power ** 2
print(y_power)  # Tensor([9 1 4])
y_power.backward()
print(x_power.grad)  # Tensor([6 2 4])
print("------------------------------ neg ------------------------------")
x_neg = Tensor(np.array([3, 1, 2]))
y_neg = neg(x_neg)
print(y_neg)  # Tensor([-3 -1 -2])
y_neg.backward()
print(x_neg.grad)  # Tensor([-1 -1 -1])

clear_tensors(x_neg)

y_neg = -x_neg
print(y_neg)  # Tensor([-3 -1 -2])
y_neg.backward()
print(x_neg.grad)  # Tensor([-1 -1 -1])
print("------------------------------ mod ------------------------------")
x1_mod = Tensor(np.array([[24, 12, 32], [42, 52, 62]]))
x2_mod = Tensor(np.array([[2, 4, 6], [6, 7, 8]]))
y_mod = mod(x1_mod, x2_mod)
print(y_mod)  # Tensor([[0 0 2] [0 3 6]])
y_mod.backward()
print(x1_mod.grad)  # Tensor([[1 1 1] [1 1 1]])
print(x2_mod.grad)  # Tensor([[-12.  -3.  -5.] [ -7.  -7.  -7.]])

clear_tensors(x1_mod, x2_mod)

y_mod = x1_mod % x2_mod
print(y_mod)  # Tensor([[0 0 2] [0 3 6]])
y_mod.backward()
print(x1_mod.grad)  # Tensor([[1 1 1] [1 1 1]])
print(x2_mod.grad)  # Tensor([[-12.  -3.  -5.] [ -7.  -7.  -7.]])
print("------------------------------ 综合 ------------------------------")
zx_1_x = Tensor(np.array([2]))
zx_1_y = (zx_1_x ** 3 + zx_1_x) * 5
zx_1_y.backward()
print(zx_1_x.grad)  # Tensor([65])
