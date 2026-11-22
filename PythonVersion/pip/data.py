from pathlib import Path

# Starting values representing which byte to start writing
# at for different information / data
HUFFMAN_START = 331
HUFFMAN_PAD_START = 6
SERIAL_START = 11
SERIAL_PAD_START = 4
SERIAL_COUNT_START = 8

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


# WRITING DECOMPRESSED -> COMPRESSED

# Writes the generated huffman codes corresponding to the original files contents
def write_codes(read_path, codes, write_path) -> int:
    buffer = [0] * 8
    buffer_size = 0
    BUFFER_CAPACITY = 8 

    path = Path(write_path) 

    try:
        with open(read_path, "rb") as r:
            content = r.read()

        with open(write_path, "r+b") as f:
            f.seek(HUFFMAN_START, 0)

            # Read char by char, find the corresponding code and append to buffer
            for byte in content:
                code = codes[byte]

                for c in code:
                    buffer[buffer_size] = int(c)
                    buffer_size += 1

                    if buffer_size == BUFFER_CAPACITY:
                        n = buffer_to_number(buffer)
                        f.write(n.to_bytes(1, 'big'))
                        buffer_size = 0 


            padding_start_bit = -1 # -1 indicates the final byte wasnt padded

            if buffer_size == 0:
                f.seek(HUFFMAN_PAD_START, 0)
                s = f"{padding_start_bit}"
                f.write(s.encode())
                return 1

            # If buffer is not empty after encoding
            # Have to add padding bits to make a full byte
            padding_start_bit = buffer_size # Save where padded bit started

            while buffer_size != 8:
                buffer[buffer_size] = 0
                buffer_size += 1

            # Write last byte
            n = buffer_to_number(buffer)
            f.write(n.to_bytes(1, 'big'))

            # Write encoded files padding start bit
            f.seek(HUFFMAN_PAD_START, 0)
            s = f"+{padding_start_bit}"
            f.write(s.encode())

    except Exception as e:
        print(f"\033[31mFile error occured {e}\n\033[0m")

        if path.exists():
            path.unlink()
        return -1

    return 1

# Writes the serialized representation of the tree to file
# Uses the same method as writing the huffman codes
def write_serial(serial, write_path) -> int:
    buffer = [0] * 8
    buffer_size = 0
    BUFFER_CAPACITY = 8
    byte_counter = 0

    path = Path(write_path) 
    
    try:
        with open(write_path, "r+b") as f:
            f.seek(SERIAL_START, 0)

            i = 0
            while i < len(serial):
                if serial[i] == '0':
                    buffer[buffer_size] = 0
                    buffer_size += 1
                    if buffer_size == BUFFER_CAPACITY:
                        n = buffer_to_number(buffer)
                        f.write(n.to_bytes(1, 'big'))
                        buffer_size = 0
                        byte_counter += 1
                    i += 1
                    continue

                if serial[i] == '1':
                    buffer[buffer_size] = 1
                    buffer_size += 1
                    if buffer_size == BUFFER_CAPACITY:
                        n = buffer_to_number(buffer)
                        f.write(n.to_bytes(1, 'big'))
                        buffer_size = 0
                        byte_counter += 1

                    i += 1
                    num = ord(serial[i])
                    binary = f"{num:08b}"

                    for b in binary:
                        buffer[buffer_size] = int(b)
                        buffer_size += 1
                        if buffer_size == BUFFER_CAPACITY:
                            n = buffer_to_number(buffer)
                            f.write(n.to_bytes(1, 'big'))
                            buffer_size = 0
                            byte_counter += 1

                    i += 1

            padding_start_bit = -1

            if buffer_size == 0:
                f.seek(SERIAL_PAD_START, 0)
                s = f"{padding_start_bit}"
                f.write(s.encode())
                f.seek(SERIAL_COUNT_START, 0)
                byte_counter -= 1

                if byte_counter >= 0 and byte_counter <= 9:
                    s = f"00{byte_counter}"
                elif byte_counter >= 10 and byte_counter <= 99:
                    s = f"0{byte_counter}"
                else:
                    s = f"{byte_counter}"

                f.write(s.encode()) 
                return 1
 
            padding_start_bit = buffer_size

            while buffer_size != 8:
                buffer[buffer_size] = 0
                buffer_size += 1

            byte_counter += 1

            # Write last byte
            n = buffer_to_number(buffer)
            f.write(n.to_bytes(1, 'big'))

            # Write serials padding start bit
            f.seek(SERIAL_PAD_START, 0)
            s = f"+{padding_start_bit}"
            f.write(s.encode())

            # Write count
            f.seek(SERIAL_COUNT_START, 0)

            if byte_counter >= 0 and byte_counter <= 9:
                s = f"00{byte_counter}"
            elif byte_counter >= 10 and byte_counter <= 99:
                s = f"0{byte_counter}"
            else:
                s = f"{byte_counter}"

            f.write(s.encode())

    except Exception as e:
        print(f"\033[31mFile error occured {e}\n\033[0m")

        if path.exists():
            path.unlink()
        return -1

    return 1

def write_encoded_file(read_path, ds, write_path) -> int:
    path = Path(write_path)

    # Write signature "COMP" at beggining of file
    try:
        with open(write_path, "wb") as f:
            f.seek(0, 0)
            f.write(b"COMP")

    except Exception as e:
        print(f"\033[31mFile error occured {e}\n\033[0m")

        if path.exists():
            path.unlink()
        return -1

    ws = write_serial(ds[1], write_path)

    wc = write_codes(read_path, ds[0], write_path)

    if ws == -1 or wc == -1:
        return -1

    return 1


# WRITING COMPRESSED -> DECOMPRESSED

# Reads a decompressed file, and decodes it to write
# back the files regular contents
def write_decoded_file(read_path, codes, write_path) -> int:
    buffer = []
    path = Path(write_path)

    try:
        with open(read_path, "rb") as r, open(write_path, "wb") as f:
            r.seek(HUFFMAN_PAD_START,0)
            padding_bit = r.read(2)
            padded = padding_bit[0] != ord('-')

            last_byte = r.seek(0, 2) - 1
            r.seek(HUFFMAN_START, 0)

            while r.tell() < last_byte:
                byte = num_to_bin(int.from_bytes(r.read(1), 'big'))

                for b in byte:
                    buffer.append(str(b))

                    if "".join(buffer) in codes:
                        value = codes["".join(buffer)]
                        f.write(value.to_bytes(1, 'big'))
                        buffer = []

            byte = num_to_bin(int.from_bytes(r.read(1), 'big')) # Last byte of file
            last_bit = 8 if not padded else int(chr(padding_bit[1]))

            for i in range(0, last_bit):
                buffer.append(str(byte[i]))

                if "".join(buffer) in codes:
                    value = codes["".join(buffer)]
                    f.write(value.to_bytes(1, 'big'))
                    buffer = []

    except Exception as e:
        print("File data")
        print(f"\033[31mFile error occured: {e}\n\033[0m")

        if path.exists():
            path.unlink()
        return -1

    return 1
