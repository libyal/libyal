#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to generate libyal man pages."""

import argparse
import logging
import os
import sys

from yaldevtools import configuration
from yaldevtools import output_writers
from yaldevtools.source_generators import manpage as manpage_source_generator


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates man page of the libyal libraries.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='CONFIGURATION_FILE',
      default='source.conf', help='The source generation configuration file.')

  argument_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='path of the output files to write to.')

  argument_parser.add_argument(
      '-p', '--projects', dest='projects_directory', action='store',
      metavar='PROJECTS_DIRECTORY', default=None,
      help='path of the projects.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print('Config file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not os.path.exists(options.configuration_file):
    print('No such configuration file: {0:s}.'.format(
        options.configuration_file))
    print('')
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print('No such output directory: {0:s}.'.format(options.output_directory))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  project_configuration = configuration.ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_directory = options.projects_directory
  if not projects_directory:
    projects_directory = os.path.dirname(libyal_directory)

  data_directory = os.path.join(libyal_directory, 'data')
  manuals_directory = os.path.join(data_directory, 'source', 'manuals')

  SOURCE_GENERATORS = [
      ('libyal.3', manpage_source_generator.LibraryManPageGenerator),
  ]

  for source_category, source_generator_class in SOURCE_GENERATORS:
    template_directory = os.path.join(manuals_directory, source_category)
    source_generator_object = source_generator_class(
        projects_directory, data_directory, template_directory)

    if options.output_directory:
      output_writer = output_writers.FileWriter(options.output_directory)
    else:
      output_writer = output_writers.StdoutWriter()

    source_generator_object.Generate(project_configuration, output_writer)

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
