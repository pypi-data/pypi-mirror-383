# dlab/data_strcutre/linked_list.py

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = new_node
    
    def insert_at_beginning(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete(self, data):
        temp = self.head
        prev = None
        while temp:
            if temp.data == data:
                if prev:
                    prev.next = temp.next
                else:
                    self.head = temp.next
                return True
            prev = temp
            temp = temp.next
        return False

    def clear(self):
        self.head = None

    def search(self, data):
        temp = self.head
        while temp:
            if temp.data == data:
                return True
            temp = temp.next
        return False
    
    def display(self):
        elements = []
        temp = self.head
        while temp:
            elements.append(temp.data)
            temp = temp.next
        return elements

    def reverse(self):
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    def insert(self, index, data):
        if index == 0:
            self.insert_at_beginning(data)
            return
        temp = self.head
        for _ in range(index - 1):
            if temp is None:
                print("Index out of bounds")
                return
            temp = temp.next
        if temp is None:
            print("Index out of bounds")
            return
        new_node = Node(data)
        new_node.next = temp.next
        temp.next = new_node

class DoublyNode(Node):
    def __init__(self, data):
        super().__init__(data)
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = new_node
        else:
            temp = self.head
            while temp.next:
                temp = temp.next
            temp.next = new_node
            new_node.prev = temp

    def insert_at_beginning(self, data):
        new_node = DoublyNode(data)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        self.head = new_node

    def delete(self, data):
        temp = self.head
        while temp:
            if temp.data == data:
                if temp.prev:
                    temp.prev.next = temp.next
                else:
                    self.head = temp.next
                if temp.next:
                    temp.next.prev = temp.prev
                return True
            temp = temp.next
        return False

    def clear(self):
        self.head = None

    def search(self, data):
        temp = self.head
        while temp:
            if temp.data == data:
                return True
            temp = temp.next
        return False

    def display(self):
        elements = []
        temp = self.head
        while temp:
            elements.append(temp.data)
            temp = temp.next
        return elements

    def reverse(self):
        temp = None
        current = self.head
        while current:
            temp = current.prev
            current.prev = current.next
            current.next = temp
            current = current.prev
        if temp:
            self.head = temp.prev

    def insert(self, index, data):
        if index == 0:
            self.insert_at_beginning(data)
            return
        temp = self.head
        for _ in range(index - 1):
            if temp is None:
                print("Index out of bounds")
                return
            temp = temp.next
        if temp is None:
            print("Index out of bounds")
            return
        new_node = DoublyNode(data)
        new_node.next = temp.next
        new_node.prev = temp
        if temp.next:
            temp.next.prev = new_node
        temp.next = new_node

class CircularLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = self.head
        else:
            temp = self.head
            while temp.next != self.head:
                temp = temp.next
            temp.next = new_node
            new_node.next = self.head

    def insert_at_beginning(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            new_node.next = self.head
        else:
            temp = self.head
            while temp.next != self.head:
                temp = temp.next
            new_node.next = self.head
            temp.next = new_node
            self.head = new_node

    def delete(self, data):
        if not self.head:
            return False
        current = self.head
        prev = None
        while True:
            if current.data == data:
                if prev:
                    prev.next = current.next
                else:
                    # Deleting head
                    temp = self.head
                    while temp.next != self.head:
                        temp = temp.next
                    temp.next = current.next
                    self.head = current.next
                return True
            prev = current
            current = current.next
            if current == self.head:
                break
        return False

    def clear(self):
        self.head = None

    def search(self, data):
        temp = self.head
        if not temp:
            return False
        while True:
            if temp.data == data:
                return True
            temp = temp.next
            if temp == self.head:
                break
        return False

    def display(self):
        elements = []
        if not self.head:
            return elements
        temp = self.head
        while True:
            elements.append(temp.data)
            temp = temp.next
            if temp == self.head:
                break
        return elements

    def insert(self, index, data):
        if not self.head:
            if index == 0:
                self.head = Node(data)
                self.head.next = self.head
            else:
                print("Index out of bounds")
            return
        if index == 0:
            self.insert_at_beginning(data)
            return
        temp = self.head
        for _ in range(index - 1):
            temp = temp.next
            if temp == self.head:
                print("Index out of bounds")
                return
        new_node = Node(data)
        new_node.next = temp.next
        temp.next = new_node