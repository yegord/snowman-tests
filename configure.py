#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse, glob, hashlib, ninja_syntax, os, sys

scriptdir = os.path.abspath(os.path.dirname(__file__))

class Generator(object):
    def __init__(self, builddir, **kwargs):
        self.builddir = os.path.abspath(builddir)

        if not os.path.isdir(builddir):
            os.makedirs(builddir)

        script_filename = os.path.join(builddir, 'build.ninja')

        self.output = open(script_filename, 'w')
        self.ninja = ninja_syntax.Writer(self.output)
        self.ninja.include(ninja_syntax.escape_path(os.path.abspath(os.path.join(scriptdir, 'ninja.rules'))))
        self.ninja.variable('builddir', builddir)
        self.ninja.variable('run', [sys.executable, os.path.abspath(os.path.join(scriptdir, 'run.py'))])

        if sys.platform == 'win32':
            self.ninja.variable('diff', [sys.executable, os.path.abspath(os.path.join(scriptdir, 'diff.py'))])
            self.ninja.variable('tee', [sys.executable, os.path.abspath(os.path.join(scriptdir, 'tee.py'))])

        for key, value in kwargs.items():
            if value != None:
                self.ninja.variable(key, value)

    def __del__(self):
        self.close()

    def close(self):
        self.output.close()

    def add_tests(self, filenames, **kwargs):
        for filename in filenames:
            self.add_test(filename, **kwargs)

    def add_test(self, filename, **kwargs):
        timeout = self.get_property(filename, 'exitCode')
        if timeout != None:
            kwargs['exit_code'] = int(timeout)
        stdout, stderr = self.decompile(filename, **kwargs)

        correct_stdout = self.get_property_filename(filename, 'stdout')
        if os.path.isfile(correct_stdout):
            self.check_equal(correct_stdout, stdout)

        correct_stderr = self.get_property_filename(filename, 'stderr')
        if os.path.isfile(correct_stderr):
            self.check_equal(correct_stderr, stderr)

    def decompile(self, filename, **kwargs):
        basepath = os.path.abspath((os.path.join(self.builddir, hashlib.sha256(filename).hexdigest())))
        stdout = basepath + '.stdout'
        stderr = basepath + '.stderr'

        variables = kwargs
        variables['stdout'] = stdout
        variables['stderr'] = stderr
        variables['description'] = 'Decompile %s' % filename

        self.ninja.build([stdout, stderr], 'decompile', inputs=[os.path.abspath(filename)], variables=variables)

        return stdout, stderr

    def check_equal(self, filename1, filename2):
        filename1 = os.path.abspath(filename1)
        filename2 = os.path.abspath(filename2)
        outfile = os.path.join(self.builddir, hashlib.sha256(filename1 + ':' + filename2).hexdigest()) + '.diff'

        variables = {}
        variables['description'] = 'Diff %s and %s' % (filename1, filename2)

        self.ninja.build([outfile], 'check_equal', inputs=[filename1, filename2], variables=variables)

    def get_property(self, filename, property):
        return self.try_read_file(self.get_property_filename(filename, property))

    def get_property_filename(self, filename, property):
        return os.path.join(os.path.dirname(filename), 'cookies', os.path.basename(filename) + '.' + property)

    def try_read_file(self, filename):
        if os.path.isfile(filename):
            file = open(filename, 'r')
            try:
                return file.read()
            finally:
                file.close()
        return None

def main():
    parser = argparse.ArgumentParser(description='Generates ninja build script for running tests.')
    parser.add_argument('--decompiler', help='Decompiler executable.')
    parser.add_argument('builddir', help='Where to generate build.ninja.')
    parser.add_argument('test', nargs='*', help='Test to create.')

    args = parser.parse_args()

    if len(args.test) == 0:
        args.test.extend(glob.glob(os.path.join(scriptdir, 'arm', '[0-9][0-9][0-9]_*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'bulk-mingw32', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'bulk-x86-64', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'debian-armel', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'debian-armhf', '*')))
        args.test.extend(glob.glob(os.path.join(scriptdir, 'hand-made', '[0-9][0-9][0-9]_*')))

    gen = Generator(builddir = args.builddir, decompiler = os.path.abspath(args.decompiler))
    gen.add_tests(args.test)
    gen.close()

    sys.exit(0)

if __name__ == '__main__':
    main()
