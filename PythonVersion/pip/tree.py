from .sort import tsort
from collections import deque

# CLASS DEFINITIONS
class InternalNode:
    def __init__(self, weight, left, right):
        self.weight = weight
        self.left = left
        self.right = right

    def combine(self, n) -> InternalNode:
        w = self.weight + n.weight
        return InternalNode(w, self, n)

class LeafNode:
    def __init__(self, value, weight):
        self.value = value
        self.weight = weight

    def combine(self, n) -> InternalNode:
        w = self.weight + n.weight
        return InternalNode(w, self, n)

class Tree:
    def __init__(self, root):
        self.root = root

# TREE HELPER AND BUILDER FUNCTIONS
def make_leaf_list(bytes_, frequencies) -> list[LeafNode]:
    nodes = deque([])
    for i in bytes_:
        n = make_leaf_node(i, frequencies)
        nodes.append(n)

    return nodes

def make_leaf_node(value, frequencies) -> LeafNode:
    weight = frequencies[value]
    return LeafNode(value, weight)

def build_tree_from_frequencies(frequencies, bytes_) -> Tree:
    if len(bytes_) == 0:
        return None

    # If file is made up of only one byte value
    if len(bytes_) == 1:
        value = bytes_[0]
        weight = frequencies[value]
        return Tree(LeafNode(value, weight))

    nodes = make_leaf_list(bytes_, frequencies)

    # Combine first two leaf nodes
    current_internal = nodes.popleft().combine(nodes.popleft())

    # If file is made up of only two byte values
    if len(bytes_) == 2:
        return Tree(current_internal)

    nodes.appendleft(current_internal)
    tsort(nodes)

    entry_one = None
    entry_two = None

    while len(nodes) > 1:
        entry_one = nodes.popleft()
        entry_two = nodes.popleft()

        if isinstance(entry_one, InternalNode) and isinstance(entry_two, LeafNode):
            current_internal = entry_two.combine(entry_one)
        else:
            current_internal = entry_one.combine(entry_two) 

        nodes.appendleft(current_internal)
        tsort(nodes)
    
    return Tree(current_internal)
