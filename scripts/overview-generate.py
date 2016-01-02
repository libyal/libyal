#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of an overview of the libyal libraries."""

from __future__ import print_function
import abc
import argparse
import glob
import json
import logging
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


class M4ScriptFile(object):
  """Class that defines a m4 script file.

  Attributes:
    name: a string containing the name.
    version: a string containing the version.
  """

  def __init__(self, path):
    """Initializes a m4 script file.

    Args:
      path: a string containing the path.
    """
    super(M4ScriptFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.version = None

  def ReadVersion(self):
    """Reads the version from the m4 script file.

    Returns:
      A boolean to indicate the version was read from the file.
    """
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(b'dnl Version: '):
          _, _, version = line.rpartition(b'dnl Version: ')
          # TODO: convert version to integer?
          self.version = version.decode(u'ascii')

          return True

    return False

class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  def __init__(self, data_directory, template_directory):
    """Initialize a wiki page generator.

    Args:
      data_directory: a string containing the path of the data directory.
      template_directory: a string containing the path of the template
                          directory.
    """
    super(WikiPageGenerator, self).__init__()
    self._data_directory = data_directory
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

  @abc.abstractmethod
  def Generate(self, projects, output_writer):
    """Generates a wiki page.

    Args:
      projects: a list of project objects (instances of Project).
      output_writer: an output writer object (instance of OutputWriter).
    """


class OverviewWikiPageGenerator(WikiPageGenerator):
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
          u'Several libraries for different "utility" functionality'),
  }

  _CATEGORIES_ORDER = (
      u'cross_platform', u'data_format', u'file_format', u'in_file_format',
      u'file_system_format', u'volume_system_format',
      u'storage_media_image_format', u'utility')

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


class StatusWikiPageGenerator(WikiPageGenerator):
  """Class that generates the "Status" wiki page."""

  _PROJECT_GROUPS = (
      (u'libcstring', u'libcerror', u'libcthreads', ),
      (u'libcdata', u'libcdatetime', u'libclocale', u'libcnotify',
       u'libcsplit', ),
      (u'libuna', ),
      (u'libcdirectory', u'libcfile', u'libcpath', u'libcsystem'),
      (u'libbfio', u'libsigscan', ),
      (u'libfcache', u'libfdata', u'libfdatetime', u'libfguid', u'libfmapi',
       u'libfole', u'libftxf', u'libftxr', u'libfusn', u'libfvalue',
       u'libfwevt', u'libfwnt', u'libfwps', u'libfwsi', ),
      (u'libcaes', u'libhmac', ),
      (u'libagdb', u'libcreg', u'libesedb', u'libevt', u'libevtx', u'libexe',
       u'liblnk', u'libmdmp', u'libmsiecf', u'libnk2', u'libnsfdb',
       u'libolecf', u'libpff', u'libregf', u'libscca', u'libswf', u'libwtcdb', ),
      (u'libmapidb', u'libwrc', ),
      (u'libfsclfs', u'libfsext', u'libfshfs', u'libfsntfs', u'libfsrefs', ),
      (u'libbde', u'libfvde', u'libluksde', u'libvshadow', u'libvslvm',
       u'libvsmbr', ),
      (u'libewf', u'libhibr', u'libodraw', u'libphdi', u'libqcow', u'libsmdev',
       u'libsmraw', u'libvhdi', u'libvmdk', ),
  )

  def _FormatProjectNames(self, project_names):
    """Formats the project names.

    Args:
      project_names: a list of strings containing the project names.

    Returns:
      A string containing the formatted project names.
    """
    lines = []
    for project_group in self._PROJECT_GROUPS:
      line = []
      for project in project_group:
        if project in project_names:
          line.append(project)
          project_names.pop(project_names.index(project))

      if line:
        lines.append(u', '.join(line))

    if project_names:
      lines.append(u', '.join(project_names))

    return u'<br>'.join(lines)

  def Generate(self, projects, output_writer):
    """Generates a wiki page.

    Args:
      projects: a list of project objects (instances of Project).
      output_writer: an output writer object (instance of OutputWriter).
    """
    m4_script_glob = os.path.join(self._data_directory, u'm4', u'*.m4')
    versions_per_m4_script = {}
    for path in glob.glob(m4_script_glob):
      m4_script_file = M4ScriptFile(path)

      version = None
      if m4_script_file.ReadVersion():
        version = m4_script_file.version
      if not version:
        version = u'missing'

      versions_per_m4_script[m4_script_file.name] = {version: []}

    for project in projects:
      project_m4_scripts_path = os.path.dirname(self._data_directory)
      project_m4_scripts_path = os.path.dirname(project_m4_scripts_path)
      project_m4_scripts_path = os.path.join(
          project_m4_scripts_path, project.name, u'm4')

      for m4_script in versions_per_m4_script.keys():
        m4_script_path = os.path.join(project_m4_scripts_path, m4_script)
        if not os.path.exists(m4_script_path):
          continue

        m4_script_file = M4ScriptFile(m4_script_path)

        version = None
        if m4_script_file.ReadVersion():
          version = m4_script_file.version
        if not version:
          version = u'missing'

        projects_per_version = versions_per_m4_script[m4_script]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    self._GenerateSection(u'introduction.txt', {}, output_writer)

    for m4_script, projects_per_version in sorted(
        versions_per_m4_script.items()):
      template_mappings = {
          u'title': m4_script,
      }
      self._GenerateSection(
          u'table_header.txt', template_mappings, output_writer)

      for version, project_names in sorted(
            projects_per_version.items(), reverse=True):
        project_names = self._FormatProjectNames(project_names)

        template_mappings = {
            u'project_names': project_names,
            u'version': version,
        }
        self._GenerateSection(
            u'table_entry.txt', template_mappings, output_writer)


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

  wiki_pages = [
      (u'Overview', OverviewWikiPageGenerator),
      (u'Status', StatusWikiPageGenerator),
  ]

  for page_name, page_generator_class in wiki_pages:
    data_directory = os.path.join(libyal_directory, u'data')
    template_directory = os.path.join(data_directory, u'wiki', page_name)
    wiki_page = page_generator_class(data_directory, template_directory)

    if options.output_directory:
      filename = u'{0:s}.md'.format(page_name)
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

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
