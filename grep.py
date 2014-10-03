#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, re, sys

def matches(line, regexp):
    return regexp.search(line) != None

def matches_any(line, regexps):
    for regexp in regexps:
        if matches(line, regexp):
            return True
    return False

def grep(file, expressions):
    found = False
    for line in file:
        if matches_any(line, expressions):
            sys.stdout.write(line)
            found = True
    return found

def main():
    parser = argparse.ArgumentParser(description='Prints lines matching a regular expression.')
    parser.add_argument('-e', metavar='PATTERN', help='Regular expression.')
    parser.add_argument('-f', metavar='FILE', help='File with regular expressions, one by line.')
    parser.add_argument('file', nargs='*', help='File.')

    args = parser.parse_args()

    regexps = []

    if args.e != None:
        regexps.append(re.compile(args.e))

    if args.f:
        f = open(args.f, 'U')
        try:
            for line in f:
                regexps.append(re.compile(line.rstrip('\n')))
        finally:
            f.close()

    found = False
    if len(args.file) == 0:
        if grep(sys.stdin, regexps):
            found = True
    else:
        for filename in args.file:
            if filename == '-':
                if grep(sys.stdin, regexps):
                    found = True
            else:
                file = open(filename, 'U')
                try:
                    if grep(file, regexps):
                        found = True
                finally:
                    file.close()

    if found:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()