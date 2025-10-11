# dlab/data_strcutre/non_linea_data_strcutre/tree.py

# =================== Base Classes ===================
class BaseTree:
    def insert(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def search(self, key):
        raise NotImplementedError

    def traverse_inorder(self):
        raise NotImplementedError

    def traverse_preorder(self):
        raise NotImplementedError

    def traverse_postorder(self):
        raise NotImplementedError

    def traverse_level_order(self):
        raise NotImplementedError

# ================== Binary Tree ==================
class BinaryTree(BaseTree):
    class Node:
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None

    def __init__(self):
        self.root = None

    def insert(self, key):
        if not self.root:
            self.root = self.Node(key)
        else:
            self._insert_recursive(self.root, key)

    def _insert_recursive(self, current, key):
        if key < current.key:
            if current.left:
                self._insert_recursive(current.left, key)
            else:
                current.left = self.Node(key)
        else:
            if current.right:
                self._insert_recursive(current.right, key)
            else:
                current.right = self.Node(key)

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        if not node:
            return False
        if node.key == key:
            return True
        elif key < node.key:
            return self._search_recursive(node.left, key)
        else:
            return self._search_recursive(node.right, key)

    def traverse_inorder(self):
        def _inorder(node):
            return _inorder(node.left) + [node.key] + _inorder(node.right) if node else []
        return _inorder(self.root)

    def traverse_preorder(self):
        def _preorder(node):
            return [node.key] + _preorder(node.left) + _preorder(node.right) if node else []
        return _preorder(self.root)

    def traverse_postorder(self):
        def _postorder(node):
            return _postorder(node.left) + _postorder(node.right) + [node.key] if node else []
        return _postorder(self.root)

    def traverse_level_order(self):
        result = []
        if not self.root:
            return result
        queue = [self.root]  # use list as queue
        while queue:
            node = queue.pop(0)  # pop from front
            result.append(node.key)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

# ================== Binary Search Tree ==================
class BinarySearchTree(BaseTree):
    class Node:
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None

    def __init__(self):
        self.root = None

    def insert(self, key):
        def _insert(node, key):
            if not node:
                return self.Node(key)
            if key < node.key:
                node.left = _insert(node.left, key)
            elif key > node.key:
                node.right = _insert(node.right, key)
            return node
        self.root = _insert(self.root, key)

    def search(self, key):
        def _search(node, key):
            if not node:
                return False
            if node.key == key:
                return True
            elif key < node.key:
                return _search(node.left, key)
            else:
                return _search(node.right, key)
        return _search(self.root, key)

    def delete(self, key):
        def _delete(node, key):
            if not node:
                return node
            if key < node.key:
                node.left = _delete(node.left, key)
            elif key > node.key:
                node.right = _delete(node.right, key)
            else:
                # Node found
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left
                else:
                    temp = self._min_value_node(node.right)
                    node.key = temp.key
                    node.right = _delete(node.right, temp.key)
            return node

        self.root = _delete(self.root, key)

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def traverse_inorder(self):
        def _inorder(node):
            return _inorder(node.left) + [node.key] + _inorder(node.right) if node else []
        return _inorder(self.root)

    def traverse_preorder(self):
        def _preorder(node):
            return [node.key] + _preorder(node.left) + _preorder(node.right) if node else []
        return _preorder(self.root)

    def traverse_postorder(self):
        def _postorder(node):
            return _postorder(node.left) + _postorder(node.right) + [node.key] if node else []
        return _postorder(self.root)

    def traverse_level_order(self):
        result = []
        if not self.root:
            return result
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            result.append(node.key)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

# ================== AVL Tree ==================
class AVLTree(BaseTree):
    class Node:
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None
            self.height = 1

    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _height(self, node):
        return node.height if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    def _rotate_right(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _balance(self, node):
        self._update_height(node)
        balance = self._balance_factor(node)

        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _insert(self, node, key):
        if not node:
            return self.Node(key)
        elif key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node
        return self._balance(node)

    def search(self, key):
        def _search(node, key):
            if not node:
                return False
            if node.key == key:
                return True
            elif key < node.key:
                return _search(node.left, key)
            else:
                return _search(node.right, key)
        return _search(self.root, key)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if not node:
            return node
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            temp = self._min_value_node(node.right)
            node.key = temp.key
            node.right = self._delete(node.right, temp.key)
        return self._balance(node)

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def traverse_inorder(self):
        def _inorder(node):
            return _inorder(node.left) + [node.key] + _inorder(node.right) if node else []
        return _inorder(self.root)

    def traverse_preorder(self):
        def _preorder(node):
            return [node.key] + _preorder(node.left) + _preorder(node.right) if node else []
        return _preorder(self.root)

    def traverse_postorder(self):
        def _postorder(node):
            return _postorder(node.left) + _postorder(node.right) + [node.key] if node else []
        return _postorder(self.root)

    def traverse_level_order(self):
        result = []
        if not self.root:
            return result
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            result.append(node.key)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

# ================== Red-Black Tree ==================
class RedBlackTree(BaseTree):
    class Node:
        def __init__(self, key):
            self.key = key
            self.color = 'red'
            self.left = None
            self.right = None
            self.parent = None

    def __init__(self):
        self.NIL_LEAF = self.Node(None)
        self.NIL_LEAF.color = 'black'
        self.NIL_LEAF.left = None
        self.NIL_LEAF.right = None
        self.root = self.NIL_LEAF

    def insert(self, key):
        new_node = self.Node(key)
        new_node.left = self.NIL_LEAF
        new_node.right = self.NIL_LEAF
        self._bst_insert(self.root, new_node)
        self._fix_insert(new_node)

    def _bst_insert(self, root, node):
        if self.root == self.NIL_LEAF:
            self.root = node
            self.root.color = 'black'
            self.root.parent = None
            return
        current = self.root
        parent = None
        while current != self.NIL_LEAF:
            parent = current
            if node.key < current.key:
                current = current.left
            else:
                current = current.right
        node.parent = parent
        if node.key < parent.key:
            parent.left = node
        else:
            parent.right = node

    def _fix_insert(self, node):
        while node != self.root and node.parent and node.parent.color == 'red':
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle and uncle.color == 'red':
                    node.parent.color = 'black'
                    uncle.color = 'black'
                    node.parent.parent.color = 'red'
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._rotate_left(node)
                    node.parent.color = 'black'
                    node.parent.parent.color = 'red'
                    self._rotate_right(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle and uncle.color == 'red':
                    node.parent.color = 'black'
                    uncle.color = 'black'
                    node.parent.parent.color = 'red'
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._rotate_right(node)
                    node.parent.color = 'black'
                    node.parent.parent.color = 'red'
                    self._rotate_left(node.parent.parent)
        self.root.color = 'black'

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL_LEAF:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL_LEAF:
            x.right.parent = y
        x.parent = y.parent
        if not y.parent:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def search(self, key):
        node = self._search_node(self.root, key)
        return node != self.NIL_LEAF and node.key == key

    def _search_node(self, node, key):
        if node == self.NIL_LEAF or node is None:
            return self.NIL_LEAF
        if key == node.key:
            return node
        elif key < node.key:
            return self._search_node(node.left, key)
        else:
            return self._search_node(node.right, key)

    def delete(self, key):
        # deletion in red-black trees is complex; omitted for brevity
        pass

    def traverse_inorder(self):
        def _inorder(node):
            if node != self.NIL_LEAF:
                return _inorder(node.left) + [node.key] + _inorder(node.right)
            else:
                return []
        return _inorder(self.root)

    def traverse_preorder(self):
        def _preorder(node):
            if node != self.NIL_LEAF:
                return [node.key] + _preorder(node.left) + _preorder(node.right)
            else:
                return []
        return _preorder(self.root)

    def traverse_postorder(self):
        def _postorder(node):
            if node != self.NIL_LEAF:
                return _postorder(node.left) + _postorder(node.right) + [node.key]
            else:
                return []
        return _postorder(self.root)

    def traverse_level_order(self):
        result = []
        if self.root == self.NIL_LEAF or not self.root:
            return result
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            if node != self.NIL_LEAF:
                result.append(node.key)
                if node.left != self.NIL_LEAF:
                    queue.append(node.left)
                if node.right != self.NIL_LEAF:
                    queue.append(node.right)
        return result

# ================== Trie ==================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie(BaseTree):
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end_of_word

    def delete(self, word):
        def _delete(node, word, index):
            if index == len(word):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                return len(node.children) == 0
            ch = word[index]
            if ch in node.children:
                should_delete = _delete(node.children[ch], word, index + 1)
                if should_delete:
                    del node.children[ch]
                    return len(node.children) == 0
            return False
        _delete(self.root, word, 0)

    def traverse_inorder(self):
        result = []

        def _dfs(node, prefix):
            if node.is_end_of_word:
                result.append(prefix)
            for ch, child in node.children.items():
                _dfs(child, prefix + ch)

        _dfs(self.root, "")
        return result

    def traverse_preorder(self):
        return self.traverse_inorder()

    def traverse_postorder(self):
        return self.traverse_inorder()

    def traverse_level_order(self):
        return self.traverse_inorder()

# ================== N-ary Tree ==================
class NAryNode:
    def __init__(self, key):
        self.key = key
        self.children = []

class NAryTree(BaseTree):
    def __init__(self):
        self.root = None

    def insert(self, key, parent=None):
        new_node = NAryNode(key)
        if not self.root:
            self.root = new_node
            return
        # Insert under parent if provided
        if parent:
            parent_node = self._find(self.root, parent)
            if parent_node:
                parent_node.children.append(new_node)

    def _find(self, node, key):
        if node.key == key:
            return node
        for child in node.children:
            result = self._find(child, key)
            if result:
                return result
        return None

    def search(self, key):
        def _search(node, key):
            if node.key == key:
                return True
            for child in node.children:
                if _search(child, key):
                    return True
            return False
        return _search(self.root, key) if self.root else False

    def traverse_inorder(self):
        result = []

        def _preorder(node):
            if node:
                result.append(node.key)
                for child in node.children:
                    _preorder(child)
        _preorder(self.root)
        return result

    def traverse_preorder(self):
        return self.traverse_inorder()

    def traverse_postorder(self):
        result = []

        def _postorder(node):
            if node:
                for child in node.children:
                    _postorder(child)
                result.append(node.key)
        _postorder(self.root)
        return result

    def traverse_level_order(self):
        result = []
        if not self.root:
            return result
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            result.append(node.key)
            for child in node.children:
                queue.append(child)
        return result