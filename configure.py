#!/usr/bin/env python
# -*- coding: utf-8 -*-

# "THE JUICE-WARE LICENSE" (Revision 42)
#
# <yegor.derevenets@gmail.com> wrote this file. As long as you
# keep this notice, you can do whatever you want with this stuff.
# If we meet someday, and you think this stuff is worth it, you
# can buy me a glass of juice in return. Yegor Derevenets

import argparse, contextlib, glob, hashlib, ninja_syntax, os, sys

scriptdir = os.path.abspath(os.path.dirname(__file__))

def main():
    parser = argparse.ArgumentParser(description='Generates ninja build script for running tests.')
    parser.add_argument('--decompiler', help='Decompiler executable.')
    parser.add_argument('builddir', help='Where to generate build.ninja.')
    parser.add_argument('tests', metavar='test', nargs='*', help='Test to generate targets for.')

    args = parser.parse_args()

    if len(args.tests) == 0:
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'arm', '[0-9][0-9][0-9]_*')))
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'bulk-mingw32', '*')))
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'bulk-x86-64', '*')))
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'debian-armel', '*')))
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'debian-armhf', '*')))
        args.tests.extend(glob.glob(os.path.join(scriptdir, 'hand-made', '[0-9][0-9][0-9]_*')))
        args.tests.append(os.path.join(scriptdir, 'hand-made/src'))

    create_build_file(args.builddir, args.decompiler, args.tests)

    sys.exit(0)

def create_build_file(builddir, decompiler, tests):
    escape = ninja_syntax.escape_path

    builddir = os.path.abspath(builddir)
    create_dir(builddir)

    with ninja_writer(os.path.join(builddir, 'build.ninja')) as ninja:
        ninja.include(escape(os.path.join(scriptdir, 'rules.ninja')))
        ninja.variable('builddir', escape(builddir))

        if decompiler:
            decompiler = os.path.abspath(decompiler)
            ninja.variable('decompiler', escape(decompiler))

        define_tool_paths(ninja)

        targets = dict(decompile=[], check=[], update=[])

        for test in tests:
            add_test(ninja, builddir, test, targets)

        add_special_targets(ninja, targets)
        ninja.default(['decompile', 'check'])

@contextlib.contextmanager
def ninja_writer(filename):
    with open(filename, 'w') as f:
        yield ninja_syntax.Writer(f)

def define_tool_paths(ninja):
    escape = ninja_syntax.escape_path
    python = escape(sys.executable)

    ninja.variable('run', [python, escape(os.path.join(scriptdir, 'run.py'))])

    if sys.platform == 'win32':
        ninja.variable('shell', ['cmd', '/c'])
        ninja.variable('diff', [python, escape(os.path.join(scriptdir, 'diff.py'))])
        ninja.variable('grep', [python, escape(os.path.join(scriptdir, 'grep.py'))])
        ninja.variable('tee',  [python, escape(os.path.join(scriptdir, 'tee.py'))])
        ninja.variable('cp', ['xcopy', '/Y'])

def add_test(ninja, builddir, filename, targets):
    filename = os.path.abspath(filename)

    if filename.startswith(scriptdir + '/'):
        output_base = os.path.join(builddir, os.path.relpath(filename, scriptdir))
    else:
        output_base = os.path.join(builddir, os.path.relpath(filename, '/'))

    stdout = output_base + '.stdout'
    stderr = output_base + '.stderr'

    cookies_base = os.path.join(os.path.dirname(filename), 'cookies', os.path.basename(filename))
    answer_stdout = cookies_base + '.stdout'
    answer_stderr = cookies_base + '.stderr'
    stdout_regexp = cookies_base + '.stdout.regexp'
    stderr_regexp = cookies_base + '.stderr.regexp'

    timeout = read_int(cookies_base + '.timeout')
    exit_code = read_int(cookies_base + '.exitCode')

    targets['decompile'].extend(decompile(ninja, filename, stdout, stderr, timeout, exit_code))

    check_output(ninja, stdout, answer_stdout, stdout_regexp, targets)
    check_output(ninja, stderr, answer_stderr, stderr_regexp, targets)

def decompile(ninja, filename, stdout, stderr, timeout, exit_code):
    variables = { 'stdout': stdout, 'stderr': stderr }
    if timeout != None:
        variables['timeout'] = timeout
    if exit_code != None:
        variables['exit_code'] = exit_code
    return ninja.build([stdout, stderr], 'decompile', inputs=[filename], variables=variables)

def check_output(ninja, output_file, answer_file, regexps_file, targets):
    if os.path.isfile(answer_file):
        targets['check'].extend(check_equal(ninja, output_file, answer_file))
        targets['update'].extend(update_answer(ninja, output_file, answer_file))
    for regexp in read_regexps(regexps_file):
        targets['check'].extend(check_matches(ninja, output_file, regexp))

def check_equal(ninja, output_file, answer_file):
    return ninja.build(['%s.diff' % output_file], 'check_equal', inputs=[answer_file, output_file])

def update_answer(ninja, output_file, answer_file):
    return ninja.build(['%s.update' % answer_file], 'update_answer', inputs=[output_file, answer_file])

def check_matches(ninja, output_file, regexp):
    hashsum = hashlib.sha256(regexp).hexdigest()
    regexp_file = '{output_file}.regexp.{hashsum}'.format(output_file=output_file, hashsum=hashsum)
    write_file(regexp_file, regexp)
    return ninja.build(['%s.matches' % regexp_file], 'check_matches', inputs=[regexp_file, output_file])

def add_special_targets(ninja, targets):
    for target, subtargets in targets.iteritems():
        ninja.build([target], 'phony', subtargets)

def read_file(filename):
    if os.path.isfile(filename):
        with open(filename, 'U') as f:
            return f.read()
    return None

def read_int(filename):
    result = read_file(filename)
    if result != None:
        return int(result)
    else:
        return None

def read_lines(filename):
    result = read_file(filename)
    if result != None:
        return result.splitlines()
    else:
        return []

def read_regexps(filename):
    return filter(
        lambda line: not is_comment(line) and not is_empty(line),
        read_lines(filename))

def is_comment(line):
    return line.startswith('#')

def is_empty(line):
    return len(line.strip()) == 0

def write_file(filename, content):
    create_dir(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write(content)

def create_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

if __name__ == '__main__':
    main()
