import argparse
import struct
import hashlib

"""
LZ4 SEQUENCE

1-byte      token
0-n bytes   literal-length
0-L bytes   literals
2-bytes     offset
0-n bytes   match-length

n -> tamany del window
m -> tamany del match

n = 8192
m = 128
"""




def config_args():
    parser = argparse.ArgumentParser(description="lz4 algorithm to compress and deflate files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--c', '--compress', action='store_true')
    group.add_argument('--d', '--decompress', action='store_false')
    parser.add_argument('file')
    return parser.parse_args()

def read_file(path_file):
    f = open(path_file, "r")
    res = f.read()
    f.close()
    return res


def decompress(filename):
    with open(filename, "rb") as stream:
        decompressed_text = read_blocks(stream, bytearray())

    print(decompressed_text)
    f = open(filename + '.out', "wb")
    f.write(decompressed_text)
    f.close()

def read_blocks(stream, output):
    # Primer byte del bloc -> token
    token = stream.read(1)
    while token:
        # Primera part (4 bits) del token -> mida (bytes) dels literals
        literal_length = (token[0] >> 4)
        if literal_length == 15:  # if 1111, we calculate Linear small-integer code (LSIC)
            literal_length += calculate_lsic(stream)
        
        # 'literal_length' bytes de literal
        literal = stream.read(literal_length)

        # offset per calcular següents literals a afegir
        offset_little_endian = bytes(stream.read(2))
        offset = little_endian_to_value(offset_little_endian)

        # mida de bytes a duplicar
        sequence_length = token[0] & 0x0F
        if sequence_length == 15:
            sequence_length += calculate_lsic(stream)
        sequence_length += 4

        # number of bytes already decoded
        output += literal
        output_length = len(output)

        duplication_starting_point = output_length - offset
        output += output[duplication_starting_point:duplication_starting_point+sequence_length]
        token = stream.read(1)

    return output


def calculate_lsic(stream):
    new_value = stream.read(1)[0]
    accumulator = new_value
    # anem acumulant el valor dels bytes mentre que siguin igual a 255
    while new_value == 255:
        new_value = stream.read(1)[0]
        accumulator += new_value
    return accumulator


def little_endian_to_value(little_endian):
    if little_endian:
        return struct.unpack("<h", little_endian)[0]
    else:
        return 0


def main():
    # args = config_args()
    # if args.c:
    #     print(hex2bin(args.file))
    #     # compress(args.file)
    # elif args.d:
    #     print(bin2hex(args.file))
    #     # decompress(args.file)
    decompress('../wells_the_invisible_man.txt.lz4')



if __name__ == '__main__':
    main()
    
