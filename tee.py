#!/usr/bin/env python
# -*- coding: utf-8 -*-

# "THE JUICE-WARE LICENSE" (Revision 42)
#
# <yegor.derevenets@gmail.com> wrote this file. As long as you
# keep this notice, you can do whatever you want with this stuff.
# If we meet someday, and you think this stuff is worth it, you
# can buy me a glass of juice in return. Yegor Derevenets

import argparse, sys

def main():
    parser = argparse.ArgumentParser(description='Copy stdin to stdout and to the given files.')
    parser.add_argument('--append', action='store_true', help='Append to the given files, do not overwrite them.')
    parser.add_argument('file', nargs='*', help='File.')

    args = parser.parse_args()

    mode = args.append and 'a' or 'w'
    files = [sys.stdout] + [open(filename, mode) for filename in args.file]

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        for file in files:
            file.write(line)

if __name__ == '__main__':
    main()
