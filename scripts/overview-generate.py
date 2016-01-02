#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of an overview of the libyal libraries."""

from __future__ import print_function
import argparse
import json
import os
import string
import sys

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class Project(object):
  """Class that defines a project.

  Attributes:
    appveyor_identifier: a string containing the AppVeyor identifier.
    category: a string containing the category.
    description: a string containing the description.
    documentation_only: a boolean indicating if the project only contains
                        documentation.
    name: a string containing the name.
  """

  def __init__(self, name):
    """Initializes a project object.

    Args:
      name: a string containing the name.
    """
    super(Project, self).__init__()
    self.appveyor_identifier = None
    self.category = None
    self.description = None
    self.documentation_only = False
    self.name = name


class ProjectsReader(object):
  """Class that defines a project reader."""

  def __init__(self):
    """Initializes a projects reader object."""
    super(ProjectsReader, self).__init__()
    # TODO: replace by:
    # self._config_parser = configparser. ConfigParser(interpolation=None)
    self._config_parser = configparser.RawConfigParser()

  def _GetConfigValue(self, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      section_name: the name of the section that contains the value.
      value_name: the name of the value.

    Returns:
      An object containing the value.
    """
    return json.loads(self._config_parser.get(section_name, value_name))

  def ReadFromFile(self, filename):
    """Reads the projects from file.

    Args:
      filename: a string containing the filename.

    Returns:
      A list of project objects (instances of Project).
    """
    self._config_parser.read([filename])

    projects = []
    for project_name in self._config_parser.sections():
      project = Project(project_name)

      try:
        project.appveyor_identifier = self._GetConfigValue(
            project_name, u'appveyor_identifier')
      except configparser.NoOptionError:
        pass

      project.category = self._GetConfigValue(project_name, u'category')
      project.description = self._GetConfigValue(project_name, u'description')

      try:
        project.documentation_only = self._GetConfigValue(
            project_name, u'documentation_only')
      except configparser.NoOptionError:
        pass

      projects.append(project)

    return projects


class OverviewWikiPageGenerator(object):
  """Class that generates the "Overview" wiki page."""

  _CATEGORIES = {
      u'cross_platform': (
          u'Cross-platform functionality',
          u'Several libraries for cross-platform C functions'),
      u'data_format': (
          u'Data formats',
          u'Several libraries for different types of file format data'),
      u'file_format': (
          u'File formats',
          u'Several libraries for different types of file formats'),
      u'in_file_format': (
          u'In-file formats',
          u'Several libraries for different types of in-file formats'),
      u'file_system_format': (
          u'File system formats',
          u'Several libraries for different types of file systems'),
      u'volume_system_format': (
          u'Volume (system) formats',
          u'Several libraries for different types of volume (system) formats'),
      u'storage_media_image_format': (
          u'Storage media image formats',
          (u'Several libraries for different types of storage media image '
           u'formats')),
      u'utility': (
          u'Utility libraries',
          u'Several libraries for different "utility" functionality')
  }

  _CATEGORIES_ORDER = [
      u'cross_platform', u'data_format', u'file_format', u'in_file_format',
      u'file_system_format', u'volume_system_format',
      u'storage_media_image_format', u'utility']

  def __init__(self, template_directory):
    """Initialize a wiki page generator.

    Args:
      template_directory: the path of the template directory.
    """
    super(OverviewWikiPageGenerator, self).__init__()
    self._template_directory = template_directory

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer):
    """Generates a section from template filename.

    Args:
      template_filename: a string containing the name of the template file.
      template_mpppings: a dictionary containing the template mappings, where
                         the key maps to the name of a template variable.
      output_writer: an output writer object (instance of OutputWriter).
    """
    template_string = self._ReadTemplateFile(template_filename)
    output_data = template_string.substitute(template_mappings)
    output_writer.Write(output_data)

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename: the name of the file containing the template string.

    Returns:
      A template string (instance of string.Template).
    """
    path = os.path.join(self._template_directory, filename)
    file_object = open(path, 'rb')
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  def Generate(self, projects, output_writer):
    """Generates a wiki page.

    Args:
      projects: a list of project objects (instances of Project).
      output_writer: an output writer object (instance of OutputWriter).
    """
    self._GenerateSection(u'introduction.txt', {}, output_writer)

    projects_per_category = {}
    for project in projects:
      if project.category not in projects_per_category:
        projects_per_category[project.category] = []

      projects_per_category[project.category].append(project)

    for category in self._CATEGORIES_ORDER:
      template_mappings = {
          u'category_description': self._CATEGORIES[category][1],
          u'category_title': self._CATEGORIES[category][0]
      }
      self._GenerateSection(u'category.txt', template_mappings, output_writer)

      projects = projects_per_category[category]
      for project in projects_per_category[category]:
        appveyor_build_status = u''
        if project.appveyor_identifier:
          appveyor_build_status = (
              u'[![Build status]'
              u'(https://ci.appveyor.com/api/projects/status/{0:s}?svg=true)]'
              u'(https://ci.appveyor.com/project/joachimmetz/{1:s})').format(
                  project.appveyor_identifier, project.name)

        if project.documentation_only:
          project_description = (
              u'{0:s} (**at the moment [documentation]'
              u'(https://github.com/libyal/{1:s}/blob/master/documentation) '
              u'only**)').format(project.description, project.name)

          travis_build_status = u''
        else:
          project_description = project.description

          travis_build_status = (
              u'[![Build status]'
              u'(https://travis-ci.org/libyal/{0:s}.svg?branch=master)]'
              u'(https://travis-ci.org/libyal/{0:s})').format(
                  project.name)

        # TODO: solve this in a more elegant way.
        if project.name == u'libtableau':
          travis_build_status = u''

        template_mappings = {
            u'appveyor_build_status': appveyor_build_status,
            u'project_description': project_description,
            u'project_name': project.name,
            u'travis_build_status': travis_build_status
        }
        self._GenerateSection(u'library.txt', template_mappings, output_writer)

    self._GenerateSection(u'other.txt', {}, output_writer)


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
    return

  def Write(self, data):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      data: the data to write.
    """
    print(data, end=u'')


def Main():
  args_parser = argparse.ArgumentParser(description=(
      u'Generates an overview of the libyal libraries.'))

  args_parser.add_argument(
      u'configuration_file', action=u'store', metavar=u'CONFIGURATION_FILE',
      default=u'projects.ini', help=(
          u'The overview generation configuration file.'))

  args_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  options = args_parser.parse_args()

  if not options.configuration_file:
    print(u'Configuration file missing.')
    print(u'')
    args_parser.print_help()
    print(u'')
    return False

  if not os.path.exists(options.configuration_file):
    print(u'No such configuration file: {0:s}.'.format(
        options.configuration_file))
    print(u'')
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print(u'No such output directory: {0:s}.'.format(options.output_directory))
    print(u'')
    return False

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_reader = ProjectsReader()

  projects = projects_reader.ReadFromFile(options.configuration_file)
  if not projects:
    print(u'Unable to read projects from configuration file: {0:s}.'.format(
        options.configuration_file))
    print(u'')
    return False

  page_name = u'Overview'
  template_directory = os.path.join(
      libyal_directory, u'data', u'wiki', page_name)
  wiki_page = OverviewWikiPageGenerator(template_directory)

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

  wiki_page.Generate(projects, output_writer)

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
