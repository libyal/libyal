#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of an overview of the libyal libraries."""

from __future__ import print_function
from __future__ import unicode_literals

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
    appveyor_identifier (str): AppVeyor identifier.
    category (str): category.
    coverty_badge (int): Coverty badge identifier.
    description (str): description.
    display_name (str): display name.
    documentation_only (bool): True if the project only contains documentation.
    group (int): group.
    name (str): name.
  """

  def __init__(self, name):
    """Initializes a project.

    Args:
      name (str): name.
    """
    super(Project, self).__init__()
    self.appveyor_identifier = None
    self.category = None
    self.coverty_badge = None
    self.description = None
    self.display_name = name
    self.documentation_only = False
    self.group = None
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
      section_name (str): name of the section that contains the value.
      value_name (str): name of the value.

    Returns:
      object: value.
    """
    return json.loads(self._config_parser.get(section_name, value_name))

  def ReadFromFile(self, filename):
    """Reads the projects from file.

    Args:
      filename (str): path of the projects file.

    Returns:
      list[Project]: project.
    """
    self._config_parser.read([filename])

    projects = []
    for project_name in self._config_parser.sections():
      project = Project(project_name)

      try:
        project.appveyor_identifier = self._GetConfigValue(
            project_name, 'appveyor_identifier')
      except configparser.NoOptionError:
        pass

      project.category = self._GetConfigValue(project_name, 'category')

      try:
        project.coverty_badge = self._GetConfigValue(
            project_name, 'coverty_badge')
      except configparser.NoOptionError:
        pass

      project.description = self._GetConfigValue(project_name, 'description')

      try:
        project.display_name = self._GetConfigValue(
            project_name, 'display_name')
      except configparser.NoOptionError:
        pass

      try:
        project.documentation_only = self._GetConfigValue(
            project_name, 'documentation_only')
      except configparser.NoOptionError:
        pass

      try:
        project.group = self._GetConfigValue(project_name, 'group')
      except configparser.NoOptionError:
        pass

      projects.append(project)

    return projects


