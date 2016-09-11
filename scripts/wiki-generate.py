#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of wiki pages of the libyal libraries."""

from __future__ import print_function
import abc
import argparse
import json
import string
import os
import re
import sys

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class ConfigError(Exception):
  """Class that defines a configuration error."""


class ProjectConfiguration(object):
  """Class that defines a project configuration."""

  def __init__(self):
    """Initializes a project configuation."""
    super(ProjectConfiguration, self).__init__()
    self.project_name = None
    self.project_status = None
    self.project_description = None
    self.project_documentation_url = None
    self.project_download_url = None
    self.project_git_url = None

    # Functionality the project offsers.
    self.supports_debug_output = False
    self.supports_tests = False
    self.supports_tools = False
    self.supports_python = False

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

    self.library_build_dependencies = None

    self.development_main_object = None
    self.development_main_object_filename = None
    self.development_main_object_pre_open_python = None
    self.development_main_object_post_open_python = None
    self.development_main_object_post_open_file_object_python = None
    self.development_main_object_size = None
    self.development_glob = False
    self.development_pytsk3 = False

    self.tests_supports_valgrind = None
    self.tests_profiles = None
    self.tests_example_filename1 = None
    self.tests_example_filename2 = None

    self.troubleshooting_example = None

    self.tools_names = None
    self.tools_directory = None

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

    self.mount_tool_additional_arguments = None
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
    """Retrieves a configuration value from the config parser.

    Args:
      config_parser (ConfigParser): configuration parser.
      section_name (str): name of the section that contains the value.
      value_name (str): name of the value.

    Returns:
      object: value.
    """
    return json.loads(config_parser.get(section_name, value_name))

  def _GetOptionalConfigValue(
      self, config_parser, section_name, value_name, default_value=None):
    """Retrieves an optional configuration value from the config parser.

    Args:
      config_parser (ConfigParser): configuration parser.
      section_name (str): name of the section that contains the value.
      value_name (str): name of the value.

    Returns:
      object: value or default value if not available.
    """
    try:
      return self._GetConfigValue(config_parser, section_name, value_name)
    except configparser.NoOptionError:
      return default_value

  def ReadFromFile(self, filename):
    """Reads the configuration from file.

    Args:
      filename (str): path of the configuration file.
    """
    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.project_name = self._GetConfigValue(
        config_parser, u'project', u'name')
    self.project_status = self._GetConfigValue(
        config_parser, u'project', u'status')

    self.project_documentation_url = self._GetOptionalConfigValue(
        config_parser, u'project', u'documentation_url')

    self.project_download_url = self._GetConfigValue(
        config_parser, u'project', u'download_url')
    self.project_git_url = self._GetConfigValue(
        config_parser, u'project', u'git_url')

    features = self._GetConfigValue(
        config_parser, u'project', u'features')

    self.supports_debug_output = u'debug_output' in features
    self.supports_python = u'python' in features

    self.supports_dokan = u'dokan' in features
    self.supports_fuse = u'fuse' in features

    self.library_build_dependencies = self._GetConfigValue(
        config_parser, u'library', u'build_dependencies')

    if config_parser.has_section(u'development'):
      features = self._GetOptionalConfigValue(
          config_parser, u'development', u'features')

      if features:
        self.development_glob = u'glob' in features
        self.development_pytsk3 = u'pytsk3' in features

      self.development_main_object = self._GetConfigValue(
          config_parser, u'development', u'main_object')

      self.development_main_object_filename = self._GetConfigValue(
          config_parser, u'development', u'main_object_filename')

      self.development_main_object_size = self._GetOptionalConfigValue(
          config_parser, u'development', u'main_object_size')

      self.development_main_object_pre_open_python = (
          self._GetOptionalConfigValue(
              config_parser, u'development', u'main_object_pre_open_python'))

      self.development_main_object_post_open_python = (
          self._GetOptionalConfigValue(
              config_parser, u'development', u'main_object_post_open_python'))

      self.development_main_object_post_open_file_object_python = (
          self._GetOptionalConfigValue(
              config_parser, u'development',
              u'main_object_post_open_file_object_python'))

    if config_parser.has_section(u'tests'):
      self.supports_tests = True
      tests_features = self._GetConfigValue(
          config_parser, u'tests', u'features')

      self.tests_supports_valgrind = u'valgrind' in tests_features

      if u'profiles' in tests_features:
        self.tests_profiles = self._GetConfigValue(
            config_parser, u'tests', u'profiles')
        self.tests_example_filename1 = self._GetOptionalConfigValue(
            config_parser, u'tests', u'example_filename1')
        self.tests_example_filename2 = self._GetOptionalConfigValue(
            config_parser, u'tests', u'example_filename2')

    if config_parser.has_section(u'troubleshooting'):
      self.troubleshooting_example = self._GetOptionalConfigValue(
          config_parser, u'troubleshooting', u'example')

    if config_parser.has_section(u'tools'):
      self.supports_tools = True
      self.tools_directory = self._GetConfigValue(
          config_parser, u'tools', u'directory')
      self.tools_names = self._GetConfigValue(
          config_parser, u'tools', u'names')

    if config_parser.has_section(u'cygwin'):
      self.supports_cygwin = True
      self.cygwin_build_dependencies = self._GetConfigValue(
          config_parser, u'cygwin', u'build_dependencies')
      self.cygwin_dll_dependencies = self._GetConfigValue(
          config_parser, u'cygwin', u'dll_dependencies')
      self.cygwin_dll_filename = self._GetConfigValue(
          config_parser, u'cygwin', u'dll_filename')

    if config_parser.has_section(u'gcc'):
      self.supports_gcc = True
      self.gcc_build_dependencies = self._GetConfigValue(
          config_parser, u'gcc', u'build_dependencies')
      self.gcc_static_build_dependencies = self._GetConfigValue(
          config_parser, u'gcc', u'static_build_dependencies')

    if config_parser.has_section(u'mingw'):
      self.supports_mingw = True
      self.mingw_build_dependencies = self._GetConfigValue(
          config_parser, u'mingw', u'build_dependencies')
      self.mingw_dll_dependencies = self._GetConfigValue(
          config_parser, u'mingw', u'dll_dependencies')
      self.mingw_dll_filename = self._GetConfigValue(
          config_parser, u'mingw', u'dll_filename')

    if config_parser.has_section(u'msvscpp'):
      self.supports_msvscpp = True
      self.msvscpp_build_dependencies = self._GetConfigValue(
          config_parser, u'msvscpp', u'build_dependencies')
      self.msvscpp_dll_dependencies = self._GetConfigValue(
          config_parser, u'msvscpp', u'dll_dependencies')

    if config_parser.has_section(u'dpkg'):
      self.supports_dpkg = True
      self.dpkg_build_dependencies = self._GetConfigValue(
          config_parser, u'dpkg', u'build_dependencies')

    if config_parser.has_section(u'rpm'):
      self.supports_rpm = True
      self.rpm_build_dependencies = self._GetConfigValue(
          config_parser, u'rpm', u'build_dependencies')

    if ((self.supports_dokan or self.supports_fuse) and
        not config_parser.has_section(u'mount_tool')):
      raise ConfigError((
          u'Support for dokan and/or fuse enabled but no corresponding '
          u'section: mount_tool is missing.'))

    if config_parser.has_section(u'mount_tool'):
      self.mount_tool_additional_arguments = self._GetOptionalConfigValue(
          config_parser, u'mount_tool', u'additional_arguments')

      self.mount_tool_missing_backend_error = self._GetConfigValue(
          config_parser, u'mount_tool', u'missing_backend_error')
      self.mount_tool_mount_point = self._GetConfigValue(
          config_parser, u'mount_tool', u'mount_point')
      self.mount_tool_mounted_description = self._GetConfigValue(
          config_parser, u'mount_tool', u'mounted_description')
      self.mount_tool_mounted_dokan = self._GetConfigValue(
          config_parser, u'mount_tool', u'mounted_dokan')
      self.mount_tool_mounted_fuse = self._GetConfigValue(
          config_parser, u'mount_tool', u'mounted_fuse')
      self.mount_tool_source = self._GetConfigValue(
          config_parser, u'mount_tool', u'source')
      self.mount_tool_source_description = self._GetConfigValue(
          config_parser, u'mount_tool', u'source_description')

      # If the long source description is not set it will default to
      # source description.
      self.mount_tool_source_description_long = self._GetOptionalConfigValue(
          config_parser, u'mount_tool', u'source_description_long')

      self.mount_tool_source_type = self._GetConfigValue(
          config_parser, u'mount_tool', u'source_type')

      if self.mount_tool_source_type not in [u'image', u'volume']:
        raise ConfigError(u'unsupported mount tool source type: {0:s}'.format(
            self.mount_tool_source_type))

      self.mount_tool_supported_backends = self._GetConfigValue(
          config_parser, u'mount_tool', u'supported_backends')

    self.msvscpp_zlib_dependency = False
    for dependency in self.msvscpp_build_dependencies:
      if dependency.startswith(u'zlib '):
        self.msvscpp_zlib_dependency = True

  def GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      dict[str, str]: template mappings.
    """
    building_table_of_contents = u''

    project_status = u''

    build_dependencies = u''

    documentation = u''

    development_table_of_contents = u''

    development_main_object_pre_open_python = u''
    development_main_object_post_open_python = u''
    development_main_object_post_open_file_object_python = u''

    tests_profiles = u''

    troubleshooting_example = u''

    cygwin_build_dependencies = u''
    cygwin_dll_dependencies = u''
    cygwin_executables = u''

    gcc_build_dependencies = u''
    gcc_static_build_dependencies = u''
    gcc_mount_tool = u''

    mingw_build_dependencies = u''
    mingw_dll_dependencies = u''
    mingw_executables = u''

    msvscpp_build_dependencies = u''
    msvscpp_build_git = u''
    msvscpp_dll_dependencies = u''
    msvscpp_mount_tool = u''

    dpkg_build_dependencies = u''
    dpkg_filenames = u''

    macosx_pkg_configure_options = u''

    rpm_build_dependencies = u''
    rpm_filenames = u''
    rpm_rename_source_package = u''

    mount_tool_additional_arguments = u''
    mount_tool_source_description_long = u''
    mount_tool_supported_backends = u''

    development_prefix = self.project_name[3:]
    python_bindings_name = u'py{0:s}'.format(self.project_name[3:])
    mount_tool_name = u'{0:s}mount'.format(self.project_name[3:])
    tools_name = u'{0:s}tools'.format(self.project_name[3:])

    if self.project_status:
      project_status += u'-{0:s}'.format(self.project_status)

    if self.project_documentation_url:
      documentation = u'* [Documentation]({0:s})\n'.format(
          self.project_documentation_url)

    if self.library_build_dependencies:
      for dependency in self.library_build_dependencies:
        build_dependencies += u'* {0:s}\n'.format(dependency)

    if self.supports_tests and self.tests_profiles:
      for profile in self.tests_profiles:
        tests_profiles += u'* {0:s}\n'.format(profile)

    if self.troubleshooting_example:
      troubleshooting_example = self.troubleshooting_example

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      building_table_of_contents += (
          u'The {0:s} source code can be build with different compilers:\n'
          u'\n').format(self.project_name)

    if self.supports_gcc:
      building_table_of_contents += (
          u'* [Using GNU Compiler Collection (GCC)]'
          u'(Building#using-gnu-compiler-collection-gcc)\n')

      if self.gcc_build_dependencies:
        gcc_build_dependencies = (
            u'\n'
            u'Also make sure to have the following dependencies including '
            u'source headers installed:\n')

        for dependency in self.gcc_build_dependencies:
          gcc_build_dependencies += u'* {0:s}\n'.format(dependency)

      if self.gcc_static_build_dependencies:
        for dependency in self.gcc_static_build_dependencies:
          gcc_static_build_dependencies += u'* {0:s}\n'.format(dependency)

      if self.supports_fuse:
        gcc_static_build_dependencies += (
            u'* fuse (optional, can be disabled by --with-libfuse=no)\n')

      if self.supports_cygwin:
        building_table_of_contents += '  * [Using Cygwin](Building#cygwin)\n'

        if self.cygwin_build_dependencies:
          for dependency in self.cygwin_build_dependencies:
            cygwin_build_dependencies += u'* {0:s}\n'.format(dependency)

        if self.cygwin_dll_dependencies:
          for dependency in self.cygwin_dll_dependencies:
            cygwin_dll_dependencies += u'* {0:s}\n'.format(dependency)

        if self.supports_tools:
          cygwin_executables += (
              u'And the following executables:\n'
              u'```\n')

          for name in self.tools_names:
            cygwin_executables += (
                u'{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

          cygwin_executables += (
              u'```\n')

      if self.supports_fuse:
        gcc_mount_tool += (
            u'\n'
            u'If you want to be able to use {0:s}, make sure that:\n'
            u'\n'
            u'* on a Linux system you have libfuse-dev (Debian-based) or '
            u'fuse-devel (RedHat-based) installed.\n'
            u'* on a Mac OS X system, you have OSXFuse '
            u'(http://osxfuse.github.com/) installed.\n').format(
                mount_tool_name)

    if self.supports_mingw:
      building_table_of_contents += (
          u'* [Using Minimalist GNU for Windows (MinGW)]'
          u'(Building#using-minimalist-gnu-for-windows-mingw)\n')

      if self.mingw_build_dependencies:
        for dependency in self.mingw_build_dependencies:
          mingw_build_dependencies += u'* {0:s}\n'.format(dependency)

      if self.mingw_dll_dependencies:
        for dependency in self.mingw_dll_dependencies:
          mingw_dll_dependencies += u'* {0:s}\n'.format(dependency)

      if self.supports_tools:
        mingw_executables += (
            u'And the following executables:\n'
            u'```\n')

        for name in self.tools_names:
          mingw_executables += (
              u'{0:s}/.libs/{1:s}.exe\n'.format(self.tools_directory, name))

        mingw_executables += (
            u'```\n'
            u'\n')

    if self.supports_msvscpp:
      building_table_of_contents += (
          u'* [Using Microsoft Visual Studio]'
          u'(Building#using-microsoft-visual-studio)\n')

      if self.msvscpp_build_dependencies:
        msvscpp_build_dependencies = (
            u'\n'
            u'To compile {0:s} using Microsoft Visual Studio you\'ll '
            u'need:\n'
            u'\n').format(self.project_name)

        for dependency in self.msvscpp_build_dependencies:
          msvscpp_build_dependencies += u'* {0:s}\n'.format(dependency)

      if self.msvscpp_dll_dependencies:
        msvscpp_dll_dependencies = u'{0:s}.dll is dependent on:\n'.format(
            self.project_name)

        for dependency in self.msvscpp_dll_dependencies:
          msvscpp_dll_dependencies += u'* {0:s}\n'.format(dependency)

        msvscpp_dll_dependencies += (
            u'\n'
            u'These DLLs can be found in the same directory as '
            u'{0:s}.dll.\n').format(self.project_name)

      msvscpp_build_git = (
          u'\n'
          u'Note that if you want to build {0:s} from source checked out of '
          u'git with Visual Studio make sure the autotools are able to make '
          u'a distribution package of {0:s} before trying to build it.\n'
          u'You can create distribution package by running: '
          u'"make dist".\n').format(self.project_name)

      if self.supports_dokan:
        msvscpp_mount_tool += (
            u'\n'
            u'If you want to be able to use {0:s} you\'ll need Dokan library '
            u'see the corresponding section below.\n'
            u'Otherwise ignore or remove the dokan_dll and {0:s} Visual Studio '
            u'project files.\n').format(mount_tool_name)

    if self.supports_gcc or self.supports_mingw or self.supports_msvscpp:
      building_table_of_contents += u'\n'

    building_table_of_contents += (
        u'Or directly packaged with different package managers:\n\n')

    if self.supports_dpkg:
      building_table_of_contents += (
          u'* [Using Debian package tools (DEB)]'
          u'(Building#using-debian-package-tools-deb)\n')

      if self.dpkg_build_dependencies is None:
        dpkg_build_dependencies = []
      else:
        dpkg_build_dependencies = list(self.dpkg_build_dependencies)

      if self.supports_fuse:
        dpkg_build_dependencies.append(u'libfuse-dev')

      if self.supports_python:
        dpkg_build_dependencies.append(u'python-all-dev')
        dpkg_build_dependencies.append(u'python3-all-dev')

      dpkg_build_dependencies = ' '.join(dpkg_build_dependencies)

      dpkg_filenames += (
          u'{0:s}_<version>-1_<arch>.deb\n'
          u'{0:s}-dev_<version>-1_<arch>.deb').format(
              self.project_name)

      if self.supports_python:
        dpkg_filenames += (
            u'\n{0:s}-python_<version>-1_<arch>.deb').format(
                self.project_name)
        dpkg_filenames += (
            u'\n{0:s}-python3_<version>-1_<arch>.deb').format(
                self.project_name)

      if self.supports_tools:
        dpkg_filenames += (
            u'\n{0:s}-tools_<version>-1_<arch>.deb').format(
                self.project_name)

    if self.supports_rpm:
      building_table_of_contents += (
          u'* [Using RedHat package tools (RPM)]'
          u'(Building#using-redhat-package-tools-rpm)\n')

      if self.rpm_build_dependencies is None:
        rpm_build_dependencies = []
      else:
        rpm_build_dependencies = list(self.rpm_build_dependencies)

      if self.supports_fuse:
        rpm_build_dependencies.append(u'fuse-devel')

      if self.supports_python:
        rpm_build_dependencies.append(u'python-devel')
        rpm_build_dependencies.append(u'python3-devel')

      rpm_build_dependencies = ' '.join(rpm_build_dependencies)

      if self.project_status:
        rpm_rename_source_package += (
            u'mv {0:s}-{1:s}-<version>.tar.gz {0:s}-<version>.tar.gz\n'.format(
                self.project_name, self.project_status))

      rpm_filenames += (
          u'~/rpmbuild/RPMS/<arch>/{0:s}-<version>-1.<arch>.rpm\n'
          u'~/rpmbuild/RPMS/<arch>/{0:s}-devel-<version>-1.<arch>'
          u'.rpm\n').format(self.project_name)

      if self.supports_python:
        rpm_filenames += (
            u'~/rpmbuild/RPMS/<arch>/{0:s}-python-<version>-1.<arch>'
            u'.rpm\n').format(self.project_name)
        rpm_filenames += (
            u'~/rpmbuild/RPMS/<arch>/{0:s}-python3-<version>-1.<arch>'
            u'.rpm\n').format(self.project_name)

      if self.supports_tools:
        rpm_filenames += (
            u'~/rpmbuild/RPMS/<arch>/{0:s}-tools-<version>-1.<arch>'
            u'.rpm\n').format(self.project_name)

      rpm_filenames += (
          u'~/rpmbuild/SRPMS/{0:s}-<version>-1.src.rpm').format(
              self.project_name)

    building_table_of_contents += (
        u'* [Using Mac OS X pkgbuild](Building#using-mac-os-x-pkgbuild)\n')

    if self.supports_python:
      macosx_pkg_configure_options = ' --enable-python --with-pyprefix'

    if self.supports_python:
      building_table_of_contents += (
          u'* [Using setup.py](Building#using-setuppy)\n')

    development_table_of_contents += (
      u'* [C/C++ development](C-development)\n')

    if self.supports_python:
        development_table_of_contents += (
          u'* [Python development](Python-development)\n')

    if self.development_main_object_pre_open_python:
      development_main_object_pre_open_python = u'{0:s}\n'.format(
          self.development_main_object_pre_open_python)

    if self.development_main_object_post_open_python:
      development_main_object_post_open_python = u'{0:s}\n'.format(
          u'\n'.join(self.development_main_object_post_open_python))

    if self.development_main_object_post_open_file_object_python:
      development_main_object_post_open_file_object_python = u'{0:s}\n'.format(
          u'\n'.join(self.development_main_object_post_open_file_object_python))
    elif self.development_main_object_post_open_python:
      development_main_object_post_open_file_object_python = u'{0:s}\n'.format(
          u'\n'.join(self.development_main_object_post_open_python))

    if self.mount_tool_additional_arguments:
      mount_tool_additional_arguments = self.mount_tool_additional_arguments

    if self.mount_tool_source_description_long:
      mount_tool_source_description_long = (
          self.mount_tool_source_description_long)
    else:
      mount_tool_source_description_long = self.mount_tool_source_description

    if self.mount_tool_supported_backends:
      for backend in self.mount_tool_supported_backends:
        mount_tool_supported_backends += u'* {0:s}\n'.format(backend)

    template_mappings = {
        u'building_table_of_contents': building_table_of_contents,

        u'project_name': self.project_name,
        u'project_name_upper_case': self.project_name.upper(),
        u'project_status': project_status,
        u'project_description': self.project_description,
        u'project_git_url': self.project_git_url,
        u'project_download_url': self.project_download_url,

        u'build_dependencies': build_dependencies,

        u'python_bindings_name': python_bindings_name,
        u'mount_tool_name': mount_tool_name,
        u'tools_name': tools_name,

        u'documentation': documentation,

        u'development_table_of_contents': development_table_of_contents,

        u'development_prefix': development_prefix,
        u'development_main_object': self.development_main_object,
        u'development_main_object_filename': (
            self.development_main_object_filename),
        u'development_main_object_pre_open_python': (
            development_main_object_pre_open_python),
        u'development_main_object_post_open_python': (
            development_main_object_post_open_python),
        u'development_main_object_post_open_file_object_python': (
            development_main_object_post_open_file_object_python),
        u'development_main_object_size': self.development_main_object_size,

        u'tests_profiles': tests_profiles,
        u'tests_example_filename1': self.tests_example_filename1,
        u'tests_example_filename2': self.tests_example_filename2,

        u'troubleshooting_example': troubleshooting_example,

        u'cygwin_build_dependencies': cygwin_build_dependencies,
        u'cygwin_dll_dependencies': cygwin_dll_dependencies,
        u'cygwin_dll_filename': self.cygwin_dll_filename,
        u'cygwin_executables': cygwin_executables,

        u'gcc_build_dependencies': gcc_build_dependencies,
        u'gcc_static_build_dependencies': gcc_static_build_dependencies,
        u'gcc_mount_tool': gcc_mount_tool,

        u'mingw_build_dependencies': mingw_build_dependencies,
        u'mingw_dll_dependencies': mingw_dll_dependencies,
        u'mingw_dll_filename': self.mingw_dll_filename,
        u'mingw_executables': mingw_executables,

        u'msvscpp_build_dependencies': msvscpp_build_dependencies,
        u'msvscpp_build_git': msvscpp_build_git,
        u'msvscpp_dll_dependencies': msvscpp_dll_dependencies,
        u'msvscpp_mount_tool': msvscpp_mount_tool,

        u'dpkg_build_dependencies': dpkg_build_dependencies,
        u'dpkg_filenames': dpkg_filenames,

        u'macosx_pkg_configure_options': macosx_pkg_configure_options,

        u'rpm_build_dependencies': rpm_build_dependencies,
        u'rpm_filenames': rpm_filenames,
        u'rpm_rename_source_package': rpm_rename_source_package,

        u'mount_tool_additional_arguments': mount_tool_additional_arguments,
        u'mount_tool_missing_backend_error': (
            self.mount_tool_missing_backend_error),
        u'mount_tool_mount_point': self.mount_tool_mount_point,
        u'mount_tool_mounted_description': self.mount_tool_mounted_description,
        u'mount_tool_mounted_dokan': self.mount_tool_mounted_dokan,
        u'mount_tool_mounted_fuse': self.mount_tool_mounted_fuse,
        u'mount_tool_source': self.mount_tool_source,
        u'mount_tool_source_description': self.mount_tool_source_description,
        u'mount_tool_source_description_long': (
            mount_tool_source_description_long),
        u'mount_tool_supported_backends': mount_tool_supported_backends,
    }
    return template_mappings


class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  def __init__(self, template_directory):
    """Initializes a wiki page generator.

    Args:
      template_directory (str): path of the template directory.
    """
    super(WikiPageGenerator, self).__init__()
    self._template_directory = template_directory

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer):
    """Generates a section from template filename.

    Args:
      template_filename (str): path of the template file.
      template_mpppings (dict[str, str]): the template mappings, where
          the key maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_string = self._ReadTemplateFile(template_filename)
    output_data = template_string.substitute(template_mappings)
    output_writer.Write(output_data)

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename (str): path of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    path = os.path.join(self._template_directory, filename)
    file_object = open(path, 'rb')
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """

  @abc.abstractmethod
  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """


