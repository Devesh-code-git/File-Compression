# Sorts the bytes with 1 or more frequencies in ascending order
def fbsort(frequencies, bytes_) -> list[int]:
    if frequencies is None or bytes_ is None:
        return []

    for i in range(0, len(bytes_)):
        for j in range(0, len(bytes_) - 1):
            byte_one = bytes_[j]
            byte_two = bytes_[j + 1]

            if frequencies[byte_one] > frequencies[byte_two]:
                bytes_[j] = byte_two
                bytes_[j + 1] = byte_one

    return bytes_

# Sort algo that works with tree nodes instead
# Only loops over once because lowest two nodes are
# combined into one node which will be at the front of the list
# Only have to propergate it upward, while evreything else is sorted
def tsort(nodes) -> list[LeafNode | InternalNode]:
    if nodes is None:
        return []

    for i in range(0, len(nodes) - 1):
        node_one = nodes[i]
        node_two = nodes[i + 1]

        if node_one.weight > node_two.weight:
            nodes[i] = node_two
            nodes[i + 1] = node_one

    return nodes
