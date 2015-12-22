#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of wiki pages of libyal libraries."""

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
  """Class that contains the project configuration."""

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

    self.documentation_url = None

    self.source_package_url = None

    self.git_url = None
    self.git_build_dependencies = None

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

    self.project_name = self._GetConfigValue(config_parser, u'Project', u'name')
    self.project_status = self._GetConfigValue(
        config_parser, u'Project', u'status')

    try:
      self.documentation_url = self._GetConfigValue(
          config_parser, u'documentation', u'url')
    except configparser.NoOptionError:
      pass

    self.source_package_url = self._GetConfigValue(
        config_parser, u'source_package', u'url')

    self.git_url = self._GetConfigValue(config_parser, u'git', u'url')
    self.git_build_dependencies = self._GetConfigValue(
        config_parser, u'git', u'build_dependencies')

    features = self._GetConfigValue(config_parser, u'Project', u'features')

    self.supports_debug_output = u'debug_output' in features
    self.supports_tests = u'tests' in features
    self.supports_tools = u'tools' in features
    self.supports_python = u'python' in features

    self.supports_source_package = u'source_package' in features
    self.supports_git = u'git' in features

    self.supports_cygwin = u'cygwin' in features
    self.supports_gcc = u'gcc' in features
    self.supports_msvscpp = u'msvscpp' in features
    self.supports_mingw = u'mingw' in features

    self.supports_dpkg = u'dpkg' in features
    self.supports_rpm = u'rpm' in features

    self.supports_dokan = u'dokan' in features
    self.supports_fuse = u'fuse' in features

    if config_parser.has_section(u'development'):
      try:
        features = self._GetConfigValue(
            config_parser, u'development', u'features')

        self.development_glob = u'glob' in features
        self.development_pytsk3 = u'pytsk3' in features
      except configparser.NoOptionError:
        pass

      self.development_main_object = self._GetConfigValue(
          config_parser, u'development', u'main_object')

      self.development_main_object_filename = self._GetConfigValue(
          config_parser, u'development', u'main_object_filename')

      try:
        self.development_main_object_size = self._GetConfigValue(
            config_parser, u'development', u'main_object_size')
      except configparser.NoOptionError:
        pass

      try:
        self.development_main_object_pre_open_python = self._GetConfigValue(
            config_parser, u'development', u'main_object_pre_open_python')
      except configparser.NoOptionError:
        pass

      try:
        self.development_main_object_post_open_python = self._GetConfigValue(
            config_parser, u'development', u'main_object_post_open_python')
      except configparser.NoOptionError:
        pass

      try:
        self.development_main_object_post_open_file_object_python = (
            self._GetConfigValue(
                config_parser, u'development',
                u'main_object_post_open_file_object_python'))
      except configparser.NoOptionError:
        pass

    if self.supports_tests and not config_parser.has_section(u'tests'):
      raise ConfigError((
          u'Support for tests enabled but no corresponding section: '
          u'tests is missing.'))

    if config_parser.has_section(u'tests'):
      tests_features = self._GetConfigValue(
          config_parser, u'tests', u'features')

      self.tests_supports_valgrind = u'valgrind' in tests_features

      if u'profiles' in tests_features:
        self.tests_profiles = self._GetConfigValue(
            config_parser, u'tests', u'profiles')
        self.tests_example_filename1 = self._GetConfigValue(
            config_parser, u'tests', u'example_filename1')
        self.tests_example_filename2 = self._GetConfigValue(
            config_parser, u'tests', u'example_filename2')

    if config_parser.has_section(u'troubleshooting'):
      try:
        self.troubleshooting_example = self._GetConfigValue(
            config_parser, u'troubleshooting', u'example')
      except configparser.NoOptionError:
        pass

    if self.supports_tools and not config_parser.has_section(u'tools'):
      raise ConfigError((
          u'Support for tools enabled but no corresponding section: '
          u'tools is missing.'))

    if config_parser.has_section(u'tools'):
      self.tools_directory = self._GetConfigValue(
          config_parser, u'tools', u'directory')
      self.tools_names = self._GetConfigValue(
          config_parser, u'tools', u'names')

    if self.supports_cygwin and not config_parser.has_section(u'cygwin'):
      raise ConfigError((
          u'Support for Cygwin enabled but no corresponding section: '
          u'cygwin is missing.'))

    if config_parser.has_section(u'cygwin'):
      self.cygwin_build_dependencies = self._GetConfigValue(
          config_parser, u'cygwin', u'build_dependencies')
      self.cygwin_dll_dependencies = self._GetConfigValue(
          config_parser, u'cygwin', u'dll_dependencies')
      self.cygwin_dll_filename = self._GetConfigValue(
          config_parser, u'cygwin', u'dll_filename')

    if self.supports_gcc and not config_parser.has_section(u'gcc'):
      raise ConfigError((
          u'Support for GCC enabled but no corresponding section: '
          u'gcc is missing.'))

    if config_parser.has_section(u'gcc'):
      self.gcc_build_dependencies = self._GetConfigValue(
          config_parser, u'gcc', u'build_dependencies')
      self.gcc_static_build_dependencies = self._GetConfigValue(
          config_parser, u'gcc', u'static_build_dependencies')

    if self.supports_mingw and not config_parser.has_section(u'mingw'):
      raise ConfigError((
          u'Support for MinGW enabled but no corresponding section: '
          u'mingw is missing.'))

    if config_parser.has_section(u'mingw'):
      self.mingw_build_dependencies = self._GetConfigValue(
          config_parser, u'mingw', u'build_dependencies')
      self.mingw_dll_dependencies = self._GetConfigValue(
          config_parser, u'mingw', u'dll_dependencies')
      self.mingw_dll_filename = self._GetConfigValue(
          config_parser, u'mingw', u'dll_filename')

    if self.supports_msvscpp and not config_parser.has_section(u'msvscpp'):
      raise ConfigError((
          u'Support for Visual Studio enabled but no corresponding section: '
          u'msvscpp is missing.'))

    if config_parser.has_section(u'msvscpp'):
      self.msvscpp_build_dependencies = self._GetConfigValue(
          config_parser, u'msvscpp', u'build_dependencies')
      self.msvscpp_dll_dependencies = self._GetConfigValue(
          config_parser, u'msvscpp', u'dll_dependencies')

    if self.supports_dpkg and not config_parser.has_section(u'dpkg'):
      raise ConfigError((
          u'Support for dpkg enabled but no corresponding section: '
          u'dpkg is missing.'))

    if config_parser.has_section(u'dpkg'):
      self.dpkg_build_dependencies = self._GetConfigValue(
          config_parser, u'dpkg', u'build_dependencies')

    if self.supports_rpm and not config_parser.has_section(u'rpm'):
      raise ConfigError((
          u'Support for rpm enabled but no corresponding section: '
          u'rpm is missing.'))

    if config_parser.has_section(u'rpm'):
      self.rpm_build_dependencies = self._GetConfigValue(
          config_parser, u'rpm', u'build_dependencies')

    if ((self.supports_dokan or self.supports_fuse) and
        not config_parser.has_section(u'mount_tool')):
      raise ConfigError((
          u'Support for dokan and/or fuse enabled but no corresponding '
          u'section: mount_tool is missing.'))

    if config_parser.has_section(u'mount_tool'):
      try:
        self.mount_tool_additional_arguments = self._GetConfigValue(
            config_parser, u'mount_tool', u'additional_arguments')
      except configparser.NoOptionError:
        pass

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
      try:
        self.mount_tool_source_description_long = self._GetConfigValue(
            config_parser, u'mount_tool', u'source_description_long')
      except configparser.NoOptionError:
        pass

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
      A dictionary containing the string template mappings.
    """
    building_table_of_contents = u''

    project_status = u''

    documentation = u''

    git_build_dependencies = u''

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

    if self.documentation_url:
      documentation = u'* [Documentation]({0:s})\n'.format(
          self.documentation_url)

    if self.supports_git:
      if self.git_build_dependencies:
        for dependency in self.git_build_dependencies:
          git_build_dependencies += u'* {0:s}\n'.format(dependency)

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
      building_table_of_contents += u'* Using GNU Compiler Collection (GCC)\n'

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
        building_table_of_contents += '  * Using Cygwin\n'

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
          u'* Using Minimalist GNU for Windows (MinGW)\n')

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
      building_table_of_contents += u'* Using Microsoft Visual Studio\n'

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

      if self.supports_git:
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
      building_table_of_contents += u'* Using Debian package tools (DEB)\n'

      if self.dpkg_build_dependencies is None:
        dpkg_build_dependencies = []
      else:
        dpkg_build_dependencies = list(self.dpkg_build_dependencies)

      if self.supports_fuse:
        dpkg_build_dependencies.append(u'libfuse-dev')

      if self.supports_python:
        dpkg_build_dependencies.append(u'python-dev')

      if dpkg_build_dependencies:
        dpkg_build_dependencies = ' '.join(dpkg_build_dependencies)

      dpkg_filenames += (
          u'{0:s}_<version>-1_<arch>.deb\n'
          u'{0:s}-dev_<version>-1_<arch>.deb').format(
              self.project_name)

      if self.supports_python:
        dpkg_filenames += (
            u'\n{0:s}-python_<version>-1_<arch>.deb').format(
                self.project_name)

      if self.supports_tools:
        dpkg_filenames += (
            u'\n{0:s}-tools_<version>-1_<arch>.deb').format(
                self.project_name)

    if self.supports_rpm:
      building_table_of_contents += u'* Using RedHat package tools (RPM)\n'

      if self.rpm_build_dependencies is None:
        rpm_build_dependencies = []
      else:
        rpm_build_dependencies = list(self.rpm_build_dependencies)

      if self.supports_fuse:
        rpm_build_dependencies.append(u'fuse-devel')

      if self.supports_python:
        rpm_build_dependencies.append(u'python-devel')

      if rpm_build_dependencies:
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

      if self.supports_tools:
        rpm_filenames += (
            u'~/rpmbuild/RPMS/<arch>/{0:s}-tools-<version>-1.<arch>'
            u'.rpm\n').format(self.project_name)

      rpm_filenames += (
          u'~/rpmbuild/SRPMS/{0:s}-<version>-1.src.rpm').format(
              self.project_name)

    building_table_of_contents += u'* Using Mac OS X pkgbuild\n'

    if self.supports_python:
      macosx_pkg_configure_options = ' --enable-python --with-pyprefix'

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

        u'python_bindings_name': python_bindings_name,
        u'mount_tool_name': mount_tool_name,
        u'tools_name': tools_name,

        u'documentation': documentation,

        u'source_package_url': self.source_package_url,

        u'git_url': self.git_url,
        u'git_build_dependencies': git_build_dependencies,

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
    """Initialize a wiki page generator.

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

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

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


