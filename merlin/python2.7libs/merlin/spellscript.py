from __future__ import division, absolute_import, print_function, unicode_literals

import os
import sys
import cmd
import shlex
import argparse
import subprocess
from . import collections

class Interpreter(cmd.Cmd, object):
    """docstring for Interpreter"""
    def __init__(self, shell=True, completekey='tab', stdin=None, stdout=None, stderr=None):
        super(Interpreter, self).__init__(completekey, stdin, stdout)
        self.shell = shell
        self.prompt = '-> '
        if stderr is None:
            stderr = sys.stderr
        self.stderr = stderr
        self.env = collections.ChainMap({}, os.environ)

    def emptyline(self):
        """Do nothing"""
        pass

    def do_shell(self, line):
        if not self.shell:
            raise RuntimeError('shell commands are currently disabled in spellscript.')
        subprocess.call(line, stdout=self.stdout, shell=True)

    def add_cmd(self, name, func, options=[], doc=''):
        """Add command to Interpreter

        name is a string of th name of the function
        func is a function taking one parameter: a list of arguments tokenized by the Interpreter
        options is a sequence of possible options. This is used for tab completion."""
        cmd_name = 'do_'+name
        if hasattr(self, cmd_name):
            raise ValueError('a command by that name already exists')

        def run_cmd(self, line):
            args = shlex.split(line, '#', True)
            return func(args)

        def complete_cmd(self):
            pass

        run_cmd.__name__ = cmd_name
        run_cmd.__doc__ = doc

        setattr(self, cmd_name, run_cmd)

    def do_EOF(self, line):
        self.stdout.write('\n')
        return True

    def do_exit(self, line):
        """exit from the interpreter"""
        return True
        args = shlex.split(line)
        sys.exit(*args)

    def do_addnode(self, line):
        pass

    def do_set(self, line):
        """Command to set a shell variable

        The variable can then be referenced again using POSIX shell style variable syntax
        (e.g. $VAR or ${VAR})."""
        pass

    def do_unset(self, line):
        """Command to unset one or multiple variables"""
        pass
