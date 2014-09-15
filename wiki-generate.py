#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to automate generation of wiki pages of libyal libraries.
#
# Copyright (c) 2013-2014, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import string
import os
import sys

try:
  import ConfigParser as configparser
except ImportError:
  import configparser


class ConfigError(Exception):
  """Class that defines a configuration error."""


class ProjectConfiguration(object):
  """Class that contains the libyal project configuration."""

  def __init__(self):
    """Initializes the project configuation."""
    super(ProjectConfiguration, self).__init__()
    self.project_name = None
    self.project_status = None
    self.project_description = None

    # Functionality the project offsers.
    self.supports_debug_output = False
    self.supports_tests = False
    self.supports_tools = False
    self.supports_python = False

    # Source distribution methods the project offsers.
    self.supports_source_package = False
    self.supports_git = False

    # Compilers the project supports.
    self.supports_cygwin = False
    self.supports_gcc = False
    self.supports_mingw = False
    self.supports_msvscpp = False

    # Packaging methods the project supports.
    self.supports_dpkg = False
    self.supports_rpm = False

    # Other.
    self.supports_dokan = False
    self.supports_fuse = False

    self.source_package_url = None

    self.git_url = None

    self.tests_supports_valgrind = None
    self.tests_profiles = None
    self.tests_example_filename1 = None
    self.tests_example_filename2 = None

    self.tools_names = None

    self.cygwin_build_dependencies = None
    self.cygwin_dll_dependencies = None
    self.cygwin_dll_filename = None

    self.gcc_build_dependencies = None
    self.gcc_static_build_dependencies = None

    self.mingw_build_dependencies = None
    self.mingw_dll_dependencies = None
    self.mingw_dll_filename = None

    self.msvscpp_build_dependencies = None
    self.msvscpp_dll_dependencies = None
    self.msvscpp_zlib_dependency = None

    self.dpkg_build_dependencies = None

    self.rpm_build_dependencies = None

    self.mount_tool_missing_backend_error = None
    self.mount_tool_mount_point = None
    self.mount_tool_mounted_description = None
    self.mount_tool_mounted_dokan = None
    self.mount_tool_mounted_fuse = None
    self.mount_tool_source = None
    self.mount_tool_source_description = None
    self.mount_tool_source_description_long = None
    self.mount_tool_source_type = None
    self.mount_tool_supported_backends = None

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
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.project_name = self._GetConfigValue(config_parser, 'Project', 'name')
    self.project_status = self._GetConfigValue(
        config_parser, 'Project', 'status')
    self.project_description = self._GetConfigValue(
        config_parser, 'Project', 'description')

    self.source_package_url = self._GetConfigValue(
        config_parser, 'source_package', 'url')

    self.git_url = self._GetConfigValue(config_parser, 'git', 'url')

    features = self._GetConfigValue(config_parser, 'Project', 'features')

    self.supports_debug_output = 'debug_output' in features
    self.supports_tests = 'tests' in features
    self.supports_tools = 'tools' in features
    self.supports_python = 'python' in features

    self.supports_source_package = 'source_package' in features
    self.supports_git = 'git' in features

    self.supports_cygwin = 'cygwin' in features
    self.supports_gcc = 'gcc' in features
    self.supports_msvscpp = 'msvscpp' in features
    self.supports_mingw = 'mingw' in features

    self.supports_dpkg = 'dpkg' in features
    self.supports_rpm = 'rpm' in features

    self.supports_dokan = 'dokan' in features
    self.supports_fuse = 'fuse' in features

    if self.supports_tests and not config_parser.has_section('tests'):
      raise ConfigError(
          'Support for tests enabled but no corresponding section: '
          'tests is missing.')

    if config_parser.has_section('tests'):
      tests_features = self._GetConfigValue(config_parser, 'tests', 'features')

      self.tests_supports_valgrind = 'valgrind' in tests_features

      self.tests_profiles = self._GetConfigValue(
          config_parser, 'tests', 'profiles')
      self.tests_example_filename1 = self._GetConfigValue(
          config_parser, 'tests', 'example_filename1')
      self.tests_example_filename2 = self._GetConfigValue(
          config_parser, 'tests', 'example_filename2')

    if self.supports_tools and not config_parser.has_section('tools'):
      raise ConfigError(
          'Support for tools enabled but no corresponding section: '
          'tools is missing.')

    if config_parser.has_section('tools'):
      self.tools_directory = self._GetConfigValue(
          config_parser, 'tools', 'directory')
      self.tools_names = self._GetConfigValue(
          config_parser, 'tools', 'names')

    if self.supports_cygwin and not config_parser.has_section('cygwin'):
      raise ConfigError(
          'Support for Cygwin enabled but no corresponding section: '
          'cygwin is missing.')

    if config_parser.has_section('cygwin'):
      self.cygwin_build_dependencies = self._GetConfigValue(
          config_parser, 'cygwin', 'build_dependencies')
      self.cygwin_dll_dependencies = self._GetConfigValue(
          config_parser, 'cygwin', 'dll_dependencies')
      self.cygwin_dll_filename = self._GetConfigValue(
          config_parser, 'cygwin', 'dll_filename')

    if self.supports_gcc and not config_parser.has_section('gcc'):
      raise ConfigError(
          'Support for GCC enabled but no corresponding section: '
          'gcc is missing.')

    if config_parser.has_section('gcc'):
      self.gcc_build_dependencies = self._GetConfigValue(
          config_parser, 'gcc', 'build_dependencies')
      self.gcc_static_build_dependencies = self._GetConfigValue(
          config_parser, 'gcc', 'static_build_dependencies')

    if self.supports_mingw and not config_parser.has_section('mingw'):
      raise ConfigError(
          'Support for MinGW enabled but no corresponding section: '
          'mingw is missing.')

    if config_parser.has_section('mingw'):
      self.mingw_build_dependencies = self._GetConfigValue(
          config_parser, 'mingw', 'build_dependencies')
      self.mingw_dll_dependencies = self._GetConfigValue(
          config_parser, 'mingw', 'dll_dependencies')
      self.mingw_dll_filename = self._GetConfigValue(
          config_parser, 'mingw', 'dll_filename')

    if self.supports_msvscpp and not config_parser.has_section('msvscpp'):
      raise ConfigError(
          'Support for Visual Studio enabled but no corresponding section: '
          'msvscpp is missing.')

    if config_parser.has_section('msvscpp'):
      self.msvscpp_build_dependencies = self._GetConfigValue(
          config_parser, 'msvscpp', 'build_dependencies')
      self.msvscpp_dll_dependencies = self._GetConfigValue(
          config_parser, 'msvscpp', 'dll_dependencies')

    if self.supports_dpkg and not config_parser.has_section('dpkg'):
      raise ConfigError(
          'Support for dpkg enabled but no corresponding section: '
          'dpkg is missing.')

    if config_parser.has_section('dpkg'):
      self.dpkg_build_dependencies = self._GetConfigValue(
          config_parser, 'dpkg', 'build_dependencies')

    if self.supports_rpm and not config_parser.has_section('rpm'):
      raise ConfigError(
          'Support for rpm enabled but no corresponding section: '
          'rpm is missing.')

    if config_parser.has_section('rpm'):
      self.rpm_build_dependencies = self._GetConfigValue(
          config_parser, 'rpm', 'build_dependencies')

    if ((self.supports_dokan or self.supports_fuse) and
        not config_parser.has_section('mount_tool')):
      raise ConfigError(
          'Support for dokan and/or fuse enabled but no corresponding section: '
          'mount_tool is missing.')

    if config_parser.has_section('mount_tool'):
      self.mount_tool_missing_backend_error = self._GetConfigValue(
          config_parser, 'mount_tool', 'missing_backend_error')
      self.mount_tool_mount_point = self._GetConfigValue(
          config_parser, 'mount_tool', 'mount_point')
      self.mount_tool_mounted_description = self._GetConfigValue(
          config_parser, 'mount_tool', 'mounted_description')
      self.mount_tool_mounted_dokan = self._GetConfigValue(
          config_parser, 'mount_tool', 'mounted_dokan')
      self.mount_tool_mounted_fuse = self._GetConfigValue(
          config_parser, 'mount_tool', 'mounted_fuse')
      self.mount_tool_source = self._GetConfigValue(
          config_parser, 'mount_tool', 'source')
      self.mount_tool_source_description = self._GetConfigValue(
          config_parser, 'mount_tool', 'source_description')

      # If the long source description is not set it will default to
      # source description.
      try:
        self.mount_tool_source_description_long = self._GetConfigValue(
            config_parser, 'mount_tool', 'source_description_long')
      except configparser.NoOptionError:
        pass

      self.mount_tool_source_type = self._GetConfigValue(
          config_parser, 'mount_tool', 'source_type')

      if self.mount_tool_source_type not in ['image', 'volume']:
        raise ConfigError('unsupported mount tool source type: {0:s}'.format(
            self.mount_tool_source_type))

      self.mount_tool_supported_backends = self._GetConfigValue(
          config_parser, 'mount_tool', 'supported_backends')

    self.msvscpp_zlib_dependency = False
    for dependency in self.msvscpp_build_dependencies:
      if dependency.startswith('zlib '):
        self.msvscpp_zlib_dependency = True

  def GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      A dictionary containing the string template mappings.
    """
    building_table_of_contents = ''

    project_status = ''

    tests_profiles = ''

    cygwin_build_dependencies = ''
    cygwin_dll_dependencies = ''
    cygwin_executables = ''

    gcc_build_dependencies = ''
    gcc_static_build_dependencies = ''
    gcc_mount_tool = ''

    mingw_build_dependencies = ''
    mingw_dll_dependencies = ''
    mingw_executables = ''

    msvscpp_build_dependencies = ''
    msvscpp_build_git = ''
    msvscpp_dll_dependencies = ''
    msvscpp_mount_tool = ''

    dpkg_build_dependencies = ''
    dpkg_filenames = ''

    macosx_pkg_configure_options = ''

    rpm_build_dependencies = ''
    rpm_filenames = ''
    rpm_rename_source_package = ''

    mount_tool_source_description_long = ''
    mount_tool_supported_backends = ''

    python_bindings_name = 'py{0:s}'.format(self.project_name[3:])
    mount_tool_name = '{0:s}mount'.format(self.project_name[3:])
    tools_name = '{0:s}tools'.format(self.project_name[3:])

    if self.project_status:
      project_status += '-{0:s}'.format(self.project_status)

    if self.supports_tests:
      for profile in self.tests_profiles:
        tests_profiles += '* {0:s}\n'.format(profile)

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      building_table_of_contents += (
          'The {0:s} source code can be build with different compilers:\n').format(
              self.project_name)

    if self.supports_gcc:
      building_table_of_contents += '* Using GNU Compiler Collection (GCC)\n'

      if self.gcc_build_dependencies:
        gcc_build_dependencies = (
            '\n'
            'Also make sure to have the following dependencies including '
            'source headers installed:\n')

        for dependency in self.gcc_build_dependencies:
          gcc_build_dependencies += '* {0:s}\n'.format(dependency)

      if self.gcc_static_build_dependencies:
        for dependency in self.gcc_static_build_dependencies:
          gcc_static_build_dependencies += '* {0:s}\n'.format(dependency)

      if self.supports_fuse:
        gcc_static_build_dependencies += (
            '* fuse (optional, can be disabled by --with-libfuse=no)')

      if self.supports_cygwin:
        building_table_of_contents += '  * Using Cygwin\n'

        if self.cygwin_build_dependencies:
          for dependency in self.cygwin_build_dependencies:
            cygwin_build_dependencies += '* {0:s}\n'.format(dependency)

        if self.cygwin_dll_dependencies:
          for dependency in self.cygwin_dll_dependencies:
            cygwin_dll_dependencies += '* {0:s}\n'.format(dependency)

        if self.supports_tools:
          cygwin_executables += (
              'And the following executables:\n'
              '```\n')

          for name in self.tools_names:
              cygwin_executables += (
                  '{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

          cygwin_executables += (
              '```\n')

      if self.supports_fuse:
        gcc_mount_tool += (
            '\n'
            'If you want to be able to use {0:s}, make sure that:\n'
            '* on a Linux system you have libfuse-dev (Debian-based) or '
            'fuse-devel (!RedHat-based) installed.\n'
            '* on a Mac OS X system, you have OSXFuse '
            '(http://osxfuse.github.com/) installed.\n').format(mount_tool_name)

    if self.supports_mingw:
      building_table_of_contents += (
          '* Using Minimalist GNU for Windows (MinGW)\n')

      if self.mingw_build_dependencies:
        for dependency in self.mingw_build_dependencies:
          mingw_build_dependencies += '* {0:s}\n'.format(dependency)

      if self.mingw_dll_dependencies:
        for dependency in self.mingw_dll_dependencies:
          mingw_dll_dependencies += '* {0:s}\n'.format(dependency)

      if self.supports_tools:
        mingw_executables += (
            'And the following executables:\n'
            '```\n')

        for name in self.tools_names:
            mingw_executables += (
                '{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

        mingw_executables += (
            '```\n'
            '\n')

    if self.supports_msvscpp:
      building_table_of_contents += '* Using Microsoft Visual Studio\n'

      if self.msvscpp_build_dependencies:
        msvscpp_build_dependencies = (
            '\n'
            'To compile {0:s} using Microsoft Visual Studio you\'ll '
            'need:\n').format(self.project_name)

        for dependency in self.msvscpp_build_dependencies:
          msvscpp_build_dependencies += '* {0:s}\n'.format(dependency)

      if self.msvscpp_dll_dependencies:
        msvscpp_dll_dependencies = '{0:s}.dll is dependent on:\n'.format(
            self.project_name)

        for dependency in self.msvscpp_dll_dependencies:
          msvscpp_dll_dependencies += '* {0:s}\n'.format(dependency)

        msvscpp_dll_dependencies += (
            '\n'
            'These DLLs can be found in the same directory as '
            '{0:s}.dll.\n').format(self.project_name)

      if self.supports_git:
        msvscpp_build_git = (
            '\n'
            'Note that if you want to build {0:s} from source checked out of '
            'git with Visual Studio make sure the autotools are able to make a '
            'distribution package of {0:s} before trying to build it.\n'
            'You can create distribution package by running: '
            '"make dist".\n').format(self.project_name)

      if self.supports_dokan:
        msvscpp_mount_tool += (
            '\n'
            'If you want to be able to use {0:s} you\'ll need Dokan library '
            'see the corresponding section below.\n'
            'Otherwise ignore or remove the dokan_dll and {0:s} Visual Studio '
            'project files.\n').format(mount_tool_name)

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      building_table_of_contents += '\n'

    building_table_of_contents += (
        'Or directly packaged with different package managers:\n').format(
            self.project_name)

    if self.supports_dpkg:
      building_table_of_contents += '* Using Debian package tools (DEB)\n'

      if self.dpkg_build_dependencies is None:
        dpkg_build_dependencies = []
      else:
        dpkg_build_dependencies = self.dpkg_build_dependencies

      if self.supports_fuse:
        dpkg_build_dependencies.append('libfuse-dev')

      if self.supports_python:
        dpkg_build_dependencies.append('python-dev')

      if dpkg_build_dependencies:
        dpkg_build_dependencies = ' '.join(dpkg_build_dependencies)

      dpkg_filenames += (
          '{0:s}_<version>-1_<arch>.deb\n'
          '{0:s}-dev_<version>-1_<arch>.deb').format(
              self.project_name)

      if self.supports_python:
        dpkg_filenames += (
            '\n{0:s}-python_<version>-1_<arch>.deb').format(
                self.project_name)

      if self.supports_tools:
        dpkg_filenames += (
            '\n{0:s}-tools_<version>-1_<arch>.deb').format(
                self.project_name)

    if self.supports_rpm:
      building_table_of_contents += '* Using !RedHat package tools (RPM)\n'

      if self.rpm_build_dependencies is None:
        rpm_build_dependencies = []
      else:
        rpm_build_dependencies = self.rpm_build_dependencies

      if self.supports_fuse:
        rpm_build_dependencies.append('fuse-devel')

      if self.supports_python:
        rpm_build_dependencies.append('python-devel')

      if rpm_build_dependencies:
        rpm_build_dependencies = ' '.join(rpm_build_dependencies)

      if self.project_status:
        rpm_rename_source_package += (
            'mv {0:s}-{1:s}-<version>.tar.gz {0:s}-<version>.tar.gz\n'.format(
                self.project_name, self.project_status))

      rpm_filenames += (
         '~/rpmbuild/RPMS/<arch>/{0:s}-<version>-1.<arch>.rpm\n'
         '~/rpmbuild/RPMS/<arch>/{0:s}-devel-<version>-1.<arch>.rpm\n').format(
              self.project_name)

      if self.supports_python:
        rpm_filenames += (
           '~/rpmbuild/RPMS/<arch>/{0:s}-python-<version>-1.<arch>.rpm\n').format(
               self.project_name)

      if self.supports_tools:
        rpm_filenames += (
           '~/rpmbuild/RPMS/<arch>/{0:s}-tools-<version>-1.<arch>.rpm\n').format(
               self.project_name)

      rpm_filenames += (
         '~/rpmbuild/SRPMS/{0:s}-<version>-1.src.rpm').format(
             self.project_name)

    building_table_of_contents += '* Using Mac OS X pkgbuild\n'

    if self.supports_python:
      macosx_pkg_configure_options = ' --enable-python --with-pyprefix'

    if self.mount_tool_source_description_long:
      mount_tool_source_description_long = self.mount_tool_source_description_long
    else:
      mount_tool_source_description_long = self.mount_tool_source_description

    if self.mount_tool_supported_backends:
      for backend in self.mount_tool_supported_backends:
        mount_tool_supported_backends += '* {0:s}\n'.format(backend)

    template_mappings = {
        'building_table_of_contents': building_table_of_contents,

        'project_name': self.project_name,
        'project_name_upper_case': self.project_name.upper(),
        'project_status': project_status,
        'project_description': self.project_description,

        'python_bindings_name': python_bindings_name,
        'mount_tool_name': mount_tool_name,
        'tools_name': tools_name,

        'source_package_url': self.source_package_url,

        'git_url': self.git_url,

        'tests_profiles': tests_profiles,
        'tests_example_filename1': self.tests_example_filename1,
        'tests_example_filename2': self.tests_example_filename2,

        'cygwin_build_dependencies': cygwin_build_dependencies,
        'cygwin_dll_dependencies': cygwin_dll_dependencies,
        'cygwin_dll_filename': self.cygwin_dll_filename,
        'cygwin_executables': cygwin_executables,

        'gcc_build_dependencies': gcc_build_dependencies,
        'gcc_static_build_dependencies': gcc_static_build_dependencies,
        'gcc_mount_tool': gcc_mount_tool,

        'mingw_build_dependencies': mingw_build_dependencies,
        'mingw_dll_dependencies': mingw_dll_dependencies,
        'mingw_dll_filename': self.mingw_dll_filename,
        'mingw_executables': mingw_executables,

        'msvscpp_build_dependencies': msvscpp_build_dependencies,
        'msvscpp_build_git': msvscpp_build_git,
        'msvscpp_dll_dependencies': msvscpp_dll_dependencies,
        'msvscpp_mount_tool': msvscpp_mount_tool,

        'dpkg_build_dependencies': dpkg_build_dependencies,
        'dpkg_filenames': dpkg_filenames,

        'macosx_pkg_configure_options': macosx_pkg_configure_options,

        'rpm_build_dependencies': rpm_build_dependencies,
        'rpm_filenames': rpm_filenames,
        'rpm_rename_source_package': rpm_rename_source_package,

        'mount_tool_missing_backend_error': self.mount_tool_missing_backend_error,
        'mount_tool_mount_point': self.mount_tool_mount_point,
        'mount_tool_mounted_description': self.mount_tool_mounted_description,
        'mount_tool_mounted_dokan': self.mount_tool_mounted_dokan,
        'mount_tool_mounted_fuse': self.mount_tool_mounted_fuse,
        'mount_tool_source': self.mount_tool_source,
        'mount_tool_source_description': self.mount_tool_source_description,
        'mount_tool_source_description_long': mount_tool_source_description_long,
        'mount_tool_supported_backends': mount_tool_supported_backends,
    }
    return template_mappings


class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  def __init__(self, template_directory):
    """Initialize the wiki page generator.

    Args:
      template_directory: the path of the template directory.
    """
    super(WikiPageGenerator, self).__init__()
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


class BuildingPageGenerator(WikiPageGenerator):
  """Class that generates the "Building from source" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates the wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, 'introduction.txt', output_writer)

    if (project_configuration.supports_source_package or
        project_configuration.supports_git):
      self._GenerateSection(project_configuration, 'source.txt', output_writer)

      if project_configuration.supports_source_package:
        self._GenerateSection(
            project_configuration, 'source_package.txt', output_writer)

      if project_configuration.supports_git:
        self._GenerateSection(
            project_configuration, 'source_git.txt', output_writer)

    if project_configuration.supports_gcc:
      self._GenerateSection(project_configuration, 'gcc.txt', output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            project_configuration, 'gcc_debug_output.txt', output_writer)

      self._GenerateSection(
        project_configuration, 'gcc_static_library.txt', output_writer)

      if project_configuration.supports_tools:
        self._GenerateSection(
            project_configuration, 'gcc_static_executables.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, 'gcc_python.txt', output_writer)

      self._GenerateSection(project_configuration, 'cygwin.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'gcc_macosx.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, 'gcc_macosx_python.txt', output_writer)

      self._GenerateSection(
          project_configuration, 'gcc_solaris.txt', output_writer)

    if project_configuration.supports_mingw:
      self._GenerateSection(project_configuration, 'mingw.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'mingw_msys.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'mingw_dll.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'mingw_troubleshooting.txt', output_writer)

    if project_configuration.supports_msvscpp:
      self._GenerateSection(project_configuration, 'msvscpp.txt', output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            project_configuration, 'msvscpp_debug.txt', output_writer)

      if project_configuration.msvscpp_zlib_dependency:
        self._GenerateSection(
            project_configuration, 'msvscpp_zlib.txt', output_writer)

      if project_configuration.supports_dokan:
        self._GenerateSection(
            project_configuration, 'msvscpp_dokan.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, 'msvscpp_python.txt', output_writer)

      self._GenerateSection(
          project_configuration, 'msvscpp_build.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'msvscpp_dll.txt', output_writer)

      self._GenerateSection(
          project_configuration, 'msvscpp_2010.txt', output_writer)

    if project_configuration.supports_dpkg:
      self._GenerateSection(project_configuration, 'dpkg.txt', output_writer)

    if project_configuration.supports_rpm:
      self._GenerateSection(project_configuration, 'rpm.txt', output_writer)

    self._GenerateSection(
        project_configuration, 'macosx_pkg.txt', output_writer)


class HomePageGenerator(WikiPageGenerator):
  """Class that generates the "Home" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates the wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, 'introduction.txt', output_writer)


class MountingPageGenerator(WikiPageGenerator):
  """Class that generates the "Mounting a ..." wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates the wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, 'introduction.txt', output_writer)

    if project_configuration.mount_tool_source_type == 'image':
      self._GenerateSection(
          project_configuration, 'mounting_image.txt', output_writer)

    elif project_configuration.mount_tool_source_type == 'volume':
      self._GenerateSection(
          project_configuration, 'mounting_volume.txt', output_writer)

    self._GenerateSection(
        project_configuration, 'mounting_missing_backend.txt', output_writer)

    if project_configuration.mount_tool_source_type == 'volume':
      self._GenerateSection(
          project_configuration, 'mounting_volume_loopback.txt', output_writer)
      self._GenerateSection(
          project_configuration, 'obtaining_volume_offset.txt', output_writer)

    self._GenerateSection(
        project_configuration, 'mounting_root_access.txt', output_writer)

    if project_configuration.supports_dokan:
      if project_configuration.mount_tool_source_type == 'image':
        self._GenerateSection(
            project_configuration, 'mounting_image_windows.txt', output_writer)

      elif project_configuration.mount_tool_source_type == 'volume':
        self._GenerateSection(
            project_configuration, 'mounting_volume_windows.txt', output_writer)

    self._GenerateSection(
        project_configuration, 'unmounting.txt', output_writer)

    if project_configuration.supports_dokan:
      self._GenerateSection(
          project_configuration, 'unmounting_windows.txt', output_writer)

    self._GenerateSection(
        project_configuration, 'troubleshooting.txt', output_writer)


class TestingPageGenerator(WikiPageGenerator):
  """Class that generates the "Testing" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates the wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, 'tests.txt', output_writer)
    self._GenerateSection(
        project_configuration, 'tests_files.txt', output_writer)
    self._GenerateSection(
        project_configuration, 'tests_profiles.txt', output_writer)

    if project_configuration.tests_supports_valgrind:
      self._GenerateSection(
          project_configuration, 'tests_valgrind.txt', output_writer)


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initialize the output writer.

    Args:
      name: the name of the output.
    """
    super(FileWriter, self).__init__()
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
    print data,


def Main():
  args_parser = argparse.ArgumentParser(description=(
      'Generates the wiki pages of the libyal libraries.'))

  args_parser.add_argument(
      'config_file', action='store', metavar='CONFIG_FILE',
      default='wiki.conf', help='The wiki generation config file.')

  args_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='path of the output files to write to.')

  options = args_parser.parse_args()

  if not options.config_file:
    print u'Config file missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  if not os.path.exists(options.config_file):
    print u'No such config file: {0:s}.'.format(options.config_file)
    print u''
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print u'No such output directory: {0:s}.'.format(options.output_directory)
    print u''
    return False

  project_configuration = ProjectConfiguration()
  project_configuration.ReadFromFile(options.config_file)

  if options.output_directory:
    output_file = os.path.join(options.output_directory, 'Home.md')
    output_writer = FileWriter(output_file)
  else:
    output_writer = StdoutWriter()

  if not output_writer.Open():
    print u'Unable to open output writer.'
    print u''
    return False

  script_directory = os.path.dirname(os.path.abspath(__file__))

  template_directory = os.path.join(script_directory, 'wiki', 'Home')
  wiki_page = HomePageGenerator(template_directory)
  wiki_page.Generate(project_configuration, output_writer)

  output_writer.Close()

  if options.output_directory:
    output_file = os.path.join(options.output_directory, 'Building.md')
    output_writer = FileWriter(output_file)
  else:
    output_writer = StdoutWriter()

  if not output_writer.Open():
    print u'Unable to open output writer.'
    print u''
    return False

  script_directory = os.path.dirname(os.path.abspath(__file__))

  template_directory = os.path.join(script_directory, 'wiki', 'Building')
  wiki_page = BuildingPageGenerator(template_directory)
  wiki_page.Generate(project_configuration, output_writer)

  output_writer.Close()

  if project_configuration.supports_tests:
    if options.output_directory:
      output_file = os.path.join(options.output_directory, 'Testing.md')
      output_writer = FileWriter(output_file)
    else:
      output_writer = StdoutWriter()

    if not output_writer.Open():
      print u'Unable to open output writer.'
      print u''
      return False

    template_directory = os.path.join(script_directory, 'wiki', 'Testing')
    wiki_page = TestingPageGenerator(template_directory)
    wiki_page.Generate(project_configuration, output_writer)

    output_writer.Close()

  if (project_configuration.supports_dokan or
      project_configuration.supports_fuse):
    if options.output_directory:
      output_file = os.path.join(options.output_directory, 'Mounting.md')
      output_writer = FileWriter(output_file)
    else:
      output_writer = StdoutWriter()

    if not output_writer.Open():
      print u'Unable to open output writer.'
      print u''
      return False

    template_directory = os.path.join(script_directory, 'wiki', 'Mounting')
    wiki_page = MountingPageGenerator(template_directory)
    wiki_page.Generate(project_configuration, output_writer)

    output_writer.Close()

  # TODO: generate more wiki pages.
  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
