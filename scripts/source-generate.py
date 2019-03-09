#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of the libyal libraries."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sys

import configuration

from source_generators import common as common_source_generator
from source_generators import config as config_source_generator
from source_generators import documents as documents_source_generator
from source_generators import include as include_source_generator
from source_generators import library as library_source_generator
from source_generators import manpage as manpage_source_generator
from source_generators import python_module as python_module_source_generator
from source_generators import scripts as scripts_source_generator
from source_generators import tests as tests_source_generator
from source_generators import tools as tools_source_generator


class FileWriter(object):
  """File output writer."""

  def __init__(self, output_directory):
    """Initialize an output writer.

    Args:
      output_directory: string containing the path of the output directory.
    """
    super(FileWriter, self).__init__()
    self._file_object = None
    self._output_directory = output_directory

  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to file.

    Args:
      file_path: string containing the path of the file to write.
      file_data: binary string containing the data to write.
      access_mode: optional string containing the output file access mode.
    """
    self._file_object = open(file_path, access_mode)
    self._file_object.write(file_data)
    self._file_object.close()


class StdoutWriter(object):
  """Stdout output writer."""

  def __init__(self):
    """Initialize the output writer."""
    super(StdoutWriter, self).__init__()

  # pylint: disable=unused-argument
  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      file_path: string containing the path of the file to write.
      file_data: binary string containing the data to write.
      access_mode: optional string containing the output file access mode.
    """
    print('-' * 80)
    print('{0: ^80}'.format(file_path))
    print('-' * 80)
    print('')
    print(file_data, end='')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates source files of the libyal libraries.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='CONFIGURATION_FILE',
      default='source.conf', help='The source generation configuration file.')

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

  # TODO: generate more source files.
  # include headers
  # yal.net files

  if options.generators == 'all':
    generators = []
  else:
    generators = options.generators.split(',')

  SOURCE_GENERATORS = [
      ('common', common_source_generator.CommonSourceFileGenerator),
      ('config', config_source_generator.ConfigurationFileGenerator),
      ('documents', documents_source_generator.DocumentFileGenerator),
      ('include', include_source_generator.IncludeSourceFileGenerator),
      ('libyal', library_source_generator.LibrarySourceFileGenerator),
      ('pyyal', python_module_source_generator.PythonModuleSourceFileGenerator),
      ('scripts', scripts_source_generator.ScriptFileGenerator),
      ('tests', tests_source_generator.TestSourceFileGenerator),
      ('yaltools', tools_source_generator.ToolSourceFileGenerator),
  ]

  sources_directory = os.path.join(
      libyal_directory, 'data', 'source')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(sources_directory, source_category,)
    source_generator_object = source_generator_class(
        projects_directory, template_directory,
        experimental=options.experimental)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_generator_object.Generate(project_configuration, output_writer)

  # TODO: dpkg handle dependencies

  # TODO: add support for Unicode templates.

  # TODO: generate manuals/Makefile.am

  SOURCE_GENERATORS = [
      ('libyal.3', manpage_source_generator.LibraryManPageGenerator),
  ]

  manuals_directory = os.path.join(
      libyal_directory, 'data', 'source', 'manuals')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(manuals_directory, source_category)
    source_generator_object = source_generator_class(
        projects_directory, template_directory,
        experimental=options.experimental)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_generator_object.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
