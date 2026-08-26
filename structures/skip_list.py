"""
Skip List probabilística.
Basada en Pugh, W. (1990). Skip Lists: A Probabilistic Alternative to Balanced Trees.
Probabilidad p = 0.5, máximo 16 niveles, seed = 42 para reproducibilidad.
"""

import random


class SkipNode:
    __slots__ = ('key', 'value', 'forward')

    def __init__(self, key=None, value=None, level=0):
        self.key = key
        self.value = value
        self.forward = [None] * (level + 1)


class SkipList:
    def __init__(self, max_level=16, p=0.5, seed=42):
        self.max_level = max_level
        self.p = p
        self.level = 0
        self.head = SkipNode(key=None, value=None, level=max_level)
        self.size = 0
        self._rng = random.Random(seed)

    def _random_level(self):
        lvl = 0
        while self._rng.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def search(self, key):
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                x = x.forward[i]
        x = x.forward[0]
        if x is not None and x.key == key:
            return x
        return None

    def insert(self, key, value=None):
        update = [None] * (self.max_level + 1)
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                x = x.forward[i]
            update[i] = x
        x = x.forward[0]

        if x is not None and x.key == key:
            x.value = value
            return

        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.head
            self.level = lvl

        new_node = SkipNode(key, value, lvl)
        for i in range(lvl + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
        self.size += 1

    def delete(self, key):
        update = [None] * (self.max_level + 1)
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < key:
                x = x.forward[i]
            update[i] = x
        x = x.forward[0]

        if x is None or x.key != key:
            return False

        for i in range(self.level + 1):
            if update[i].forward[i] is not x:
                break
            update[i].forward[i] = x.forward[i]

        while self.level > 0 and self.head.forward[self.level] is None:
            self.level -= 1
        self.size -= 1
        return True

    def range_query(self, low, high):
        result = []
        x = self.head
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].key < low:
                x = x.forward[i]
        x = x.forward[0]
        while x is not None and x.key <= high:
            result.append(x.key)
            x = x.forward[0]
        return result

    def __len__(self):
        return self.size