class ConfigureAcFile(object):
  """Class that defines a configure.ac file.

  Attributes:
    name (str): name.
    version (str): version.
  """

  def __init__(self, path):
    """Initializes a configure.ac file.

    Args:
      path (str): path of the configure.ac file.
    """
    super(ConfigureAcFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.version = None

  def ReadVersion(self):
    """Reads the version from the configure.ac file.

    Returns:
      bool: True if the version was read from the file.
    """
    with open(self._path, 'rb') as file_object:
      line_count = 0
      for line in file_object.readlines():
        line = line.strip()
        if line_count == 2:
          version = line[1:-2]

          # TODO: convert version to integer?
          self.version = version.decode('ascii')

          return True

        elif line_count:
          line_count += 1

        elif line.startswith(b'AC_INIT('):
          line_count += 1

    return False


class DefinitionsHeaderFile(object):
  """Class that defines a definitions header file.

  Attributes:
    name (str): name.
    version (str): version.
  """

  def __init__(self, path):
    """Initializes a definitions header file.

    Args:
      path (str): path of the definitions header file.
    """
    super(DefinitionsHeaderFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.version = None

  def ReadVersion(self):
    """Reads the version from the definitions header file.

    Returns:
      bool: True if the version was read from the file.
    """
    library_name, _, _ = self.name.partition('_')
    version_line = b'#define {0:s}_VERSION'.format(library_name.upper())

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(version_line):
          _, _, version = line.rpartition(version_line)
          version = version.strip()

          # TODO: convert version to integer?
          self.version = version.decode('ascii')

          return True

    return False


class M4ScriptFile(object):
  """Class that defines a m4 script file.

  Attributes:
    name (str): name.
    version (str): version.
  """

  def __init__(self, path):
    """Initializes a m4 script file.

    Args:
      path (str): path of the m4 script file.
    """
    super(M4ScriptFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.version = None

  def ReadVersion(self):
    """Reads the version from the m4 script file.

    Returns:
      bool: True if the version was read from the file.
    """
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(b'dnl Version: '):
          _, _, version = line.rpartition(b'dnl Version: ')
          # TODO: convert version to integer?
          self.version = version.decode('ascii')

          return True

    return False


class ScriptFile(object):
  """Class that defines a script or configuration file.

  Attributes:
    name (str): name.
    version (str): version.
  """

  def __init__(self, path):
    """Initializes a script or configuration file.

    Args:
      path (str): path of the script or configuration file.
    """
    super(ScriptFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.version = None

  def ReadVersion(self):
    """Reads the version from the script or configuration file.

    Returns:
      bool: True if the version was read from the file.
    """
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(b'# Version: '):
          _, _, version = line.rpartition(b'# Version: ')
          # TODO: convert version to integer?
          self.version = version.decode('ascii')

          return True

    return False


class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  _CATEGORIES = {
      'cross_platform': (
          'Cross-platform functionality',
          'Several libraries for cross-platform C functions'),
      'data_format': (
          'Data formats',
          'Several libraries for different types of file format data'),
      'file_format': (
          'File formats',
          'Several libraries for different types of file formats'),
      'in_file_format': (
          'In-file formats',
          'Several libraries for different types of in-file formats'),
      'file_system_format': (
          'File system formats',
          'Several libraries for different types of file systems'),
      'volume_system_format': (
          'Volume (system) formats',
          'Several libraries for different types of volume (system) formats'),
      'storage_media_image_format': (
          'Storage media image formats',
          ('Several libraries for different types of storage media image '
           'formats')),
      'utility': (
          'Utility libraries',
          'Several libraries for different "utility" functionality'),
      'other': (
          'Non-library projects',
          ''),
      'knowledge_base': (
          'Knowledge base projects',
          ''),
  }

  _ORDER_OF_LIBRARY_CATEGORIES = (
      'cross_platform', 'data_format', 'file_format', 'in_file_format',
      'file_system_format', 'volume_system_format',
      'storage_media_image_format', 'utility')

  _ORDER_OF_OTHER_CATEGORIES = (
      'other', 'knowledge_base')

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

  def Generate(self, projects, output_writer):
    """Generates a wiki page.

    Args:
      projects: a list of project objects (instances of Project).
      output_writer: an output writer object (instance of OutputWriter).
    """
    self._GenerateSection('introduction.txt', {}, output_writer)

    # TODO: add support for test scripts
    # TODO: add support for source generated files

    projects_per_category = {}
    for project in projects:
      if project.category not in projects_per_category:
        projects_per_category[project.category] = []

      projects_per_category[project.category].append(project)

    for category in self._ORDER_OF_LIBRARY_CATEGORIES:
      template_mappings = {
          'category_description': self._CATEGORIES[category][1],
          'category_title': self._CATEGORIES[category][0]
      }
      self._GenerateSection(
          'category_library.txt', template_mappings, output_writer)

      projects = projects_per_category[category]
      for project in projects_per_category[category]:
        appveyor_build_status = ''
        codecov_status = ''
        coverity_status = ''
        travis_build_status = ''

        if project.documentation_only:
          project_description = (
              '{0:s} (**at the moment [documentation]'
              '(https://github.com/libyal/{1:s}/blob/master/documentation) '
              'only**)').format(project.description, project.name)

        else:
          project_description = project.description

          if project.appveyor_identifier:
            appveyor_build_status = (
                '[![Build status]'
                '(https://ci.appveyor.com/api/projects/status/{0:s}?svg=true)]'
                '(https://ci.appveyor.com/project/joachimmetz/{1:s})').format(
                    project.appveyor_identifier, project.name)

          codecov_status = (
              '[![codecov](https://codecov.io/gh/libyal/{0:s}/branch/master/'
              'graph/badge.svg)](https://codecov.io/gh/libyal/{0:s})').format(
                  project.name)

          if project.coverty_badge:
            coverity_status = (
                '[![Coverity Scan Build Status](https://scan.coverity.com/'
                'projects/{0:d}/badge.svg)](https://scan.coverity.com/projects/'
                'libyal-{1:s})').format(project.coverty_badge, project.name)

          travis_build_status = (
              '[![Build status]'
              '(https://travis-ci.org/libyal/{0:s}.svg?branch=master)]'
              '(https://travis-ci.org/libyal/{0:s})').format(
                  project.name)

        template_mappings = {
            'appveyor_build_status': appveyor_build_status,
            'codecov_status': codecov_status,
            'coverity_status': coverity_status,
            'project_description': project_description,
            'project_name': project.name,
            'travis_build_status': travis_build_status
        }
        self._GenerateSection('library.txt', template_mappings, output_writer)

    for category in self._ORDER_OF_OTHER_CATEGORIES:
      template_mappings = {
          'category_title': self._CATEGORIES[category][0]
      }
      self._GenerateSection(
          'category_other.txt', template_mappings, output_writer)

      projects = projects_per_category[category]
      for project in projects_per_category[category]:
        template_mappings = {
            'project_description': project.description,
            'project_display_name': project.display_name,
            'project_name': project.name,
        }
        self._GenerateSection('other.txt', template_mappings, output_writer)


class StatusWikiPageGenerator(WikiPageGenerator):
  """Class that generates the "Status" wiki page."""

  def _FormatProjectNames(self, project_groups, project_names):
    """Formats the project names.

    Args:
      project_groups (dict[str, list[str]]): project names per project group.
      project_names (list[str]): project names.

    Returns:
      str: formatted project names.
    """
    lines = []
    for _, project_group in sorted(project_groups.items()):
      line = []
      for project in sorted(project_group):
        if project in project_names:
          line.append(project)
          project_names.pop(project_names.index(project))

      if line:
        lines.append(', '.join(line))

    if project_names:
      lines.append(', '.join(project_names))

    return '<br>'.join(lines)

  def _GetVersionsPerConfigurationFile(self, projects):
    """Retrieves the versions per configuration file.

    Args:
      projects list[Project]: projects.

    Returns:
      dict[str, object]: configuration files, their versions and the the names
          of the project that use the specific version. In the form:
          { configuration_name: {
              configuration_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    configs_directory = os.path.join(self._data_directory, 'configs')
    versions_per_configuration = {}
    for directory_entry in os.listdir(configs_directory):
      path = os.path.join(configs_directory, directory_entry)
      configuration_file = ScriptFile(path)

      version = None
      logging.info('Reading: {0:s}'.format(path))
      if configuration_file.ReadVersion():
        version = configuration_file.version
      if not version:
        version = 'missing'

      versions_per_configuration[configuration_file.name] = {version: []}

    for project in projects:
      project_configurations_path = os.path.join(projects_path, project.name)

      for configuration in versions_per_configuration.keys():
        configuration_path = os.path.join(
            project_configurations_path, configuration)
        if not os.path.exists(configuration_path):
          continue

        configuration_file = ScriptFile(configuration_path)

        version = None
        logging.info('Reading: {0:s}'.format(configuration_path))
        if configuration_file.ReadVersion():
          version = configuration_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_configuration[configuration]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_configuration

  def _GetVersionsPerLibrary(self, projects, category):
    """Retrieves the versions per library.

    Args:
      projects list[Project]: projects.
      category (str): category.

    Returns:
      dict[str, object]: libraries, their versions and the the names of the
          project that use the specific version. In the form:
          { library_name: {
              library_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    versions_per_library = {}
    for project in projects:
      if project.category != category:
        continue

      configure_ac_path = os.path.join(
          projects_path, project.name, 'configure.ac')
      if not os.path.exists(configure_ac_path):
        continue

      configure_ac_file = ConfigureAcFile(configure_ac_path)

      version = None
      logging.info('Reading: {0:s}'.format(configure_ac_path))
      if configure_ac_file.ReadVersion():
        version = configure_ac_file.version
      if not version:
        version = 'missing'

      versions_per_library[project.name] = {version: []}

    for project in projects:
      project_path = os.path.join(projects_path, project.name)

      for library in versions_per_library.keys():
        if project.name == library:
          continue

        definitions_header_path = os.path.join(
            project_path, library, '{0:s}_definitions.h'.format(library))
        if not os.path.exists(definitions_header_path):
          continue

        definitions_header_file = DefinitionsHeaderFile(definitions_header_path)

        version = None
        logging.info('Reading: {0:s}'.format(definitions_header_path))
        if definitions_header_file.ReadVersion():
          version = definitions_header_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_library[library]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_library

  def _GetVersionsPerM4Script(self, projects):
    """Retrieves the versions per m4 script.

    Args:
      projects list[Project]: projects.

    Returns:
      dict[str, object]: m4 scripts, their versions and the the names of the
          project that use the specific version. In the form:
          { m4_script_name: {
              m4_script_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    m4_script_glob = os.path.join(self._data_directory, 'm4', '*.m4')
    versions_per_m4_script = {}
    for path in glob.glob(m4_script_glob):
      m4_script_file = M4ScriptFile(path)

      version = None
      logging.info('Reading: {0:s}'.format(path))
      if m4_script_file.ReadVersion():
        version = m4_script_file.version
      if not version:
        version = 'missing'

      versions_per_m4_script[m4_script_file.name] = {version: []}

    for project in projects:
      project_m4_scripts_path = os.path.join(projects_path, project.name, 'm4')

      for m4_script in versions_per_m4_script.keys():
        m4_script_path = os.path.join(project_m4_scripts_path, m4_script)
        if not os.path.exists(m4_script_path):
          continue

        m4_script_file = M4ScriptFile(m4_script_path)

        version = None
        logging.info('Reading: {0:s}'.format(m4_script_path))
        if m4_script_file.ReadVersion():
          version = m4_script_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_m4_script[m4_script]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_m4_script

  def _GetVersionsPerPyScript(self, projects):
    """Retrieves the versions per py script.

    Args:
      projects list[Project]: projects.

    Returns:
      dict[str, object]: py scripts, their versions and the the names of the
          project that use the specific version. In the form:
          { py_script_name: {
              py_script_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    py_script_glob = os.path.join(self._data_directory, 'scripts', '*.py')
    versions_per_py_script = {}
    for path in glob.glob(py_script_glob):
      py_script_file = ScriptFile(path)

      version = None
      logging.info('Reading: {0:s}'.format(path))
      if py_script_file.ReadVersion():
        version = py_script_file.version
      if not version:
        version = 'missing'

      versions_per_py_script[py_script_file.name] = {version: []}

    for project in projects:
      project_py_scripts_path = os.path.join(projects_path, project.name)

      for py_script in versions_per_py_script.keys():
        py_script_path = os.path.join(project_py_scripts_path, py_script)
        if not os.path.exists(py_script_path):
          continue

        py_script_file = ScriptFile(py_script_path)

        version = None
        logging.info('Reading: {0:s}'.format(py_script_path))
        if py_script_file.ReadVersion():
          version = py_script_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_py_script[py_script]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_py_script

  def _GetVersionsPerScript(self, projects):
    """Retrieves the versions per script.

    Args:
      projects list[Project]: projects.

    Returns:
      dict[str, object]: scripts, their versions and the the names of the
          project that use the specific version. In the form:
          { script_name: {
              script_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    script_glob = os.path.join(self._data_directory, 'scripts', '*.*')
    versions_per_script = {}
    for path in glob.glob(script_glob):
      script_file = ScriptFile(path)

      version = None
      logging.info('Reading: {0:s}'.format(path))
      if script_file.ReadVersion():
        version = script_file.version
      if not version:
        version = 'missing'

      versions_per_script[script_file.name] = {version: []}

    for project in projects:
      project_scripts_path = os.path.join(projects_path, project.name)

      for script in versions_per_script.keys():
        script_path = os.path.join(project_scripts_path, script)
        if not os.path.exists(script_path):
          continue

        script_file = ScriptFile(script_path)

        version = None
        logging.info('Reading: {0:s}'.format(script_path))
        if script_file.ReadVersion():
          version = script_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_script[script]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_script

  def _GetVersionsPerTestScript(self, projects):
    """Retrieves the versions per test script.

    Args:
      projects list[Project]: projects.

    Returns:
      dict[str, object]: scripts, their versions and the the names of the
          project that use the specific version. In the form:
          { script_name: {
              script_version: [ project_name, ... ], ... },
              ... }
    """
    projects_path = os.path.dirname(self._data_directory)
    projects_path = os.path.dirname(projects_path)

    # TODO: determine if Python glob supports "*.{ps1,sh}".
    versions_per_script = {}
    for extension in ('ps1', 'sh'):
      extension_glob = '*.{0:s}'.format(extension)
      script_glob = os.path.join(
          self._data_directory, 'source', 'tests', extension_glob)
      for path in glob.glob(script_glob):
        if path.endswith('test_yalinfo.ps1'):
          continue

        script_file = ScriptFile(path)

        version = None
        logging.info('Reading: {0:s}'.format(path))
        if script_file.ReadVersion():
          version = script_file.version
        if not version:
          version = 'missing'

        # TODO: handle yal and pyyal place holders.
        if script_file.name in (
            'test_pyyal_set_ascii_codepage.sh',
            'test_yalexport.sh',
            'test_yalinfo.sh'):
          continue

        versions_per_script[script_file.name] = {version: []}

    for project in projects:
      project_test_scripts_path = os.path.join(
          projects_path, project.name, 'tests')

      for script in versions_per_script.keys():
        # TODO: handle yal and pyyal place holders.

        script_path = os.path.join(project_test_scripts_path, script)
        if not os.path.exists(script_path):
          continue

        script_file = ScriptFile(script_path)

        version = None
        logging.info('Reading: {0:s}'.format(script_path))
        if script_file.ReadVersion():
          version = script_file.version
        if not version:
          version = 'missing'

        projects_per_version = versions_per_script[script]
        if version not in projects_per_version:
          projects_per_version[version] = []

        projects_per_version[version].append(project.name)

    return versions_per_script

  def Generate(self, projects, output_writer):
    """Generates a wiki page.

    Args:
      projects list[Project]: projects.
      output_writer (OutputWriter): output writer.
    """
    self._GenerateSection('introduction.txt', {}, output_writer)

    versions_per_configuration = self._GetVersionsPerConfigurationFile(projects)
    versions_per_m4_script = self._GetVersionsPerM4Script(projects)
    versions_per_script = self._GetVersionsPerScript(projects)
    versions_per_test_script = self._GetVersionsPerTestScript(projects)

    projects_per_category = {}
    for project in projects:
      if project.category not in projects_per_category:
        projects_per_category[project.category] = []

      projects_per_category[project.category].append(project)

    table_of_contents = []

    table_of_contents.append('* [Configurations](Status#configurations)')
    for configuration in sorted(versions_per_configuration.keys()):
      configuration_reference = configuration.lower().replace('.', '')
      table_of_contents.append('  * [{0:s}](Status#{1:s})'.format(
          configuration, configuration_reference))

    table_of_contents.append('* [Scripts](Status#scripts)')
    for script in sorted(versions_per_script.keys()):
      script_reference = script.lower().replace('.', '')
      table_of_contents.append('  * [{0:s}](Status#{1:s})'.format(
          script, script_reference))

    table_of_contents.append('* [M4 scripts](Status#m4-scripts)')
    for m4_script in sorted(versions_per_m4_script.keys()):
      m4_script_reference = m4_script.lower().replace('.', '')
      table_of_contents.append('  * [{0:s}](Status#{1:s})'.format(
          m4_script, m4_script_reference))

    # TODO: add version check for common.

    for category in self._ORDER_OF_LIBRARY_CATEGORIES:
      category_title = self._CATEGORIES[category][0]
      catergory_reference = category_title.lower().replace(' ', '-')
      table_of_contents.append('* [{0:s}](Status#{1:s})'.format(
          category_title, catergory_reference))

      for project in projects_per_category[category]:
        table_of_contents.append('  * [{0:s}](Status#{0:s})'.format(
            project.name))

    table_of_contents.append('* [Test scripts](Status#test-scripts)')
    for script in sorted(versions_per_test_script.keys()):
      script_reference = script.lower().replace('.', '')
      table_of_contents.append('  * [{0:s}](Status#{1:s})'.format(
          script, script_reference))

    table_of_contents.append('')
    output_data = '\n'.join(table_of_contents).encode('utf-8')
    output_writer.Write(output_data)

    template_mappings = {'category_title': 'Configurations'}
    self._GenerateSection('category.txt', template_mappings, output_writer)

    project_groups = {}
    for project in projects:
      if project.group is None:
        continue

      project_group = project_groups.get(project.group, None)
      if not project_group:
        project_group = set()
        project_groups[project.group] = project_group

      project_group.add(project.name)

    for configuration, projects_per_version in sorted(
        versions_per_configuration.items()):
      template_mappings = {
          'title': configuration,
      }
      self._GenerateSection(
          'table_header.txt', template_mappings, output_writer)

      for version, project_names in sorted(
          projects_per_version.items(), reverse=True):
        project_names = self._FormatProjectNames(project_groups, project_names)

        template_mappings = {
            'project_names': project_names,
            'version': version,
        }
        self._GenerateSection(
            'table_entry.txt', template_mappings, output_writer)

    template_mappings = {'category_title': 'Scripts'}
    self._GenerateSection('category.txt', template_mappings, output_writer)

    for script, projects_per_version in sorted(
        versions_per_script.items()):
      template_mappings = {
          'title': script,
      }
      self._GenerateSection(
          'table_header.txt', template_mappings, output_writer)

      for version, project_names in sorted(
          projects_per_version.items(), reverse=True):
        project_names = self._FormatProjectNames(project_groups, project_names)

        template_mappings = {
            'project_names': project_names,
            'version': version,
        }
        self._GenerateSection(
            'table_entry.txt', template_mappings, output_writer)

    template_mappings = {'category_title': 'M4 scripts'}
    self._GenerateSection('category.txt', template_mappings, output_writer)

    for m4_script, projects_per_version in sorted(
        versions_per_m4_script.items()):
      template_mappings = {
          'title': m4_script,
      }
      self._GenerateSection(
          'table_header.txt', template_mappings, output_writer)

      for version, project_names in sorted(
          projects_per_version.items(), reverse=True):
        project_names = self._FormatProjectNames(project_groups, project_names)

        template_mappings = {
            'project_names': project_names,
            'version': version,
        }
        self._GenerateSection(
            'table_entry.txt', template_mappings, output_writer)

    # TODO: sort by groups.
    for category in self._ORDER_OF_LIBRARY_CATEGORIES:
      template_mappings = {
          'category_title': self._CATEGORIES[category][0],
      }
      self._GenerateSection('category.txt', template_mappings, output_writer)

      versions_per_library = self._GetVersionsPerLibrary(projects, category)
      for library, projects_per_version in sorted(
          versions_per_library.items()):
        template_mappings = {
            'title': library,
        }
        self._GenerateSection(
            'table_header.txt', template_mappings, output_writer)

        for version, project_names in sorted(
            projects_per_version.items(), reverse=True):
          project_names = self._FormatProjectNames(project_groups, project_names)

          template_mappings = {
              'project_names': project_names,
              'version': version,
          }
          self._GenerateSection(
              'table_entry.txt', template_mappings, output_writer)

    template_mappings = {'category_title': 'Test scripts'}
    self._GenerateSection('category.txt', template_mappings, output_writer)

    for script, projects_per_version in sorted(
        versions_per_test_script.items()):
      template_mappings = {
          'title': script,
      }
      self._GenerateSection(
          'table_header.txt', template_mappings, output_writer)

      for version, project_names in sorted(
          projects_per_version.items(), reverse=True):
        project_names = self._FormatProjectNames(project_groups, project_names)

        template_mappings = {
            'project_names': project_names,
            'version': version,
        }
        self._GenerateSection(
            'table_entry.txt', template_mappings, output_writer)


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initialize an output writer.

    Args:
      name (str): path of the output file.
    """
    super(FileWriter, self).__init__()
    self._file_object = None
    self._name = name

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    self._file_object = open(self._name, 'wb')
    return True

  def Close(self):
    """Closes the output writer object."""
    self._file_object.close()

  def Write(self, data):
    """Writes the data to file.

    Args:
      data (bytes): data to write.
    """
    self._file_object.write(data)


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self):
    """Initialize an output writer."""
    super(StdoutWriter, self).__init__()

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    return

  def Write(self, data):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      data (bytes): data to write.
    """
    print(data, end='')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates an overview of the libyal libraries.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='CONFIGURATION_FILE',
      default='projects.ini', help=(
          'The overview generation configuration file.'))

  argument_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='path of the output files to write to.')

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

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_reader = ProjectsReader()

  projects = projects_reader.ReadFromFile(options.configuration_file)
  if not projects:
    print('Unable to read projects from configuration file: {0:s}.'.format(
        options.configuration_file))
    print('')
    return False

  wiki_pages = [
      ('Overview', OverviewWikiPageGenerator),
      ('Status', StatusWikiPageGenerator),
  ]

  for page_name, page_generator_class in wiki_pages:
    data_directory = os.path.join(libyal_directory, 'data')
    template_directory = os.path.join(data_directory, 'wiki', page_name)
    wiki_page = page_generator_class(data_directory, template_directory)

    if options.output_directory:
      filename = '{0:s}.md'.format(page_name)
      output_file = os.path.join(options.output_directory, filename)
      output_writer = FileWriter(output_file)
    else:
      output_writer = StdoutWriter()

    if not output_writer.Open():
      print('Unable to open output writer.')
      print('')
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
