from .sort import fbsort
from .tree import *

def get_frequencies(path) -> list[int]:
    try:
        with open(path, "rb") as f:
            content = f.read()

        frequencies = [0] * 256

        for i in content:
            frequencies[i] += 1

        return frequencies

    except Exception as e:
        print(f"\033[31mFile error occured: {e}\n\033[0m")
        return [-1]

# Returns an sorted array of bytes whose frequencies are greater than 0
def get_sorted_bytes(frequencies) -> list[int]:
    bytes_ = []

    for i in range(0, 256):
        if frequencies[i] != 0:
            bytes_.append(i)

    return fbsort(frequencies, bytes_)

# Gives the tree used to traverse and get the codes
def encode_tree(path) -> Tree:
    f = get_frequencies(path)
    if f == [-1]:
        return None

    b = get_sorted_bytes(f)

    return build_tree_from_frequencies(f, b)

# Traverses the tree and generates the codes for the different bytes
# And a serilization of the tree which will be used when writing to the file
def encode_dict(node, codes, code, serial) -> list[dict[int, str], list[str]]:
    # When reaching a leaf node returns the full code and the value it associated with
    if isinstance(node, LeafNode):
        serial.append('1')
        serial.append(chr(node.value))
        return [{node.value : "".join(code)}, serial]

    serial.append('0')

    # Go through the left subtree
    code.append('0')
    entry = encode_dict(node.left, codes, code, serial)
    code.pop()

    codes |= entry[0]
    serial = entry[1]

    # Go through the right subtree
    code.append('1')
    entry = encode_dict(node.right, codes, code, serial)
    code.pop()

    codes |= entry[0]
    serial = entry[1]

    return [codes, serial]

def get_codes(path) -> list[dict[int, str], list[str]]:
    t = encode_tree(path)
    if t is None:
        return None

    ds = encode_dict(t.root, {}, [], [])
    return ds
