import argparse
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

def hex2bin(hex_value) -> str:
    return bin(int(hex_value, 16)).zfill(8).split('b')[1]

def bin2hex(bin_value) -> str:
    return hex(int(bin_value, 2))[2:]

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
    data = read_file(filename)
    for c in data:


def main():
    args = config_args()
    if args.c:
        print(hex2bin(args.file))
        # compress(args.file)
    else:
        print(bin2hex(args.file))
        # decompress(args.file)


if __name__ == '__main__':
    main()
    

