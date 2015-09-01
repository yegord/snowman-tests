#!/usr/bin/env python
# -*- coding: utf-8 -*-

# "THE JUICE-WARE LICENSE" (Revision 42)
#
# <yegor.derevenets@gmail.com> wrote this file. As long as you
# keep this notice, you can do whatever you want with this stuff.
# If we meet someday, and you think this stuff is worth it, you
# can buy me a glass of juice in return. Yegor Derevenets

import argparse, glob, itertools, ninja_syntax, os, sys

scriptdir = os.path.abspath(os.path.dirname(__file__))

def try_read_file(filename):
    if os.path.isfile(filename):
        with open(filename, 'U') as file:
            return file.read()
    return None

def try_read_int(filename):
    result = try_read_file(filename)
    if result != None:
        return int(result)
    else:
        return None

def try_read_lines(filename):
    result = try_read_file(filename)
    if result != None:
        return result.splitlines()
    else:
        return []

def write_file(filename, content):
    dirname = os.path.dirname(filename)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    with open(filename, 'w') as file:
        file.write(content)

class Generator(object):
    def __init__(self, builddir, decompiler = None):
        self.builddir = os.path.abspath(builddir)

        if not os.path.isdir(self.builddir):
            os.makedirs(self.builddir)

        escape_path = ninja_syntax.escape_path
        python = escape_path(sys.executable)

        self.output = open(os.path.join(self.builddir, 'build.ninja'), 'w')
        self.ninja = ninja_syntax.Writer(self.output)
        self.ninja.include(escape_path(os.path.join(scriptdir, 'rules.ninja')))
        self.ninja.variable('builddir', escape_path(self.builddir))
        self.ninja.variable('run', [python, escape_path(os.path.join(scriptdir, 'run.py'))])

        if sys.platform == 'win32':
            self.ninja.variable('shell', ['cmd', '/c'])
            self.ninja.variable('diff', [python, escape_path(os.path.join(scriptdir, 'diff.py'))])
            self.ninja.variable('grep', [python, escape_path(os.path.join(scriptdir, 'grep.py'))])
            self.ninja.variable('tee',  [python, escape_path(os.path.join(scriptdir, 'tee.py'))])

        if decompiler != None:
            decompiler = os.path.abspath(decompiler)
            self.ninja.variable('decompiler', decompiler)

    def __del__(self):
        self.close()

    def close(self):
        self.output.close()

    def add_tests(self, filenames):
        for filename in filenames:
            self.add_test(filename)

    def add_test(self, filename):
        filename = os.path.abspath(filename)

        if filename.startswith(scriptdir + '/'):
            output_base = os.path.join(self.builddir, os.path.relpath(filename, scriptdir))
        else:
            output_base = os.path.join(self.builddir, os.path.relpath(filename, '/'))

        stdout = output_base + '.stdout'
        stderr = output_base + '.stderr'

        cookies_base = os.path.join(os.path.dirname(filename), 'cookies', os.path.basename(filename))
        correct_stdout = cookies_base + '.stdout'
        correct_stderr = cookies_base + '.stderr'
        stdout_regexp = cookies_base + '.stdout.regexp'
        stderr_regexp = cookies_base + '.stderr.regexp'

        timeout = try_read_int(cookies_base + '.timeout')
        exit_code = try_read_int(cookies_base + '.exitCode')

        self.decompile(filename, stdout, stderr, timeout, exit_code)

        self.check_output(stdout, correct_stdout, stdout_regexp)
        self.check_output(stderr, correct_stderr, stderr_regexp)

    def decompile(self, filename, stdout, stderr, timeout, exit_code):
        variables = {
            'stdout': stdout,
            'stderr': stderr,
        }
        if timeout != None:
            variables['timeout'] = timeout
        if exit_code != None:
            variables['exit_code'] = exit_code

        self.ninja.build([stdout, stderr], 'decompile', inputs=[filename], variables=variables)

    def check_output(self, output, correct_output, output_regexp):
        if os.path.isfile(correct_output):
            self.check_equal("%s.diff" % output, output, correct_output)

        regexps = filter(
            lambda line: not line.startswith('#') and line.strip(),
            try_read_lines(output_regexp))

        for i, regexp in zip(itertools.count(1), regexps):
            regexp_file = "%s.regexp.%d" % (output, i)
            write_file(regexp_file, regexp)
            self.check_matches('%s.grep.%d' % (output, i), output, regexp_file)

    def check_equal(self, diff_output, output, correct_output):
        self.ninja.build([diff_output], 'check_equal', inputs=[output, correct_output])

    def check_matches(self, grep_output, output, regexp_file):
        self.ninja.build([grep_output], 'check_matches', inputs=[regexp_file, output])

def main():
    parser = argparse.ArgumentParser(description='Generates ninja build script for running tests.')
    parser.add_argument('--decompiler', help='Decompiler executable.')
    parser.add_argument('builddir', help='Where to generate build.ninja.')
    parser.add_argument('test', nargs='*', help='Test to generate code for.')

    args = parser.parse_args()

    if len(args.test) == 0:
        args.test.extend(glob.glob(os.path.join(scriptdir, 'arm', '[0-9][0-9][0-9]_*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'mipsel', '[0-9][0-9][0-9]_*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'mipseb', '[0-9][0-9][0-9]_*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'bulk-mingw32', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'bulk-x86-64', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'debian-armel', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'debian-armhf', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'mipsbin', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'hand-made', '[0-9][0-9][0-9]_*')))
        args.test.append(os.path.join(scriptdir, 'hand-made/src'))

    gen = Generator(builddir = args.builddir, decompiler = args.decompiler)
    gen.add_tests(args.test)
    gen.close()

    sys.exit(0)

if __name__ == '__main__':
    main()
