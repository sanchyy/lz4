import argparse
import struct
import time

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

MAX_OFFSET = 2**(8*2) - 1
MIN_MATCH = 4
LIMIT_BYTES = 13  # Els ultims 13 bytes no els comprimim


def config_args():
    parser = argparse.ArgumentParser(description="lz4 algorithm to compress and deflate files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '-compress', action='store_true')
    group.add_argument('-d', '-decompress', action='store_false')
    parser.add_argument('file')
    return parser.parse_args()

def read_file(path_file):
    f = open(path_file, "r")
    res = f.read()
    f.close()
    return res

def decompress(filename):
    with open(filename, "rb") as stream:
        decompressed_text = read_blocks(stream)

    decompressed_file = open(f"{filename}.out", "wb")
    # decompressed_file = open('.'.join(filename.split('.')[:-1]), "wb")
    decompressed_file.write(decompressed_text)
    decompressed_file.close()

def read_blocks(stream):
    print("hola")
    output = bytearray()
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
        match_length = token[0] & 0x0F
        if match_length == 15:
            match_length += calculate_lsic(stream)
        match_length += 4

        # number of bytes already decoded

        output += literal
        output_length = len(output)

        duplication_starting_point = len(output) - offset
        min_sequence = min(match_length, offset)
        while min_sequence > 0:
            output += output[duplication_starting_point:duplication_starting_point + min_sequence]
            match_length -= min_sequence
            duplication_starting_point += min_sequence
            min_sequence = min(match_length, offset)

        token = stream.read(1)

    return output

def compress(filename):
    with open(filename, "rb") as f:
        buff = bytearray(f.read())
        compressed_file = compress_sequence(buff)
    f = open(f"{filename}.lz4", 'wb')
    f.write(compressed_file)
    f.close()

def compress_sequence(buff):
    buff_len = len(buff)
    table = {}
    read_ptr = 0
    write_ptr = 0
    literal_ptr = 0 # pointer of the initial position of the literal
    output = bytearray()
    max_index = buff_len - LIMIT_BYTES
    while read_ptr < max_index:
        val = bytes(buff[read_ptr:read_ptr+4])
        match_ptr = find_match(table, val, read_ptr)
        if match_ptr:
            match_len = get_max_match_len(buff, match_ptr, read_ptr)

            output += write_block(buff, buff[literal_ptr:read_ptr], read_ptr - match_ptr, match_len)
            read_ptr += match_len
            literal_ptr = read_ptr
        else:
            table[val] = read_ptr
            read_ptr += 1

    output += write_block(buff, buff[literal_ptr:buff_len], 0, 0)
    return output

def write_block(buff, literal, offset, match_len):
    # definitions
    token = bytearray(1)
    extended1 = bytearray()
    extended2 = bytearray()
    little_endian_offset = bytearray()

    literal_len = len(literal)
    if literal_len >= 15:
        # token first 4 bits
        token[0] = (15 << 4)
        remain_len = literal_len - 15

        extended1_len = remain_len // 255
        extended1 = bytearray([255] * extended1_len)
        extended_last_byte = remain_len % 255
        if extended_last_byte:
            extended1 += bytearray([extended_last_byte])
    else:
        token[0] = (literal_len << 4)

    if match_len > 0:
        little_endian_offset = bytes(value_to_little_endian(offset))

        match_len -= 4
        if match_len >= 15:
            # token last 4 bits
            token[0] = token[0] | 15
            remain_len = match_len - 15

            extended2_len = remain_len // 255
            extended2 = bytearray([255] * extended2_len)
            extended_last_byte = remain_len % 255
            if extended_last_byte:
                extended2 += bytearray([extended_last_byte])

        else:
            token[0] = token[0] | match_len

    return token + extended1 + literal + little_endian_offset + extended2
    
def find_match(table, value, ptr) -> int:
    pos = table.get(value)
    if pos and (ptr - pos) < MAX_OFFSET: 
        return pos
    else:
        return None 

def get_max_match_len(buff, it1, it2) -> int:
    """
    it1 -> previous occurence of the word
    it2 -> actual occurrence
    returns max match length
    """
    match_len = 0
    while buff[it1] == buff[it2]:
        match_len += 1
        it1 += 1
        it2 += 1
    return match_len

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
        return struct.unpack("<H", little_endian)[0]
    else:
        return 0

def value_to_little_endian(value):
    return struct.pack("<H", value)

def main():
    args = config_args()
    print(args)
    if args.c:
        compress(args.file)
    else:
        decompress(args.file)


if __name__ == '__main__':
    main()
    

