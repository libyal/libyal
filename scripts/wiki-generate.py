#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of wiki pages of the libyal libraries."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import string
import os
import re
import sys

import configuration


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

  def _GetTemplateMappings(self, project_configuration):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    building_table_of_contents = ''

    project_status = ''

    build_dependencies = ''

    documentation = ''

    development_table_of_contents = ''

    development_main_object_pre_open_python = ''
    development_main_object_post_open_python = ''
    development_main_object_post_open_file_object_python = ''

    tests_profiles = ''

    troubleshooting_example = ''

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

    mount_tool_additional_arguments = ''
    mount_tool_source_description_long = ''
    mount_tool_supported_backends = ''

    development_prefix = project_configuration.project_name[3:]
    python_bindings_name = 'py{0:s}'.format(
        project_configuration.project_name[3:])
    mount_tool_name = '{0:s}mount'.format(
        project_configuration.project_name[3:])
    tools_name = '{0:s}tools'.format(project_configuration.project_name[3:])

    if project_configuration.project_status:
      project_status += '-{0:s}'.format(project_configuration.project_status)

    if project_configuration.project_documentation_url:
      documentation = '* [Documentation]({0:s})\n'.format(
          project_configuration.project_documentation_url)

    if project_configuration.library_build_dependencies:
      for dependency in project_configuration.library_build_dependencies:
        build_dependencies += '* {0:s}\n'.format(dependency)

    if (project_configuration.HasTests() and
        project_configuration.tests_profiles):
      for profile in project_configuration.tests_profiles:
        tests_profiles += '* {0:s}\n'.format(profile)

    if project_configuration.troubleshooting_example:
      troubleshooting_example = project_configuration.troubleshooting_example

    building_table_of_contents += (
        'The {0:s} source code can be build with different compilers:\n'
        '\n').format(project_configuration.project_name)

    # GCC support.
    building_table_of_contents += (
        '* [Using GNU Compiler Collection (GCC)]'
        '(Building#using-gnu-compiler-collection-gcc)\n')

    if project_configuration.gcc_build_dependencies:
      gcc_build_dependencies = (
          '\n'
          'Also make sure to have the following dependencies including '
          'source headers installed:\n')

      for dependency in project_configuration.gcc_build_dependencies:
        gcc_build_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.gcc_static_build_dependencies:
      for dependency in project_configuration.gcc_static_build_dependencies:
        gcc_static_build_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.HasDependencyFuse():
      gcc_static_build_dependencies += (
          '* fuse (optional, can be disabled by --with-libfuse=no)\n')

    # Cygwin support.
    building_table_of_contents += '  * [Using Cygwin](Building#cygwin)\n'

    if project_configuration.cygwin_build_dependencies:
      for dependency in project_configuration.cygwin_build_dependencies:
        cygwin_build_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.cygwin_dll_dependencies:
      for dependency in project_configuration.cygwin_dll_dependencies:
        cygwin_dll_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.HasTools():
      cygwin_executables += (
          'And the following executables:\n'
          '```\n')

      for name in project_configuration.tools_names:
        cygwin_executables += (
            '{0:s}/.libs/{1:s}.exe\n'.format(
                project_configuration.tools_directory, name))

      cygwin_executables += (
          '```\n')

    # Fuse support.
    if project_configuration.HasDependencyFuse():
      gcc_mount_tool += (
          '\n'
          'If you want to be able to use {0:s}, make sure that:\n'
          '\n'
          '* on a Linux system you have libfuse-dev (Debian-based) or '
          'fuse-devel (RedHat-based) installed.\n'
          '* on a Mac OS X system, you have OSXFuse '
          '(http://osxfuse.github.com/) installed.\n').format(
              mount_tool_name)

    # MinGW support.
    building_table_of_contents += (
        '* [Using Minimalist GNU for Windows (MinGW)]'
        '(Building#using-minimalist-gnu-for-windows-mingw)\n')

    if project_configuration.mingw_build_dependencies:
      for dependency in project_configuration.mingw_build_dependencies:
        mingw_build_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.mingw_dll_dependencies:
      for dependency in project_configuration.mingw_dll_dependencies:
        mingw_dll_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.HasTools():
      mingw_executables += (
          'And the following executables:\n'
          '```\n')

      for name in project_configuration.tools_names:
        mingw_executables += (
            '{0:s}/.libs/{1:s}.exe\n'.format(
                project_configuration.tools_directory, name))

      mingw_executables += (
          '```\n'
          '\n')

    # Visual Studio support.
    building_table_of_contents += (
        '* [Using Microsoft Visual Studio]'
        '(Building#using-microsoft-visual-studio)\n')

    if project_configuration.msvscpp_build_dependencies:
      msvscpp_build_dependencies = (
          '\n'
          'To compile {0:s} using Microsoft Visual Studio you\'ll '
          'need:\n'
          '\n').format(project_configuration.project_name)

      for dependency in project_configuration.msvscpp_build_dependencies:
        msvscpp_build_dependencies += '* {0:s}\n'.format(dependency)

    if project_configuration.msvscpp_dll_dependencies:
      msvscpp_dll_dependencies = '{0:s}.dll is dependent on:\n'.format(
          project_configuration.project_name)

      for dependency in project_configuration.msvscpp_dll_dependencies:
        msvscpp_dll_dependencies += '* {0:s}\n'.format(dependency)

      msvscpp_dll_dependencies += (
          '\n'
          'These DLLs can be found in the same directory as '
          '{0:s}.dll.\n').format(project_configuration.project_name)

    msvscpp_build_git = (
        '\n'
        'Note that if you want to build {0:s} from source checked out of '
        'git with Visual Studio make sure the autotools are able to make '
        'a distribution package of {0:s} before trying to build it.\n'
        'You can create distribution package by running: '
        '"make dist".\n').format(project_configuration.project_name)

    if project_configuration.HasDependencyDokan():
      msvscpp_mount_tool += (
          '\n'
          'If you want to be able to use {0:s} you\'ll need Dokan library '
          'see the corresponding section below.\n'
          'Otherwise ignore or remove the dokan_dll and {0:s} Visual Studio '
          'project files.\n').format(mount_tool_name)

    building_table_of_contents += '\n'

    building_table_of_contents += (
        'Or directly packaged with different package managers:\n\n')

    if project_configuration.HasDpkg():
      building_table_of_contents += (
          '* [Using Debian package tools (DEB)]'
          '(Building#using-debian-package-tools-deb)\n')

      if project_configuration.dpkg_build_dependencies is None:
        dpkg_build_dependencies = []
      else:
        dpkg_build_dependencies = list(
            project_configuration.dpkg_build_dependencies)

      if project_configuration.HasDependencyFuse():
        dpkg_build_dependencies.append('libfuse-dev')

      if project_configuration.HasPythonModule():
        dpkg_build_dependencies.append('python-all-dev')
        dpkg_build_dependencies.append('python3-all-dev')

      dpkg_build_dependencies = ' '.join(dpkg_build_dependencies)

      dpkg_filenames += (
          '{0:s}_<version>-1_<arch>.deb\n'
          '{0:s}-dev_<version>-1_<arch>.deb').format(
              project_configuration.project_name)

      if project_configuration.HasPythonModule():
        dpkg_filenames += (
            '\n{0:s}-python_<version>-1_<arch>.deb').format(
                project_configuration.project_name)
        dpkg_filenames += (
            '\n{0:s}-python3_<version>-1_<arch>.deb').format(
                project_configuration.project_name)

      if project_configuration.HasTools():
        dpkg_filenames += (
            '\n{0:s}-tools_<version>-1_<arch>.deb').format(
                project_configuration.project_name)

    if project_configuration.HasRpm():
      building_table_of_contents += (
          '* [Using RedHat package tools (RPM)]'
          '(Building#using-redhat-package-tools-rpm)\n')

      if project_configuration.rpm_build_dependencies is None:
        rpm_build_dependencies = []
      else:
        rpm_build_dependencies = list(
            project_configuration.rpm_build_dependencies)

      if project_configuration.HasDependencyFuse():
        rpm_build_dependencies.append('fuse-devel')

      if project_configuration.HasPythonModule():
        rpm_build_dependencies.append('python-devel')
        rpm_build_dependencies.append('python3-devel')

      rpm_build_dependencies = ' '.join(rpm_build_dependencies)

      if project_configuration.project_status:
        rpm_rename_source_package += (
            'mv {0:s}-{1:s}-<version>.tar.gz {0:s}-<version>.tar.gz\n'.format(
                project_configuration.project_name,
                project_configuration.project_status))

      rpm_filenames += (
          '~/rpmbuild/RPMS/<arch>/{0:s}-<version>-1.<arch>.rpm\n'
          '~/rpmbuild/RPMS/<arch>/{0:s}-devel-<version>-1.<arch>'
          '.rpm\n').format(project_configuration.project_name)

      if project_configuration.HasPythonModule():
        rpm_filenames += (
            '~/rpmbuild/RPMS/<arch>/{0:s}-python-<version>-1.<arch>'
            '.rpm\n').format(project_configuration.project_name)
        rpm_filenames += (
            '~/rpmbuild/RPMS/<arch>/{0:s}-python3-<version>-1.<arch>'
            '.rpm\n').format(project_configuration.project_name)

      if project_configuration.HasTools():
        rpm_filenames += (
            '~/rpmbuild/RPMS/<arch>/{0:s}-tools-<version>-1.<arch>'
            '.rpm\n').format(project_configuration.project_name)

      rpm_filenames += (
          '~/rpmbuild/SRPMS/{0:s}-<version>-1.src.rpm').format(
              project_configuration.project_name)

    building_table_of_contents += (
        '* [Using Mac OS X pkgbuild](Building#using-mac-os-x-pkgbuild)\n')

    if project_configuration.HasPythonModule():
      macosx_pkg_configure_options = ' --enable-python --with-pyprefix'

    if project_configuration.HasPythonModule():
      building_table_of_contents += (
          '* [Using setup.py](Building#using-setuppy)\n')

    development_table_of_contents += (
        '* [C/C++ development](C-development)\n')

    if project_configuration.HasPythonModule():
      development_table_of_contents += (
          '* [Python development](Python-development)\n')

    if project_configuration.development_main_object_pre_open_python:
      development_main_object_pre_open_python = '{0:s}\n'.format(
          project_configuration.development_main_object_pre_open_python)

    if project_configuration.development_main_object_post_open_python:
      development_main_object_post_open_python = '{0:s}\n'.format(
          '\n'.join(project_configuration.development_main_object_post_open_python))

    if project_configuration.development_main_object_post_open_file_object_python:
      development_main_object_post_open_file_object_python = '{0:s}\n'.format(
          '\n'.join(project_configuration.development_main_object_post_open_file_object_python))
    elif project_configuration.development_main_object_post_open_python:
      development_main_object_post_open_file_object_python = '{0:s}\n'.format(
          '\n'.join(project_configuration.development_main_object_post_open_python))

    if project_configuration.mount_tool_additional_arguments:
      mount_tool_additional_arguments = project_configuration.mount_tool_additional_arguments

    if project_configuration.mount_tool_source_description_long:
      mount_tool_source_description_long = (
          project_configuration.mount_tool_source_description_long)
    else:
      mount_tool_source_description_long = project_configuration.mount_tool_source_description

    if project_configuration.mount_tool_supported_backends:
      for backend in project_configuration.mount_tool_supported_backends:
        mount_tool_supported_backends += '* {0:s}\n'.format(backend)

    template_mappings = {
        'building_table_of_contents': building_table_of_contents,

        'project_name': project_configuration.project_name,
        'project_name_upper_case': project_configuration.project_name.upper(),
        'project_status': project_status,
        'project_description': project_configuration.project_description,
        'project_git_url': project_configuration.project_git_url,
        'project_downloads_url': project_configuration.project_downloads_url,

        'build_dependencies': build_dependencies,

        'python_bindings_name': python_bindings_name,
        'mount_tool_name': mount_tool_name,
        'tools_name': tools_name,

        'documentation': documentation,

        'development_table_of_contents': development_table_of_contents,

        'development_prefix': development_prefix,
        'development_main_object': project_configuration.development_main_object,
        'development_main_object_filename': (
            project_configuration.development_main_object_filename),
        'development_main_object_pre_open_python': (
            development_main_object_pre_open_python),
        'development_main_object_post_open_python': (
            development_main_object_post_open_python),
        'development_main_object_post_open_file_object_python': (
            development_main_object_post_open_file_object_python),
        'development_main_object_size': project_configuration.development_main_object_size,

        'tests_profiles': tests_profiles,
        'tests_example_filename1': project_configuration.tests_example_filename1,
        'tests_example_filename2': project_configuration.tests_example_filename2,

        'troubleshooting_example': troubleshooting_example,

        'cygwin_build_dependencies': cygwin_build_dependencies,
        'cygwin_dll_dependencies': cygwin_dll_dependencies,
        'cygwin_dll_filename': project_configuration.cygwin_dll_filename,
        'cygwin_executables': cygwin_executables,

        'gcc_build_dependencies': gcc_build_dependencies,
        'gcc_static_build_dependencies': gcc_static_build_dependencies,
        'gcc_mount_tool': gcc_mount_tool,

        'mingw_build_dependencies': mingw_build_dependencies,
        'mingw_dll_dependencies': mingw_dll_dependencies,
        'mingw_dll_filename': project_configuration.mingw_dll_filename,
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

        'mount_tool_additional_arguments': mount_tool_additional_arguments,
        'mount_tool_missing_backend_error': (
            project_configuration.mount_tool_missing_backend_error),
        'mount_tool_mount_point': project_configuration.mount_tool_mount_point,
        'mount_tool_mounted_description': project_configuration.mount_tool_mounted_description,
        'mount_tool_mounted_dokan': project_configuration.mount_tool_mounted_dokan,
        'mount_tool_mounted_fuse': project_configuration.mount_tool_mounted_fuse,
        'mount_tool_source': project_configuration.mount_tool_source,
        'mount_tool_source_description': project_configuration.mount_tool_source_description,
        'mount_tool_source_description_long': (
            mount_tool_source_description_long),
        'mount_tool_supported_backends': mount_tool_supported_backends,
    }
    return template_mappings

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
    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection('introduction.txt', template_mappings, output_writer)

    self._GenerateSection('source.txt', template_mappings, output_writer)
    self._GenerateSection(
        'source_distribution_package.txt', template_mappings, output_writer)
    self._GenerateSection('source_git.txt', template_mappings, output_writer)

    self._GenerateSection('gcc.txt', template_mappings, output_writer)

    if project_configuration.supports_debug_output:
      self._GenerateSection(
          'gcc_debug_output.txt', template_mappings, output_writer)

    self._GenerateSection(
        'gcc_static_library.txt', template_mappings, output_writer)

    if project_configuration.HasTools():
      self._GenerateSection(
          'gcc_static_executables.txt', template_mappings, output_writer)

    if project_configuration.HasPythonModule():
      self._GenerateSection(
          'gcc_python.txt', template_mappings, output_writer)

    self._GenerateSection('cygwin.txt', template_mappings, output_writer)
    self._GenerateSection('gcc_macosx.txt', template_mappings, output_writer)

    if project_configuration.HasPythonModule():
      self._GenerateSection(
          'gcc_macosx_python.txt', template_mappings, output_writer)

    self._GenerateSection(
        'gcc_solaris.txt', template_mappings, output_writer)

    # MinGW support.
    self._GenerateSection('mingw.txt', template_mappings, output_writer)
    self._GenerateSection('mingw_msys.txt', template_mappings, output_writer)
    self._GenerateSection('mingw_dll.txt', template_mappings, output_writer)
    self._GenerateSection(
        'mingw_troubleshooting.txt', template_mappings, output_writer)

    # Visual Studio support.
    self._GenerateSection('msvscpp.txt', template_mappings, output_writer)

    if project_configuration.supports_debug_output:
      self._GenerateSection(
          'msvscpp_debug.txt', template_mappings, output_writer)

    if project_configuration.msvscpp_zlib_dependency:
      self._GenerateSection(
          'msvscpp_zlib.txt', template_mappings, output_writer)

    if project_configuration.HasDependencyDokan():
      self._GenerateSection(
          'msvscpp_dokan.txt', template_mappings, output_writer)

    if project_configuration.HasPythonModule():
      self._GenerateSection(
          'msvscpp_python.txt', template_mappings, output_writer)

    self._GenerateSection(
        'msvscpp_build.txt', template_mappings, output_writer)
    self._GenerateSection(
        'msvscpp_dll.txt', template_mappings, output_writer)

    self._GenerateSection(
        'msvscpp_2010.txt', template_mappings, output_writer)

    if project_configuration.HasDpkg():
      self._GenerateSection('dpkg.txt', template_mappings, output_writer)

    if project_configuration.HasRpm():
      self._GenerateSection('rpm.txt', template_mappings, output_writer)

    self._GenerateSection('macosx_pkg.txt', template_mappings, output_writer)

    if project_configuration.HasPythonModule():
      self._GenerateSection('setup_py.txt', template_mappings, output_writer)

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
    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection('main.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return project_configuration.HasPythonModule()


class CDevelopmentPageGenerator(WikiPageGenerator):
  """Class that generates the "C/C++ development" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for also_see.txt, main_object.txt

    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection('main.txt', template_mappings, output_writer)

    if project_configuration.development_main_object:
      if project_configuration.development_glob:
        self._GenerateSection(
            'main_object_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection(
            'main_object.txt', template_mappings, output_writer)

    self._GenerateSection('also_see.txt', template_mappings, output_writer)

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
    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection('main.txt', template_mappings, output_writer)

    if project_configuration.development_main_object:
      if project_configuration.development_glob:
        self._GenerateSection(
            'main_object_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection(
            'main_object.txt', template_mappings, output_writer)

    if project_configuration.development_pytsk3:
      if project_configuration.development_glob:
        self._GenerateSection(
            'pytsk3_with_glob.txt', template_mappings, output_writer)

      else:
        self._GenerateSection('pytsk3.txt', template_mappings, output_writer)

    # TODO: move main object out of this template and create on demand.
    self._GenerateSection('also_see.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    return project_configuration.HasPythonModule()


class HomePageGenerator(WikiPageGenerator):
  """Class that generates the "Home" wiki page."""

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection('introduction.txt', template_mappings, output_writer)

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
    template_mappings = self._GetTemplateMappings(project_configuration)
    if (project_configuration.HasDependencyDokan() or
        project_configuration.HasDependencyFuse()):
      self._GenerateSection(
          'introduction.txt', template_mappings, output_writer)

      if project_configuration.mount_tool_source_type == 'image':
        self._GenerateSection(
            'mounting_image.txt', template_mappings, output_writer)

      elif project_configuration.mount_tool_source_type == 'volume':
        self._GenerateSection(
            'mounting_volume.txt', template_mappings, output_writer)

      self._GenerateSection(
          'mounting_missing_backend.txt', template_mappings, output_writer)

      if project_configuration.mount_tool_source_type == 'volume':
        self._GenerateSection(
            'mounting_volume_loopback.txt', template_mappings,
            output_writer)
        self._GenerateSection(
            'obtaining_volume_offset.txt', template_mappings,
            output_writer)

      self._GenerateSection(
          'mounting_root_access.txt', template_mappings, output_writer)

      if project_configuration.HasDependencyDokan():
        if project_configuration.mount_tool_source_type == 'image':
          self._GenerateSection(
              'mounting_image_windows.txt', template_mappings,
              output_writer)

        elif project_configuration.mount_tool_source_type == 'volume':
          self._GenerateSection(
              'mounting_volume_windows.txt', template_mappings,
              output_writer)

      self._GenerateSection(
          'unmounting.txt', template_mappings, output_writer)

      if project_configuration.HasDependencyDokan():
        self._GenerateSection(
            'unmounting_windows.txt', template_mappings, output_writer)

      self._GenerateSection(
          'troubleshooting.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    if (project_configuration.HasDependencyDokan() or
        project_configuration.HasDependencyFuse()):
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
    template_mappings = self._GetTemplateMappings(project_configuration)
    if project_configuration.HasTests():
      self._GenerateSection('tests.txt', template_mappings, output_writer)

      if project_configuration.tests_profiles:
        if (project_configuration.tests_example_filename1 and
            project_configuration.tests_example_filename2):
          self._GenerateSection(
              'tests_files.txt', template_mappings, output_writer)

        self._GenerateSection(
            'tests_profiles.txt', template_mappings, output_writer)

        if (project_configuration.tests_example_filename1 and
            project_configuration.tests_example_filename2):
          self._GenerateSection(
              'tests_profiles_files.txt', template_mappings, output_writer)

      if project_configuration.tests_supports_valgrind:
        self._GenerateSection(
            'tests_valgrind.txt', template_mappings, output_writer)

  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the generator will generate content.
    """
    if project_configuration.HasTests():
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
    template_mappings = self._GetTemplateMappings(project_configuration)
    self._GenerateSection(
        'introduction.txt', template_mappings, output_writer)
    self._GenerateSection(
        'build_errors.txt', template_mappings, output_writer)
    self._GenerateSection(
        'runtime_errors.txt', template_mappings, output_writer)

    if project_configuration.supports_debug_output:
      self._GenerateSection(
          'format_errors.txt', template_mappings, output_writer)

    if project_configuration.HasTools():
      self._GenerateSection(
          'crashes.txt', template_mappings, output_writer)

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
    print(data, end='')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates wiki pages of the libyal libraries.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='CONFIGURATION_FILE',
      default='project-wiki.ini', help=(
          'The wiki generation configuration file.'))

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

  project_configuration = configuration.ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  readme_file = os.path.join(
      os.path.dirname(options.configuration_file), 'README')

  LINK_RE = re.compile(r'\* (.*): (http[s]://.*)')

  project_description = []
  if os.path.exists(readme_file):
    with open(readme_file, 'rb') as file_object:
      for line in file_object.readlines():
        if line.startswith('For more information see:'):
          project_description.pop()
          break

        line = LINK_RE.sub(r'* [\1](\2)', line)
        project_description.append(line)

        if line.endswith(':\n'):
          # Add an empty line to make sure unnumbered list are formatted
          # correctly by most markdown parsers.
          project_description.append('\n')

  project_configuration.project_description = ''.join(project_description)

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  # TODO: generate more wiki pages.
  wiki_pages = [
      ('Building', BuildingPageGenerator),
      ('Development', DevelopmentPageGenerator),
      ('Home', HomePageGenerator),
      ('Mounting', MountingPageGenerator),
      ('C development', CDevelopmentPageGenerator),
      ('Python development', PythonDevelopmentPageGenerator),
      ('Testing', TestingPageGenerator),
      ('Troubleshooting', TroubleshootingPageGenerator),
  ]

  for page_name, page_generator_class in wiki_pages:
    template_directory = os.path.join(
        libyal_directory, 'data', 'wiki', page_name)
    wiki_page = page_generator_class(template_directory)

    if not wiki_page.HasContent(project_configuration):
      continue

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

    wiki_page.Generate(project_configuration, output_writer)

    output_writer.Close()

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
