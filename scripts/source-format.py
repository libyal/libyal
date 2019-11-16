#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to format a source file."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import io
import sys


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Formats source files of the libyal libraries.'))

  argument_parser.add_argument(
      'source_file', action='store', metavar='PATH',
      default='libyal.ini', help='path of the source file.')

  options = argument_parser.parse_args()

  if not options.source_file:
    print('Source file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  with io.open(options.source_file, 'r', encoding='utf8') as file_object:
    file_content = file_object.read()

  with io.open(options.source_file, 'w', encoding='utf8') as file_object:
    lines = file_content.split('\n')

    in_function = False

    for line in lines[:-1]:
      line = line.rstrip()

      if in_function:
        if line == '}':
          in_function = False
        else:
          index = 0
          line_length = len(line)

          while index < line_length:
            end_index = index + 8
            if line[index:end_index] != '        ':
              break

            line = '{0:s}\t{1:s}'.format(line[:index], line[end_index:])
            line_length = len(line)

            index += 8

      elif line == '{':
        in_function = True

      file_object.write('{0:s}\n'.format(line))

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
