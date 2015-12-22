#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of libyal libraries."""

from __future__ import print_function
import abc
import argparse
import json
import string
import os
import sys

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class ConfigError(Exception):
  """Class that defines a configuration error."""


class ProjectConfiguration(object):
  """Class that contains the project configuration."""

  def __init__(self):
    """Initializes the project configuation."""
    super(ProjectConfiguration, self).__init__()
    self.project_authors = None
    self.project_copyright = None

    self.library_name = None
    self.library_description = None

  def _GetConfigValue(self, config_parser, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      config_parser: the configuration parser (instance of ConfigParser).
      section_name: the name of the section that contains the value.
      value_name: the name of the value.

    Returns:
      An object containing the value.
    """
    return json.loads(config_parser.get(section_name, value_name))

  def ReadFromFile(self, filename):
    """Reads the configuration from file.

    Args:
      filename: the configuration filename.
    """
    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.library_name = self._GetConfigValue(
        config_parser, u'Library', u'name')
    self.library_name = self._GetConfigValue(
        config_parser, u'Library', u'description')

  def GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      A dictionary containing the string template mappings.
    """
    template_mappings = {
        u'library_name': self.library_name,
        u'library_name_upper_case': self.library_name.upper(),
        u'library_description': self.library_description,
    }
    return template_mappings


class SourceFileGenerator(object):
  """Class that generates source files."""

  def __init__(self, template_directory):
    """Initialize the source file generator.

    Args:
      template_directory: the path of the template directory.
    """
    super(SourceFileGenerator, self).__init__()
    self._template_directory = template_directory

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename: the name of the file containing the template string.

    Returns:
      A template string (instance of string.Template).
    """
    file_object = open(os.path.join(self._template_directory, filename))
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  def _GenerateSection(
      self, project_configuration, template_filename, output_writer):
    """Generates a section from template filename.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      template_filename: the name of the file containing the template string.
      output_write: the output writer.
    """
    template_string = self._ReadTemplateFile(template_filename)

    output_writer.Write(
        template_string.substitute(
            project_configuration.GetTemplateMappings()))

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """

  @abc.abstractmethod
  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """


class LibrarySourceFileGenerator(SourceFileGenerator):
  """Class that generates the library source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates a library source file.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    # TODO: process *.[ch] *.rc.in files in the libyal directory
    filename = u''

    self._GenerateSection(project_configuration, filename, output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    return True


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initialize the output writer.

    Args:
      name: the name of the output.
    """
    super(FileWriter, self).__init__()
    self._file_object = None
    self._name = name

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    self._file_object = open(self._name, 'wb')
    return True

  def Close(self):
    """Closes the output writer object."""
    self._file_object.close()

  def Write(self, data):
    """Writes the data to file.

    Args:
      data: the data to write.
    """
    self._file_object.write(data)


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self):
    """Initialize the output writer."""
    super(StdoutWriter, self).__init__()

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def Write(self, data):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      data: the data to write.
    """
    print(data, end=u'')


def Main():
  args_parser = argparse.ArgumentParser(description=(
      u'Generates source files of the libyal libraries.'))

  args_parser.add_argument(
      u'config_file', action=u'store', metavar=u'CONFIG_FILE',
      default='source.conf', help=u'The source generation config file.')

  args_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  options = args_parser.parse_args()

  if not options.config_file:
    print(u'Config file missing.')
    print(u'')
    args_parser.print_help()
    print(u'')
    return False

  if not os.path.exists(options.config_file):
    print(u'No such config file: {0:s}.'.format(options.config_file))
    print(u'')
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print(u'No such output directory: {0:s}.'.format(options.output_directory))
    print(u'')
    return False

  project_configuration = ProjectConfiguration()
  project_configuration.ReadFromFile(options.config_file)

  script_directory = os.path.dirname(os.path.abspath(__file__))

  # TODO: generate more source files.
  source_files = [
      (u'libyal', LibrarySourceFileGenerator),
  ]

  # TODO: implement
  for page_name, page_generator_class in source_files:
    template_directory = os.path.join(script_directory, u'source', page_name)
    source_file = page_generator_class(template_directory)

    if not source_file.HasContent(project_configuration):
      continue

    filename = u'{0:s}.md'.format(page_name)

    if options.output_directory:
      output_file = os.path.join(options.output_directory, filename)
      output_writer = FileWriter(output_file)
    else:
      output_writer = StdoutWriter()

    if not output_writer.Open():
      print(u'Unable to open output writer.')
      print(u'')
      return False

    source_file.Generate(project_configuration, output_writer)

    output_writer.Close()

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
