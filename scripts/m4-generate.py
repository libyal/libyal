#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate a library M4 file based on an include header."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import datetime
import logging
import os
import string
import sys

from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

import template_string


class LibraryM4FileGenerator(object):
  """Library M4 file generator."""

  def __init__(self, templates_path):
    """Initializes a generator.

    Args:
      templates_path (str): templates path.
    """
    super(LibraryM4FileGenerator, self).__init__()


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates a library M4 file based on an include header.'))

  argument_parser.add_argument(
      u'--templates-path', u'--templates_path', dest=u'templates_path',
      action=u'store', metavar=u'PATH', default=None, help=(
          u'Path to the template files.'))

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=u'path of the libyal project.')

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  if not os.path.isfile(options.source):
    print(u'No such file: {0:s}'.format(options.source))
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  templates_path = options.templates_path
  if not templates_path:
    templates_path = os.path.dirname(__file__)
    templates_path = os.path.dirname(templates_path)
    templates_path = os.path.join(templates_path, u'data')

  source_generator = LibraryM4FileGenerator(templates_path)

  # TODP: read main include header
  # source_generator.Generate()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
