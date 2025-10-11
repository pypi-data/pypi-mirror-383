# Shared singleton stack (optional)
_shared_stack = []

def push(item):
    _shared_stack.append(item)

def pop():
    if not _shared_stack:
        raise IndexError("Pop from empty stack")
    return _shared_stack.pop()

def peek():
    if not _shared_stack:
        raise IndexError("Peek from empty stack")
    return _shared_stack[-1]

def is_empty():
    return len(_shared_stack) == 0

def size():
    return len(_shared_stack)

def display_all():
    return _shared_stack.copy()

def search(item):
    return item in _shared_stack

def clear():
    _shared_stack.clear()