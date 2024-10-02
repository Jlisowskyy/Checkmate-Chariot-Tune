#!/bin/python

import sys
from Worker.main_cli import main_cli

if __name__ == '__main__':
    rv = main_cli(sys.argv[1:])
    exit(rv)