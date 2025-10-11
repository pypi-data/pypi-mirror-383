import heapq


class PriorityQueue:
    """
    heapq模块实现的简单的优先级队列（来源于网络）
    """

    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        # 把priority取负值是未来让队列能够按元素的优先级从高到低的顺序排列
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def len(self):
        return len(self._queue)
