#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of the libyal libraries."""

from __future__ import print_function
import abc
import argparse
import collections
import datetime
import json
import logging
import os
import stat
import string
import sys
import time

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class ProjectConfiguration(object):
  """Class that defines a project configuration."""

  def __init__(self):
    """Initializes a project configuation object."""
    super(ProjectConfiguration, self).__init__()
    self.project_authors = None
    self.project_name = None
    self.project_year_of_creation = None

    self.library_description = None
    self.library_name = None
    self.library_name_suffix = None
    # TODO: determine public types based on include header.
    self.library_public_types = None

    self.python_module_authors = None
    self.python_module_name = None
    self.python_module_year_of_creation = None

    self.tools_authors = None
    self.tools_name = None

    self.tests_authors = None

  def _GetConfigValue(self, config_parser, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      config_parser (ConfigParser): configuration parser.
      section_name (str): name of the section that contains the value.
      value_name (name): name of the value.

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
      value_name (name): name of the value.
      default_value (Optional[object]): default value.

    Returns:
      object: value or default value if not available.
    """
    try:
      return self._GetConfigValue(config_parser, section_name, value_name)
    except (configparser.NoOptionError, configparser.NoSectionError):
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
    self.project_authors = self._GetConfigValue(
        config_parser, u'project', u'authors')
    self.project_year_of_creation = self._GetConfigValue(
        config_parser, u'project', u'year_of_creation')

    self.library_description = self._GetConfigValue(
        config_parser, u'library', u'description')
    self.library_name = self.project_name
    self.library_name_suffix = self.project_name[3:]
    self.library_public_types = self._GetOptionalConfigValue(
        config_parser, u'library', u'public_types', default_value=[])

    self.python_module_authors = self._GetOptionalConfigValue(
        config_parser, u'python_module', u'authors',
        default_value=self.project_authors)
    self.python_module_name = u'py{0:s}'.format(self.library_name_suffix)
    self.python_module_year_of_creation = self._GetOptionalConfigValue(
        config_parser, u'python_module', u'year_of_creation',
        default_value=self.project_year_of_creation)

    self.tools_authors = self._GetOptionalConfigValue(
        config_parser, u'tools', u'authors', default_value=self.project_authors)
    self.tools_name = u'{0:s}tools'.format(self.library_name_suffix)

    self.tests_authors = self._GetOptionalConfigValue(
        config_parser, u'tests', u'authors', default_value=self.project_authors)

    self.project_year_of_creation = int(self.project_year_of_creation, 10)
    self.python_module_year_of_creation = int(
        self.python_module_year_of_creation, 10)

  def GetTemplateMappings(self, authors_separator=u', '):
    """Retrieves the template mappings.

    Args:
      authors_separator (Optional[str]): authors separator.

    Returns:
      dict[str, str]: string template mappings.

    Raises:
      ValueError: if the year of creation value is out of bounds.
    """
    date = datetime.date.today()
    if self.project_year_of_creation > date.year:
      raise ValueError(u'Year of creation value out of bounds.')

    if self.project_year_of_creation == date.year:
      project_copyright = u'{0:d}'.format(self.project_year_of_creation)
    else:
      project_copyright = u'{0:d}-{1:d}'.format(
          self.project_year_of_creation, date.year)

    if self.python_module_year_of_creation == date.year:
      python_module_copyright = u'{0:d}'.format(
          self.python_module_year_of_creation)
    else:
      python_module_copyright = u'{0:d}-{1:d}'.format(
          self.python_module_year_of_creation, date.year)

    authors = authors_separator.join(self.project_authors)
    python_module_authors = authors_separator.join(self.python_module_authors)
    tools_authors = authors_separator.join(self.tools_authors)
    tests_authors = authors_separator.join(self.tests_authors)

    template_mappings = {
        u'authors': authors,
        u'copyright': project_copyright,

        u'library_name': self.library_name,
        u'library_name_upper_case': self.library_name.upper(),
        u'library_name_suffix': self.library_name_suffix,
        u'library_name_suffix_upper_case': self.library_name_suffix.upper(),
        u'library_description': self.library_description,

        u'python_module_authors': python_module_authors,
        u'python_module_name': self.python_module_name,
        u'python_module_name_upper_case': self.python_module_name.upper(),
        u'python_module_copyright': python_module_copyright,

        u'tools_authors': tools_authors,
        u'tools_name': self.tools_name,
        u'tools_name_upper_case': self.tools_name.upper(),

        u'tests_authors': tests_authors,
    }
    return template_mappings


class FunctionArgument(object):
  """Class that defines a function argument."""

  def __init__(self, argument_string):
    """Initializes a function argument.

    Args:
      argument_string (str): function argument.
    """
    super(FunctionArgument, self).__init__()
    self._strings = [argument_string]

  def AddArgumentString(self, argument_string):
    """Adds an argument string to the function argument.

    Args:
      argument_string (str): function argument.
    """
    self._strings.append(argument_string)

  def CopyToString(self):
    """Copies the function argument to a string.

    Returns:
      str: function argument.
    """
    number_of_strings = len(self._strings)

    argument_string = u''
    if number_of_strings == 1:
      argument_string = self._strings[0]

    elif number_of_strings > 1:
      argument_string = u'{0:s}{1:s}'.format(
          self._strings[0], u', '.join(self._strings[1:]))

    return argument_string


class FunctionPrototype(object):
  """Class that defines a function prototype.

  Attributes:
    have_bfio (bool): True if the function prototype is defined if BFIO is
        defined.
    have_debug_output (bool): True if the function prototype is defined if
        debug output is defined.
    have_wide_character_type (bool): True if the function prototype is
        defined if the wide character type is defined.
    name (str): name.
    return_type (str): return type.
  """

  def __init__(self, name, return_type):
    """Initializes a function prototype.

    Args:
      name (str): name.
      return_type (str): return type.
    """
    super(FunctionPrototype, self).__init__()
    self._arguments = []
    self.have_bfio = False
    self.have_debug_output = False
    self.have_wide_character_type = False
    self.name = name
    self.return_type = return_type

  def AddArgument(self, argument):
    """Adds an argument to the function prototype.

    Args:
      argument (FunctionArgument): function argument.
    """
    self._arguments.append(argument)

  def AddArgumentString(self, argument_string):
    """Adds an argument string to the function prototype.

    Args:
      argument_string (str): function argument.
    """
    function_argument = FunctionArgument(argument_string)
    self._arguments.append(function_argument)

  def CopyToString(self):
    """Copies the function prototype to a string.

    Returns:
      str: function prototype.
    """
    argument_strings = []
    for function_argument in self._arguments:
      argument_string = function_argument.CopyToString()
      argument_strings.append(argument_string)

    return u', '.join(argument_strings)


class LibraryIncludeHeaderFile(object):
  """Class that defines a library include header file.

  Attributes:
    functions_per_name (dict[str, list[FunctionPrototype]]): function
        prototypes per name.
    functions_per_section (dict[str, list[FunctionPrototype]]): function
        prototypes per section.
    name (str): name.
    section_names (list[str]): section names.
  """

  def __init__(self, path):
    """Initializes a library include header file.

    Args:
      path (str): path library include header file.
    """
    super(LibraryIncludeHeaderFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.functions_per_name = collections.OrderedDict()
    self.functions_per_section = {}
    self.section_names = []

  def ReadFunctions(self, project_configuration):
    """Reads the functions from the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the functions were read from the file.
    """
    define_deprecated = b'{0:s}_DEPRECATED'.format(
        project_configuration.library_name.upper())

    define_extern = b'{0:s}_EXTERN'.format(
        project_configuration.library_name.upper())

    define_have_bfio = b'#if defined( {0:s}_HAVE_BFIO )'.format(
        project_configuration.library_name.upper())

    define_have_debug_output = b'#if defined( HAVE_DEBUG_OUTPUT )'

    define_have_wide_character_type = (
        b'#if defined( {0:s}_HAVE_WIDE_CHARACTER_TYPE )').format(
            project_configuration.library_name.upper())

    function_argument = None
    function_prototype = None
    have_bfio = False
    have_debug_output = False
    have_wide_character_type = False
    in_define_deprecated = False
    in_define_extern = False
    in_section = False
    section_name = None
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if in_define_extern:
          line = line.decode(u'ascii')

          if function_prototype:
            # Check if we have a callback function argument.
            if line.endswith(u'('):
              argument_string = u'{0:s} '.format(line)
              function_argument = FunctionArgument(argument_string)

            else:
              if line.endswith(u' );'):
                argument_string = line[:-3]

              else:
                # Get the part of the line before the ','.
                argument_string, _, _ = line.partition(u',')

              if not function_argument:
                function_prototype.AddArgumentString(argument_string)

              else:
                function_argument.AddArgumentString(argument_string)

            if function_argument and line.endswith(u' ),'):
              function_prototype.AddArgument(function_argument)
              function_argument = None

            elif line.endswith(u' );'):
              if not in_define_deprecated:
                self.functions_per_name[function_prototype.name] = (
                    function_prototype)

                self.functions_per_section[section_name].append(
                    function_prototype)

              function_prototype = None
              in_define_deprecated = False
              in_define_extern = False

          elif line.endswith(u';'):
            # The line contains a variable definition.
            in_define_extern = False

          else:
            # Get the part of the line before the library name.
            return_type, _, _ = line.partition(
                project_configuration.library_name)

            # Get the part of the line after the return type.
            line = line[len(return_type):]
            return_type = return_type.strip()

            # Get the part of the remainder of the line before the '('.
            name, _, _ = line.partition(u'(')

            function_prototype = FunctionPrototype(name, return_type)
            function_prototype.have_bfio = have_bfio
            function_prototype.have_debug_output = have_debug_output
            function_prototype.have_wide_character_type = (
                have_wide_character_type)

        elif in_section:
          if line.startswith(b'* '):
            section_name = line[2:]
            self.section_names.append(section_name)
            self.functions_per_section[section_name] = []
            in_section = False

        elif line.startswith(define_deprecated):
          in_define_deprecated = True

        elif line.startswith(define_extern):
          in_define_extern = True

        elif line == (
            b'/* -------------------------------------------------------------'
            b'------------'):
          in_section = True

        elif line.startswith(b'#endif'):
          have_bfio = False
          have_debug_output = False
          have_wide_character_type = False

        elif line.startswith(define_have_debug_output):
          have_debug_output = True

        elif line.startswith(define_have_bfio):
          have_bfio = True

        elif line.startswith(define_have_wide_character_type):
          have_wide_character_type = True

    return True


class LibraryMakefileAMFile(object):
  """Class that defines a library Makefile.am file.

  Attributes:
    libraries (list[str]): library names.
  """

  def __init__(self, path):
    """Initializes a library Makefile.am file.

    Args:
      path (str): path of the Makefile.am file.
    """
    super(LibraryMakefileAMFile, self).__init__()
    self._path = path

    self.libraries = []

  def ReadLibraries(self, project_configuration):
    """Reads the libraries from the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the libraries were read from the file.
    """
    library_libadd = b'{0:s}_la_LIBADD'.format(
        project_configuration.library_name)

    in_libadd = False
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_libadd:
          if line.endswith(b'\\'):
            line = line[:-1].strip()

          if line.startswith(b'@') and line.endswith(b'_LIBADD@'):
            self.libraries.append(line[1:-8].lower())

        elif line.startswith(library_libadd):
          in_libadd = True

    self.libraries = sorted(self.libraries)

    return True


class MainMakefileAMFile(object):
  """Class that defines a main Makefile.am file.

  Attributes:
    libraries (list[str]): library names.
  """

  def __init__(self, path):
    """Initializes a main Makefile.am file.

    Args:
      path (str): path of the Makefile.am file.
    """
    super(MainMakefileAMFile, self).__init__()
    self._path = path

    self.libraries = []

  def ReadLibraries(self, project_configuration):
    """Reads the libraries from the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the libraries were read from the file.
    """
    in_subdirs = False
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_subdirs:
          if line.endswith(b'\\'):
            line = line[:-1].strip()

          if not line:
            in_subdirs = False

          elif (line.startswith(b'lib') and
                line != project_configuration.library_name):
            self.libraries.append(line)

        elif line.startswith(b'SUBDIRS'):
          in_subdirs = True

    self.libraries = sorted(self.libraries)

    return True


class TypesIncludeHeaderFile(object):
  """Class that defines a types include header file.

  Attributes:
    types (list[str]): section names.
  """

  def __init__(self, path):
    """Initializes a types include header file.

    Args:
      path (str): path of the include header file.
    """
    super(TypesIncludeHeaderFile, self).__init__()
    self._path = path

    self.types = []

  def ReadTypes(self, project_configuration):
    """Reads the types from the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the types were read from the file.
    """
    typedef = b'typedef intptr_t {0:s}_'.format(
        project_configuration.library_name)

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(typedef) and line.endswith(b'_t;'):
          self.types.append(line[len(typedef):-3])

    return True


class SourceFileGenerator(object):
  """Class that generates source files."""

  def __init__(self, projects_directory, template_directory):
    """Initialize the source file generator.

    Args:
      projects_directory (str): path of the projects directory.
      template_directory (str): path of the template directory.
    """
    super(SourceFileGenerator, self).__init__()
    self._projects_directory = projects_directory
    self._template_directory = template_directory

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer,
      output_filename, access_mode='wb'):
    """Generates a section from template filename.

    Args:
      template_filename (str): name of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    template_string = self._ReadTemplateFile(template_filename)
    try:
      output_data = template_string.substitute(template_mappings)
    except ValueError as exception:
      logging.error(u'Unable to format template: {0:s}'.format(
          template_filename))
      return

    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename (str): name of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    file_object = open(filename, 'rb')
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """


class CommonSourceFileGenerator(SourceFileGenerator):
  """Class that generates the common source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates common source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')
    template_mappings[u'authors'] = u'Joachim Metz <joachim.metz@gmail.com>'

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(u'common', directory_entry)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class ConfigurationFileGenerator(SourceFileGenerator):
  """Class that generates the configuration files."""

  def Generate(self, project_configuration, output_writer):
    """Generates configuration files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: generate spec file, what about Python versus non-Python?
    # TODO: generate dpkg files, what about Python versus non-Python?
    # TODO: appveyor.yml
    #   - cmd: git clone https://github.com/joachimmetz/dokan.git && move dokan ..\

    makefile_am_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name, u'Makefile.am')

    makefile_am_file = LibraryMakefileAMFile(makefile_am_path)
    makefile_am_file.ReadLibraries(project_configuration)

    template_mappings = project_configuration.GetTemplateMappings()
    pc_libs_private = []
    for library in makefile_am_file.libraries:
      if library == u'libdl':
        continue

      pc_lib_private = u'@ax_{0:s}_pc_libs_private@'.format(library)
      pc_libs_private.append(pc_lib_private)

    template_mappings[u'pc_libs_private'] = u' '.join(pc_libs_private)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == u'libyal.pc.in':
        output_filename = u'{0:s}.pc.in'.format(
            project_configuration.library_name)
      else:
        output_filename = directory_entry

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class LibrarySourceFileGenerator(SourceFileGenerator):
  """Class that generates the library source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates library source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for libuna/libuna_types.h
    # TODO: types.h alingment of debug types?
    # TODO: do not generate libuna/libuna_libcstring.h
    # TODO: libsmraw/libsmraw_codepage.h alignment of definitions
    # TODO: libfvalue/libfvalue_codepage.h different

    include_header_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'include', project_configuration.library_name, u'types.h.in')

    include_header_file = TypesIncludeHeaderFile(include_header_path)
    include_header_file.ReadTypes(project_configuration)

    library_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name)

    codepage_header_file = os.path.join(
        library_path, u'{0:s}_codepage.h'.format(
            project_configuration.library_name))
    error_header_file = os.path.join(
        library_path, u'{0:s}_error.h'.format(
            project_configuration.library_name))
    notify_header_file = os.path.join(
        library_path, u'{0:s}_notify.h'.format(
            project_configuration.library_name))
    types_header_file = os.path.join(
        library_path, u'{0:s}_types.h'.format(
            project_configuration.library_name))

    if include_header_file.types:
      longest_type_name = max(include_header_file.types, key=len)
      longest_library_debug_type_prefix = (
          u'typedef struct {0:s}_{1:s} {{}}').format(
              project_configuration.library_name, longest_type_name)

    library_debug_type_definitions = []
    library_type_definitions = []
    for type_name in include_header_file.types:
      library_debug_type_prefix = u'typedef struct {0:s}_{1:s} {{}}'.format(
          project_configuration.library_name, type_name)

      # TODO: fix alignment of libcdatetime/libcdatetime_types.h
      alignment_length = (
          len(longest_library_debug_type_prefix) -
          len(library_debug_type_prefix))
      alignment_length, alignment_remainder = divmod(alignment_length, 8)
      if alignment_remainder >= 8:
          alignment_length += 1

      alignment = u'\t' * (1 + alignment_length)

      library_debug_type_definitions.append(
          u'typedef struct {0:s}_{1:s} {{}}{2:s}{0:s}_{1:s}_t;'.format(
              project_configuration.library_name, type_name, alignment))
      library_type_definitions.append(
          u'typedef intptr_t {0:s}_{1:s}_t;'.format(
              project_configuration.library_name, type_name))

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')
    template_mappings[u'library_debug_type_definitions'] = u'\n'.join(
        library_debug_type_definitions)
    template_mappings[u'library_type_definitions'] = u'\n'.join(
        library_type_definitions)

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith(u'libyal_'):
        continue

      if directory_entry.endswith(u'_{0:s}.h'.format(
          project_configuration.library_name)):
        continue

      if (directory_entry.endswith(u'_codepage.h') and (
          not os.path.exists(codepage_header_file) or
          project_configuration.library_name == u'libclocale')):
        continue

      if ((directory_entry.endswith(u'_libcerror.h') or
           directory_entry.endswith(u'_error.c') or
           directory_entry.endswith(u'_error.h')) and (
               not os.path.exists(error_header_file) or
               project_configuration.library_name == u'libcerror')):
        continue

      if ((directory_entry.endswith(u'_libcnotify.h') or
           directory_entry.endswith(u'_notify.c') or
           directory_entry.endswith(u'_notify.h')) and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == u'libcnotify')):
        continue

      # TODO: improve generation of _types.h file
      if (directory_entry.endswith(u'_types.h') and (
              not os.path.exists(types_header_file) or
              project_configuration.library_name in (
                  u'libcerror', u'libcstring', u'libcthreads'))):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = u'{0:s}_{1:s}'.format(
          project_configuration.library_name, directory_entry[7:])
      output_filename = os.path.join(
          project_configuration.library_name, output_filename)

      if not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class LibraryManPageGenerator(SourceFileGenerator):
  """Class that generates the library man page file (libyal.3)."""

  def Generate(self, project_configuration, output_writer):
    """Generates a library man page file (libyal.3).

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for libcthreads.h - messed up
    # TODO: add support for libcstring.h - macros
    # TODO: add support for libcsystem.h - additional types
    # TODO: add support for libsigscan.h - not detecting wchar
    # TODO: add support for libsmraw.h - not detecting wchar
    #       (multiple function in single define?)
    # TODO: warn about [a-z]), in include header

    include_header_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'include', u'{0:s}.h.in'.format(project_configuration.library_name))

    # TODO: improve method of determining main include header has changed.
    stat_object = os.stat(include_header_path)
    modification_time = time.gmtime(stat_object.st_mtime)

    include_header_file = LibraryIncludeHeaderFile(include_header_path)
    include_header_file.ReadFunctions(project_configuration)

    output_filename = u'{0:s}.3'.format(project_configuration.library_name)
    output_filename = os.path.join(u'manuals', output_filename)

    template_filename = os.path.join(self._template_directory, u'header.txt')
    template_mappings = project_configuration.GetTemplateMappings()
    template_mappings[u'date'] = time.strftime(
        u'%B %d, %Y', modification_time).replace(u' 0', u'  ')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    have_wide_character_type_functions = False
    for section_name in include_header_file.section_names:
      functions_per_section = include_header_file.functions_per_section.get(
          section_name, [])

      if not functions_per_section:
        continue

      section_template_mappings = {
          u'section_name': section_name,
      }
      template_filename = os.path.join(self._template_directory, u'section.txt')
      self._GenerateSection(
          template_filename, section_template_mappings, output_writer,
          output_filename, access_mode='ab')

      bfio_functions = []
      debug_output_functions = []
      functions = []
      wide_character_type_functions = []
      for function_prototype in functions_per_section:
        if function_prototype.have_bfio:
          bfio_functions.append(function_prototype)
        elif function_prototype.have_debug_output:
          debug_output_functions.append(function_prototype)
        elif function_prototype.have_wide_character_type:
          wide_character_type_functions.append(function_prototype)
        else:
          functions.append(function_prototype)

      for function_prototype in functions:
        function_arguments_string = function_prototype.CopyToString()
        function_template_mappings = {
            u'function_arguments': function_arguments_string,
            u'function_name': function_prototype.name,
            u'function_return_type': function_prototype.return_type,
        }
        template_filename = os.path.join(
            self._template_directory, u'function.txt')
        self._GenerateSection(
            template_filename, function_template_mappings, output_writer,
            output_filename, access_mode='ab')

      if wide_character_type_functions:
        have_wide_character_type_functions = True

        # Ignore adding the wide string support section header in some cases.
        if project_configuration.library_name != u'libcsplit':
          section_template_mappings = {
              u'section_name': (
                  u'Available when compiled with wide character string support:')
          }
          template_filename = os.path.join(
              self._template_directory, u'section.txt')
          self._GenerateSection(
              template_filename, section_template_mappings, output_writer,
              output_filename, access_mode='ab')

        for function_prototype in wide_character_type_functions:
          function_arguments_string = function_prototype.CopyToString()
          function_template_mappings = {
              u'function_arguments': function_arguments_string,
              u'function_name': function_prototype.name,
              u'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, u'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

      if bfio_functions:
        section_template_mappings = {
            u'section_name': (
                u'Available when compiled with libbfio support:')
        }
        template_filename = os.path.join(
            self._template_directory, u'section.txt')
        self._GenerateSection(
            template_filename, section_template_mappings, output_writer,
            output_filename, access_mode='ab')

        for function_prototype in bfio_functions:
          function_arguments_string = function_prototype.CopyToString()
          function_template_mappings = {
              u'function_arguments': function_arguments_string,
              u'function_name': function_prototype.name,
              u'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, u'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

      # TODO: add support for debug output functions.

    template_filename = os.path.join(
        self._template_directory, u'description.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if have_wide_character_type_functions:
      template_filename = os.path.join(self._template_directory, u'notes.txt')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if have_wide_character_type_functions:
      template_filename = os.path.join(
          self._template_directory, u'notes_wchar.txt')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(self._template_directory, u'footer.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')


class PythonModuleSourceFileGenerator(SourceFileGenerator):
  """Class that generates the Python module source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates Python module source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    python_module_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.python_module_name)

    # TODO: generate pyX-python2/Makefile.am and pyX-python3/Makefile.am

    if not os.path.exists(python_module_path):
      return

    codepage_header_file = os.path.join(
        python_module_path, u'{0:s}_codepage.h'.format(
            project_configuration.python_module_name))

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')

    # Used to align source in pyyal/pyyal_file_object_io_handle.c
    alignment_padding = len(project_configuration.library_name) - 6
    template_mappings[u'alignment_padding'] = u' ' * alignment_padding

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith(u'pyyal_'):
        continue

      if (directory_entry.endswith(u'_codepage.h') and
          not os.path.exists(codepage_header_file)):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = u'{0:s}_{1:s}'.format(
          project_configuration.python_module_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.python_module_name, output_filename)
      if not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class ScriptFileGenerator(SourceFileGenerator):
  """Class that generates the script files."""

  def Generate(self, project_configuration, output_writer):
    """Generates script files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    makefile_am_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'Makefile.am')

    makefile_am_file = MainMakefileAMFile(makefile_am_path)
    makefile_am_file.ReadLibraries(project_configuration)

    template_mappings = project_configuration.GetTemplateMappings()
    template_mappings[u'local_libs'] = u' '.join(makefile_am_file.libraries)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = directory_entry

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class TestsSourceFileGenerator(SourceFileGenerator):
  """Class that generates the tests source files."""

  _API_FUNCTION_NAMES = (
      u'get_version', u'get_codepage', 'get_decimal_point', u'error',
      u'notify', u'print', u'stream')

  _API_FUNCTION_WITH_INPUT_NAMES = (
      u'open_close', u'seek', u'read')

  _PYTHON_FUNCTION_NAMES = (
      u'get_version', )

  _PYTHON_FUNCTION_WITH_INPUT_NAMES = (
      u'open_close', u'seek', u'read')

  def _GenerateAPITypeTest(
      self, project_configuration, template_mappings, library_type,
      type_function, include_header_file, output_writer, output_filename):
    """Generates an API type test within the API type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      library_type (str): library type.
      type_function (str): type function.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.

    Returns:
      str: call of test to run or None.
    """
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, library_type, type_function)
    if function_name not in include_header_file.functions_per_name:
      return

    template_filename = u'{0:s}.c'.format(type_function)
    template_filename = os.path.join(
        self._template_directory, u'yal_test_type', template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    return (
        u'\t{0:s}_TEST_RUN(\n'
        u'\t "{1:s}_{2:s}_{3:s}",\n'
        u'\t {4:s}_test_{2:s}_{3:s} );\n'
        u'\n').format(
            project_configuration.library_name_suffix.upper(),
            project_configuration.library_name, library_type,
            type_function, project_configuration.library_name_suffix)

  def _GenerateAPITypeTests(
      self, project_configuration, template_mappings, library_type,
      include_header_file, output_writer, output_filename):
    """Generates an API type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      library_type (str): library type.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_mappings[u'library_type'] = library_type

    function_name = u'{0:s}_{1:s}_open'.format(
        project_configuration.library_name, library_type)

    type_with_input = function_name in include_header_file.functions_per_name

    if type_with_input:
      template_filename = os.path.join(
          self._template_directory, u'yal_test_type', u'header_with_input.c')
    else:
      template_filename = os.path.join(
          self._template_directory, u'yal_test_type', u'header.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    tests_to_run = []
    tests_to_run_with_input = []

    for type_function in (u'initialize', u'free'):
      test_to_run = self._GenerateAPITypeTest(
          project_configuration, template_mappings, library_type, type_function,
          include_header_file, output_writer, output_filename)
      if test_to_run:
        tests_to_run.append(test_to_run)

    if type_with_input:
      for type_function in (u'open', u'get_ascii_codepage'):
        test_to_run = self._GenerateAPITypeTestWithInput(
            project_configuration, template_mappings, library_type, type_function,
            include_header_file, output_writer, output_filename)
        if test_to_run:
          tests_to_run_with_input.append(test_to_run)

    test_to_run = self._GenerateAPITypeTest(
        project_configuration, template_mappings, library_type,
        u'set_ascii_codepage', include_header_file, output_writer,
        output_filename)
    if test_to_run:
      tests_to_run.append(test_to_run)

    if type_with_input:
      for function_name in include_header_file.functions_per_name.keys():
        name_prefix = u'{0:s}_{1:s}_get_number_of_'.format(
            project_configuration.library_name, library_type)
        name_prefix_length = len(name_prefix)

        if function_name.startswith(name_prefix):
          template_filename = u'get_number_of_value.c'
          template_mappings[u'value_name'] = function_name[name_prefix_length:]
        else:
          continue

        template_filename = os.path.join(
            self._template_directory, u'yal_test_type', template_filename)

        if not os.path.exists(template_filename):
          continue

        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

        test_to_run = (
            u'\t\t{0:s}_TEST_RUN_WITH_ARGS(\n'
            u'\t\t "{1:s}_{2:s}_{3:s}",\n'
            u'\t\t {4:s}_test_{2:s}_{3:s},\n'
            u'\t\t {2:s} );\n'
            u'\n').format(
                project_configuration.library_name_suffix.upper(),
                project_configuration.library_name, library_type,
                type_function, project_configuration.library_name_suffix)
              
        tests_to_run_with_input.append(test_to_run)

    # TODO: create generic test for get_number_of_X API functions.
    # TODO: generate run test macros.

    template_mappings[u'test_to_run'] = u''.join(tests_to_run)
    template_mappings[u'tests_to_run_with_input'] = u''.join(
        tests_to_run_with_input)

    if type_with_input:
      template_filename = os.path.join(
          self._template_directory, u'yal_test_type', u'main_with_input.c')
    else:
      template_filename = os.path.join(
          self._template_directory, u'yal_test_type', u'main.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateAPITypeTestWithInput(
      self, project_configuration, template_mappings, library_type,
      type_function, include_header_file, output_writer, output_filename):
    """Generates an API type test within the API type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      library_type (str): library type.
      type_function (str): type function.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.

    Returns:
      str: call of test to run or None.
    """
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, library_type, type_function)
    if function_name not in include_header_file.functions_per_name:
      return

    template_filename = u'{0:s}.c'.format(type_function)
    template_filename = os.path.join(
        self._template_directory, u'yal_test_type', template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    return (
        u'\t\t{0:s}_TEST_RUN_WITH_ARGS(\n'
        u'\t\t "{1:s}_{2:s}_{3:s}",\n'
        u'\t\t {4:s}_test_{2:s}_{3:s},\n'
        u'\t\t {2:s} );\n'
        u'\n').format(
            project_configuration.library_name_suffix.upper(),
            project_configuration.library_name, library_type,
            type_function, project_configuration.library_name_suffix)

  def _SortIncludeHeaders(self, project_configuration, output_filename):
    """Sorts the include headers.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = [line for line in file_object.readlines()]

    include_header_start = b'#include "{0:s}_test_'.format(
        project_configuration.library_name_suffix)

    include_headers = []
    in_include_headers = False

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        if line.startswith(include_header_start):
          include_headers.append(line)
          in_include_headers = True

        elif in_include_headers:
          file_object.writelines(sorted(include_headers))
          file_object.write(line)
          in_include_headers = False

        else:
          file_object.write(line)

  def Generate(self, project_configuration, output_writer):
    """Generates tests source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    tests_path = os.path.join(
        self._projects_directory, project_configuration.library_name, u'tests')

    if not os.path.exists(tests_path):
      return

    # TODO: handle non-template files differently.
    # TODO: yal_test_open_close.c handle file, handle, volume

    library_header = u'yal_test_{0:s}.h'.format(
        project_configuration.library_name)

    test_api_functions = []
    for function_name in self._API_FUNCTION_NAMES:
      if (function_name == u'error' and
          project_configuration.library_name == u'libcerror'):
        continue

      output_filename = u'{0:s}_test_{1:s}.c'.format(
          project_configuration.library_name_suffix, function_name)
      output_filename = os.path.join(u'tests', output_filename)
      if os.path.exists(output_filename):
        test_api_functions.append(function_name)

    test_api_functions_with_input = []
    for function_name in self._API_FUNCTION_WITH_INPUT_NAMES:
      output_filename = u'{0:s}_test_{1:s}.c'.format(
          project_configuration.library_name_suffix, function_name)
      output_filename = os.path.join(u'tests', output_filename)
      if os.path.exists(output_filename):
        test_api_functions_with_input.append(function_name)

    test_python_functions = []
    for function_name in self._PYTHON_FUNCTION_NAMES:
      output_filename = u'{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join(u'tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions.append(function_name)

    test_python_functions_with_input = []
    for function_name in self._PYTHON_FUNCTION_WITH_INPUT_NAMES:
      output_filename = u'{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join(u'tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions_with_input.append(function_name)

    template_mappings = project_configuration.GetTemplateMappings()

    template_mappings[u'test_api_functions'] = u' '.join(test_api_functions)
    template_mappings[u'test_api_functions_with_input'] = u' '.join(
        test_api_functions_with_input)

    template_mappings[u'test_python_functions'] = u' '.join(
        test_python_functions)
    template_mappings[u'test_python_functions_with_input'] = u' '.join(
        test_python_functions_with_input)

    template_mappings[u'test_api_types'] = u' '.join(
        project_configuration.library_public_types)
    template_mappings[u'test_api_types_with_input'] = u''

    template_mappings[u'alignment_padding'] = (
        u' ' * len(project_configuration.library_name_suffix))

    for directory_entry in os.listdir(self._template_directory):
      # Ignore yal_test_library.h in favor of yal_test_libyal.h
      if directory_entry == library_header:
        continue

      # For libcerror skip generating yal_test_error.c.
      if (directory_entry == u'yal_test_error.c' and
          project_configuration.library_name == u'libcerror'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == u'yal_test_libyal.h':
        output_filename = u'{0:s}_test_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      elif directory_entry.startswith(u'yal_test_'):
        output_filename = u'{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[4:])

      elif directory_entry.startswith(u'pyyal_test_'):
        output_filename = u'{0:s}_{1:s}'.format(
            project_configuration.python_module_name, directory_entry[6:])

      elif (directory_entry.startswith(u'test_yal') and
            directory_entry.endswith(u'.sh')):
        output_filename = u'test_{0:s}{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[8:])

      elif (directory_entry.startswith(u'test_pyyal') and
            directory_entry.endswith(u'.sh')):
        output_filename = u'test_{0:s}{1:s}'.format(
            project_configuration.python_module_name, directory_entry[10:])

      else:
        output_filename = directory_entry

      if (output_filename.startswith(u'test_api_types.') and
          project_configuration.library_public_types):
        force_create = True
      else:
        force_create = False

      output_filename = os.path.join(u'tests', output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if output_filename.endswith(u'.c'):
        self._SortIncludeHeaders(project_configuration, output_filename)

      elif output_filename.endswith(u'.sh'):
        # Set x-bit for .sh scripts.
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

    # TODO: detect if library type takes input.

    include_header_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'include', u'{0:s}.h.in'.format(project_configuration.library_name))

    include_header_file = LibraryIncludeHeaderFile(include_header_path)
    include_header_file.ReadFunctions(project_configuration)

    for library_type in project_configuration.library_public_types:
      output_filename = u'{0:s}_test_{1:s}.c'.format(
          project_configuration.library_name_suffix, library_type)
      output_filename = os.path.join(u'tests', output_filename)

      self._GenerateAPITypeTests(
          project_configuration, template_mappings, library_type,
          include_header_file, output_writer, output_filename)


class ToolsSourceFileGenerator(SourceFileGenerator):
  """Class that generates the tools source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates tools source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    tools_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.tools_name)

    library_header = u'yaltools_{0:s}.h'.format(
        project_configuration.library_name)

    if not os.path.exists(tools_path):
      return

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')

    # TODO: add support for ouput.[ch]

    for directory_entry in os.listdir(self._template_directory):
      # Ignore yaltools_library.h in favor of yaltools_libyal.h
      if directory_entry == library_header:
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == u'yaltools_libyal.h':
        output_filename = u'{0:s}tools_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      output_filename = u'{0:s}_{1:s}'.format(
          project_configuration.tools_name, directory_entry[9:])
      output_filename = os.path.join(
          project_configuration.tools_name, output_filename)

      if not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, output_directory):
    """Initialize the output writer.

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
  """Class that defines a stdout output writer."""

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
    print(u'-' * 80)
    print(u'{0: ^80}'.format(file_path))
    print(u'-' * 80)
    print(u'')
    print(file_data, end=u'')


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates source files of the libyal libraries.'))

  argument_parser.add_argument(
      u'configuration_file', action=u'store', metavar=u'CONFIGURATION_FILE',
      default='source.conf', help=u'The source generation configuration file.')

  argument_parser.add_argument(
      u'-e', u'--experimental', dest=u'experimental', action=u'store_true',
      default=False, help=u'enable experimental functionality.')

  argument_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  argument_parser.add_argument(
      u'-p', u'--projects', dest=u'projects_directory', action=u'store',
      metavar=u'PROJECTS_DIRECTORY', default=None,
      help=u'path of the projects.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print(u'Config file missing.')
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

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_directory = options.projects_directory
  if not projects_directory:
    projects_directory = os.path.dirname(libyal_directory)

  # TODO: generate more source files.
  # configure.ac
  # include headers
  # yal.net files

  source_files = [
      (u'common', CommonSourceFileGenerator),
      (u'config', ConfigurationFileGenerator),
      (u'libyal', LibrarySourceFileGenerator),
      (u'pyyal', PythonModuleSourceFileGenerator),
      (u'scripts', ScriptFileGenerator),
      (u'tests', TestsSourceFileGenerator),
      (u'yaltools', ToolsSourceFileGenerator),
  ]
  if options.experimental:
    source_files.extend([
        (u'bogus', None),
    ])

  for page_name, page_generator_class in source_files:
    template_directory = os.path.join(
        libyal_directory, u'data', u'source', page_name)
    source_file = page_generator_class(
        projects_directory, template_directory)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  source_files = [
      (u'libyal.3', LibraryManPageGenerator),
  ]

  for page_name, page_generator_class in source_files:
    template_directory = os.path.join(
        libyal_directory, u'data', u'source', u'manuals', page_name)
    source_file = page_generator_class(
        projects_directory, template_directory)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
