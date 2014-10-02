#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, difflib, os, sys, time

def main():
    parser = argparse.ArgumentParser(description='Compares two text files line by line.')
    parser.add_argument('-u', action='store_true', help='Produce unified diff.')
    parser.add_argument('--lines', type=int, default=3, help='Show so many lines of context.')
    parser.add_argument('file', nargs=2, help='File.')

    args = parser.parse_args()

    fromfile, tofile = args.file # as specified in the usage string

    fromdate = time.ctime(os.stat(fromfile).st_mtime)
    todate = time.ctime(os.stat(tofile).st_mtime)
    fromlines = open(fromfile, 'U').readlines()
    tolines = open(tofile, 'U').readlines()

    if args.u:
        diff = difflib.unified_diff(fromlines, tolines, fromfile, tofile,
                                    fromdate, todate, n=args.lines)
    else:
        diff = difflib.context_diff(fromlines, tolines, fromfile, tofile,
                                    fromdate, todate, n=args.lines)

    differ = False
    for line in diff:
        sys.stdout.write(line)
        differ = True

    if differ:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
