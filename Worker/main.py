#!/bin/python

import sys
from cli import CliTranslator
from Utils.Logger import Logger
from ProjectInfo.ProjectInfo import ProjectInfoInstance


def main(args: list[str]) -> None:
    ProjectInfoInstance.display_info("Worker")

    cli = CliTranslator()

    cli.parse_args(args)
    cli.parse_stdin()


if __name__ == '__main__':
    main(sys.argv)
