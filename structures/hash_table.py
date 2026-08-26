"""
Tabla Hash con encadenamiento (chaining).
Basada en Cormen et al., Introduction to Algorithms (2009), Capítulo 11.
Capacidad inicial: 16, factor de carga umbral α = 0.75.
Función hash: método de la división h(k) = k mod m.
Rehashing automático al superar α.
"""


class HashTable:
    def __init__(self, capacity=16, load_factor_threshold=0.75):
        self.capacity = capacity
        self.load_factor_threshold = load_factor_threshold
        self.size = 0
        self.table = [[] for _ in range(self.capacity)]

    def _hash(self, key):
        return key % self.capacity

    def _rehash(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_table:
            for key, value in bucket:
                self._insert_no_rehash(key, value)

    def _insert_no_rehash(self, key, value):
        index = self._hash(key)
        bucket = self.table[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def insert(self, key, value=None):
        if (self.size + 1) / self.capacity > self.load_factor_threshold:
            self._rehash()
        self._insert_no_rehash(key, value)

    def search(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return (k, v)
        return None

    def delete(self, key):
        index = self._hash(key)
        bucket = self.table[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.size -= 1
                return True
        return False

    def range_query(self, low, high):
        result = []
        for bucket in self.table:
            for k, v in bucket:
                if low <= k <= high:
                    result.append(k)
        return result

    def __len__(self):
        return self.size