class BuildingPageGenerator(WikiPageGenerator):
  """Class that generates the "Building from source" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, u'introduction.txt', output_writer)

    if (project_configuration.supports_source_package or
        project_configuration.supports_git):
      self._GenerateSection(project_configuration, u'source.txt', output_writer)

      if project_configuration.supports_source_package:
        self._GenerateSection(
            project_configuration, u'source_package.txt', output_writer)

      if project_configuration.supports_git:
        self._GenerateSection(
            project_configuration, u'source_git.txt', output_writer)

    if project_configuration.supports_gcc:
      self._GenerateSection(project_configuration, u'gcc.txt', output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            project_configuration, u'gcc_debug_output.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'gcc_static_library.txt', output_writer)

      if project_configuration.supports_tools:
        self._GenerateSection(
            project_configuration, u'gcc_static_executables.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, u'gcc_python.txt', output_writer)

      self._GenerateSection(project_configuration, u'cygwin.txt', output_writer)
      self._GenerateSection(
          project_configuration, u'gcc_macosx.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, u'gcc_macosx_python.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'gcc_solaris.txt', output_writer)

    if project_configuration.supports_mingw:
      self._GenerateSection(project_configuration, u'mingw.txt', output_writer)
      self._GenerateSection(
          project_configuration, u'mingw_msys.txt', output_writer)
      self._GenerateSection(
          project_configuration, u'mingw_dll.txt', output_writer)
      self._GenerateSection(
          project_configuration, u'mingw_troubleshooting.txt', output_writer)

    if project_configuration.supports_msvscpp:
      self._GenerateSection(
          project_configuration, u'msvscpp.txt', output_writer)

      if project_configuration.supports_debug_output:
        self._GenerateSection(
            project_configuration, u'msvscpp_debug.txt', output_writer)

      if project_configuration.msvscpp_zlib_dependency:
        self._GenerateSection(
            project_configuration, u'msvscpp_zlib.txt', output_writer)

      if project_configuration.supports_dokan:
        self._GenerateSection(
            project_configuration, u'msvscpp_dokan.txt', output_writer)

      if project_configuration.supports_python:
        self._GenerateSection(
            project_configuration, u'msvscpp_python.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'msvscpp_build.txt', output_writer)
      self._GenerateSection(
          project_configuration, u'msvscpp_dll.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'msvscpp_2010.txt', output_writer)

    if project_configuration.supports_dpkg:
      self._GenerateSection(project_configuration, u'dpkg.txt', output_writer)

    if project_configuration.supports_rpm:
      self._GenerateSection(project_configuration, u'rpm.txt', output_writer)

    self._GenerateSection(
        project_configuration, u'macosx_pkg.txt', output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    return True


class DevelopmentPageGenerator(WikiPageGenerator):
  """Class that generates the "Development" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    # TODO: add support for c_cpp_also_see.txt, c_cpp_main_object.txt, c_cpp.txt

    if project_configuration.supports_python:
      self._GenerateSection(
          project_configuration, u'python.txt', output_writer)

      if project_configuration.development_main_object:
        if project_configuration.development_glob:
          self._GenerateSection(
              project_configuration, u'python_main_object_with_glob.txt',
              output_writer)

        else:
          self._GenerateSection(
              project_configuration, u'python_main_object.txt', output_writer)

      if project_configuration.development_pytsk3:
        if project_configuration.development_glob:
          self._GenerateSection(
              project_configuration, u'python_pytsk3_with_glob.txt',
              output_writer)

        else:
          self._GenerateSection(
              project_configuration, u'python_pytsk3.txt', output_writer)

      # TODO: move main object out of this template and create on demand.
      self._GenerateSection(
          project_configuration, u'python_also_see.txt', output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    if project_configuration.supports_python:
      return True

    return False


class HomePageGenerator(WikiPageGenerator):
  """Class that generates the "Home" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, u'introduction.txt', output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    return True


class MountingPageGenerator(WikiPageGenerator):
  """Class that generates the "Mounting a ..." wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    if (project_configuration.supports_dokan or
        project_configuration.supports_fuse):
      self._GenerateSection(
          project_configuration, u'introduction.txt', output_writer)

      if project_configuration.mount_tool_source_type == u'image':
        self._GenerateSection(
            project_configuration, u'mounting_image.txt', output_writer)

      elif project_configuration.mount_tool_source_type == u'volume':
        self._GenerateSection(
            project_configuration, u'mounting_volume.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'mounting_missing_backend.txt', output_writer)

      if project_configuration.mount_tool_source_type == u'volume':
        self._GenerateSection(
            project_configuration, u'mounting_volume_loopback.txt',
            output_writer)
        self._GenerateSection(
            project_configuration, u'obtaining_volume_offset.txt',
            output_writer)

      self._GenerateSection(
          project_configuration, u'mounting_root_access.txt', output_writer)

      if project_configuration.supports_dokan:
        if project_configuration.mount_tool_source_type == u'image':
          self._GenerateSection(
              project_configuration, u'mounting_image_windows.txt',
              output_writer)

        elif project_configuration.mount_tool_source_type == u'volume':
          self._GenerateSection(
              project_configuration, u'mounting_volume_windows.txt',
              output_writer)

      self._GenerateSection(
          project_configuration, u'unmounting.txt', output_writer)

      if project_configuration.supports_dokan:
        self._GenerateSection(
            project_configuration, u'unmounting_windows.txt', output_writer)

      self._GenerateSection(
          project_configuration, u'troubleshooting.txt', output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
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
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    if project_configuration.supports_tests:
      self._GenerateSection(
          project_configuration, u'tests.txt', output_writer)

      if project_configuration.tests_profiles:
        self._GenerateSection(
            project_configuration, u'tests_files.txt', output_writer)
        self._GenerateSection(
            project_configuration, u'tests_profiles.txt', output_writer)

      if project_configuration.tests_supports_valgrind:
        self._GenerateSection(
            project_configuration, u'tests_valgrind.txt', output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    if project_configuration.supports_tests:
      return True

    return False


class TroubleshootingPageGenerator(WikiPageGenerator):
  """Class that generates the "Troubleshooting" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    self._GenerateSection(
        project_configuration, u'introduction.txt', output_writer)
    self._GenerateSection(
        project_configuration, u'build_errors.txt', output_writer)
    self._GenerateSection(
        project_configuration, u'runtime_errors.txt', output_writer)

    if project_configuration.supports_debug_output:
      self._GenerateSection(
          project_configuration, u'format_errors.txt', output_writer)

    if project_configuration.supports_tools:
      self._GenerateSection(
          project_configuration, u'crashes.txt', output_writer)

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
      u'Generates wiki pages of the libyal libraries.'))

  args_parser.add_argument(
      u'config_file', action=u'store', metavar=u'CONFIG_FILE',
      default=u'wiki.conf', help=u'The wiki generation config file.')

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

  readme_file = os.path.join(
      os.path.dirname(options.config_file), u'README')

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

  script_directory = os.path.dirname(os.path.abspath(__file__))

  # TODO: generate more wiki pages.
  wiki_pages = [
      (u'Building', BuildingPageGenerator),
      (u'Development', DevelopmentPageGenerator),
      (u'Home', HomePageGenerator),
      (u'Mounting', MountingPageGenerator),
      (u'Testing', TestingPageGenerator),
      (u'Troubleshooting', TroubleshootingPageGenerator),
  ]

  for page_name, page_generator_class in wiki_pages:
    template_directory = os.path.join(script_directory, u'wiki', page_name)
    wiki_page = page_generator_class(template_directory)

    if not wiki_page.HasContent(project_configuration):
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

    wiki_page.Generate(project_configuration, output_writer)

    output_writer.Close()

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
