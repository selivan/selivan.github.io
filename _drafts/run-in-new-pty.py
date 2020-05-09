#!/usr/bin/env python3
import pty
import os
import sys
import subprocess
import argparse
import contextlib

parser = argparse.ArgumentParser(description='Run command in pseudo-terminal')
parser.add_argument('-s', '--shell', dest='shell', default='/bin/bash',
                    help='Shell to use')
parser.add_argument('-c', '--command', dest='command', required=True,
                    help='Command to run')
args = parser.parse_args()

pid, fd = pty.fork()
if pid == 0:
    os.execl(args.shell, args.shell, '-c', args.command)
else:
    _, exit_status = os.waitpid(pid, 0)
    print(f'pid: {pid}, fd: {fd}')
    os.dup2(fd, 0)
    os.dup2(fd, 1)
    os.dup2(fd, 2)
    sys.exit(exit_status)
