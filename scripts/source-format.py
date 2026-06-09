#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Script to format a source file."""

import argparse
import sys

from yaldevtools import source_formatter


class SourceFileParser:
    """Source file parser."""

    _STATE_NONE = 0
    _STATE_IN_COMMENT = 1

    def __init__(self):
        """Initializes a source file parser."""
        super().__init__()
        self._functions = []

    def ReadFile(self, path):
        """Reads a source file.

        Args:
          path (str): path of the source file.
        """
        state = self._STATE_NONE
        group = []

        with open(path, encoding="utf8") as file_object:
            for line in file_object.readlines():
                stripped_line = line.strip()

                if state == self._STATE_NONE:
                    if stripped_line.startswith("/*"):
                        state = self._STATE_IN_COMMENT
                        group = [line]

                elif state == self._STATE_IN_COMMENT:
                    group.append(line)

                    if stripped_line.startswith("*/"):
                        print("".join(group))

                        state = self._STATE_NONE
                        group = []


def Main():
    """Entry point of console script.

    Returns:
      int: exit code that is provided to sys.exit().
    """
    argument_parser = argparse.ArgumentParser(
        description=("Formats source files of the libyal libraries.")
    )
    argument_parser.add_argument(
        "source_file",
        action="store",
        metavar="PATH",
        default="libyal.ini",
        help="path of the source file.",
    )
    options = argument_parser.parse_args()

    if not options.source_file:
        print("Source file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return 1

    # TODO: remove trailing whitespace

    # parser = SourceFileParser()
    # parser.ReadFile(options.source_file)

    with open(options.source_file, encoding="utf8") as file_object:
        file_content = file_object.read()

    lines = file_content.split("\n")

    formatter = source_formatter.SourceFormatter()
    formatted_lines = formatter.FormatSource(lines)
    formatted_file_content = "\n".join(formatted_lines)

    with open(options.source_file, "w", encoding="utf8") as file_object:
        file_object.write(formatted_file_content)

    return 0


if __name__ == "__main__":
    sys.exit(Main())
