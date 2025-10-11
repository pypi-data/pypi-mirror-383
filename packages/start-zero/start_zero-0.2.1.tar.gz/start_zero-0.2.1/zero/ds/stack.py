class Stack:
    """
    栈的简单实现（来源于网络）
    """

    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.items:
            return None
        else:
            return self.items.pop()

    def peek(self):
        if not self.items:
            return None
        else:
            return self.items[-1]

    def size(self):
        return len(self.items)
