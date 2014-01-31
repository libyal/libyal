#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to automate generation of wiki pages of libyal libraries.
#
# Copyright (c) 2013, Joachim Metz <joachim.metz@gmail.com>
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


def GetConfigValue(config_parser, section_name, value_name):
  return json.loads(config_parser.get(section_name, value_name))


class ProjectConfiguration(object):
  """Class that contains the libyal project configuration."""

  def __init__(self):
    """Initializes the project configuation."""
    super(ProjectConfiguration, self).__init__()
    self.project_name = None
    self.project_status = None

    # Functionality the project offsers.
    self.supports_debug_output = False
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
    self.supports_package_maker = False
    self.supports_rpm = False

    # Other.
    self.supports_dokan = False
    self.supports_fuse = False

    self.source_package_url = None

    self.git_url = None

    self.tools_names = None

    self.cygwin_build_dependencies = None
    self.cygwin_dll_dependencies = None
    self.cygwin_dll_filename = None

    self.gcc_build_dependencies = None
    self.gcc_static_build_dependencies = None

    self.mingw_build_dependencies = None
    self.mingw_dll_dependencies = None
    self.mingw_dll_filename = None

    self.msvsvpp_build_dependencies = None
    self.msvsvpp_dll_dependencies = None
    self.msvsvpp_zlib_dependency = None

    self.dpkg_build_dependencies = None

    self.rpm_build_dependencies = None

  def ReadFromFile(self, filename):
    """Reads the configuration from file.

    Args:
      filename: the configuration filename.
    """
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.project_name = GetConfigValue(config_parser, 'Project', 'name')
    self.project_status = GetConfigValue(config_parser, 'Project', 'status')

    self.source_package_url = GetConfigValue(config_parser, 'source_package', 'url')

    self.git_url = GetConfigValue(config_parser, 'git', 'url')

    features = GetConfigValue(config_parser, 'Project', 'features')

    self.supports_debug_output = 'debug_output' in features
    self.supports_tools = 'tools' in features
    self.supports_python = 'python' in features

    self.supports_source_package = 'source_package' in features
    self.supports_git = 'git' in features

    self.supports_cygwin = 'cygwin' in features
    self.supports_gcc = 'gcc' in features
    self.supports_msvscpp = 'msvscpp' in features
    self.supports_mingw = 'mingw' in features

    self.supports_dpkg = 'dpkg' in features
    self.supports_package_maker = 'package_maker' in features
    self.supports_rpm = 'rpm' in features

    self.supports_dokan = 'dokan' in features
    self.supports_fuse = 'fuse' in features

    self.tools_directory = GetConfigValue(config_parser, 'tools', 'directory')
    self.tools_names = GetConfigValue(config_parser, 'tools', 'names')

    self.cygwin_build_dependencies = GetConfigValue(config_parser, 'cygwin', 'build_dependencies')
    self.cygwin_dll_dependencies = GetConfigValue(config_parser, 'cygwin', 'dll_dependencies')
    self.cygwin_dll_filename = GetConfigValue(config_parser, 'cygwin', 'dll_filename')

    self.gcc_build_dependencies = GetConfigValue(config_parser, 'gcc', 'build_dependencies')
    self.gcc_static_build_dependencies = GetConfigValue(config_parser, 'gcc', 'static_build_dependencies')

    self.mingw_build_dependencies = GetConfigValue(config_parser, 'mingw', 'build_dependencies')
    self.mingw_dll_dependencies = GetConfigValue(config_parser, 'mingw', 'dll_dependencies')
    self.mingw_dll_filename = GetConfigValue(config_parser, 'mingw', 'dll_filename')

    self.msvscpp_build_dependencies = GetConfigValue(config_parser, 'msvscpp', 'build_dependencies')
    self.msvscpp_dll_dependencies = GetConfigValue(config_parser, 'msvscpp', 'dll_dependencies')

    self.dpkg_build_dependencies = GetConfigValue(config_parser, 'dpkg', 'build_dependencies')

    self.rpm_build_dependencies = GetConfigValue(config_parser, 'rpm', 'build_dependencies')

    self.msvsvpp_zlib_dependency = False
    for dependency in self.msvscpp_build_dependencies:
      if dependency.startswith('zlib '):
        self.msvsvpp_zlib_dependency = True

  def GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      A dictionary containing the string template mappings.
    """
    table_of_contents = ''
    project_status = ''
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
    msvscpp_dll_dependencies = ''
    msvscpp_mount_tool = ''
    dpkg_build_dependencies = ''
    dpkg_filenames = ''
    package_maker_configure_options = ''
    package_maker_pyprefix = ''
    rpm_build_dependencies = ''
    rpm_filenames = ''
    rpm_rename_source_package = ''

    python_bindings_name = 'py{0:s}'.format(self.project_name[3:])
    mount_tool_name = '{0:s}mount'.format(self.project_name[3:])

    if self.project_status:
      project_status += '-{0:s}'.format(self.project_status)

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      table_of_contents += (
          'The {0:s} source code can be build with different compilers:\n').format(
              self.project_name)

    if self.supports_gcc:
      table_of_contents += '  * Using GNU Compiler Collection (GCC)\n'

      if self.gcc_build_dependencies:
        gcc_build_dependencies += (
            '\n'
            'Also make sure to have the following dependencies including '
            'source headers installed:\n')

        for dependency in self.gcc_build_dependencies:
          gcc_build_dependencies += '  * {0:s}\n'.format(dependency)

      if self.gcc_static_build_dependencies:
        for dependency in self.gcc_static_build_dependencies:
          gcc_static_build_dependencies += '  * {0:s}\n'.format(dependency)

      if self.supports_cygwin:
        table_of_contents += '    * Using Cygwin\n'

        if self.cygwin_build_dependencies:
          for dependency in self.cygwin_build_dependencies:
            cygwin_build_dependencies += '  * {0:s}\n'.format(dependency)

        if self.cygwin_dll_dependencies:
          for dependency in self.cygwin_dll_dependencies:
            cygwin_dll_dependencies += '  * {0:s}\n'.format(dependency)

        if self.supports_tools:
          cygwin_executables += (
              'And the following executables:\n'
              '{{{\n')

          for name in self.tools_names:
              cygwin_executables += (
                  '{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

          cygwin_executables += (
              '}}}\n'
              '\n')

      if self.supports_fuse:
        gcc_mount_tool += (
            '\n'
            'If you want to be able to use {0:s}, make sure that:\n'
            '  * on a Linux system you have libfuse-dev (Debian-based) or fuse-devel (!RedHat-based) installed.\n'
            '  * on a Mac OS X system, you have OSXFuse (http://osxfuse.github.com/) installed.\n').format(
                mount_tool_name)

    if self.supports_mingw:
      table_of_contents += '  * Using Minimalist GNU for Windows (MinGW)\n'

      if self.mingw_build_dependencies:
        for dependency in self.mingw_build_dependencies:
          mingw_build_dependencies += '  * {0:s}\n'.format(dependency)

      if self.mingw_dll_dependencies:
        for dependency in self.mingw_dll_dependencies:
          mingw_dll_dependencies += '  * {0:s}\n'.format(dependency)

      if self.supports_tools:
        mingw_executables += (
            'And the following executables:\n'
            '{{{\n')

        for name in self.tools_names:
            mingw_executables += (
                '{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

        mingw_executables += (
            '}}}\n'
            '\n')

    if self.supports_msvscpp:
      table_of_contents += '  * Using Microsoft Visual Studio\n'

      if self.msvscpp_build_dependencies:
        for dependency in self.msvscpp_build_dependencies:
          msvscpp_build_dependencies += '  * {0:s}\n'.format(dependency)

      if self.msvscpp_dll_dependencies:
        msvscpp_dll_dependencies = '{0:s}.dll is dependent on:\n'.format(self.project_name)

        for dependency in self.msvscpp_dll_dependencies:
          msvscpp_dll_dependencies += '  * {0:s}\n'.format(dependency)

        msvscpp_dll_dependencies += (
            'These DLLs can be found in the same directory as {0:s}.dll.\n').format(
                self.project_name)

      if self.supports_dokan:
        msvscpp_mount_tool += (
            '\n'
            'If you want to be able to use {0:s} you\'ll need Dokan library see the corresponding section below.\n'
            'Otherwise ignore or remove the dokan_dll and {0:s} Visual Studio project files.\n').format(
                mount_tool_name)

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      table_of_contents += '\n'

    if self.supports_dpkg or self.supports_package_maker or self.supports_rpm:
      table_of_contents += (
          'Or directly packaged with different package managers:\n').format(self.project_name)

    if self.supports_dpkg:
      table_of_contents += '  * Using Debian package tools (DEB)\n'

      dpkg_build_dependencies = list(self.dpkg_build_dependencies)

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
      table_of_contents += '  * Using !RedHat package tools (RPM)\n'

      rpm_build_dependencies = list(self.rpm_build_dependencies)

      if self.supports_fuse:
        rpm_build_dependencies.append('fuse-devel')

      if self.supports_python:
        rpm_build_dependencies.append('python-devel')

      if rpm_build_dependencies:
        rpm_build_dependencies = ' '.join(rpm_build_dependencies)

      if self.project_status:
        rpm_rename_source_package += (
            'mv {0:s}{1:s}-<version>.tar.gz {0:s}-<version>.tar.gz\n'.format(
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

    if self.supports_package_maker:
      table_of_contents += '  * Using Mac OS X !PackageMaker\n'

      if self.supports_python:
        package_maker_configure_options += ' --enable-python'

        package_maker_pyprefix += (
            'Do not use --with-pyprefix here. The !PackageMaker files are '
            'configured to look for the Python-bindings in the '
            '$PWD/macosx/tmp/ path and install them into the corresponding '
            'system directory.')

    template_mappings = {
        'table_of_contents': table_of_contents,

        'project_name': self.project_name,
        'project_name_upper_case': self.project_name.upper(),
        'project_status': project_status,

        'python_bindings_name': python_bindings_name,

        'source_package_url': self.source_package_url,

        'git_url': self.git_url,

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
        'msvscpp_dll_dependencies': msvscpp_dll_dependencies,
        'msvscpp_mount_tool': msvscpp_mount_tool,

        'dpkg_build_dependencies': dpkg_build_dependencies,
        'dpkg_filenames': dpkg_filenames,

        'package_maker_configure_options': package_maker_configure_options,
        'package_maker_pyprefix': package_maker_pyprefix,

        'rpm_build_dependencies': rpm_build_dependencies,
        'rpm_filenames': rpm_filenames,
        'rpm_rename_source_package': rpm_rename_source_package,
    }
    return template_mappings


class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  def __init__(self):
    """Initialize the wiki page generator."""
    super(WikiPageGenerator, self).__init__()


class BuildPageGenerator(WikiPageGenerator):
  """Class that generates the "Building from source" wiki page."""

  def __init__(self, template_directory):
    """Initialize the wiki page generator.

    Args:
      template_directory: the path of the template directory.
    """
    super(BuildPageGenerator, self).__init__()
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

  def _GenerateSection(self, project_configuration, template_filename):
    """Generates a section from template filename.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      template_filename: the name of the file containing the template string.
    """
    template_string = self._ReadTemplateFile(template_filename)

    return template_string.substitute(
        project_configuration.GetTemplateMappings())

  def Generate(self, project_configuration):
    """Generates the wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
    """
    print self._GenerateSection(project_configuration, 'page_header.txt'),
    print self._GenerateSection(project_configuration, 'introduction.txt'),

    if (project_configuration.supports_source_package or
        project_configuration.supports_git):
      print self._GenerateSection(project_configuration, 'source.txt'),

      if project_configuration.supports_source_package:
        print self._GenerateSection(
            project_configuration, 'source_package.txt'),

      if project_configuration.supports_git:
        print self._GenerateSection(project_configuration, 'source_git.txt'),

    if project_configuration.supports_gcc:
      print self._GenerateSection(project_configuration, 'gcc.txt'),

      if project_configuration.supports_debug_output:
        print self._GenerateSection(project_configuration, 'gcc_debug_output.txt'),

      print self._GenerateSection(project_configuration, 'gcc_static_library.txt'),

      if project_configuration.supports_tools:
        print self._GenerateSection(project_configuration, 'gcc_static_executables.txt'),

      print self._GenerateSection(project_configuration, 'cygwin.txt'),
      print self._GenerateSection(project_configuration, 'gcc_macosx.txt'),
      print self._GenerateSection(project_configuration, 'gcc_solaris.txt'),

    if project_configuration.supports_mingw:
      print self._GenerateSection(project_configuration, 'mingw.txt'),

    if project_configuration.supports_msvscpp:
      print self._GenerateSection(project_configuration, 'msvscpp.txt'),

      if project_configuration.supports_debug_output:
        print self._GenerateSection(project_configuration, 'msvscpp_debug.txt'),

      if project_configuration.msvsvpp_zlib_dependency:
        print self._GenerateSection(project_configuration, 'msvscpp_zlib.txt'),

      if project_configuration.supports_dokan:
        print self._GenerateSection(project_configuration, 'msvscpp_dokan.txt'),

      if project_configuration.supports_python:
        print self._GenerateSection(project_configuration, 'msvscpp_python.txt'),

      print self._GenerateSection(project_configuration, 'msvscpp_build.txt'),
      print self._GenerateSection(project_configuration, 'msvscpp_dll.txt'),

      print self._GenerateSection(project_configuration, 'msvscpp_2010.txt'),

    if project_configuration.supports_dpkg:
      print self._GenerateSection(project_configuration, 'dpkg.txt'),

    if project_configuration.supports_rpm:
      print self._GenerateSection(project_configuration, 'rpm.txt'),

    if project_configuration.supports_package_maker:
      print self._GenerateSection(project_configuration, 'package_maker.txt'),


def Main():
  args_parser = argparse.ArgumentParser(description=(
      'Generates the wiki pages of the libyal libraries.'))

  args_parser.add_argument(
      'config_file', action='store', metavar='CONFIG_FILE',
      default='wiki.conf', help='The wiki generation config file.')

  options = args_parser.parse_args()

  if not options.config_file:
    print 'Config file missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  project_configuration = ProjectConfiguration()
  project_configuration.ReadFromFile(options.config_file)

  wiki_page = BuildPageGenerator(os.path.join('wiki', 'Building'))
  wiki_page.Generate(project_configuration)

  # TODO: generate wiki pages.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
