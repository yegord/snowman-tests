#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, subprocess, sys, threading

class ExecutionTimeout(Exception):
    def __str__(self):
        return "Execution timeout."

class UnexpectedExitCode(Exception):
    def __init__(self, returned, expected):
        self.returned = returned
        self.expected = expected

    def __str__(self):
        return "Exit code is %d, expected %d." % (self.returned, self.expected)

def run(cmdline, stdout=None, stderr=None, **kwargs):
    try:
        out = None
        err = None
        if (stdout != None):
            out = open(stdout, "w")
        if (stderr != None):
            err = open(stderr, "w")
        return execute(cmdline, stdout=out, stderr=err, **kwargs)
    finally:
        if out != None:
            out.close()
        if err != None:
            err.close()

def execute(cmdline, timeout=None, **kwargs):
    class Launcher(object):
        def __init__(self, cmdline, **kwargs):
            self.cmdline = cmdline
            self.kwargs = kwargs
            self.process = None
            self.exception = None

        def __call__(self):
            try:
                self.process = subprocess.Popen(self.cmdline, **self.kwargs)
                self.process.communicate()
            except OSError as e:
                self.exception = e

    launcher = Launcher(cmdline, **kwargs)

    thread = threading.Thread(target=launcher)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        launcher.process.terminate()
        thread.join()
        raise ExecutionTimeout()

    if launcher.exception != None:
        raise launcher.exception

    return launcher.process.returncode

def main():
    parser = argparse.ArgumentParser(description='Runs an executable.')
    parser.add_argument('--stdout', metavar='FILE', help='Redirect standard output of the program to this file.')
    parser.add_argument('--stderr', metavar='FILE', help='Redirect standard error of the program to this file.')
    parser.add_argument('--timeout', metavar='SEC', type=float, default=None, help='Kill the process after the given timeout.')
    parser.add_argument('--exit-code', type=int, default=None, help='Fail if the program does not exit with the given code.')
    parser.add_argument('program', help='Command to execute.')
    parser.add_argument('argument', nargs='*', help='Arguments to the program.')

    args = parser.parse_args()

    try:
        exit_code = run([args.program] + args.argument, stdout=args.stdout, stderr=args.stderr, timeout=args.timeout)
        if args.exit_code != None and args.exit_code != exit_code:
            raise UnexpectedExitCode(exit_code, args.exit_code)
    except ExecutionTimeout as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(100)
    except UnexpectedExitCode as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(101)

    if args.exit_code == None:
        sys.exit(exit_code)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
