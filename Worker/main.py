#!/bin/python

import sys
from cli import CliTranslator
from Utils.Logger import Logger, LogLevel


def main(args: list[str]) -> None:
    # init logger
    Logger("./log.txt", False, LogLevel.MEDIUM_FREQ)

    # init worker object

    # init worker CLI
    CliTranslator().parse_args(args).parse_stdin()


if __name__ == '__main__':
    main(sys.argv)