class BuildingPageGenerator(WikiPageGenerator):
  """Class that generates the "Building from source" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(u'introduction.txt', template_mappings, output_writer)

    self._GenerateSection(u'source.txt', template_mappings, output_writer)
    self._GenerateSection(
        u'source_distribution_package.txt', template_mappings, output_writer)
    self._GenerateSection(u'source_git.txt', template_mappings, output_writer)

    if project_configuration.supports_gcc:
      self._GenerateSection(u'gcc.txt', template_mappings, output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            u'gcc_debug_output.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'gcc_static_library.txt', template_mappings, output_writer)

      if project_configuration.supports_tools:
        self._GenerateSection(
            u'gcc_static_executables.txt', template_mappings, output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            u'gcc_python.txt', template_mappings, output_writer)

      self._GenerateSection(u'cygwin.txt', template_mappings, output_writer)
      self._GenerateSection(u'gcc_macosx.txt', template_mappings, output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            u'gcc_macosx_python.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'gcc_solaris.txt', template_mappings, output_writer)

    if project_configuration.supports_mingw:
      self._GenerateSection(u'mingw.txt', template_mappings, output_writer)
      self._GenerateSection(u'mingw_msys.txt', template_mappings, output_writer)
      self._GenerateSection(u'mingw_dll.txt', template_mappings, output_writer)
      self._GenerateSection(
          u'mingw_troubleshooting.txt', template_mappings, output_writer)

    if project_configuration.supports_msvscpp:
      self._GenerateSection(u'msvscpp.txt', template_mappings, output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            u'msvscpp_debug.txt', template_mappings, output_writer)

      if project_configuration.msvscpp_zlib_dependency:
        self._GenerateSection(
            u'msvscpp_zlib.txt', template_mappings, output_writer)

      if project_configuration.supports_dokan:
        self._GenerateSection(
            u'msvscpp_dokan.txt', template_mappings, output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            u'msvscpp_python.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'msvscpp_build.txt', template_mappings, output_writer)
      self._GenerateSection(
          u'msvscpp_dll.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'msvscpp_2010.txt', template_mappings, output_writer)

    if project_configuration.supports_dpkg:
      self._GenerateSection(u'dpkg.txt', template_mappings, output_writer)

    if project_configuration.supports_rpm:
      self._GenerateSection(u'rpm.txt', template_mappings, output_writer)

    self._GenerateSection(u'macosx_pkg.txt', template_mappings, output_writer)

    if project_configuration.supports_python:
      self._GenerateSection(u'setup_py.txt', template_mappings, output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return True


class DevelopmentPageGenerator(WikiPageGenerator):
  """Class that generates the "Development" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(u'main.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return project_configuration.supports_python


class CDevelopmentPageGenerator(WikiPageGenerator):
  """Class that generates the "C/C++ development" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for also_see.txt, main_object.txt

    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(u'main.txt', template_mappings, output_writer)

    if project_configuration.development_main_object:
      if project_configuration.development_glob:
        self._GenerateSection(
            u'main_object_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection(
            u'main_object.txt', template_mappings, output_writer)

    self._GenerateSection(u'also_see.txt', template_mappings, output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return True


class PythonDevelopmentPageGenerator(WikiPageGenerator):
  """Class that generates the "Python development" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(u'main.txt', template_mappings, output_writer)

    if project_configuration.development_main_object:
      if project_configuration.development_glob:
        self._GenerateSection(
            u'main_object_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection(
            u'main_object.txt', template_mappings, output_writer)

    if project_configuration.development_pytsk3:
      if project_configuration.development_glob:
        self._GenerateSection(
            u'pytsk3_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection(u'pytsk3.txt', template_mappings, output_writer)

    # TODO: move main object out of this template and create on demand.
    self._GenerateSection(u'also_see.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return project_configuration.supports_python


class HomePageGenerator(WikiPageGenerator):
  """Class that generates the "Home" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(u'introduction.txt', template_mappings, output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return True


class MountingPageGenerator(WikiPageGenerator):
  """Class that generates the "Mounting a ..." wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    if (project_configuration.supports_dokan or
        project_configuration.supports_fuse):
      self._GenerateSection(
          u'introduction.txt', template_mappings, output_writer)

      if project_configuration.mount_tool_source_type == u'image':
        self._GenerateSection(
            u'mounting_image.txt', template_mappings, output_writer)

      elif project_configuration.mount_tool_source_type == u'volume':
        self._GenerateSection(
            u'mounting_volume.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'mounting_missing_backend.txt', template_mappings, output_writer)

      if project_configuration.mount_tool_source_type == u'volume':
        self._GenerateSection(
            u'mounting_volume_loopback.txt', template_mappings,
            output_writer)
        self._GenerateSection(
            u'obtaining_volume_offset.txt', template_mappings,
            output_writer)

      self._GenerateSection(
          u'mounting_root_access.txt', template_mappings, output_writer)

      if project_configuration.supports_dokan:
        if project_configuration.mount_tool_source_type == u'image':
          self._GenerateSection(
              u'mounting_image_windows.txt', template_mappings,
              output_writer)

        elif project_configuration.mount_tool_source_type == u'volume':
          self._GenerateSection(
              u'mounting_volume_windows.txt', template_mappings,
              output_writer)

      self._GenerateSection(
          u'unmounting.txt', template_mappings, output_writer)

      if project_configuration.supports_dokan:
        self._GenerateSection(
            u'unmounting_windows.txt', template_mappings, output_writer)

      self._GenerateSection(
          u'troubleshooting.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    if (project_configuration.supports_dokan or
        project_configuration.supports_fuse):
      return True

    return False


class TestingPageGenerator(WikiPageGenerator):
  """Class that generates the "Testing" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: implement testing page without input files.
    template_mappings = project_configuration.GetTemplateMappings()
    if project_configuration.supports_tests:
      self._GenerateSection(u'tests.txt', template_mappings, output_writer)

      if project_configuration.tests_profiles:
        if (project_configuration.tests_example_filename1 and
            project_configuration.tests_example_filename2):
          self._GenerateSection(
              u'tests_files.txt', template_mappings, output_writer)

        self._GenerateSection(
            u'tests_profiles.txt', template_mappings, output_writer)

        if (project_configuration.tests_example_filename1 and
            project_configuration.tests_example_filename2):
          self._GenerateSection(
              u'tests_profiles_files.txt', template_mappings, output_writer)

      if project_configuration.tests_supports_valgrind:
        self._GenerateSection(
            u'tests_valgrind.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    if project_configuration.supports_tests:
      return True

    return False


class TroubleshootingPageGenerator(WikiPageGenerator):
  """Class that generates the "Troubleshooting" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings()
    self._GenerateSection(
        u'introduction.txt', template_mappings, output_writer)
    self._GenerateSection(
        u'build_errors.txt', template_mappings, output_writer)
    self._GenerateSection(
        u'runtime_errors.txt', template_mappings, output_writer)

    if project_configuration.supports_debug_output:
      self._GenerateSection(
          u'format_errors.txt', template_mappings, output_writer)

    if project_configuration.supports_tools:
      self._GenerateSection(
          u'crashes.txt', template_mappings, output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return True


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initializes an output writer.

    Args:
      name (str): name of the output.
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
    """Initializes an output writer."""
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
    print(data, end=u'')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates wiki pages of the libyal libraries.'))

  argument_parser.add_argument(
      u'configuration_file', action=u'store', metavar=u'CONFIGURATION_FILE',
      default=u'project-wiki.ini', help=(
          u'The wiki generation configuration file.'))

  argument_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print(u'Configuration file missing.')
    print(u'')
    argument_parser.print_help()
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

  project_configuration = ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  readme_file = os.path.join(
      os.path.dirname(options.configuration_file), u'README')

  LINK_RE = re.compile(r'\* (.*): (http[s]://.*)')

  project_description = []
  if os.path.exists(readme_file):
    with open(readme_file, 'rb') as file_object:
      for line in file_object.readlines():
        if line.startswith(u'For more information see:'):
          project_description.pop()
          break

        line = LINK_RE.sub(r'* [\1](\2)', line)
        project_description.append(line)

        if line.endswith(':\n'):
          # Add an empty line to make sure unnumbered list are formatted
          # correctly by most markdown parsers.
          project_description.append(u'\n')

  project_configuration.project_description = u''.join(project_description)

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  # TODO: generate more wiki pages.
  wiki_pages = [
      (u'Building', BuildingPageGenerator),
      (u'Development', DevelopmentPageGenerator),
      (u'Home', HomePageGenerator),
      (u'Mounting', MountingPageGenerator),
      (u'C development', CDevelopmentPageGenerator),
      (u'Python development', PythonDevelopmentPageGenerator),
      (u'Testing', TestingPageGenerator),
      (u'Troubleshooting', TroubleshootingPageGenerator),
  ]

  for page_name, page_generator_class in wiki_pages:
    template_directory = os.path.join(
        libyal_directory, u'data', u'wiki', page_name)
    wiki_page = page_generator_class(template_directory)

    if not wiki_page.HasContent(project_configuration):
      continue

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

    wiki_page.Generate(project_configuration, output_writer)

    output_writer.Close()

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
