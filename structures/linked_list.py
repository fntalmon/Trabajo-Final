"""
Lista simplemente enlazada.
Basada en Cormen et al., Introduction to Algorithms (2009), Capítulo 10.
Inserción al inicio O(1), búsqueda O(n), eliminación O(n).
"""


class Node:
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def insert(self, key, value=None):
        node = Node(key, value)
        node.next = self.head
        self.head = node
        self.size += 1

    def search(self, key):
        x = self.head
        while x is not None and x.key != key:
            x = x.next
        return x

    def delete(self, key):
        prev = None
        x = self.head
        while x is not None and x.key != key:
            prev = x
            x = x.next
        if x is None:
            return False
        if prev is None:
            self.head = x.next
        else:
            prev.next = x.next
        self.size -= 1
        return True

    def range_query(self, low, high):
        result = []
        x = self.head
        while x is not None:
            if low <= x.key <= high:
                result.append(x.key)
            x = x.next
        return result

    def __len__(self):
        return self.size
