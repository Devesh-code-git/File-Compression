import sys
from . import encode
from . import decode
from .data import write_encoded_file, write_decoded_file

# Gets a name from the given file as the write path
def get_write_path(input_file_name, compress: bool) -> str:
    reversed_name = input_file_name[::-1]
    name = []
    write = False

    for i in reversed_name:
        if write:
            name.append(i)

        if i == '.': # Once past the file type, write name of file only
            write = True

    # If file didnt have a type
    if len(name) == 0:
        for i in reversed_name:
            name.append(i)

    if compress:
        name = name[::-1]
        name.append('.')
        name.append('p') # Compressed postfix, ex: file.pip
        name.append('i')
        name.append('p')
    else:
        name = name[::-1]
        name.append('_') # Decompressed add-on, ex: file_dec
        name.append('d')
        name.append('e')
        name.append('c')

    return "".join(name)


def main():
    if (len(sys.argv)) != 3:
        print("\033[31mThis script is used to compress or decompress a .pip file, need an input file and one flag{-c, -d}.\033[0m")
        sys.exit(1)

    read_path = sys.argv[1] if sys.argv[2] == "-c" or sys.argv[2] == "-d" else sys.argv[2]
    flag = sys.argv[2] if read_path == sys.argv[1] else sys.argv[1]

    if flag == "-c":
        dict_serial = encode.get_codes(read_path)
        if dict_serial is None:
            exit(1)

        write_path = get_write_path(read_path, True)
        write_encoded_file(read_path, dict_serial, write_path)
    elif flag == "-d":
        codes = decode.get_codes(read_path)
        if codes is None:
            exit(1)

        write_path = get_write_path(read_path, False)
        write_decoded_file(read_path, codes, write_path)


if __name__ == "__main__":
    main()
