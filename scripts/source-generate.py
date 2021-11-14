#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to generate source of the libyal libraries."""

import argparse
import logging
import os
import sys

from yaldevtools import configuration
from yaldevtools import output_writers
from yaldevtools.source_generators import common
from yaldevtools.source_generators import config
from yaldevtools.source_generators import documents
from yaldevtools.source_generators import include
from yaldevtools.source_generators import library
from yaldevtools.source_generators import manpage
from yaldevtools.source_generators import python_module
from yaldevtools.source_generators import scripts
from yaldevtools.source_generators import tests
from yaldevtools.source_generators import tools


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates source files of the libyal libraries.'))

  argument_parser.add_argument(
      '-e', '--experimental', dest='experimental', action='store_true',
      default=False, help='enable experimental functionality.')

  argument_parser.add_argument(
      '-g', '--generators', dest='generators', action='store', default='all',
      help='names of the generators to run.')

  argument_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='path of the output files to write to.')

  argument_parser.add_argument(
      '-p', '--projects', dest='projects_directory', action='store',
      metavar='PROJECTS_DIRECTORY', default=None,
      help='path of the projects.')

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='PATH',
      default='libyal.ini', help='path of the configuration file.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print('Configuration file missing.')
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

  # TODO: generate more source files.
  # include headers
  # yal.net files

  if options.generators == 'all':
    generators = []
  else:
    generators = options.generators.split(',')

  SOURCE_GENERATORS = [
      ('common', common.CommonSourceFileGenerator),
      ('config', config.ConfigurationFileGenerator),
      ('documents', documents.DocumentFileGenerator),
      ('include', include.IncludeSourceFileGenerator),
      ('libyal', library.LibrarySourceFileGenerator),
      ('pyyal', python_module.PythonModuleSourceFileGenerator),
      ('scripts', scripts.ScriptFileGenerator),
      ('tests', tests.TestSourceFileGenerator),
      ('yaltools', tools.ToolSourceFileGenerator),
  ]

  sources_directory = os.path.join(data_directory, 'source')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(sources_directory, source_category)
    source_generator_object = source_generator_class(
        projects_directory, data_directory, template_directory,
        experimental=options.experimental)

    if options.output_directory:
      output_writer = output_writers.FileWriter(options.output_directory)
    else:
      output_writer = output_writers.StdoutWriter()

    source_generator_object.Generate(project_configuration, output_writer)

  # TODO: dpkg handle dependencies

  # TODO: generate manuals/Makefile.am

  SOURCE_GENERATORS = [
      ('libyal.3', manpage.LibraryManPageGenerator),
  ]

  manuals_directory = os.path.join(
      libyal_directory, 'data', 'source', 'manuals')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(manuals_directory, source_category)
    source_generator_object = source_generator_class(
        projects_directory, data_directory, template_directory,
        experimental=options.experimental)

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
