"""
B-Tree.
Basado en Cormen et al., Introduction to Algorithms (2009), Capítulo 18.
Grado mínimo t = 50 fijo. Cada nodo tiene entre t-1 y 2t-1 claves.
Incluye split, búsqueda, inserción, eliminación (con borrow y merge), y range query.
"""


class BTreeNode:
    __slots__ = ('keys', 'values', 'children', 'leaf', 'n')

    def __init__(self, leaf=True):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf
        self.n = 0


class BTree:
    def __init__(self, t=50):
        self.t = t
        self.root = BTreeNode(leaf=True)
        self.size = 0

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < node.n and key > node.keys[i]:
            i += 1
        if i < node.n and key == node.keys[i]:
            return (node, i)
        if node.leaf:
            return None
        return self.search(key, node.children[i])

    def _split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BTreeNode(leaf=y.leaf)

        z.keys = y.keys[t:]
        z.values = y.values[t:]
        z.n = len(z.keys)

        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]

        median_key = y.keys[t - 1]
        median_value = y.values[t - 1]

        y.keys = y.keys[:t - 1]
        y.values = y.values[:t - 1]
        y.n = len(y.keys)

        x.children.insert(i + 1, z)
        x.keys.insert(i, median_key)
        x.values.insert(i, median_value)
        x.n += 1

    def insert(self, key, value=None):
        r = self.root
        if r.n == 2 * self.t - 1:
            s = BTreeNode(leaf=False)
            s.children.append(self.root)
            self.root = s
            self._split_child(s, 0)
            self._insert_nonfull(s, key, value)
        else:
            self._insert_nonfull(r, key, value)
        self.size += 1

    def _insert_nonfull(self, x, key, value):
        i = x.n - 1
        if x.leaf:
            x.keys.append(None)
            x.values.append(None)
            while i >= 0 and key < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                x.values[i + 1] = x.values[i]
                i -= 1
            x.keys[i + 1] = key
            x.values[i + 1] = value
            x.n += 1
        else:
            while i >= 0 and key < x.keys[i]:
                i -= 1
            i += 1
            if x.children[i].n == 2 * self.t - 1:
                self._split_child(x, i)
                if key > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.children[i], key, value)

    def delete(self, key):
        result = self._delete(self.root, key)
        if self.root.n == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        if result:
            self.size -= 1
        return result

    def _delete(self, x, key):
        t = self.t
        i = 0
        while i < x.n and key > x.keys[i]:
            i += 1

        if x.leaf:
            if i < x.n and x.keys[i] == key:
                x.keys.pop(i)
                x.values.pop(i)
                x.n -= 1
                return True
            return False

        if i < x.n and x.keys[i] == key:
            return self._delete_internal(x, i)
        else:
            if x.children[i].n < t:
                self._fill(x, i)
                if i > x.n:
                    i -= 1
            return self._delete(x.children[i], key)

    def _delete_internal(self, x, i):
        t = self.t
        key = x.keys[i]

        if x.children[i].n >= t:
            pred_node = x.children[i]
            while not pred_node.leaf:
                pred_node = pred_node.children[pred_node.n]
            pred_key = pred_node.keys[pred_node.n - 1]
            pred_val = pred_node.values[pred_node.n - 1]
            x.keys[i] = pred_key
            x.values[i] = pred_val
            return self._delete(x.children[i], pred_key)

        elif x.children[i + 1].n >= t:
            succ_node = x.children[i + 1]
            while not succ_node.leaf:
                succ_node = succ_node.children[0]
            succ_key = succ_node.keys[0]
            succ_val = succ_node.values[0]
            x.keys[i] = succ_key
            x.values[i] = succ_val
            return self._delete(x.children[i + 1], succ_key)

        else:
            self._merge(x, i)
            return self._delete(x.children[i], key)

    def _fill(self, x, i):
        t = self.t
        if i > 0 and x.children[i - 1].n >= t:
            self._borrow_from_prev(x, i)
        elif i < x.n and x.children[i + 1].n >= t:
            self._borrow_from_next(x, i)
        else:
            if i < x.n:
                self._merge(x, i)
            else:
                self._merge(x, i - 1)

    def _borrow_from_prev(self, x, i):
        child = x.children[i]
        sibling = x.children[i - 1]

        child.keys.insert(0, x.keys[i - 1])
        child.values.insert(0, x.values[i - 1])
        child.n += 1

        x.keys[i - 1] = sibling.keys[sibling.n - 1]
        x.values[i - 1] = sibling.values[sibling.n - 1]

        if not child.leaf:
            child.children.insert(0, sibling.children[sibling.n])
            sibling.children.pop()

        sibling.keys.pop()
        sibling.values.pop()
        sibling.n -= 1

    def _borrow_from_next(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]

        child.keys.append(x.keys[i])
        child.values.append(x.values[i])
        child.n += 1

        x.keys[i] = sibling.keys[0]
        x.values[i] = sibling.values[0]

        if not child.leaf:
            child.children.append(sibling.children[0])
            sibling.children.pop(0)

        sibling.keys.pop(0)
        sibling.values.pop(0)
        sibling.n -= 1

    def _merge(self, x, i):
        child = x.children[i]
        sibling = x.children[i + 1]

        child.keys.append(x.keys[i])
        child.values.append(x.values[i])

        child.keys.extend(sibling.keys)
        child.values.extend(sibling.values)

        if not child.leaf:
            child.children.extend(sibling.children)

        child.n = len(child.keys)

        x.keys.pop(i)
        x.values.pop(i)
        x.children.pop(i + 1)
        x.n -= 1

    def range_query(self, low, high):
        result = []
        self._range_query(self.root, low, high, result)
        return result

    def _range_query(self, node, low, high, result):
        i = 0
        while i < node.n and node.keys[i] < low:
            i += 1

        while i < node.n and node.keys[i] <= high:
            if not node.leaf:
                self._range_query(node.children[i], low, high, result)
            result.append(node.keys[i])
            i += 1

        if not node.leaf and i <= node.n:
            if i < len(node.children):
                self._range_query(node.children[i], low, high, result)

    def __len__(self):
        return self.size
