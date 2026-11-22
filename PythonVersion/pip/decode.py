from collections import deque
from .data import HUFFMAN_START, HUFFMAN_PAD_START, SERIAL_START, SERIAL_PAD_START, SERIAL_COUNT_START

# CLASS DEFINITIONS
class InternalNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class LeafNode:
    def __init__(self, val):
        self.val = val

# FUNCTIONS
def num_to_bin(n) -> list[int]:
    buf = [0] * 8
    index = 7

    if n == 0:
        return buf

    while n > 0:
        buf[index] = n % 2
        index -= 1
        n = n >> 1

    return buf

def buffer_to_number(buf) -> int:
    # Converts a buffer which represent an unsigned 8-bit value to a int
    return (128 * buf[0]) + (64 * buf[1]) + (32 * buf[2]) + (16 * buf[3]) + (8 * buf[4]) + (4 * buf[5]) + (2 * buf[6]) + (1 * buf[7])

def build_serial(read_path) -> str:
    serial = []

    byte_bits = [0] * 8
    byte_bits_size = 0
    BYTE_CAPACITY = 8
    reading_byte = False


    try:
        with open(read_path, "rb") as f:
            f.seek(SERIAL_PAD_START, 0)
            padding_bit = f.read(2)
            padded = padding_bit[0] != ord('-')

            f.seek(SERIAL_COUNT_START, 0)
            n = f.read(3)
            number_of_bytes = (int(chr(n[0])) * 100) + (int(chr(n[1])) * 10) + int(chr(n[2]))

            f.seek(SERIAL_START, 0)
            contents = f.read(number_of_bytes) if not padded else f.read(number_of_bytes - 1)

            for c in contents:
                bits = num_to_bin(c)

                for b in bits:
                    # Reading value that the leaf node holds
                    if reading_byte:
                        byte_bits[byte_bits_size] = b
                        byte_bits_size += 1

                        if byte_bits_size == BYTE_CAPACITY:
                            n = buffer_to_number(byte_bits)
                            byte_bits_size = 0
                            serial.append(chr(n))
                            reading_byte = False

                        continue

                    if b == 0: # Internal Node
                        serial.append('0')
                    elif b == 1: # Leaf Node
                        serial.append('1')
                        reading_byte = True

            if not padded:
                return "".join(serial)
            
            f.seek(SERIAL_START + number_of_bytes - 1, 0)
            padded_byte = num_to_bin(int.from_bytes(f.read(1), 'big'))

            # Read padded but up until when padding starts
            for i in range(0, int(chr(padding_bit[1]))):
                if reading_byte:
                    byte_bits[byte_bits_size] = padded_byte[i]
                    byte_bits_size += 1

                    if byte_bits_size == BYTE_CAPACITY:
                        n = buffer_to_number(byte_bits)
                        byte_bits_size = 0
                        serial.append(chr(n))
                        reading_byte = False

                    continue

                if padded_byte[i] == 0:
                    serial.append('0')
                elif padded_byte[i] == 1:
                    serial.append('1')
                    reading_byte = True

            return "".join(serial)


    except Exception as e:
        print("file decode")
        print(f"\033[31mFile error occured: {e}\n\033[0m")
        return None

def build_tree_from_serial(serial):
    # Reached a leaf node
    if serial[0] == '1':
        serial.popleft()
        value = serial.popleft()
        return LeafNode(value)

    # Internal Node operations
    serial.popleft()
    i = InternalNode(None, None)

    i.left = build_tree_from_serial(serial)
    i.right = build_tree_from_serial(serial)

    return i

def build_codes_from_tree(node, codes, code) -> dict[str, int]:
    # When reaching a leaf node returns the value associated with the code
    if isinstance(node, LeafNode):
        return {"".join(code) : ord(node.val)}

    # Go through the left subtree
    code.append('0')
    entry = build_codes_from_tree(node.left, codes, code)
    code.pop()

    codes |= entry

    # Go through the right subtree
    code.append('1')
    entry = build_codes_from_tree(node.right, codes, code)
    code.pop()

    codes |= entry

    return codes

def get_codes(read_path) -> dict[str, int]:
    try:
        with open(read_path, "rb") as f:
            f.seek(0, 0)
            signature = f.read(4)
            if signature[0] != ord('C') or signature[1] != ord('O') or signature[2] != ord('M') or signature[3] != ord('P'):
                print(f"\033[31mGiven file is not a .pip compressed file\n\033[0m")
                return None

    except Exception as e:
        print(f"\033[31mFile error occured {e}\n\033[0m")
        return None

    serial = build_serial(read_path)
    if serial is None:
        return None

    tree = build_tree_from_serial(deque(serial))
    return build_codes_from_tree(tree, {}, [])
