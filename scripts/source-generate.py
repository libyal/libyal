#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of the libyal libraries."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import collections
import datetime
import difflib
import glob
import logging
import os
import shutil
import stat
import string
import sys
import textwrap
import time

import configuration
import definitions
import source_formatter
import sources


class DefinitionsIncludeHeaderFile(object):
  """Definitions include header file.

  Attributes:
    enum_declarations (list[EnumDeclaration]): enumeration type declarations.
  """

  def __init__(self, path):
    """Initializes a definitions include header file.

    Args:
      path (str): path of the include header file.
    """
    super(DefinitionsIncludeHeaderFile, self).__init__()
    self._path = path

    self.definitions = []

  def Read(self, project_configuration):
    """Reads the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self.enum_declarations = []

    enum_prefix = b'enum '.format(
        project_configuration.library_name.upper())
    enum_prefix_length = len(enum_prefix)

    in_enum = False
    enum_declaration = None

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_enum:
          if line.startswith(b'};'):
            in_enum = False

            self.enum_declarations.append(enum_declaration)
            enum_declaration = None

          elif not line.startswith(b'{'):
            definition, _, value = line.partition(b'=')

            definition = definition.strip()
            definition = definition.rstrip(b',')

            value = value.strip()
            value = value.rstrip(b',')

            enum_declaration.constants[definition] = value

        if line.startswith(enum_prefix):
          in_enum = True
          enum_declaration = sources.EnumDeclaration(line[enum_prefix_length:])


class LibraryHeaderFile(object):
  """Library header file.

  Attributes:
    functions_per_name (dict[str, list[FunctionPrototype]]): function
        prototypes per name.
    have_internal_functions (bool): True if the header defines internal, non
        extern, functions.
    path (str): path of the header file.
    types (list[str]): type names.
  """

  def __init__(self, path):
    """Initializes a library header file.

    Args:
      path (str): path of the header file.
    """
    super(LibraryHeaderFile, self).__init__()
    self._library_name = None
    self.functions_per_name = collections.OrderedDict()
    self.have_internal_functions = False
    self.path = path
    self.types = []

  def GetTypeFunction(self, type_name, type_function):
    """Retrieves the function prototype of a specific type function.

    Args:
      type_name (str): type name.
      type_function (str): type function.

    Returns:
      FunctionPrototype: function prototype of the type function or None
          if no such function.
    """
    function_name = '{0:s}_{1:s}_{2:s}'.format(
        self._library_name, type_name, type_function)
    return self.functions_per_name.get(function_name, None)

  def Read(self, project_configuration):
    """Reads the header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    self.functions_per_name = collections.OrderedDict()
    self.types = []

    define_extern = b'{0:s}_EXTERN'.format(self._library_name.upper())

    define_have_debug_output = b'#if defined( HAVE_DEBUG_OUTPUT )'

    define_have_wide_character_type = (
        b'#if defined( HAVE_WIDE_CHARACTER_TYPE )')

    function_argument = None
    function_prototype = None
    have_extern = False
    have_debug_output = False
    have_wide_character_type = False
    in_function_prototype = False

    # TODO: use .h.in or run configure?
    if not os.path.exists(self.path):
      raise IOError('Missing include header file: {0:s}'.format(self.path))

    with open(self.path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_function_prototype:
          line = line.decode('ascii')

          # Check if we have a callback function argument.
          if line.endswith('('):
            argument_string = '{0:s} '.format(line)
            function_argument = sources.FunctionArgument(argument_string)

          else:
            if line.endswith(' );'):
              argument_string = line[:-3]

            else:
              # Get the part of the line before the ','.
              argument_string, _, _ = line.partition(',')

            if not function_argument:
              function_prototype.AddArgumentString(argument_string)

            else:
              function_argument.AddArgumentString(argument_string)

          if function_argument and line.endswith(' ),'):
            function_prototype.AddArgument(function_argument)
            function_argument = None

          elif line.endswith(' );'):
            self.functions_per_name[function_prototype.name] = (
                function_prototype)

            function_prototype = None
            in_function_prototype = False
            have_extern = False

        elif line.endswith(b'('):
          # Get the part of the line before the library name.
          data_type, _, _ = line.partition(self._library_name)

          # Get the part of the line after the data type.
          line = line[len(data_type):]
          data_type = data_type.strip()

          # Get the part of the remainder of the line before the '('.
          name, _, _ = line.partition('(')

          function_prototype = sources.FunctionPrototype(name, data_type)
          function_prototype.have_extern = have_extern
          function_prototype.have_debug_output = have_debug_output
          function_prototype.have_wide_character_type = (
              have_wide_character_type)

          if not have_extern:
            self.have_internal_functions = True

          in_function_prototype = True

        elif line.startswith(define_extern):
          have_extern = True

        elif line.startswith(define_have_debug_output):
          have_debug_output = True

        elif line.startswith(define_have_wide_character_type):
          have_wide_character_type = True

        elif line.startswith(b'#endif'):
          have_debug_output = False
          have_wide_character_type = False

        elif line.startswith(b'typedef struct '):
          type_name = line.split(b' ')[2]
          self.types.append(type_name)

    self.types = sorted(self.types)


class LibraryIncludeHeaderFile(object):
  """Library include header file.

  Attributes:
    functions_per_name (dict[str, list[FunctionPrototype]]): function
        prototypes per name.
    functions_per_section (dict[str, list[FunctionPrototype]]): function
        prototypes per section.
    have_bfio (bool): True if the include header supports libbfio.
    have_wide_character_type (bool): True if the include header supports
        the wide character type.
    name (str): name.
    section_names (list[str]): section names.
  """

  _SIGNATURE_TYPES = ('container', 'file', 'handle', 'store', 'volume')

  def __init__(self, path):
    """Initializes a library include header file.

    Args:
      path (str): path library include header file.
    """
    super(LibraryIncludeHeaderFile, self).__init__()
    self._api_functions_group = {}
    self._api_functions_with_input_group = {}
    self._api_pseudo_types_group = {}
    self._api_types_group = {}
    self._api_types_with_input_group = {}
    self._check_signature_type = None
    self._library_name = None
    self._path = path

    self.functions_per_name = collections.OrderedDict()
    self.functions_per_section = {}
    self.have_bfio = False
    self.have_wide_character_type = False
    self.name = os.path.basename(path)
    self.section_names = []

  def _AnalyzeFunctionGroups(self):
    """Analyzes the library include header file for function groups."""
    self._api_functions_group = {}
    self._api_functions_with_input_group = {}
    self._api_types_group = {}
    self._api_types_with_input_group = {}

    for section_name, functions in self.functions_per_section.items():
      if not functions:
        continue

      group_name = section_name.replace(' ', '_')
      group_name = group_name.replace('-', '_')
      group_name = group_name.lower()
      group_name, _, _ = group_name.rpartition('_functions')

      function_name_prefix = '{0:s}_{1:s}_'.format(
          self._library_name, group_name)

      found_match = False
      for function_prototype in functions:
        if function_prototype.name.startswith(function_name_prefix):
          found_match = True
          break

      # Ignore the section header if it is just informative.
      if not found_match:
        if group_name == 'support':
          signature_type = self.GetCheckSignatureType()
          if signature_type:
            self._api_functions_with_input_group[group_name] = section_name
          else:
            self._api_functions_group[group_name] = section_name

        else:
          # TODO: improve pseudo type detection.
          if group_name.endswith('_item'):
            group_name = group_name[:-5]

          self._api_pseudo_types_group[group_name] = section_name

      elif self._library_name != 'libcerror' and group_name == 'error':
        self._api_functions_group[group_name] = section_name

      elif (not self.HasTypeFunction(group_name, 'create') and
            not self.HasTypeFunction(group_name, 'free')):
        self._api_functions_group[group_name] = section_name

      elif not self.HasTypeFunction(group_name, 'open'):
        self._api_types_group[group_name] = section_name

      else:
        self._api_types_with_input_group[group_name] = section_name

  def GetAPIFunctionTestGroups(self):
    """Determines the API function test groups.

    Returns:
      tuple: contains:
        list[str]: names of API function groups without test data.
        list[str]: names of API function groups with test data.
    """
    if (not self._api_functions_group and
        not self._api_functions_with_input_group):
      self._AnalyzeFunctionGroups()

    return (
        self._api_functions_group.keys(),
        self._api_functions_with_input_group.keys())

  def GetAPIPseudoTypeTestGroups(self):
    """Determines the API pseudo type test groups.

    Returns:
      list[str]: names of API pseudo type groups without test data.
    """
    if not self._api_types_group and not self._api_types_with_input_group:
      self._AnalyzeFunctionGroups()

    return self._api_pseudo_types_group.keys()

  def GetAPITypeTestGroups(self):
    """Determines the API type test groups.

    Returns:
      tuple: contains:
        list[str]: names of API type groups without test data.
        list[str]: names of API type groups with test data.
    """
    if not self._api_types_group and not self._api_types_with_input_group:
      self._AnalyzeFunctionGroups()

    return self._api_types_group.keys(), self._api_types_with_input_group.keys()

  def GetCheckSignatureType(self):
    """Determines the check signature function type.

    Returns:
      str: check signature function type of None if no check signature function
          was found.
    """
    if not self._check_signature_type:
      for signature_type in self._SIGNATURE_TYPES:
        function_name = '{0:s}_check_{1:s}_signature'.format(
            self._library_name, signature_type)

        if function_name in self.functions_per_name:
          self._check_signature_type = signature_type
          break

    return self._check_signature_type

  def GetFunctionGroup(self, group_name):
    """Retrieves a function group.

    Args:
      group_name (str): group name.

    Returns:
      list[FunctionPrototype]: function prototypes of the functions in
          the group.
    """
    section_name = self._api_functions_group.get(group_name, None)
    if not section_name:
      section_name = self._api_functions_with_input_group.get(group_name, None)
    if not section_name:
      section_name = self._api_types_group.get(group_name, None)
    if not section_name:
      section_name = self._api_types_with_input_group.get(group_name, None)
    if not section_name:
      return []

    return self.functions_per_section.get(section_name, [])

  def HasErrorArgument(self, group_name):
    """Determines if a function group has functions with an error argument.

    Args:
      group_name (str): group name.

    Returns:
      bool: True if there ar functions with an error argument defined,
          False otherwise.
    """
    error_type = '{0:s}_error_t '.format(self._library_name)

    functions = self.GetFunctionGroup(group_name)
    for function_prototype in functions:
      if not function_prototype.arguments:
        continue

      function_argument = function_prototype.arguments[-1]
      function_argument_string = function_argument.CopyToString()
      if function_argument_string.startswith(error_type):
        return True

    return False

  def HasFunction(self, function_name):
    """Determines if the include header defines a specific function.

    Args:
      function_name (str): function name.

    Returns:
      bool: True if function is defined, False otherwise.
    """
    function_name = '{0:s}_{1:s}'.format(self._library_name, function_name)
    return function_name in self.functions_per_name

  def HasTypeFunction(self, type_name, type_function):
    """Determines if the include header defines a specific type function.

    Args:
      type_name (str): type name.
      type_function (str): type function.

    Returns:
      bool: True if function is defined, False otherwise.
    """
    function_name = '{0:s}_{1:s}_{2:s}'.format(
        self._library_name, type_name, type_function)
    return function_name in self.functions_per_name

  def Read(self, project_configuration):
    """Reads the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    self.functions_per_name = collections.OrderedDict()
    self.functions_per_section = {}
    self.have_bfio = False
    self.have_wide_character_type = False
    self.section_names = []

    define_deprecated = b'{0:s}_DEPRECATED'.format(self._library_name.upper())

    define_extern = b'{0:s}_EXTERN'.format(self._library_name.upper())

    define_have_bfio = b'#if defined( {0:s}_HAVE_BFIO )'.format(
        self._library_name.upper())

    define_have_debug_output = b'#if defined( HAVE_DEBUG_OUTPUT )'

    define_have_wide_character_type = (
        b'#if defined( {0:s}_HAVE_WIDE_CHARACTER_TYPE )').format(
            self._library_name.upper())

    function_argument = None
    function_prototype = None
    have_bfio = False
    have_extern = False
    have_debug_output = False
    have_wide_character_type = False
    in_define_deprecated = False
    in_section = False
    section_name = None

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if have_extern:
          line = line.decode('ascii')

          if function_prototype:
            # Check if we have a callback function argument.
            if line.endswith('('):
              argument_string = '{0:s} '.format(line)
              function_argument = sources.FunctionArgument(argument_string)

            else:
              if line.endswith(' );'):
                argument_string = line[:-3]

              else:
                # Get the part of the line before the ','.
                argument_string, _, _ = line.partition(',')

              if not function_argument:
                function_prototype.AddArgumentString(argument_string)

              else:
                function_argument.AddArgumentString(argument_string)

            if function_argument and line.endswith(' ),'):
              function_prototype.AddArgument(function_argument)
              function_argument = None

            elif line.endswith(' );'):
              if not in_define_deprecated:
                # TODO: handle section_name is None
                self.functions_per_name[function_prototype.name] = (
                    function_prototype)

                self.functions_per_section[section_name].append(
                    function_prototype)

              function_prototype = None
              in_define_deprecated = False
              have_extern = False

          elif line.endswith(';'):
            # The line contains a variable definition.
            have_extern = False

          else:
            # Get the part of the line before the library name.
            data_type, _, _ = line.partition(self._library_name)

            # Get the part of the line after the data type.
            line = line[len(data_type):]
            data_type = data_type.strip()

            # Get the part of the remainder of the line before the '('.
            name, _, _ = line.partition('(')

            function_prototype = sources.FunctionPrototype(name, data_type)
            function_prototype.have_bfio = have_bfio
            function_prototype.have_extern = have_extern
            function_prototype.have_debug_output = have_debug_output
            function_prototype.have_wide_character_type = (
                have_wide_character_type)

            if have_bfio:
              self.have_bfio = True
            if have_wide_character_type:
              self.have_wide_character_type = True

        elif in_section:
          if line.startswith(b'* '):
            section_name = line[2:]
            self.section_names.append(section_name)
            self.functions_per_section[section_name] = []
            in_section = False

        elif line == (
            b'/* -------------------------------------------------------------'
            b'------------'):
          in_section = True

        elif line.startswith(define_deprecated):
          in_define_deprecated = True

        elif line.startswith(define_have_bfio):
          have_bfio = True

        elif line.startswith(define_extern):
          have_extern = True

        elif line.startswith(define_have_debug_output):
          have_debug_output = True

        elif line.startswith(define_have_wide_character_type):
          have_wide_character_type = True

        elif line.startswith(b'#endif'):
          have_bfio = False
          have_debug_output = False
          have_wide_character_type = False


class LibraryMakefileAMFile(object):
  """Library Makefile.am file.

  Attributes:
    cppflags (list[str]): C preprocess flags.
    libraries (list[str]): library names.
    sources (list[str]): source and header file paths.
  """

  def __init__(self, path):
    """Initializes a library Makefile.am file.

    Args:
      path (str): path of the Makefile.am file.
    """
    super(LibraryMakefileAMFile, self).__init__()
    self._library_name = None
    self._path = path
    self.cppflags = []
    self.libraries = []
    self.sources = []

  def Read(self, project_configuration):
    """Reads the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    self.cppflags = []
    self.libraries = []
    self.sources = []

    library_sources = b'{0:s}_la_SOURCES'.format(self._library_name)
    library_libadd = b'{0:s}_la_LIBADD'.format(self._library_name)

    in_section = None

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_section:
          if not line:
            in_section = None
            continue

          if line.endswith(b'\\'):
            line = line[:-1].strip()

          if (in_section == 'cppflags' and line.startswith(b'@') and
              line.endswith(b'_CPPFLAGS@')):
            self.cppflags.append(line[1:-10].lower())

          elif (in_section == 'libadd' and line.startswith(b'@') and
                line.endswith(b'_LIBADD@')):
            self.libraries.append(line[1:-8].lower())

          elif in_section == 'sources':
            sources = line.split(b' ')
            self.sources.extend(sources)

        elif line == b'AM_CPPFLAGS = \\':
          in_section = 'cppflags'

        elif line.startswith(library_libadd):
          in_section = 'libadd'

        elif line.startswith(library_sources):
          in_section = 'sources'


class MainMakefileAMFile(object):
  """Main Makefile.am file.

  Attributes:
    libraries (list[str]): library names.
    library_dependencies (list[str]): names of the dependencies of the main
        library.
    tools_dependencies (list[str]): names of the dependencies of the tools.
  """

  def __init__(self, path):
    """Initializes a main Makefile.am file.

    Args:
      path (str): path of the Makefile.am file.
    """
    super(MainMakefileAMFile, self).__init__()
    self._library_name = None
    self._path = path
    self.libraries = []
    self.library_dependencies = []
    self.tools_dependencies = []

  def Read(self, project_configuration):
    """Reads the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    in_subdirs = False
    in_library_dependencies = True

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_subdirs:
          if line.endswith(b'\\'):
            line = line[:-1].strip()

          if not line:
            in_subdirs = False

          elif line.startswith(b'lib'):
            if line == self._library_name:
              in_library_dependencies = False
            else:
              self.libraries.append(line)

              if in_library_dependencies:
                self.library_dependencies.append(line)
              else:
                self.tools_dependencies.append(line)

        elif line.startswith(b'SUBDIRS'):
          in_subdirs = True


class TypesIncludeHeaderFile(object):
  """Types include header file.

  Attributes:
    types (list[str]): type names.
  """

  def __init__(self, path):
    """Initializes a types include header file.

    Args:
      path (str): path of the include header file.
    """
    super(TypesIncludeHeaderFile, self).__init__()
    self._library_name = None
    self._path = path
    self.types = []

  def Read(self, project_configuration):
    """Reads the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    self.types = []

    typedef_prefix = b'typedef intptr_t {0:s}_'.format(self._library_name)
    typedef_prefix_length = len(typedef_prefix)

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(typedef_prefix) and line.endswith(b'_t;'):
          self.types.append(line[typedef_prefix_length:-3])


class SourceFileGenerator(object):
  """Source files generator."""

  def __init__(
      self, projects_directory, template_directory, experimental=False):
    """Initialize a source file generator.

    Args:
      projects_directory (str): path of the projects directory.
      template_directory (str): path of the template directory.
      experimental (bool): True if experimental features should be enabled.
    """
    super(SourceFileGenerator, self).__init__()
    self._definitions_include_header_file = None
    self._definitions_include_header_path = None
    self._experimental = experimental
    self._has_tests = None
    self._library_include_header_file = None
    self._library_include_header_path = None
    self._library_makefile_am_file = None
    self._library_makefile_am_path = None
    self._library_path = None
    self._projects_directory = projects_directory
    self._python_module_path = None
    self._template_directory = template_directory
    self._tests_path = None
    self._tools_path = None
    self._types_include_header_file = None
    self._types_include_header_path = None

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
    except (KeyError, ValueError) as exception:
      logging.error(
          'Unable to format template: {0:s} with error: {1:s}'.format(
              template_filename, exception))
      return

    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)

  def _GetDefinitionsIncludeHeaderFile(self, project_configuration):
    """Retrieves the definitions include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      DefinitionsIncludeHeaderFile: definitions include header file or None if
          the definitions include header file cannot be found.
    """
    if not self._definitions_include_header_file:
      self._definitions_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', project_configuration.library_name, 'definitions.h.in')

      if os.path.exists(self._definitions_include_header_path):
        self._definitions_include_header_file = DefinitionsIncludeHeaderFile(
            self._definitions_include_header_path)
        self._definitions_include_header_file.Read(project_configuration)

    return self._definitions_include_header_file

  def _GetLibraryIncludeHeaderFile(self, project_configuration):
    """Retrieves the library include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      LibraryIncludeHeaderFile: library include header file or None if
          the library include header file cannot be found.
    """
    if not self._library_include_header_file:
      self._library_include_header_path = '{0:s}.h.in'.format(
          project_configuration.library_name)
      self._library_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', self._library_include_header_path)

      if os.path.exists(self._library_include_header_path):
        self._library_include_header_file = LibraryIncludeHeaderFile(
            self._library_include_header_path)
        self._library_include_header_file.Read(project_configuration)

    return self._library_include_header_file

  def _GetLibraryMakefileAM(self, project_configuration):
    """Retrieves the library Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      LibraryMakefileAMFile: library Makefile.am file or None if
          the library Makefile.am file cannot be found.
    """
    if not self._library_makefile_am_file:
      self._library_makefile_am_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          project_configuration.library_name, 'Makefile.am')

      if os.path.exists(self._library_makefile_am_path):
        self._library_makefile_am_file = LibraryMakefileAMFile(
            self._library_makefile_am_path)
        self._library_makefile_am_file.Read(project_configuration)

    return self._library_makefile_am_file

  def _GetMainMakefileAM(self, project_configuration):
    """Retrieves the main Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      MainMakefileAMFile: main Makefile.am file or None if the main
          Makefile.am file cannot be found.
    """
    # TODO: cache MainMakefileAMFile object and makefile_am_path
    makefile_am_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        'Makefile.am')

    makefile_am_file = MainMakefileAMFile(makefile_am_path)
    makefile_am_file.Read(project_configuration)

    return makefile_am_file

  def _GetTemplateMappings(self, project_configuration, authors_separator=', '):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      authors_separator (Optional[str]): authors separator.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.

    Raises:
      ValueError: if the year of creation value is out of bounds.
    """
    date = datetime.date.today()
    if project_configuration.project_year_of_creation > date.year:
      raise ValueError('Year of creation value out of bounds.')

    if project_configuration.project_year_of_creation == date.year:
      project_copyright = '{0:d}'.format(
          project_configuration.project_year_of_creation)
    else:
      project_copyright = '{0:d}-{1:d}'.format(
          project_configuration.project_year_of_creation, date.year)

    if project_configuration.python_module_year_of_creation == date.year:
      python_module_copyright = '{0:d}'.format(
          project_configuration.python_module_year_of_creation)
    else:
      python_module_copyright = '{0:d}-{1:d}'.format(
          project_configuration.python_module_year_of_creation, date.year)

    authors = authors_separator.join(project_configuration.project_authors)
    python_module_authors = authors_separator.join(
        project_configuration.python_module_authors)
    tools_authors = authors_separator.join(project_configuration.tools_authors)
    tests_authors = authors_separator.join(project_configuration.tests_authors)

    library_description_lower_case = '{0:s}{1:s}'.format(
        project_configuration.library_description[0].lower(),
        project_configuration.library_description[1:])

    library_version = time.strftime('%Y%m%d', time.gmtime())

    template_mappings = {
        'authors': authors,
        'copyright': project_copyright,

        'library_name': project_configuration.library_name,
        'library_name_upper_case': project_configuration.library_name.upper(),
        'library_name_suffix': project_configuration.library_name_suffix,
        'library_name_suffix_upper_case': (
            project_configuration.library_name_suffix.upper()),
        'library_description': project_configuration.library_description,
        'library_description_lower_case': library_description_lower_case,
        'library_version': library_version,

        'python_module_authors': python_module_authors,
        'python_module_name': project_configuration.python_module_name,
        'python_module_name_upper_case': (
            project_configuration.python_module_name.upper()),
        'python_module_copyright': python_module_copyright,

        'tools_authors': tools_authors,
        'tools_name': project_configuration.tools_directory,
        'tools_name_upper_case': project_configuration.tools_directory.upper(),
        'tools_description': project_configuration.tools_description,

        'tests_authors': tests_authors,
    }
    return template_mappings

  def _GetTypeLibraryHeaderFile(self, project_configuration, type_name):
    """Retrieves a type specific library include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of the type.

    Returns:
      LibraryHeaderFile: library header file or None if the library header file
          cannot be found.
    """
    if not self._library_path:
      self._library_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          project_configuration.library_name)

    # TODO: cache header files.
    header_file_path = '{0:s}_{1:s}.h'.format(
        project_configuration.library_name, type_name)
    header_file_path = os.path.join(self._library_path, header_file_path)
    header_file = LibraryHeaderFile(header_file_path)

    return header_file

  def _GetTypesIncludeHeaderFile(self, project_configuration):
    """Retrieves the types include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      TypesIncludeHeaderFile: types include header file or None if
          the types include header file cannot be found.
    """
    if not self._types_include_header_file:
      self._types_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', project_configuration.library_name, 'types.h.in')

      if os.path.exists(self._types_include_header_path):
        self._types_include_header_file = TypesIncludeHeaderFile(
            self._types_include_header_path)
        self._types_include_header_file.Read(project_configuration)

    return self._types_include_header_file

  def _HasTests(self, project_configuration):
    """Determines if the project has tests.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the tests path exits.
    """
    if not self._tests_path:
      self._tests_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'tests')

      self._has_tests = os.path.exists(self._tests_path)

    return self._has_tests

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

  def _SetSequenceTypeNameInTemplateMappings(
      self, template_mappings, type_name):
    """Sets the sequence type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): sequence type name.
    """
    if not type_name:
      template_mappings['sequence_type_description'] = ''
      template_mappings['sequence_type_name'] = ''
      template_mappings['sequence_type_name_camel_case'] = ''
      template_mappings['sequence_type_name_upper_case'] = ''
    else:
      template_mappings['sequence_type_description'] = type_name.replace(
          '_', ' ')
      template_mappings['sequence_type_name'] = type_name
      template_mappings['sequence_type_name_camel_case'] = ''.join([
          word.title() for word in type_name.split('_')])
      template_mappings['sequence_type_name_upper_case'] = type_name.upper()

  def _SetSequenceValueNameInTemplateMappings(
      self, template_mappings, value_name):
    """Sets the sequence value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): sequence value name.
    """
    if not value_name:
      template_mappings['sequence_value_description'] = ''
      template_mappings['sequence_value_name'] = ''
      template_mappings['sequence_value_name_upper_case'] = ''
    else:
      template_mappings['sequence_value_description'] = value_name.replace(
          '_', ' ')
      template_mappings['sequence_value_name'] = value_name
      template_mappings['sequence_value_name_upper_case'] = value_name.upper()

  def _SetTypeFunctionInTemplateMappings(
      self, template_mappings, type_function):
    """Sets the type function in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_function (str): type function.
    """
    if not type_function:
      template_mappings['type_function'] = ''
      template_mappings['type_function_upper_case'] = ''
    else:
      template_mappings['type_function'] = type_function
      template_mappings['type_function_upper_case'] = type_function.upper()

  def _SetTypeNameInTemplateMappings(self, template_mappings, type_name):
    """Sets the type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): type name.
    """
    if not type_name:
      template_mappings['type_description'] = ''
      template_mappings['type_name'] = ''
      template_mappings['type_name_camel_case'] = ''
      template_mappings['type_name_upper_case'] = ''
    else:
      template_mappings['type_description'] = type_name.replace('_', ' ')
      template_mappings['type_name'] = type_name
      template_mappings['type_name_camel_case'] = ''.join([
          word.title() for word in type_name.split('_')])
      template_mappings['type_name_upper_case'] = type_name.upper()

  def _SetValueNameInTemplateMappings(self, template_mappings, value_name):
    """Sets value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): value name.
    """
    if not value_name:
      template_mappings['value_description'] = ''
      template_mappings['value_name'] = ''
      template_mappings['value_name_upper_case'] = ''
    else:
      template_mappings['value_description'] = value_name.replace('_', ' ')
      template_mappings['value_name'] = value_name
      template_mappings['value_name_upper_case'] = value_name.upper()

  def _SetValueTypeInTemplateMappings(self, template_mappings, value_type):
    """Sets value type in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the type of a template variable.
      value_type (str): value type.
    """
    if not value_type:
      template_mappings['value_type'] = ''
      template_mappings['value_type_description'] = ''
      template_mappings['value_type_upper_case'] = ''
    else:
      template_mappings['value_type'] = value_type
      template_mappings['value_type_description'] = value_type.replace(
          '_', ' ')
      template_mappings['value_type_upper_case'] = value_type.upper()

  def _SortIncludeHeaders(self, project_configuration, output_filename):
    """Sorts the include headers within a source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

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

  def _SortVariableDeclarations(self, output_filename):
    """Sorts the variable declarations within a source file.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    formatter = source_formatter.SourceFormatter()
    variable_declarations = None
    in_variable_declarations = False

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        stripped_line = line.rstrip()
        if stripped_line == b'{':
          file_object.write(line)
          variable_declarations = []
          in_variable_declarations = True

        elif in_variable_declarations:
          if (b'(' not in stripped_line or
              stripped_line.startswith(b'#if defined(')):
            variable_declarations.append(line)

          else:
            sorted_lines = formatter.FormatSource(variable_declarations)

            file_object.writelines(sorted_lines)
            file_object.write(line)
            in_variable_declarations = False

        else:
          file_object.write(line)

    lines = formatter.FormatSource(lines)

  def _VerticalAlignAssignmentStatements(self, output_filename):
    """Vertically aligns assignment statements.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    assigment_statements = []
    in_assigment_statements_block = False

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        if b' = ' in line:
          if not in_assigment_statements_block:
            in_assigment_statements_block = True

          assigment_statements.append(line)
          continue

        if in_assigment_statements_block:
          if len(assigment_statements) == 1:
            file_object.write(assigment_statements[0])

          else:
            alignment_offset = 0
            for assigment_statement in assigment_statements:
              prefix, _, _ = assigment_statement.rpartition(b'=')
              prefix = prefix.rstrip()
              alignment_offset = max(alignment_offset, len(prefix) + 1)

            for assigment_statement in assigment_statements:
              prefix, _, suffix = assigment_statement.rpartition(b'=')
              prefix = prefix.rstrip()
              alignment_length = alignment_offset - len(prefix)

              assigment_statement_line = b'{0:s}{1:s}={2:s}'.format(
                  prefix, b' ' * alignment_length, suffix)
              file_object.write(assigment_statement_line)

          in_assigment_statements_block = False
          assigment_statements = []

        file_object.write(line)

  def _VerticalAlignTabs(self, output_filename):
    """Vertically aligns tabs.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    alignment_offset = 0
    for line in lines:
      if b'\t' not in line.lstrip(b'\t'):
        continue

      prefix, _, suffix = line.rpartition(b'\t')
      prefix = prefix.rstrip(b'\t')
      formatted_prefix = prefix.replace(b'\t', ' ' * 8)

      equal_sign_offset = len(formatted_prefix) + 8
      equal_sign_offset, _ = divmod(equal_sign_offset, 8)
      equal_sign_offset *= 8

      if alignment_offset == 0:
        alignment_offset = equal_sign_offset
      else:
        alignment_offset = max(alignment_offset, equal_sign_offset)

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        if b'\t' in line.lstrip(b'\t'):
          prefix, _, suffix = line.rpartition(b'\t')
          prefix = prefix.rstrip(b'\t')
          formatted_prefix = prefix.replace(b'\t', ' ' * 8)

          alignment_size = alignment_offset - len(formatted_prefix)
          alignment_size, remainder = divmod(alignment_size, 8)
          if remainder > 0:
            alignment_size += 1

          alignment = b'\t' * alignment_size

          line = b'{0:s}{1:s}{2:s}'.format(prefix, alignment, suffix)

        file_object.write(line)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """


class CommonSourceFileGenerator(SourceFileGenerator):
  """Common source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates common source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')
    template_mappings['authors'] = 'Joachim Metz <joachim.metz@gmail.com>'

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join('common', directory_entry)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class ConfigurationFileGenerator(SourceFileGenerator):
  """Configuration files generator."""

  def _GenerateAppVeyorYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the appveyor.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'appveyor.yml')

    template_filename = os.path.join(
        template_directory, 'environment-header.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(
          template_directory, 'environment-python.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(
        template_directory, 'environment-footer.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasDependencyDokan():
      template_filename = os.path.join(template_directory, 'install-dokan.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if (project_configuration.HasDependencyLex() or
        project_configuration.HasDependencyYacc()):
      template_filename = os.path.join(
          template_directory, 'install-winflexbison.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if 'zlib' in project_configuration.library_build_dependencies:
      template_filename = os.path.join(template_directory, 'install-zlib.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    cygwin_build_dependencies = self._GetCygwinBuildDependencies(
        project_configuration)

    if cygwin_build_dependencies:
      cygwin_build_dependencies = ' '.join([
          '-P {0:s}'.format(name) for name in cygwin_build_dependencies])
      template_mappings['cygwin_build_dependencies'] = cygwin_build_dependencies

      template_filename = os.path.join(template_directory, 'install-cygwin.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['cygwin_build_dependencies']

    mingw_msys_build_dependencies = self._GetMinGWMSYSBuildDependencies(
        project_configuration)

    if mingw_msys_build_dependencies:
      mingw_msys_build_dependencies = ' '.join(mingw_msys_build_dependencies)
      template_mappings['mingw_msys_build_dependencies'] = (
          mingw_msys_build_dependencies)

      template_filename = os.path.join(
          template_directory, 'install-mingw-msys.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['mingw_msys_build_dependencies']

    template_filename = os.path.join(
        template_directory, 'build_script-header.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: make this configuration driven
    if project_configuration.library_name == 'libevt':
      template_filename = os.path.join(
          template_directory, 'build_script-vs2017-nuget.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')
    else:
      template_filename = os.path.join(
          template_directory, 'build_script-vs2017.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(
          template_directory, 'build_script-python.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(
        template_directory, 'build_script-footer.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'test_script.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'after_test.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: make this configuration driven
    if project_configuration.library_name == 'libevt':
      template_filename = os.path.join(template_directory, 'deploy.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

  def _GenerateCodecovYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .codecov.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, '.codecov.yml')

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    ignore_paths = list(makefile_am_file.libraries)
    ignore_paths.append('tests')

    template_mappings['codecov_ignore'] = '\n'.join([
        '    - "{0:s}/*"'.format(path) for path in sorted(ignore_paths)])

    template_filename = os.path.join(
        template_directory, 'body.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['codecov_ignore']

  def _GenerateConfigureAC(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the configure.ac configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    # TODO: change indentation of templates.

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    libraries = list(makefile_am_file.libraries)
    library_dependencies = list(makefile_am_file.library_dependencies)

    libcrypto_index = len(library_dependencies)
    if 'libcaes' in library_dependencies:
      libcrypto_index = min(
          libcrypto_index, library_dependencies.index('libcaes'))

    if 'libhmac' in library_dependencies:
      libcrypto_index = min(
          libcrypto_index, library_dependencies.index('libhmac'))

    if 'crypto' in project_configuration.library_build_dependencies:
      if libcrypto_index == len(library_dependencies):
        libraries.append('libcrypto')
        library_dependencies.append('libcrypto')

    if 'sgutils' in project_configuration.library_build_dependencies:
      libraries.append('sgutils2')
      library_dependencies.append('sgutils2')

    # Have zlib checked before libcrypto.
    if 'zlib' in project_configuration.library_build_dependencies:
      if libcrypto_index < len(library_dependencies):
        libraries.insert(libcrypto_index, 'zlib')
        library_dependencies.insert(libcrypto_index, 'zlib')
      else:
        libraries.append('zlib')
        library_dependencies.append('zlib')

    template_directory = os.path.join(self._template_directory, 'configure.ac')

    template_filename = os.path.join(template_directory, 'header.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'programs.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'compiler_language.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'build_features.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if (include_header_file and include_header_file.have_wide_character_type or
        project_configuration.HasTools()):
      template_filename = os.path.join(
          template_directory, 'check_wide_character_support.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(
        template_directory, 'check_types_support.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(
        template_directory, 'check_common_support.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if library_dependencies:
      for name in library_dependencies:
        template_mappings['local_library_name'] = name
        template_mappings['local_library_name_upper_case'] = name.upper()

        template_filename = os.path.join(
            template_directory, 'check_dependency_support.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      # TODO: add additional zlib checks

      del template_mappings['local_library_name']
      del template_mappings['local_library_name_upper_case']

    template_filename = os.path.join( template_directory, 'check_library_support.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(
          template_directory, 'check_python_support.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasJavaBindings():
      template_filename = os.path.join(
          template_directory, 'check_java_support.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasTools():
      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      if tools_dependencies:
        for name in tools_dependencies:
          template_mappings['local_library_name'] = name
          template_mappings['local_library_name_upper_case'] = name.upper()

          template_filename = os.path.join(
              template_directory, 'check_dependency_support.ac')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

        del template_mappings['local_library_name']
        del template_mappings['local_library_name_upper_case']

      template_filename = os.path.join(
          template_directory, 'check_tools_support.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

    if project_configuration.HasDebugOutput():
      template_filename = os.path.join(
          template_directory, 'check_debug_output.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join( template_directory, 'check_tests_support.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'dll_support.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'compiler_flags.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if library_dependencies:
      local_library_tests = []
      for name in library_dependencies:
        if name in makefile_am_file.library_dependencies:
          local_library_test = 'test "x$ac_cv_{0:s}" = xyes'.format(name)
        else:
          local_library_test = 'test "x$ac_cv_{0:s}" != xno'.format(name)

        local_library_tests.append(local_library_test)

      if 'libcaes' in library_dependencies or 'libhmac' in library_dependencies:
        local_library_tests.append('test "x$ac_cv_libcrypto" != xno')

      template_mappings['local_library_tests'] = ' || '.join(
          local_library_tests)

      template_filename = os.path.join(
          template_directory, 'spec_requires_library.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['local_library_tests']

    if project_configuration.HasTools():
      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      if tools_dependencies:
        local_library_tests = []
        for name in tools_dependencies:
          if name == 'libfuse':
            local_library_test = 'test "x$ac_cv_{0:s}" != xno'.format(name)
          else:
            local_library_test = 'test "x$ac_cv_{0:s}" = xyes'.format(name)

          local_library_tests.append(local_library_test)

        template_mappings['local_library_tests'] = ' || '.join(
            local_library_tests)

        template_filename = os.path.join(
            template_directory, 'spec_requires_tools.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

        del template_mappings['local_library_tests']

    template_filename = os.path.join(template_directory, 'dates.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(
        template_directory, 'config_files_start.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if makefile_am_file.library_dependencies:
      for name in makefile_am_file.library_dependencies:
        template_mappings['local_library_name'] = name

        template_filename = os.path.join(
            template_directory, 'config_files_dependency.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      del template_mappings['local_library_name']

    template_filename = os.path.join(
        template_directory, 'config_files_library.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(
          template_directory, 'config_files_python.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasDotNetBindings():
      template_filename = os.path.join(
          template_directory, 'config_files_dotnet.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasJavaBindings():
      template_filename = os.path.join(
          template_directory, 'config_files_java.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasTools():
      if makefile_am_file.tools_dependencies:
        for name in makefile_am_file.tools_dependencies:
          template_mappings['local_library_name'] = name

          template_filename = os.path.join(
              template_directory, 'config_files_dependency.ac')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

        del template_mappings['local_library_name']

      template_filename = os.path.join(
          template_directory, 'config_files_tools.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

    # TODO: add support for Makefile in documents (libuna)

    template_filename = os.path.join(
        template_directory, 'config_files_common.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasDotNetBindings():
      template_filename = os.path.join(
          template_directory, 'config_files_dotnet_rc.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'config_files_end.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    maximum_description_length = 0

    build_information = []
    for name in libraries:
      if name not in ('libcrypto', 'zlib'):
        description = '{0:s} support'.format(name)
        value = '$ac_cv_{0:s}'.format(name)
        build_information.append((description, value))

        maximum_description_length = max(
            maximum_description_length, len(description))

      if name == 'libcaes':
        description = 'AES support'
        build_information.append((description, '$ac_cv_libcaes_aes'))

        maximum_description_length = max(
            maximum_description_length, len(description))

      elif name == 'libhmac':
        description = 'SHA256 support'
        build_information.append((description, '$ac_cv_libhmac_sha256'))

        maximum_description_length = max(
            maximum_description_length, len(description))

      elif name == 'zlib':
        description = 'DEFLATE compression support'
        build_information.append((description, '$ac_cv_inflate'))

        maximum_description_length = max(
            maximum_description_length, len(description))

    if 'fuse' in project_configuration.tools_build_dependencies:
      description = 'FUSE support'
      build_information.append((description, '$ac_cv_libfuse'))

      maximum_description_length = max(
          maximum_description_length, len(description))

    features_information = []
    if (project_configuration.library_name == 'libcthreads' or
        'libcthreads' in makefile_am_file.libraries):
      description = 'Multi-threading support'
      value = '$ac_cv_libcthreads_multi_threading'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if (include_header_file and include_header_file.have_wide_character_type or
        project_configuration.HasTools()):
      description = 'Wide character type support'
      value = '$ac_cv_enable_wide_character_type'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasTools():
      description = '{0:s} are build as static executables'.format(
          project_configuration.tools_directory)
      value = '$ac_cv_enable_static_executables'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasPythonModule():
      description = 'Python ({0:s}) support'.format(
          project_configuration.python_module_name)
      value = '$ac_cv_enable_python'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

      description = 'Python version 2 ({0:s}) support'.format(
          project_configuration.python_module_name)
      value = '$ac_cv_enable_python2'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

      description = 'Python version 3 ({0:s}) support'.format(
          project_configuration.python_module_name)
      value = '$ac_cv_enable_python3'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasDebugOutput():
      description = 'Verbose output'
      value = '$ac_cv_enable_verbose_output'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

      description = 'Debug output'
      value = '$ac_cv_enable_debug_output'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    notice_message = []

    if build_information:
      notice_message.append('Building:')

      for description, value in build_information:
        padding_length = maximum_description_length - len(description)
        padding = ' ' * padding_length

        notice_line = '   {0:s}: {1:s}{2:s}'.format(description, padding, value)
        notice_message.append(notice_line)

      notice_message.append('')

    if features_information:
      notice_message.append('Features:')

      for description, value in features_information:
        padding_length = maximum_description_length - len(description)
        padding = ' ' * padding_length

        notice_line = '   {0:s}: {1:s}{2:s}'.format(description, padding, value)
        notice_message.append(notice_line)

    template_mappings['notice_message'] = '\n'.join(notice_message)

    template_filename = os.path.join(template_directory, 'footer.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['notice_message']

  def _GenerateDpkg(
      self, project_configuration, template_mappings, output_writer,
      output_directory):
    """Generates the dpkg packaging files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_directory (str): path of the output directory.
    """
    # TODO: add support for projects without Python bindings.
    # TODO: fix lintian issues.

    template_directory = os.path.join(self._template_directory, 'dpkg')

    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if (directory_entry.startswith('control') or
          directory_entry.startswith('rules')):
        continue

      if directory_entry.endswith('.install'):
        if (not project_configuration.HasPythonModule() and
            '-python' in directory_entry):
          continue

        if (not project_configuration.HasTools() and
            '-tools' in directory_entry):
          continue

      output_filename = directory_entry
      if output_filename.startswith('libyal'):
        output_filename = '{0:s}{1:s}'.format(
            project_configuration.library_name, output_filename[6:])

      output_filename = os.path.join(output_directory, output_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    dpkg_build_dependencies = self._GetDpkgBuildDependenciesDpkgControl(
        project_configuration)

    template_mappings['dpkg_build_dependencies'] = ', '.join(dpkg_build_dependencies)

    template_filename = os.path.join(template_directory, 'control')
    output_filename = os.path.join(output_directory, 'control')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if project_configuration.HasTools():
      template_filename = os.path.join(template_directory, 'control-tools')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'control-python')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if (project_configuration.HasPythonModule() and
        project_configuration.HasTools()):
      template_filename = 'rules-with-python-and-tools'
    elif project_configuration.HasPythonModule():
      template_filename = 'rules-with-python'
    elif project_configuration.HasTools():
      template_filename = 'rules-with-tools'
    else:
      template_filename = 'rules'

    template_filename = os.path.join(template_directory, template_filename)
    output_filename = os.path.join(output_directory, 'rules')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'dpkg', 'source')
    output_directory = os.path.join(output_directory, 'source')

    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

  def _GenerateGitignore(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .gitignore configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    template_directory = os.path.join(self._template_directory, '.gitignore')

    template_filename = os.path.join(template_directory, 'header')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'library')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: add support for lex yacc BUILT_SOURCES

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'python_module')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasDotNetBindings():
      template_filename = os.path.join(template_directory, 'dotnet_bindings')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasJavaBindings():
      template_filename = os.path.join(template_directory, 'java_bindings')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasTools():
      tools_executables = []
      for name in sorted(project_configuration.tools_names):
        tools_executable = '/{0:s}/{1:s}'.format(
            project_configuration.tools_directory, name)
        tools_executables.append(tools_executable)

      template_mappings['tools_executables'] = '\n'.join(tools_executables)

      template_filename = os.path.join(template_directory, 'tools')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['tools_executables']

    source_glob = '{0:s}_test_*.c'.format(
        project_configuration.library_name_suffix)
    source_glob = os.path.join('tests', source_glob)

    tests_files = ['/tests/tmp*']
    if os.path.exists(os.path.join('tests', 'input')):
      tests_files.append('/tests/input')

    for source_file in sorted(glob.glob(source_glob)):
      if (source_file.endswith('_functions.c') or
          source_file.endswith('_getopt.c') or
          source_file.endswith('_memory.c')):
        continue

      source_file = '/{0:s}'.format(source_file[:-2])
      tests_files.append(source_file)

    template_mappings['tests_files'] = '\n'.join(sorted(tests_files))

    template_filename = os.path.join(template_directory, 'tests')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['tests_files']

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    libraries = [
        '/{0:s}'.format(name) for name in sorted(makefile_am_file.libraries)]

    if libraries:
      template_mappings['local_libraries'] = '\n'.join(libraries)

      template_filename = os.path.join(template_directory, 'local_libraries')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['local_libraries']

  def _GenerateRpmSpec(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the RPM spec file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_directory = os.path.join(
        self._template_directory, 'libyal.spec.in')

    template_filename = os.path.join(template_directory, 'header.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    library_dependencies = list(makefile_am_file.library_dependencies)

    if 'crypto' in project_configuration.library_build_dependencies:
      library_dependencies.append('libcrypto')
    if 'zlib' in project_configuration.library_build_dependencies:
      library_dependencies.append('zlib')

    if library_dependencies:
      spec_requires = []
      spec_build_requires = []
      for name in sorted(library_dependencies):
        requires = '@ax_{0:s}_spec_requires@'.format(name)
        spec_requires.append(requires)

        build_requires = '@ax_{0:s}_spec_build_requires@'.format(name)
        spec_build_requires.append(build_requires)

      template_mappings['spec_requires'] = ' '.join(spec_requires)
      template_mappings['spec_build_requires'] = ' '.join(spec_build_requires)

      template_filename = os.path.join(template_directory, 'requires.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['spec_requires']
      del template_mappings['spec_build_requires']

    template_filename = os.path.join(template_directory, 'package.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'package-python.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasTools():
      requires_library = '{0:s} = %{{version}}-%{{release}}'.format(
          project_configuration.library_name)

      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'crypto' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libcrypto')
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      spec_requires = [requires_library]
      spec_build_requires = []
      for name in sorted(tools_dependencies):
        requires = '@ax_{0:s}_spec_requires@'.format(name)
        spec_requires.append(requires)

        build_requires = '@ax_{0:s}_spec_build_requires@'.format(name)
        spec_build_requires.append(build_requires)

      template_mappings['spec_requires'] = ' '.join(spec_requires)

      template_filename = os.path.join(
          template_directory, 'package-tools-header.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['spec_requires']

      if tools_dependencies:
        template_mappings['spec_build_requires'] = ' '.join(spec_build_requires)

        template_filename = os.path.join(
            template_directory, 'package-tools-requires.in')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

        del template_mappings['spec_build_requires']

      template_filename = os.path.join(
          template_directory, 'package-tools-footer.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'prep.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'build-python.in')
    else:
      template_filename = os.path.join(template_directory, 'build.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'install.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'files.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'files-python.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.HasTools():
      template_filename = os.path.join(template_directory, 'files-tools.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'changelog.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateTravisYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .travis.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, '.travis.yml')

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_filename = os.path.join(
        template_directory, 'header.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if project_configuration.coverty_scan_token:
      template_mappings['coverty_scan_token'] = (
          project_configuration.coverty_scan_token)

      template_filename = os.path.join(template_directory, 'env.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['coverty_scan_token']

    template_filename = os.path.join(template_directory, 'matrix-header.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.coverty_scan_token:
      template_filename = os.path.join(template_directory, 'matrix-coverty.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'matrix-footer.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    template_filename = os.path.join(template_directory, 'before_install.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['dpkg_build_dependencies']

    if project_configuration.coverty_scan_token:
      template_filename = os.path.join(
          template_directory, 'before_install-coverity.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'install.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.coverty_scan_token:
      template_filename = 'script-coverity.yml'
    else:
      template_filename = 'script.yml'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'after_success.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GetDpkgBuildDependencies(self, project_configuration):
    """Retrieves the dpkg build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies.
    """
    dpkg_build_dependencies = ['autopoint']

    if 'zlib' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('zlib1g-dev')

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if 'fuse' in project_configuration.tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse-dev')

    dpkg_build_dependencies.extend(
        project_configuration.dpkg_build_dependencies)

    return dpkg_build_dependencies

  def _GetDpkgBuildDependenciesDpkgControl(self, project_configuration):
    """Retrieves the dpkg build dependencies for the dpkg/control file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies.
    """
    dpkg_build_dependencies = ['debhelper (>= 9)', 'dh-autoreconf', 'pkg-config']

    if 'zlib' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('zlib1g-dev')
    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if project_configuration.HasPythonModule():
      dpkg_build_dependencies.extend(['python-dev', 'python3-dev'])

    if 'fuse' in project_configuration.tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse-dev')

    if project_configuration.dpkg_build_dependencies:
      dpkg_build_dependencies.extend(project_configuration.dpkg_build_dependencies)

    return dpkg_build_dependencies

  def _GetCygwinBuildDependencies(self, project_configuration):
    """Retrieves the Cygwin build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    cygwin_build_dependencies = list(
        project_configuration.cygwin_build_dependencies)

    if project_configuration.HasDependencyYacc():
      cygwin_build_dependencies.append('bison')
    if project_configuration.HasDependencyLex():
      cygwin_build_dependencies.append('flex')

    if 'zlib' in project_configuration.library_build_dependencies:
      cygwin_build_dependencies.append('zlib-devel')
    if project_configuration.HasDependencyBzip2():
      cygwin_build_dependencies.append('bzip2-devel')
    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      cygwin_build_dependencies.append('openssl-devel')

    if project_configuration.HasPythonModule():
      cygwin_build_dependencies.append('python2-devel')
      cygwin_build_dependencies.append('python3-devel')

    return cygwin_build_dependencies

  def _GetMinGWMSYSBuildDependencies(self, project_configuration):
    """Retrieves the MinGW-MSYS build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    mingw_msys_build_dependencies = list(
        project_configuration.mingw_msys_build_dependencies)

    # TODO: add support for other dependencies.
    if 'zlib' in project_configuration.library_build_dependencies:
      mingw_msys_build_dependencies.append('libz-dev')

    return mingw_msys_build_dependencies

  def Generate(self, project_configuration, output_writer):
    """Generates configuration files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: generate spec file, what about Python versus non-Python?

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          'Missing: {0:s} skipping generation of configuration files.'.format(
              self._library_makefile_am_path))
      return

    pc_libs_private = []
    for library in sorted(makefile_am_file.libraries):
      if library == 'libdl':
        continue

      pc_lib_private = '@ax_{0:s}_pc_libs_private@'.format(library)
      pc_libs_private.append(pc_lib_private)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    template_mappings['authors'] = 'Joachim Metz <joachim.metz@gmail.com>'

    template_mappings['pc_libs_private'] = ' '.join(pc_libs_private)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == 'libyal.nuspec':
        output_filename = '{0:s}.nuspec'.format(
            project_configuration.library_name)

      elif directory_entry == 'libyal.pc.in':
        output_filename = '{0:s}.pc.in'.format(
            project_configuration.library_name)

      else:
        output_filename = directory_entry

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['pc_libs_private']

    self._GenerateCodecovYML(
        project_configuration, template_mappings, output_writer, '.codecov.yml')

    self._GenerateGitignore(
        project_configuration, template_mappings, output_writer, '.gitignore')

    self._GenerateTravisYML(
        project_configuration, template_mappings, output_writer, '.travis.yml')

    self._GenerateAppVeyorYML(
        project_configuration, template_mappings, output_writer, 'appveyor.yml')

    self._GenerateConfigureAC(
        project_configuration, template_mappings, output_writer, 'configure.ac')

    self._GenerateDpkg(
        project_configuration, template_mappings, output_writer, 'dpkg')

    output_filename = '{0:s}.spec.in'.format(project_configuration.library_name)
    self._GenerateRpmSpec(
        project_configuration, template_mappings, output_writer,
        output_filename)


class IncludeSourceFileGenerator(SourceFileGenerator):
  """Include source files generator."""

  def _GenerateFeaturesHeader(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, output_writer, output_filename):
    """Generates a features header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (MainMakefileAMFile): project main Makefile.am file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(
        self._template_directory, 'libyal', 'features.h.in')

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: fix check for libsigscan.
    if include_header_file.have_wide_character_type:
      template_filename = os.path.join(
          template_directory, 'wide_character_type.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: improve detection if include is needed.
    if 'libcthreads' in makefile_am_file.libraries:
      template_filename = os.path.join(template_directory, 'multi_thread.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if include_header_file.have_bfio:
      template_filename = os.path.join(template_directory, 'bfio.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateMakefileAM(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, output_writer, output_filename):
    """Generates a tests Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (LibraryMakefileAMFile): library Makefile.am file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    library_name = project_configuration.library_name

    pkginclude_headers = [
        '\t{0:s}/definitions.h \\'.format(library_name),
        '\t{0:s}/extern.h \\'.format(library_name),
        '\t{0:s}/features.h \\'.format(library_name),
        '\t{0:s}/types.h'.format(library_name)]

    # TODO: detect if header file exits.
    if library_name != 'libcerror':
      pkginclude_header = '\t{0:s}/error.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    if include_header_file.HasFunction('get_codepage'):
      pkginclude_header = '\t{0:s}/codepage.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name in ('libnk2', 'libpff'):
      pkginclude_header = '\t{0:s}/mapi.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name == 'libolecf':
      pkginclude_header = '\t{0:s}/ole.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    pkginclude_headers = sorted(pkginclude_headers)

    template_mappings['pkginclude_headers'] = '\n'.join(pkginclude_headers)

    template_filename = os.path.join(self._template_directory, 'Makefile.am')

    output_filename = os.path.join('include', 'Makefile.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

  def _GenerateTypesHeader(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates a types header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(
        self._template_directory, 'libyal', 'types.h.in')

    type_definitions = []
    # TODO: deprecate project_configuration.library_public_types ?
    for type_name in sorted(project_configuration.library_public_types):
      type_definition = 'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings['library_type_definitions'] = '\n'.join(
        type_definitions)

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if type_definitions:
      template_filename = os.path.join(template_directory, 'public_types.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def Generate(self, project_configuration, output_writer):
    """Generates include source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    output_filename = os.path.join('include', 'Makefile.am')
    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

    output_directory = os.path.join(
        'include', project_configuration.library_name)
    template_directory = os.path.join(self._template_directory, 'libyal')
    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      if (directory_entry not in ('definitions.h.in', 'extern.h') and
          not os.path.exists(output_filename)):
        continue

      # Do not overwrite defintions.h.in when it exist.
      if (directory_entry != 'definitions.h.in' and
          os.path.exists(output_filename)):
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in ('codepage.h', 'definitions.h.in', 'error.h'):
        self._VerticalAlignTabs(output_filename)

    output_filename = os.path.join(output_directory, 'features.h.in')
    self._GenerateFeaturesHeader(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

    output_filename = os.path.join(output_directory, 'types.h.in')
    self._GenerateTypesHeader(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)


class LibrarySourceFileGenerator(SourceFileGenerator):
  """Library source files generator."""

  def Generate(self, project_configuration, output_writer):
    """Generates library source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: libcsplit skip wide_string.[ch]
    # TODO: add support for libuna/libuna_types.h
    # TODO: types.h alingment of debug types?
    # TODO: libsmraw/libsmraw_codepage.h alignment of definitions
    # TODO: libfvalue/libfvalue_codepage.h different

    include_header_file = self._GetTypesIncludeHeaderFile(project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of library source files.'.format(
              self._types_include_header_path))
      return

    library_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name)

    codepage_header_file = os.path.join(
        library_path, '{0:s}_codepage.h'.format(
            project_configuration.library_name))
    error_header_file = os.path.join(
        library_path, '{0:s}_error.h'.format(
            project_configuration.library_name))
    notify_header_file = os.path.join(
        library_path, '{0:s}_notify.h'.format(
            project_configuration.library_name))
    types_header_file = os.path.join(
        library_path, '{0:s}_types.h'.format(
            project_configuration.library_name))

    if include_header_file.types:
      longest_type_name = max(include_header_file.types, key=len)
      longest_library_debug_type_prefix = (
          'typedef struct {0:s}_{1:s} {{}}').format(
              project_configuration.library_name, longest_type_name)

    library_debug_type_definitions = []
    type_definitions = []
    for type_name in include_header_file.types:
      library_debug_type_prefix = 'typedef struct {0:s}_{1:s} {{}}'.format(
          project_configuration.library_name, type_name)

      library_debug_type_definition = (
          'typedef struct {0:s}_{1:s} {{}}\t{0:s}_{1:s}_t;').format(
              project_configuration.library_name, type_name)
      library_debug_type_definitions.append(library_debug_type_definition)

      type_definition = 'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')
    template_mappings['library_debug_type_definitions'] = '\n'.join(
        library_debug_type_definitions)
    template_mappings['library_type_definitions'] = '\n'.join(
        type_definitions)

    authors_template_mapping = template_mappings['authors']

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith('libyal'):
        continue

      if directory_entry.endswith('_{0:s}.h'.format(
          project_configuration.library_name)):
        continue

      if (directory_entry == 'libyal_codepage.h' and (
          not os.path.exists(codepage_header_file) or
          project_configuration.library_name == 'libclocale')):
        continue

      if ((directory_entry == 'libyal_libcerror.h' or
           directory_entry == 'libyal_error.c' or
           directory_entry == 'libyal_error.h') and (
               not os.path.exists(error_header_file) or
               project_configuration.library_name == 'libcerror')):
        continue

      if ((directory_entry == 'libyal_libcnotify.h' or
           directory_entry == 'libyal_notify.c' or
           directory_entry == 'libyal_notify.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == 'libcnotify')):
        continue

      if ((directory_entry == 'libyal_wide_string.c' or
           directory_entry == 'libyal_wide_string.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == 'libcsplit')):
        continue

      # TODO: improve generation of _types.h file
      if (directory_entry == 'libyal_types.h' and (
          not os.path.exists(types_header_file) or
          project_configuration.library_name in (
              'libcerror', 'libcthreads'))):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = '{0:s}{1:s}'.format(
          project_configuration.library_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.library_name, output_filename)

      if not os.path.exists(output_filename) and not directory_entry in (
          'libyal.c', 'libyal_extern.h', 'libyal.rc.in', 'libyal_support.c',
          'libyal_support.h', 'libyal_unused.h'):
        continue

      if directory_entry == 'libyal.rc.in':
        template_mappings['authors'] = ', '.join(
            project_configuration.project_authors)
      else:
        template_mappings['authors'] = authors_template_mapping

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in ('libyal_codepage.h', 'libyal_types.h'):
        self._VerticalAlignTabs(output_filename)


class LibraryManPageGenerator(SourceFileGenerator):
  """Library man page file (libyal.3) generator."""

  def _GenerateLibraryManPage(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates a libyal.3 man page file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    backup_filename = '{0:s}.{1:d}'.format(output_filename, os.getpid())
    shutil.copyfile(output_filename, backup_filename)

    template_mappings['date'] = time.strftime(
        '%B %d, %Y', time.gmtime()).replace(' 0', '  ')

    template_filename = os.path.join(self._template_directory, 'header.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    have_wide_character_type_functions = False
    for section_name in include_header_file.section_names:
      functions_per_section = include_header_file.functions_per_section.get(
          section_name, [])

      if not functions_per_section:
        continue

      section_template_mappings = {
          'section_name': section_name,
      }
      template_filename = os.path.join(self._template_directory, 'section.txt')
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
            'function_arguments': function_arguments_string,
            'function_name': function_prototype.name,
            'function_return_type': function_prototype.return_type,
        }
        template_filename = os.path.join(
            self._template_directory, 'function.txt')
        self._GenerateSection(
            template_filename, function_template_mappings, output_writer,
            output_filename, access_mode='ab')

      if wide_character_type_functions:
        have_wide_character_type_functions = True

        # Ignore adding the wide string support section header in some cases.
        if project_configuration.library_name != 'libcsplit':
          section_template_mappings = {
              'section_name': (
                  'Available when compiled with wide character string support:')
          }
          template_filename = os.path.join(
              self._template_directory, 'section.txt')
          self._GenerateSection(
              template_filename, section_template_mappings, output_writer,
              output_filename, access_mode='ab')

        for function_prototype in wide_character_type_functions:
          function_arguments_string = function_prototype.CopyToString()
          function_template_mappings = {
              'function_arguments': function_arguments_string,
              'function_name': function_prototype.name,
              'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, 'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

      if bfio_functions:
        section_template_mappings = {
            'section_name': (
                'Available when compiled with libbfio support:')
        }
        template_filename = os.path.join(
            self._template_directory, 'section.txt')
        self._GenerateSection(
            template_filename, section_template_mappings, output_writer,
            output_filename, access_mode='ab')

        for function_prototype in bfio_functions:
          function_arguments_string = function_prototype.CopyToString()
          function_template_mappings = {
              'function_arguments': function_arguments_string,
              'function_name': function_prototype.name,
              'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, 'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

      # TODO: add support for debug output functions.

    template_filename = os.path.join(
        self._template_directory, 'description.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if have_wide_character_type_functions:
      template_filename = os.path.join(self._template_directory, 'notes.txt')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if have_wide_character_type_functions:
      template_filename = os.path.join(
          self._template_directory, 'notes_wchar.txt')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(self._template_directory, 'footer.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    backup_file = open(backup_filename, 'rb')
    backup_lines = backup_file.readlines()

    output_file = open(output_filename, 'rb')
    output_lines = output_file.readlines()

    diff_lines = list(difflib.ndiff(backup_lines[1:], output_lines[1:]))
    diff_lines = [line for line in diff_lines if line.startswith(b'-')]

    # Check if there are changes besides the date.
    if diff_lines:
      os.remove(backup_filename)
    else:
      shutil.move(backup_filename, output_filename)

  def Generate(self, project_configuration, output_writer):
    """Generates a library man page file (libyal.3).

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for libcsystem.h - additional types
    # TODO: add support for libsigscan.h - not detecting wchar
    # TODO: add support for libsmraw.h - not detecting wchar
    #       (multiple function in single define?)
    # TODO: warn about [a-z]), in include header
    # TODO: fix libbde_volume_read_startup_key_wide ending up in wrong section

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of library man page.'.format(
              self._library_include_header_path))
      return

    template_mappings = self._GetTemplateMappings(project_configuration)

    output_filename = '{0:s}.3'.format(project_configuration.library_name)
    output_filename = os.path.join('manuals', output_filename)

    self._GenerateLibraryManPage(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)


class PythonModuleSourceFileGenerator(SourceFileGenerator):
  """Python module source files generator."""

  def _CopyFunctionToOutputFile(self, lines, search_string, output_filename):
    """Copies a function to the output file.

    Args:
      lines (list[bytes]): lines of the input file to copy from.
      search_string (bytes): string to search the input for.
      output_filename (str): path of the output file.

    Returns:
      bool: True if the function was found and copied, False otherwise.
    """
    function_index = None
    for index, line in enumerate(lines):
      if line.startswith(search_string):
        # TODO: improve this to determine start of comment based on lines.
        function_index = index - 3
        break

    if function_index is None:
      return False

    with open(output_filename, 'ab') as file_object:
      line = lines[function_index]
      while not line.startswith(b'}'):
        file_object.write(line)

        function_index += 1
        line = lines[function_index]

      file_object.write(line)
      file_object.write(lines[function_index + 1])

    return True

  def _CorrectDescriptionSpelling(self, name, output_filename):
    """Corrects the spelling of a type or value decription.

    Args:
      name (str): type or value name.
      output_filename (str): path of the output file.
    """
    if not name or name[0] not in ('a', 'e', 'i', 'o', ''):
      return

    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    name = name.replace('_', ' ')
    description = ' a {0:s}'.format(name)
    corrected_description = ' an {0:s}'.format(name)

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        line = line.replace(description, corrected_description)
        file_object.write(line)

  def _GenerateDefinitionsHeaderFile(
      self, project_configuration, template_mappings, definitions_name,
      enum_declaration, output_writer):
    """Generates a Python definitions object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      definitions_name (str): name of definitions.
      enum_declaration (EnumDeclaration): enumeration type declaration.
      output_writer (OutputWriter): output writer.
    """
    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_definitions')

    template_mappings['definitions_name'] = definitions_name
    template_mappings['definitions_name_upper_case'] = definitions_name.upper()
    template_mappings['definitions_description'] = definitions_name.replace(
        '_', ' ')

    template_filename = os.path.join(template_directory, 'pyyal_definitions.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(definitions_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateDefinitionsSourceFile(
      self, project_configuration, template_mappings, definitions_name,
      enum_declaration, output_writer):
    """Generates a Python definitions object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      definitions_name (str): name of definitions.
      enum_declaration (EnumDeclaration): enumeration type declaration.
      output_writer (OutputWriter): output writer.
    """
    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_definitions')

    template_mappings['definitions_name'] = definitions_name
    template_mappings['definitions_name_upper_case'] = definitions_name.upper()
    template_mappings['definitions_description'] = definitions_name.replace(
        '_', ' ')

    template_mappings['definition_name'] = definitions_name[:-1]
    template_mappings['definition_name_upper_case'] = (
        definitions_name[:-1].upper())

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    constant_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, definitions_name[:-1])
    constant_name_prefix_length = len(constant_name_prefix)

    for constant_name in enum_declaration.constants.keys():
      constant_name = constant_name.lower()
      if not constant_name.startswith(constant_name_prefix):
        continue

      constant_name = constant_name[constant_name_prefix_length:]

      if constant_name in ('undefined', 'unknown'):
        continue

      template_mappings['constant_name'] = constant_name
      template_mappings['constant_name_upper_case'] = constant_name.upper()

      template_filename = os.path.join(template_directory, 'constant.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')
      self._CorrectDescriptionSpelling(constant_name, output_filename)

    template_filename = os.path.join(template_directory, 'footer.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(definitions_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)

  def _GenerateSequenceTypeHeaderFile(
      self, project_configuration, template_mappings, type_name, output_writer):
    """Generates a Python sequence type object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
    """
    sequence_type_name = self._GetSequenceName(type_name)

    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_sequence_type')

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_filename = os.path.join(
        template_directory, 'pyyal_sequence_type.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(sequence_type_name, output_filename)
    self._CorrectDescriptionSpelling(type_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateSequenceTypeSourceFile(
      self, project_configuration, template_mappings, type_name, output_writer,
      type_is_object=False):
    """Generates a Python sequence type object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
      type_is_object (Optional[bool]): True if the type is an object.
    """
    sequence_type_name = self._GetSequenceName(type_name)

    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_sequence_type')

    python_module_include_names = set([
        project_configuration.library_name, sequence_type_name, 'libcerror',
        'python'])

    if type_is_object:
      python_module_include_names.add(type_name)

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = '#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_mappings['python_module_includes'] = '\n'.join(
        python_module_includes)

    template_filename = os.path.join(
        template_directory, 'pyyal_sequence_type.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)
    self._CorrectDescriptionSpelling(sequence_type_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)
    # TODO: combine vertical align functions.
    self._VerticalAlignAssignmentStatements(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateTypeHeaderFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, is_pseudo_type=False):
    """Generates a Python type object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.
    """
    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    open_support = 'open' in python_function_prototypes
    with_parent = (
        'initialize' not in python_function_prototypes and
        'free' in python_function_prototypes)

    if is_pseudo_type:
      template_directory = os.path.join(
          self._template_directory, 'pyyal_pseudo_type')
    else:
      template_directory = os.path.join(self._template_directory, 'pyyal_type')

    if is_pseudo_type:
      # TODO: determine base type.
      template_mappings['base_type_name'] = 'item'
      # TODO: determine base type.
      template_mappings['base_type_description'] = 'item'
      # TODO: determine base indicator.
      template_mappings['base_type_indicator'] = ''

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if open_support:
      template_filename = 'includes_with_input.h'
    else:
      template_filename = 'includes.h'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if open_support:
      template_filename = 'typedef_with_input.h'
    elif with_parent:
      template_filename = 'typedef_with_parent.h'
    else:
      template_filename = 'typedef.h'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    python_type_prefix = '{0:s}_{1:s}'.format(
        project_configuration.python_module_name, type_name)

    if not is_pseudo_type:
      if with_parent:
        template_filename = 'new_with_parent.h'
      else:
        template_filename = 'new.h'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if open_support:
        template_filename = os.path.join(template_directory, 'new_open.h')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

      # TODO: make open with file object object generated conditionally?
      # if 'open_file_object' in python_function_prototypes:

    if not is_pseudo_type:
      template_filename = os.path.join(template_directory, 'init.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if not is_pseudo_type:
      template_filename = os.path.join(template_directory, 'free.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      value_name = python_function_prototype.value_name

      template_filename = '{0:s}.h'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None
        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET):

          if python_function_prototype.DataTypeIsDatetime():
            template_filename = 'get_datetime_value.h'

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):

          value_name_prefix = ''
          if value_name.startswith('recovered_'):
            value_name_prefix = 'recovered_'
            value_name = value_name[10:]

          template_filename = 'get_{0:s}{1:s}_value_by_index.h'.format(
              value_name_prefix, python_function_prototype.data_type)

          sequence_value_name = self._GetSequenceName(value_name)
          self._SetSequenceValueNameInTemplateMappings(
              template_mappings, sequence_value_name)

        if not template_filename:
          if python_function_prototype.arguments:
            template_filename = 'type_object_function_with_args.h'
          else:
            template_filename = 'type_object_function.h'

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            'Unable to generate Python type object header for: {0:s}.{1:s} '
            'missing template: {1:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetTypeFunctionInTemplateMappings(template_mappings, type_function)
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')
      self._CorrectDescriptionSpelling(value_name, output_filename)

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateTypeSourceFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, is_pseudo_type=False):
    """Generates a Python type object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.
    """
    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    lines = []
    if os.path.exists(output_filename):
      with open(output_filename, 'rb') as file_object:
        lines = file_object.readlines()

    bfio_support = 'open_file_object' in python_function_prototypes
    codepage_support = 'get_ascii_codepage' in python_function_prototypes
    open_support = 'open' in python_function_prototypes
    with_parent = (
        'initialize' not in python_function_prototypes and
        'free' in python_function_prototypes)

    python_module_include_names = set([
        project_configuration.library_name, type_name, 'error', 'libcerror',
        'python', 'unused'])

    if bfio_support:
      python_module_include_names.update(
          set(['file_object_io_handle', 'libbfio']))

    if codepage_support:
      python_module_include_names.update(set(['codepage', 'libclocale']))

    for python_function_prototype in python_function_prototypes.values():
      if python_function_prototype.data_type in (
          definitions.DATA_TYPE_FAT_DATE_TIME,
          definitions.DATA_TYPE_POSIX_TIME):
        python_module_include_names.update(set(['datetime']))

      if python_function_prototype.data_type in (
          definitions.DATA_TYPE_FILETIME,
          definitions.DATA_TYPE_FLOATINGTIME):
        python_module_include_names.update(set(['datetime', 'integer']))

      elif python_function_prototype.data_type == definitions.DATA_TYPE_GUID:
        python_module_include_names.add('guid')

      elif python_function_prototype.data_type in (
          definitions.DATA_TYPE_SIZE64,
          definitions.DATA_TYPE_OFF64,
          definitions.DATA_TYPE_UINT64):
        python_module_include_names.add('integer')

      elif python_function_prototype.data_type == definitions.DATA_TYPE_OBJECT:
        python_module_include_names.add(python_function_prototype.object_type)

        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = self._GetSequenceName(
              python_function_prototype.object_type)
          python_module_include_names.add(sequence_type_name)

      elif python_function_prototype.data_type == definitions.DATA_TYPE_STRING:
        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = python_function_prototype.arguments[0]

          sequence_type_prefix, _, sequence_type_suffix = (
              sequence_type_name.rpartition('_'))

          if sequence_type_suffix in ('entry', 'index'):
            sequence_type_name = sequence_type_prefix

          sequence_type_name = self._GetSequenceName(sequence_type_name)
          python_module_include_names.add(sequence_type_name)

    if is_pseudo_type:
      template_directory = os.path.join(
          self._template_directory, 'pyyal_pseudo_type')
    else:
      template_directory = os.path.join(self._template_directory, 'pyyal_type')

    if is_pseudo_type:
      # TODO: determine base type.
      template_mappings['base_type_name'] = 'item'
      # TODO: determine base type.
      template_mappings['base_type_description'] = 'item'
      # TODO: determine base indicator.
      template_mappings['base_type_indicator'] = ''

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: include header of sub types

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = '#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    template_mappings['python_module_includes'] = '\n'.join(
        python_module_includes)

    if codepage_support:
      template_filename = 'includes_with_codepage.c'
    else:
      template_filename = 'includes.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if bfio_support:
      template_filename = os.path.join(template_directory, 'have_bfio.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    self._GenerateTypeSourceFileTypeObjectMethods(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    self._GenerateTypeSourceFileTypeObjectGetSetDefinitions(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'type_object.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if not is_pseudo_type:
      if with_parent:
        template_filename = 'new_with_parent.c'
      else:
        template_filename = 'new.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if open_support:
      template_filename = os.path.join(template_directory, 'new_open.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if not is_pseudo_type:
      if with_parent:
        template_filename = 'init_with_parent.c'
      elif open_support:
        template_filename = 'init_with_input.c'
      else:
        template_filename = 'init.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if not is_pseudo_type:
      if with_parent:
        template_filename = 'free_with_parent.c'
      else:
        template_filename = 'free.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    generate_get_value_type_object = False
    value_type_objects = set([])

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      # TODO: use prefix in template?
      value_name, value_name_prefix = (
          python_function_prototype.GetValueNameAndPrefix())

      # TODO: add get_cache_directory template

      if type_function == 'get_format_version':
        self._SetValueTypeInTemplateMappings(
            template_mappings, python_function_prototype.value_type)

      template_filename = '{0:s}.c'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None

        # TODO: make more generic.
        if type_function == 'set_key':
          template_filename = 'set_key_with_mode.c'

        elif type_function == 'set_keys':
          template_filename = 'set_keys_with_mode.c'

        elif type_function == 'set_password':
          template_filename = 'set_{0:s}_value.c'.format('string')

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_COPY_FROM):
          template_filename = 'copy_from_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_COPY):
          template_filename = 'copy_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type in (
            definitions.FUNCTION_TYPE_GET,
            definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
            definitions.FUNCTION_TYPE_GET_BY_INDEX,
            definitions.FUNCTION_TYPE_GET_BY_NAME,
            definitions.FUNCTION_TYPE_GET_BY_PATH):

          if value_name.startswith('recovered_'):
            value_name_prefix = 'recovered_'
            value_name = value_name[10:]

          elif value_name_prefix:
            value_name_prefix = '{0:s}_'.format(value_name_prefix)

          else:
            value_name_prefix = ''

          if python_function_prototype.function_type == (
              definitions.FUNCTION_TYPE_GET):
            if not python_function_prototype.arguments:
              if value_name.startswith('number_of_recovered_'):
                value_name = value_name[20:]
                template_filename = 'get_number_of_recovered_{0:s}_value.c'.format(
                    python_function_prototype.data_type)

              else:
                template_filename = 'get_{0:s}{1:s}_value.c'.format(
                    value_name_prefix, python_function_prototype.data_type)

          elif python_function_prototype.function_type == (
              definitions.FUNCTION_TYPE_GET_BY_INDEX):

            template_filename = 'get_{0:s}{1:s}_value_by_index.c'.format(
                value_name_prefix, python_function_prototype.data_type)

            if python_function_prototype.object_type:
              sequence_type_name = self._GetSequenceName(
                  python_function_prototype.object_type)
              self._SetSequenceTypeNameInTemplateMappings(
                  template_mappings, sequence_type_name)

            sequence_value_name = self._GetSequenceName(value_name)
            self._SetSequenceValueNameInTemplateMappings(
                template_mappings, sequence_value_name)

          elif python_function_prototype.function_type in (
              definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
              definitions.FUNCTION_TYPE_GET_BY_NAME,
              definitions.FUNCTION_TYPE_GET_BY_PATH):

            _, _, type_function_suffix = type_function.partition('_by_')

            template_filename = 'get_{0:s}{1:s}_value_by_{2:s}.c'.format(
                value_name_prefix, python_function_prototype.data_type,
                type_function_suffix)

          if python_function_prototype.data_type == (
              definitions.DATA_TYPE_OBJECT):
            if value_name_prefix != 'root_':
              value_name_prefix = ''

            if python_function_prototype.value_type not in value_type_objects:
              generate_get_value_type_object = True
              value_type_objects.add(python_function_prototype.value_type)

          if python_function_prototype.object_type:
            self._SetValueTypeInTemplateMappings(
                template_mappings, python_function_prototype.object_type)

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_IS):
          template_filename = 'is_value.c'

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            'Unable to generate Python type object source code for: '
            '{0:s}.{1:s} missing template: {1:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      if generate_get_value_type_object:
        search_string = (
            'PyTypeObject *{0:s}_{1:s}_get_{2:s}_type_object(').format(
                project_configuration.python_module_name, type_name,
                value_name)

        search_string = search_string.encode('ascii')
        result = self._CopyFunctionToOutputFile(
            lines, search_string, output_filename)

        if not result:
          additional_template_filename = 'get_value_type_object.c'
          additional_template_filename = os.path.join(
              template_directory, additional_template_filename)
          self._GenerateSection(
              additional_template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

        generate_get_value_type_object = False

      result = False
      if type_function in (
          'get_data_as_datetime', 'get_data_as_floating_point',
          'get_data_as_integer'):
        search_string = (
            'PyObject *{0:s}_{1:s}_{2:s}(').format(
                project_configuration.python_module_name, type_name,
                type_function)

        search_string = search_string.encode('ascii')
        result = self._CopyFunctionToOutputFile(
            lines, search_string, output_filename)

      if not result:
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)
    # TODO: combine vertical align functions.
    self._VerticalAlignAssignmentStatements(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateTypeSourceFileTypeObjectMethods(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, output_filename):
    """Generates the type object methods for a Python type source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'pyyal_type')

    python_type_object_methods = []
    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      if not python_function_prototype.arguments:
        arguments_flags = 'METH_NOARGS'
      else:
        arguments_flags = 'METH_VARARGS | METH_KEYWORDS'

      arguments_string = ', '.join(python_function_prototype.arguments)
      data_type = python_function_prototype.GetDataTypeDescription()
      python_type_object_methods.extend([
          '',
          '\t{{ "{0:s}",'.format(type_function),
          '\t  (PyCFunction) {0:s},'.format(python_function_prototype.name),
          '\t  {0:s},'.format(arguments_flags),
          '\t  "{0:s}({1:s}) -> {2:s}\\n"'.format(
              type_function, arguments_string, data_type),
          '\t  "\\n"'])

      if (type_function == 'get_offset' and
          'read_buffer' in python_function_prototypes and
          'seek_offset' in python_function_prototypes):

        description = ['Retrieves the current offset within the data.']
      else:
        description = python_function_prototype.GetDescription()

      for index, line in enumerate(description):
        # Correct xml => XML in description for pyevtx.
        line = line.replace(' xml ', ' XML ')

        if index < len(description) - 1:
          python_type_object_methods.append('\t  "{0:s}\\n"'.format(line))
        else:
          python_type_object_methods.append('\t  "{0:s}" }},'.format(line))

      if (type_function == 'get_offset' and
          'read_buffer' in python_function_prototypes and
          'seek_offset' in python_function_prototypes):

        python_type_object_methods.extend([
            '',
            '\t{ "read",',
            '\t  (PyCFunction) {0:s}_{1:s}_read_buffer,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_VARARGS | METH_KEYWORDS,',
            '\t  "read(size) -> String\\n"',
            '\t  "\\n"',
            '\t  "Reads a buffer of data." },',
            '',
            '\t{ "seek",',
            '\t  (PyCFunction) {0:s}_{1:s}_seek_offset,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_VARARGS | METH_KEYWORDS,',
            '\t  "seek(offset, whence) -> None\\n"',
            '\t  "\\n"',
            '\t  "Seeks an offset within the data." },',
            '',
            '\t{ "tell",',
            '\t  (PyCFunction) {0:s}_{1:s}_get_offset,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_NOARGS,',
            '\t  "tell() -> Integer\\n"',
            '\t  "\\n"',
            '\t  "Retrieves the current offset within the data." },'])

      elif (python_function_prototype.DataTypeIsDatetime() and
            type_function != 'get_data_as_datetime'):
        python_type_object_methods.extend([
            '',
            '\t{{ "{0:s}_as_integer",'.format(type_function),
            '\t  (PyCFunction) {0:s}_as_integer,'.format(
                python_function_prototype.name),
            '\t  METH_NOARGS,',
            '\t  "{0:s}_as_integer({1:s}) -> Integer or None\\n"'.format(
                type_function, arguments_string),
            '\t  "\\n"'])

        if python_function_prototype.data_type == (
            definitions.DATA_TYPE_FAT_DATE_TIME):
          description[0] = (
              '{0:s} as a 32-bit integer containing a FAT date time '
              'value.').format(description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_FILETIME):
          description[0] = (
              '{0:s} as a 64-bit integer containing a FILETIME value.').format(
                  description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_FLOATINGTIME):
          description[0] = (
              '{0:s} as a 64-bit integer containing a floatingtime value.').format(
                  description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_POSIX_TIME):
          description[0] = (
              '{0:s} as a 32-bit integer containing a POSIX timestamp '
              'value.').format(description[0][:-1])

        for index, line in enumerate(description):
          if index < len(description) - 1:
            python_type_object_methods.append('\t  "{0:s}\\n"'.format(line))
          else:
            python_type_object_methods.append('\t  "{0:s}" }},'.format(line))

      elif (python_function_prototype.arguments and
            python_function_prototype.data_type in (
                definitions.DATA_TYPE_OBJECT,
                definitions.DATA_TYPE_STRING)):
          # TODO: add method for the sequence object.
        pass

    python_type_object_methods.extend([
        '',
        '\t/* Sentinel */',
        '\t{ NULL, NULL, 0, NULL }'])

    template_mappings['python_type_object_methods'] = '\n'.join(
        python_type_object_methods)

    template_filename = os.path.join(
        template_directory, 'type_object_methods.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateTypeSourceFileTypeObjectGetSetDefinitions(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, output_filename):
    """Generates the type object definitions for a Python type source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'pyyal_type')

    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if python_function_prototype.function_type not in (
          definitions.FUNCTION_TYPE_COPY,
          definitions.FUNCTION_TYPE_GET,
          definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
          definitions.FUNCTION_TYPE_GET_BY_INDEX,
          definitions.FUNCTION_TYPE_GET_BY_NAME,
          definitions.FUNCTION_TYPE_GET_BY_PATH):
        continue

      if (type_function.endswith('_by_name') or
          type_function.endswith('_by_path')):
        continue

      if (type_function == 'get_offset' and
          'read_buffer' in python_function_prototypes and
          'seek_offset' in python_function_prototypes):
        continue

      if type_function != 'get_ascii_codepage':
        setter_function = '0'
      else:
        setter_function = (
            '{0:s}_{1:s}_set_ascii_codepage_setter').format(
                project_configuration.python_module_name, type_name)

      description = python_function_prototype.GetAttributeDescription()

      # Correct xml => XML in description for pyevtx.
      description = description.replace(' xml ', ' XML ')

      # TODO: fix libcreg getter name keies instead of keys.

      if not python_function_prototype.arguments:
        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(type_function[4:]),
            '\t  (getter) {0:s},'.format(python_function_prototype.name),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}",'.format(description),
            '\t  NULL },'])

      if (python_function_prototype.arguments and
          python_function_prototype.data_type in (
              definitions.DATA_TYPE_OBJECT,
              definitions.DATA_TYPE_STRING)):

        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(sequence_type_function),
            '\t  (getter) {0:s},'.format(sequence_type_getter),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}.",'.format(sequence_type_description),
            '\t  NULL },'])

      if type_function == 'get_cache_directory':
        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(sequence_type_function),
            '\t  (getter) {0:s},'.format(sequence_type_getter),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}.",'.format(sequence_type_description),
            '\t  NULL },'])

    python_type_object_get_set_definitions.extend([
        '',
        '\t/* Sentinel */',
        '\t{ NULL, NULL, NULL, NULL, NULL }'])

    template_mappings['python_type_object_get_set_definitions'] = '\n'.join(
        python_type_object_get_set_definitions)

    template_filename = os.path.join(
        template_directory, 'type_object_get_set_definitions.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GetPythonTypeObjectFunctionPrototype(
      self, project_configuration, type_name, type_function, function_prototype,
      is_pseudo_type=False):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): type name.
      type_function (str): type function.
      function_prototype (FunctionPrototype): C function prototype.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.

    Returns:
      PythonTypeObjectFunctionPrototype: Python type object function prototype
          or None.
    """
    if len(function_prototype.arguments) < 2:
      logging.warning('Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    if type_function in ('free', 'initialize'):
      self_argument = '{0:s}_{1:s}_t **{1:s}'.format(
          project_configuration.library_name, type_name)

    elif is_pseudo_type:
      base_type_name = 'item'
      self_argument = '{0:s}_{1:s}_t *{2:s}'.format(
          project_configuration.library_name, base_type_name, type_name)

    else:
      self_argument = '{0:s}_{1:s}_t *{1:s}'.format(
          project_configuration.library_name, type_name)

    function_argument = function_prototype.arguments[0]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != self_argument:
      logging.warning('Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    function_argument = function_prototype.arguments[-1]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != 'libcerror_error_t **error':
      logging.warning('Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    # TODO: add support for glob functions
    # TODO: add support for has, is functions

    arguments = []
    function_type = None
    object_type = None
    data_type = definitions.DATA_TYPE_NONE
    value_type = None

    # TODO: add override for
    # if (type_function == 'copy_link_target_identifier_data' and
    #    project_configuration.library_name == 'liblnk'):

    if (type_function == 'get_cache_directory_name' and
        project_configuration.library_name == 'libmsiecf'):
      type_function = 'get_cache_directory'

      arguments = ['cache_directory_index']
      function_type = definitions.FUNCTION_TYPE_GET_BY_INDEX
      data_type = definitions.DATA_TYPE_NARROW_STRING

    elif type_function == 'close':
      function_type = definitions.FUNCTION_TYPE_CLOSE

    elif type_function.startswith('copy_from'):
      function_type = definitions.FUNCTION_TYPE_COPY_FROM

      value_argument_index = 1

      function_argument = function_prototype.arguments[value_argument_index]
      value_argument_string = function_argument.CopyToString()

      _, _, argument_name = value_argument_string.rpartition(' ')
      argument_name.lstrip('*')
      arguments.append(argument_name)

      function_argument = function_prototype.arguments[
          value_argument_index + 1]
      value_size_argument_string = function_argument.CopyToString()

      if (value_argument_string == 'const uint8_t *byte_stream' and
          value_size_argument_string == 'size_t byte_stream_size'):
        data_type = definitions.DATA_TYPE_BINARY_DATA

      elif (value_argument_string == 'const uint8_t *data' and
            value_size_argument_string == 'size_t data_size'):
        data_type = definitions.DATA_TYPE_BINARY_DATA

    elif type_function.startswith('copy_'):
      function_type = definitions.FUNCTION_TYPE_COPY
      data_type = definitions.DATA_TYPE_BINARY_DATA

      # TODO: change copy to or add copy_to

    elif type_function == 'free':
      function_type = definitions.FUNCTION_TYPE_FREE

    elif type_function.startswith('get_'):
      function_type = definitions.FUNCTION_TYPE_GET

      if type_function == 'get_ascii_codepage':
        # TODO: replace this by definitions.DATA_TYPE_NARROW_STRING ?
        data_type = 'String'

      elif type_function == 'get_format_version':
        function_argument = function_prototype.arguments[1]
        value_argument_string = function_argument.CopyToString()

        data_type = definitions.DATA_TYPE_STRING
        value_type, _, _ = value_argument_string.partition(' ')

      else:
        type_function_prefix, _, type_function_suffix = (
            type_function.partition('_by_'))

        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, value_argument_suffix = value_argument_string.rpartition('_')

        # Not all get_by_index functions have the suffix _by_index so we need
        # to detect them based on the function arguments.
        if (value_argument_string.startswith('int ') and
            value_argument_suffix in ('entry', 'index')):
          function_type = definitions.FUNCTION_TYPE_GET_BY_INDEX

          _, _, argument_name = value_argument_string.rpartition(' ')

          arguments.append(argument_name)
          value_argument_index = 2

        elif type_function_suffix == 'identifier':
          function_type = definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER

          arguments.append(type_function_suffix)
          value_argument_index = 2

        elif type_function_suffix in ('utf8_name', 'utf8_path'):
          type_function_suffix = type_function_suffix[5:]

          if value_argument_string != 'const uint8_t *utf8_string':
            logging.warning('Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return

          function_argument = function_prototype.arguments[2]
          function_argument_string = function_argument.CopyToString()

          if function_argument_string != 'size_t utf8_string_length':
            logging.warning('Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return

          if type_function_suffix == 'name':
            function_type = definitions.FUNCTION_TYPE_GET_BY_NAME
          else:
            function_type = definitions.FUNCTION_TYPE_GET_BY_PATH

          arguments.append(type_function_suffix)
          value_argument_index = 3

        if value_argument_index != 1:
          function_argument = function_prototype.arguments[value_argument_index]
          value_argument_string = function_argument.CopyToString()

        if value_argument_index + 1 < len(function_prototype.arguments):
          function_argument = function_prototype.arguments[
              value_argument_index + 1]
          value_size_argument_string = function_argument.CopyToString()

          if value_argument_string == 'uint64_t *filetime':
            data_type = definitions.DATA_TYPE_FILETIME

          elif value_argument_string == 'uint64_t *floatingtime':
            data_type = definitions.DATA_TYPE_FLOATINGTIME

          elif value_argument_string == 'uint32_t *fat_date_time':
            data_type = definitions.DATA_TYPE_FAT_DATE_TIME

          elif value_argument_string == 'uint32_t *posix_time':
            data_type = definitions.DATA_TYPE_POSIX_TIME

          elif (value_argument_string == 'uint8_t *data' and
                value_size_argument_string == 'size_t data_size'):
            data_type = definitions.DATA_TYPE_BINARY_DATA

          elif (value_argument_string == 'uint8_t *guid_data' and
                value_size_argument_string == 'size_t guid_data_size'):
            data_type = definitions.DATA_TYPE_GUID

          elif (value_argument_string == 'uint8_t *utf8_string' and
                value_size_argument_string == 'size_t utf8_string_size'):
            data_type = definitions.DATA_TYPE_STRING

          elif (value_argument_string == 'char *string' and
                value_size_argument_string == 'size_t string_size'):
            data_type = definitions.DATA_TYPE_NARROW_STRING

          elif value_argument_string.startswith('double *'):
            data_type = definitions.DATA_TYPE_DOUBLE

          elif value_argument_string.startswith('float *'):
            data_type = definitions.DATA_TYPE_FLOAT

          elif value_argument_string.startswith('int *'):
            data_type = definitions.DATA_TYPE_INT

          elif value_argument_string.startswith('int32_t *'):
            data_type = definitions.DATA_TYPE_INT32

          elif value_argument_string.startswith('off64_t *'):
            data_type = definitions.DATA_TYPE_OFF64

          elif value_argument_string.startswith('size32_t *'):
            data_type = definitions.DATA_TYPE_SIZE32

          elif value_argument_string.startswith('size64_t *'):
            data_type = definitions.DATA_TYPE_SIZE64

          elif value_argument_string.startswith('uint8_t *'):
            data_type = definitions.DATA_TYPE_UINT8

          elif value_argument_string.startswith('uint16_t *'):
            data_type = definitions.DATA_TYPE_UINT16

          elif value_argument_string.startswith('uint32_t *'):
            data_type = definitions.DATA_TYPE_UINT32

          elif value_argument_string.startswith('uint64_t *'):
            data_type = definitions.DATA_TYPE_UINT64

          elif value_argument_string.startswith(
              project_configuration.library_name):
            data_type = definitions.DATA_TYPE_OBJECT

            object_type, _, _ = value_argument_string.partition(' ')
            _, _, object_type = object_type.partition('_')
            object_type = object_type[:-2]

    elif type_function == 'initialize':
      function_type = definitions.FUNCTION_TYPE_INITIALIZE

    elif type_function.startswith('is_'):
      function_type = definitions.FUNCTION_TYPE_IS
      data_type = definitions.DATA_TYPE_BOOLEAN

    elif type_function == 'open' or type_function.startswith('open_'):
      function_type = definitions.FUNCTION_TYPE_OPEN

      if type_function == 'open':
        arguments = ['filename', 'mode=\'r\'']

      elif type_function == 'open_file_io_handle':
        arguments = ['file_object', 'mode=\'r\'']

    elif type_function.startswith('read_'):
      function_type = definitions.FUNCTION_TYPE_READ

      if type_function == 'read_buffer':
        data_type = definitions.DATA_TYPE_BINARY_DATA
        arguments = ['size']

      elif type_function == 'read_buffer_at_offset':
        data_type = definitions.DATA_TYPE_BINARY_DATA
        arguments = ['size', 'offset']

    elif type_function.startswith('seek_'):
      function_type = definitions.FUNCTION_TYPE_SEEK

      if type_function == 'seek_offset':
        arguments = ['offset', 'whence']

    elif type_function.startswith('set_'):
      function_type = definitions.FUNCTION_TYPE_SET

      # TODO: make more generic.
      if type_function == 'set_ascii_codepage':
        arguments = ['codepage']

      elif type_function == 'set_parent_file':
        arguments = ['parent_file']

      elif type_function == 'set_key':
        arguments = ['mode', 'key']

      elif type_function == 'set_keys':
        arguments = ['mode', 'key', 'tweak_key']

      elif type_function in (
          'set_password', 'set_recovery_password', 'set_utf8_password'):
        arguments = ['password']

      else:
        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, argument_name = value_argument_string.rpartition(' ')
        argument_name.lstrip('*')
        arguments.append(argument_name)

        function_argument = function_prototype.arguments[
            value_argument_index + 1]
        value_size_argument_string = function_argument.CopyToString()

        if (value_argument_string == 'uint8_t *data' and
            value_size_argument_string == 'size_t data_size'):
          data_type = definitions.DATA_TYPE_BINARY_DATA

        elif (value_argument_string == 'uint8_t *utf8_string' and
              value_size_argument_string == 'size_t utf8_string_size'):
          data_type = definitions.DATA_TYPE_STRING

        elif (value_argument_string == 'char *string' and
              value_size_argument_string == 'size_t string_size'):
          data_type = definitions.DATA_TYPE_NARROW_STRING

        elif value_argument_string.startswith(
            project_configuration.library_name):
          data_type = definitions.DATA_TYPE_OBJECT

          object_type, _, _ = value_argument_string.partition(' ')
          _, _, object_type = object_type.partition('_')
          object_type = object_type[:-2]

    elif type_function == 'signal_abort':
      function_type = definitions.FUNCTION_TYPE_UTILITY

    # elif type_function.startswith('write_'):
    #   function_type = definitions.FUNCTION_TYPE_WRITE

    python_function_prototype = sources.PythonTypeObjectFunctionPrototype(
        project_configuration.python_module_name, type_name, type_function)

    python_function_prototype.arguments = arguments
    python_function_prototype.data_type = data_type
    python_function_prototype.function_type = function_type
    python_function_prototype.object_type = object_type
    python_function_prototype.value_type = value_type

    return python_function_prototype

  def _GetPythonTypeObjectFunctionPrototypes(
      self, project_configuration, type_name, is_pseudo_type=False):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.

    Returns:
      dict[str, PythonTypeObjectFunctionPrototype]: Python type object
          function prototypes per name.
    """
    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)

    # TODO: handle types in non-matching header files.
    try:
      header_file.Read(project_configuration)
    except IOError:
      logging.warning('Skipping: {0:s}'.format(header_file.path))
      return

    function_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    functions_per_name = header_file.functions_per_name

    python_function_prototypes = collections.OrderedDict()
    for function_name, function_prototype in iter(functions_per_name.items()):
      if not function_prototype.have_extern:
        continue

      if not function_name.startswith(function_name_prefix):
        logging.warning('Skipping unsupported API function: {0:s}'.format(
            function_name))
        continue

      type_function = function_name[function_name_prefix_length:]
      # Skip functions that are a wide character variant of another function.
      if type_function.endswith('_wide'):
        continue

      # Skip functions that retrieves the size of binary data.
      if (type_function.startswith('get_') and
          type_function.endswith('_data_size')):
        continue

      # Skip functions that retrieve the size of an UTF-8 string.
      if (type_function.startswith('get_utf8_') and
          type_function.endswith('_size')):
        continue

      if (type_function.startswith('get_') and
          type_function.endswith('_utf8_string_size')):
        continue

      # Skip functions that are a UTF-16 variant of another function.
      if (type_function.startswith('get_utf16_') or
          type_function.startswith('set_utf16_') or
          (type_function.startswith('get_') and (
              type_function.endswith('_by_utf16_name') or
              type_function.endswith('_by_utf16_path') or
              type_function.endswith('_utf16_string') or
              type_function.endswith('_utf16_string_size')))):
        continue

      # TODO: ignore these functions for now.
      # TODO: improve check only to apply for types with pseudo types.
      if (type_function == 'get_type' and (
          project_configuration.library_name in (
              'libmsiecf', 'libolecf', 'libpff'))):
        continue

      # TODO: remove when removed after deprecation.
      if (type_function.startswith('get_value_') and
          type_function != 'get_value_type' and
          project_configuration.library_name in (
              'libolecf', )):
        continue

      if (type_function == 'get_version' and (
          project_configuration.library_name in (
              'libevt', 'libevtx'))):
        continue

      if (type_function.startswith('write_buffer') and (
          project_configuration.library_name not in (
              'libewf', ))):
        continue

      if type_function in (
          'get_flags', 'get_offset_range',
          'get_number_of_unallocated_blocks', 'get_unallocated_block'):
        continue

      python_function_prototype = self._GetPythonTypeObjectFunctionPrototype(
          project_configuration, type_name, type_function, function_prototype,
          is_pseudo_type=is_pseudo_type)

      if (not python_function_prototype or
          not python_function_prototype.function_type):
        logging.warning('Skipping unsupported type function: {0:s}'.format(
            function_name))
        continue

      # TODO: Skip functions that retrieve the size of a narrow string.

      type_function = python_function_prototype.type_function
      python_function_prototypes[type_function] = python_function_prototype

    return python_function_prototypes

  def _GetSequenceName(self, name):
    """Determines the sequence type or value name.

    Args:
      name (str): name of type or value.

    Returns:
      str: sequence type or value name.
    """
    if name == 'key':
      return '{0:s}s'.format(name)

    if (name[-1] in ('s', 'x', 'z') or (
        name[-1] == 'h'  and name[-2] in ('c', 's'))):
      return '{0:s}es'.format(name)

    if name[-1] == 'y':
      return '{0:s}ies'.format(name[:-1])

    return '{0:s}s'.format(name)

  def _GetSequenceType(self, python_function_prototype):
    """Determines if the function prototype implies a sequence type.

    Args:
      python_function_prototype (PythonTypeObjectFunctionPrototype): Python
          type object function prototype.

    Returns:
      tuple: contains:
        str: sequence type name or None.
        bool: True if the sequence type is an object type or None.
    """
    if not python_function_prototype.arguments:
      return None, None

    if python_function_prototype.function_type not in (
        definitions.FUNCTION_TYPE_GET,
        definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
        definitions.FUNCTION_TYPE_GET_BY_INDEX,
        definitions.FUNCTION_TYPE_GET_BY_NAME,
        definitions.FUNCTION_TYPE_GET_BY_PATH):
      return None, None

    if python_function_prototype.data_type == definitions.DATA_TYPE_OBJECT:
      return python_function_prototype.object_type, True

    elif python_function_prototype.data_type == definitions.DATA_TYPE_STRING:
      return python_function_prototype.value_name, False

    return None, None

  def _GetTemplateMappings(self, project_configuration):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = super(
        PythonModuleSourceFileGenerator, self)._GetTemplateMappings(
            project_configuration,
            authors_separator=',\n *                          ')

    # TODO: have source formatter take care of the alignment.
    # Used to align source in pyyal/pyyal_file_object_io_handle.c
    alignment_padding = len(project_configuration.library_name) - 6
    template_mappings['alignment_padding'] = ' ' * alignment_padding

    return template_mappings

  def _VerticalAlignFunctionArguments(self, output_filename):
    """Vertically aligns function arguments.

    Note this is a very basic approach that should suffice for the Python
    module source files.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    alignment_number_of_spaces = 0
    alignment_number_of_tabs = 0
    in_function_call = False
    with open(output_filename, 'wb') as file_object:
      for line in lines:
        if not line.startswith(b'\t'):
          file_object.write(line)
          continue

        stripped_line = line.rstrip()

        if in_function_call:
          if stripped_line.endswith(b')') or stripped_line.endswith(b');'):
            in_function_call = False

          stripped_line = line.lstrip()
          line = b'{0:s}{1:s}{2:s}'.format(
              b'\t' * alignment_number_of_tabs,
              b' ' * alignment_number_of_spaces,
              stripped_line)

        elif stripped_line.endswith(b'('):
          in_function_call = True
          stripped_line = line.lstrip()

          alignment_number_of_spaces = stripped_line.rfind(b' ')
          if alignment_number_of_spaces == -1:
            alignment_number_of_spaces = 1
          else:
            alignment_number_of_spaces += 2

          alignment_number_of_tabs = len(line) - len(stripped_line)

        file_object.write(line)

  def Generate(self, project_configuration, output_writer):
    """Generates Python module source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: pycaes add support for object without parent and file_io_handle
    # TODO: add tests configuration e.g. test data, libfwnt or use in-line
    # generator hints
    # TODO: add support for get_object_by_type
    # TODO: add support for get_object_by_identifier
    # TODO: add support for copy from
    # TODO: add support for definitions without "definition prefix"
    # TODO: add support for pyolecf_property_value
    # TODO: sequence object rename ${type_name}_index to item_index
    # TODO: generate non type files.
    # TODO: generate pyyal.c
    # TODO: generate pyyal/Makefile.am
    # TODO: generate pyyal-python2/Makefile.am
    # TODO: generate pyyal-python3/Makefile.am

    if not project_configuration.HasPythonModule():
      return

    template_mappings = self._GetTemplateMappings(project_configuration)

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith('pyyal_'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      force_create = False

      output_filename = '{0:s}_{1:s}'.format(
          project_configuration.python_module_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.python_module_name, output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry == 'pyyal_file_object_io_handle.c':
        self._SortVariableDeclarations(output_filename)

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning((
          'Missing: {0:s} skipping generation of Python type object '
          'source and header files.').format(
              self._library_include_header_path))
    else:
      api_types, api_types_with_input = (
          include_header_file.GetAPITypeTestGroups())

      api_pseudo_types = include_header_file.GetAPIPseudoTypeTestGroups()

      api_types.extend(api_types_with_input)
      api_types.extend(api_pseudo_types)
      types_with_sequence_types = set([])

      for type_name in api_types:
        self._SetTypeNameInTemplateMappings(template_mappings, type_name)

        is_pseudo_type = type_name in api_pseudo_types

        python_function_prototypes = self._GetPythonTypeObjectFunctionPrototypes(
            project_configuration, type_name, is_pseudo_type=is_pseudo_type)

        if not python_function_prototypes:
          logging.warning((
              'Missing function prototypes for type: {0:s} skipping '
              'generation of Python type object source and header '
              'files.').format(type_name))
          continue

        for type_function, python_function_prototype in iter(
            python_function_prototypes.items()):

          sequence_type_name, type_is_object = self._GetSequenceType(
              python_function_prototype)
          if sequence_type_name:
            types_with_sequence_types.add((sequence_type_name, type_is_object))

        self._GenerateTypeSourceFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer,
            is_pseudo_type=is_pseudo_type)

        self._GenerateTypeHeaderFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer,
            is_pseudo_type=is_pseudo_type)

      for sequence_type_name, type_is_object in types_with_sequence_types:
        self._SetTypeNameInTemplateMappings(
            template_mappings, sequence_type_name)

        self._GenerateSequenceTypeSourceFile(
            project_configuration, template_mappings, sequence_type_name,
            output_writer, type_is_object=type_is_object)

        self._GenerateSequenceTypeHeaderFile(
            project_configuration, template_mappings, sequence_type_name,
            output_writer)

    include_header_file = self._GetDefinitionsIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning((
          'Missing: {0:s} skipping generation of Python definitions object '
          'source and header files.').format(
              self._definitions_include_header_path))
    else:
      definitions_name_prefix = '{0:s}_'.format(
          project_configuration.library_name)
      definitions_name_prefix_length = len(definitions_name_prefix)

      for enum_declaration in include_header_file.enum_declarations:
        definitions_name = enum_declaration.name.lower()
        if not definitions_name.startswith(definitions_name_prefix):
          continue

        # TODO: skip flags definitions
        definitions_name = definitions_name[definitions_name_prefix_length:]
        if definitions_name in ('access_flags', 'endian'):
          continue

        self._GenerateDefinitionsSourceFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)

        self._GenerateDefinitionsHeaderFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)


class ScriptFileGenerator(SourceFileGenerator):
  """Script files generator."""

  def Generate(self, project_configuration, output_writer):
    """Generates script files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_mappings = self._GetTemplateMappings(project_configuration)
    template_mappings['local_libs'] = ' '.join(
        sorted(makefile_am_file.libraries))
    template_mappings['shared_libs'] = ' '.join(makefile_am_file.libraries)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = directory_entry

      if (directory_entry in ('syncwinflexbison.ps1', 'synczlib.ps1') and
          not os.path.exists(output_filename)):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if output_filename.endswith('.sh'):
        # Set x-bit for .sh scripts.
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)


class TestsSourceFileGenerator(SourceFileGenerator):
  """Tests source files generator."""

  _PYTHON_FUNCTION_NAMES = (
      'support', )

  # TODO: replace by type specific test scripts.
  _PYTHON_FUNCTION_WITH_INPUT_NAMES = (
      'open_close', 'seek', 'read', 'file', 'volume')

  def _FormatTestData(self, data):
    """Formats the test data as a C byte array.

    Args:
      data (bytes): data.

    Returns:
      str: data as a C byte array.
    """
    # TODO: print text as text?

    hexadecimal_lines = []
    data_size = len(data)
    for block_index in xrange(0, data_size, 16):
      data_string = data[block_index:block_index + 16]

      hexadecimal_string = ', '.join([
          '0x{0:02x}'.format(ord(byte_value))
          for byte_value in data_string[0:16]])

      if len(data_string) < 16:
        hexadecimal_lines.append('\t{0:s}'.format(hexadecimal_string))
      else:
        hexadecimal_lines.append('\t{0:s},'.format(hexadecimal_string))

    return '\n'.join(hexadecimal_lines)

  def _GenerateAPISupportTests(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates an API support tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    signature_type = include_header_file.GetCheckSignatureType()

    test_options = self._GetTestOptions(project_configuration, signature_type)

    template_directory = os.path.join(
        self._template_directory, 'yal_test_support')

    output_filename = '{0:s}_test_support.c'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join('tests', output_filename)

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: add check for has codepage function for libsigscan and include
    # libcerror.
    if signature_type:
      template_mappings['signature_type'] = signature_type

    if signature_type:
      template_filename = os.path.join(
          template_directory, 'includes-with_input.c')
    else:
      template_filename = os.path.join(template_directory, 'includes.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for support_function in (
        'get_version', 'get_access_flags_read', 'get_codepage',
        'set_codepage'):
      if not include_header_file.HasFunction(support_function):
        continue

      template_filename = '{0:s}.c'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if signature_type:
      template_filename = os.path.join(template_directory, 'check_signature.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      test_getopt_string = []
      test_options_variable_declarations = []
      for option, argument in test_options:
        getopt_string = option
        if argument:
          getopt_string = '{0:s}:'.format(getopt_string)

        test_getopt_string.append(getopt_string)

        if argument == 'offset': 
          test_options_variable_declarations.extend([
              '\tlibcerror_error_t *error = NULL;',
              '\tsystem_character_t *option_{0:s} = NULL;'.format(argument),
              '\toff64_t {0:s}_offset = 0;'.format(signature_type),
              '\tsize_t string_length = 0;',
              '\tint result = 0;'])

      variable_declaration = '\tsystem_character_t *source = NULL;'
      test_options_variable_declarations.append(variable_declaration)

      template_mappings['test_getopt_string'] = ''.join(test_getopt_string)
      template_mappings['test_options_variable_declarations'] = '\n'.join(
          sorted(test_options_variable_declarations))

      template_filename = os.path.join(
          template_directory, 'main-start_with_input-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['test_getopt_string']
      del template_mappings['test_options_variable_declarations']

      switch_case_unused = []
      for option, argument in test_options:
        if argument == 'offset': 
          template_mappings['test_option'] = option
          template_mappings['test_option_argument'] = argument

          template_filename = os.path.join(
              template_directory, 'main-start_with_input-switch_case.c')
          self._GenerateSection(
              template_filename, template_mappings, output_writer, output_filename,
              access_mode='ab')

          del template_mappings['test_option']
          del template_mappings['test_option_argument']

        else:
          switch_case_unused.append(
              '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option))

      if switch_case_unused:
        template_mappings['test_options_switch_case_unused'] = '\n'.join(
            switch_case_unused)

        template_filename = os.path.join(
            template_directory, 'main-start_with_input-switch_case_unused.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

        del template_mappings['test_options_switch_case_unused']

      template_filename = os.path.join(
          template_directory, 'main-start_with_input-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = os.path.join(
            template_directory, 'main-option_offset.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      template_filename = os.path.join(
          template_directory, 'main-body_with_input.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = 'main-end_with_offset.c'
      else:
        template_filename = 'main-end_with_input.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    else:
      template_filename = os.path.join(template_directory, 'main.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if signature_type:
      del template_mappings['signature_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateMakefileAM(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, api_functions, api_functions_with_input, api_types,
      api_types_with_input, api_pseudo_types, internal_types,
      python_module_types, output_writer):
    """Generates a tests Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (LibraryMakefileAMFile): library Makefile.am file.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      api_pseudo_types (list[str]): names of API pseudo types to test.
      internal_types (list[str]): names of internal types to test.
      python_module_types (list[str]): names of Python module types to test.
      output_writer (OutputWriter): output writer.
    """
    tests = set(api_functions).union(set(api_functions_with_input))
    tests.update(set(api_types).union(set(api_types_with_input)))
    tests.update(set(api_pseudo_types))
    tests.update(set(internal_types))
    tests = sorted(tests)

    template_directory = os.path.join(
        self._template_directory, 'Makefile.am')
    output_filename = os.path.join('tests', 'Makefile.am')

    test_scripts = []
    if (api_functions or api_functions_with_input or api_types or
        api_types_with_input or api_pseudo_types):
      test_script = 'test_library.sh'
      test_scripts.append(test_script)

    for tool_name_suffix in ('export', 'info', 'verify'):
      tool_name = '{0:s}{1:s}'.format(
          project_configuration.library_name_suffix, tool_name_suffix)
      if tool_name in project_configuration.tools_names:
        test_script = 'test_{0:s}.sh'.format(tool_name)
        test_scripts.append(test_script)

    check_scripts = ['test_runner.sh']
    check_scripts.extend(test_scripts)

    python_scripts = []
    python_test_scripts = ['test_python_module.sh']

    if project_configuration.HasPythonModule():
      for python_module_type in python_module_types:
        test_script = '{0:s}_test_{1:s}.py'.format(
            project_configuration.python_module_name, python_module_type)
        python_scripts.append(test_script)

      test_script = '{0:s}_test_support.py'.format(
          project_configuration.python_module_name)
      python_scripts.append(test_script)

      check_scripts.extend(python_scripts)
      check_scripts.extend(python_test_scripts)

    check_scripts = sorted(check_scripts)

    if project_configuration.HasPythonModule():
      test_script = '$(TESTS_{0:s})'.format(
          project_configuration.python_module_name.upper())
      test_scripts.append(test_script)

    check_programs = []
    for test in tests:
      check_program = '{0:s}_test_{1:s}'.format(
          project_configuration.library_name_suffix, test)
      check_programs.append(check_program)

    cppflags = list(makefile_am_file.cppflags)
    if api_functions_with_input or api_types_with_input:
      # Add libcsystem before non libyal cppflags.
      index = 0
      while index < len(cppflags):
        cppflag = cppflags[index]
        if not cppflag.startswith('lib') or cppflag == 'libcrypto':
          break
        index += 1

    cppflags = ['@{0:s}_CPPFLAGS@'.format(name.upper()) for name in cppflags]

    cppflag = '@{0:s}_DLL_IMPORT@'.format(
        project_configuration.library_name.upper())
    cppflags.append(cppflag)

    template_mappings['cppflags'] = ' \\\n'.join(
        ['\t{0:s}'.format(name) for name in cppflags])
    template_mappings['python_tests'] = ' \\\n'.join(
        ['\t{0:s}'.format(filename) for filename in python_test_scripts])
    template_mappings['tests'] = ' \\\n'.join(
        ['\t{0:s}'.format(filename) for filename in test_scripts])
    template_mappings['check_scripts'] = ' \\\n'.join(
        ['\t{0:s}'.format(filename) for filename in check_scripts])
    template_mappings['check_programs'] = ' \\\n'.join(
        ['\t{0:s}'.format(filename) for filename in check_programs])

    template_filename = os.path.join(template_directory, 'header.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'python.am')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'body.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for group_name in tests:
      if group_name in api_functions:
        has_error_argument = include_header_file.HasErrorArgument(group_name)
        if (project_configuration.library_name != 'libcerror' and
            group_name not in ('error', 'notify') and has_error_argument):
          template_filename = 'yal_test_function.am'
        else:
          template_filename = 'yal_test_function_no_error.am'

        template_mappings['library_function'] = group_name

      elif group_name in api_functions_with_input:
        if group_name == 'support':
          template_filename = 'yal_test_support_with_input.am'
        else:
          template_filename = 'yal_test_function_with_input.am'

        template_mappings['library_function'] = group_name

      elif (group_name in api_types or group_name in api_pseudo_types or
            group_name in internal_types):
        if project_configuration.library_name == 'libcerror':
          template_filename = 'yal_test_type_no_error.am'
        else:
          template_filename = 'yal_test_type.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      elif group_name in api_types_with_input:
        template_filename = 'yal_test_type_with_input.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'footer.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._SortSources(output_filename)

  def _GeneratePythonModuleSupportTests(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates a Python module support tests script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, 'pyyal_test_support')

    output_filename = '{0:s}_test_support.py'.format(
        project_configuration.python_module_name)
    output_filename = os.path.join('tests', output_filename)

    template_filename = os.path.join(template_directory, 'header.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'imports.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'test_case.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for support_function in (
        'get_version', ):
      if not include_header_file.HasFunction(support_function):
        continue

      template_filename = '{0:s}.py'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'main.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GeneratePythonModuleTypeTests(
      self, project_configuration, template_mappings, type_name, output_writer,
      with_input=False):
    """Generates a Python module type tests script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      bool: True if successful or False if not.
    """
    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)

    # TODO: handle types in non-matching header files.
    try:
      header_file.Read(project_configuration)
    except IOError:
      logging.warning('Skipping: {0:s}'.format(header_file.path))
      return False

    template_directory = os.path.join(
        self._template_directory, 'pyyal_test_type')

    output_filename = '{0:s}_test_{1:s}.py'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join('tests', output_filename)

    template_filename = os.path.join(template_directory, 'header.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'imports.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'test_case.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for type_function in (
        'signal_abort', 'open', 'set_ascii_codepage', 'read_buffer',
        'seek_offset'):
      function_prototype = header_file.GetTypeFunction(type_name, type_function)
      if not function_prototype:
        continue

      template_filename = '{0:s}.py'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'main.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateTypeTest(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, output_writer, output_filename,
      initialize_is_internal=False, with_input=False):
    """Generates a test for a type function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      initialize_is_internal (Optional[bool]): True if the initialize function
          is not externally available.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      tuple: contains:
        str: name of library type function.
        str: name of the test function corresponding to the library type function.
        bool: True if the function prototype was externally available.
    """
    function_name = self._GetFunctionName(
        project_configuration, type_name, type_function)

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return function_name, None, last_have_extern

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    template_filename = None
    value_name = None
    value_type = None

    if (type_function.startswith('get_utf8_') or
        type_function.startswith('get_utf16_')):
      function_argument = function_prototype.arguments[1]
      function_argument_string = function_argument.CopyToString()

      value_name = type_function[4:]
      value_type, _, _ = function_argument_string.partition(' ')

      if type_function.endswith('_size'):
        if len(function_prototype.arguments) == 3:
          if with_input:
            template_filename = 'get_value_with_input.c'
          else:
            template_filename = 'get_value.c'

      else:
        if len(function_prototype.arguments) == 4:
          if with_input:
            template_filename = 'get_string_value_with_input.c'
          else:
            template_filename = 'get_string_value.c'

    elif (type_function.startswith('get_') and
          len(function_prototype.arguments) in (3, 4)):
      function_argument = function_prototype.arguments[1]
      function_argument_string = function_argument.CopyToString()

      value_name = type_function[4:]
      value_type, _, _ = function_argument_string.partition(' ')

      if len(function_prototype.arguments) == 3:
        if value_type.startswith(project_configuration.library_name):
          value_type = value_type[:-2]

          if with_input:
            template_filename = 'get_type_value_with_input.c'
          else:
            template_filename = 'get_type_value.c'
        else:
          if with_input:
            template_filename = 'get_value_with_input.c'
          else:
            template_filename = 'get_value.c'

      elif function_argument_string == 'uint8_t *guid_data':
        if with_input:
          template_filename = 'get_guid_value_with_input.c'
        else:
          template_filename = 'get_guid_value.c'

    if not template_filename:
      template_filename = '{0:s}.c'.format(type_function)

    self._SetValueNameInTemplateMappings(template_mappings, value_name)
    self._SetValueTypeInTemplateMappings(template_mappings, value_type)

    template_filename = os.path.join(template_directory, template_filename)
    if not os.path.exists(template_filename):
      logging.warning((
          'Unable to generate test type source code for type function: '
          '{0:s} with error: missing template').format(type_function))
      return function_name, None, last_have_extern

    if not initialize_is_internal:
      if not function_prototype.have_extern and last_have_extern:
        internal_template_filename = os.path.join(
            template_directory, 'define_internal-start.c')
        self._GenerateSection(
            internal_template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      elif function_prototype.have_extern and not last_have_extern:
        internal_template_filename = os.path.join(
            template_directory, 'define_internal-end.c')
        self._GenerateSection(
            internal_template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    test_function_name = self._GetTestFunctionName(
        project_configuration, type_name, type_function)

    return function_name, test_function_name, function_prototype.have_extern

  def _GenerateTypeTestOpenFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      test_options, have_extern, header_file, output_writer, output_filename,
      function_names, tests_to_run):
    """Generates a test for a type open function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      test_options (list[tuple[str, str]]): test options.
      have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.

    Returns:
      bool: True if the function prototype was externally available.
    """
    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if function_prototype:
      self._GenerateTypeTestOpen(
          project_configuration, template_mappings, type_name, type_function,
          test_options, output_writer, output_filename)

      function_name = self._GetFunctionName(
          project_configuration, type_name, type_function)
      test_function_name = self._GetTestFunctionName(
          project_configuration, type_name, type_function)

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    return have_extern

  def _GenerateTypeTestOpen(
      self, project_configuration, template_mappings, type_name, test_name,
      test_options, output_writer, output_filename):
    """Generates an open test for a type.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_name (str): name of test.
      test_options (list[tuple[str, str]]): test options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    needs_glob = self._NeedsGlob(project_configuration, type_name)

    function_arguments = ['     const system_character_t *source']
    for _, argument in test_options:
      if argument != 'offset':
        function_arguments.append(
            '     const system_character_t *{0:s}'.format(argument))

    function_arguments = ',\n'.join(function_arguments)

    function_variables = ['\tint result = 0;']
    if test_options:
      function_variables.append('\tsize_t string_length = 0;')

    function_variables = '\n'.join(function_variables)

    template_mappings['test_options_function_arguments'] = function_arguments
    template_mappings['test_options_function_variables'] = function_variables

    if needs_glob:
      template_filename = '{0:s}-start-with_glob.c'.format(test_name)
    else:
      template_filename = '{0:s}-start.c'.format(test_name)

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['test_options_function_arguments']
    del template_mappings['test_options_function_variables']

    for _, argument in test_options:
      if argument != 'offset':
        template_filename = '{0:s}-set_{1:s}.c'.format(test_name, argument)
        template_filename = os.path.join(template_directory, template_filename)
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

    if needs_glob:
      template_filename = '{0:s}-end-with_glob.c'.format(test_name)
    else:
      template_filename = '{0:s}-end.c'.format(test_name)

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateTypeTestWithCloneFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      have_extern, header_file, output_writer, output_filename,
      function_names, tests_to_run, clone_function=None, free_function=None):
    """Generates a test for a type function with clone function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.
      clone_function (Optional[str]): name of the clone function.
      free_function (Optional[str]): name of the free function.

    Returns:
      bool: True if the function prototype was externally available.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if function_prototype:
      if clone_function:
        value_name, _, _ = clone_function.rpartition('_clone_function')
        self._SetValueNameInTemplateMappings(template_mappings, value_name)

        template_filename = '{0:s}_with_clone_function.c'.format(type_function)
      else:
        template_filename = '{0:s}.c'.format(type_function)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      function_name = self._GetFunctionName(
          project_configuration, type_name, type_function)
      test_function_name = self._GetTestFunctionName(
          project_configuration, type_name, type_function)

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    return have_extern

  def _GenerateTypeTestWithFreeFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      have_extern, header_file, output_writer, output_filename,
      function_names, tests_to_run, free_function=None):
    """Generates a test for a type function with free function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.
      free_function (Optional[str]): name of the free function.

    Returns:
      bool: True if the function prototype was externally available.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if function_prototype:
      if free_function:
        value_name, _, _ = free_function.rpartition('_free_function')
        self._SetValueNameInTemplateMappings(template_mappings, value_name)

        template_filename = '{0:s}_with_free_function.c'.format(type_function)
      else:
        template_filename = '{0:s}.c'.format(type_function)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      function_name = self._GetFunctionName(
          project_configuration, type_name, type_function)
      test_function_name = self._GetTestFunctionName(
          project_configuration, type_name, type_function)

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    return have_extern

  def _GenerateTypeTests(
      self, project_configuration, template_mappings, type_name, output_writer,
      is_internal=False, with_input=False):
    """Generates a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
      is_internal (Optional[bool]): True if the type is an internal type.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      bool: True if successful or False if not.
    """
    output_filename = '{0:s}_test_{1:s}.c'.format(
        project_configuration.library_name_suffix, type_name)
    output_filename = os.path.join('tests', output_filename)

    if os.path.exists(output_filename) and not self._experimental:
      return False

    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)

    # TODO: handle types in non-matching header files.
    try:
      header_file.Read(project_configuration)
    except IOError:
      logging.warning('Skipping: {0:s}'.format(header_file.path))
      return False

    type_size_name = self._GetTypeSizeName(project_configuration, type_name)
    test_options = self._GetTestOptions(project_configuration, type_name)

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    function_names = list(header_file.functions_per_name.keys())
    tests_to_run = []
    tests_to_run_with_args = []
    tests_to_run_with_input = []

    function_prototype = header_file.GetTypeFunction(
        type_name, 'open_file_io_pool')
    if function_prototype:
      bfio_type = 'pool'
    else:
      bfio_type = 'handle'

    template_mappings['bfio_type'] = bfio_type

    needs_glob = self._NeedsGlob(project_configuration, type_name)

    self._SetTypeNameInTemplateMappings(template_mappings, type_name)

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if with_input:
      template_filename = 'includes_with_input.c'
    else:
      template_filename = 'includes.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if header_file.have_internal_functions:
      template_filename = os.path.join(
          template_directory, 'includes_internal.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if with_input:
      if bfio_type == 'pool':
        template_filename = 'start_with_input-bfio_pool.c'
      else:
        template_filename = 'start_with_input-bfio_handle.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      template_filename = os.path.join(template_directory, 'start_with_input.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      function_arguments = []
      if bfio_type == 'pool':
        function_arguments.append('     libbfio_pool_t *file_io_pool')
      else:
        function_arguments.append('     libbfio_handle_t *file_io_handle')

      for _, argument in test_options:
        if argument != 'offset':
          function_arguments.append(
              '     const system_character_t *{0:s}'.format(argument))

      function_arguments = ',\n'.join(function_arguments)

      function_variables = ['\tint result = 0;']
      if test_options:
        function_variables.insert(0, '\tsize_t string_length = 0;')

      function_variables = '\n'.join(function_variables)

      template_mappings['test_options_function_arguments'] = function_arguments
      template_mappings['test_options_function_variables'] = function_variables

      template_filename = os.path.join(
          template_directory, 'open_source-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['test_options_function_arguments']
      del template_mappings['test_options_function_variables']

      for _, argument in test_options:
        if argument != 'offset':
          template_filename = 'open_source-set_{0:s}.c'.format(argument)
          template_filename = os.path.join(
              template_directory, template_filename)
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

      template_filename = os.path.join(template_directory, 'open_source-body.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      function_prototype = header_file.GetTypeFunction(
          type_name, 'open_extent_data_files')
      if function_prototype:
        template_filename = os.path.join(
            template_directory, 'open_source-extend_data_files.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      template_filename = os.path.join(template_directory, 'open_source-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      template_filename = os.path.join(template_directory, 'close_source.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # Generate test data.
    test_data_directory = os.path.join('tests', 'data')
    if os.path.exists(test_data_directory):
      for directory_entry in sorted(os.listdir(test_data_directory)):
        test_type_name, _, test_data_suffix = directory_entry.partition('.')
        if test_type_name != type_name:
          continue

        test_data_suffix, _, test_data_index = test_data_suffix.rpartition('.')
        if test_data_suffix:
          test_data_suffix = '_{0:s}'.format(test_data_suffix)

        test_data_file = os.path.join(test_data_directory, directory_entry)
        with open(test_data_file, 'rb') as file_object:
          test_data = file_object.read()

        template_mappings['test_data'] = self._FormatTestData(test_data)
        template_mappings['test_data_size'] = len(test_data)
        template_mappings['test_data_index'] = test_data_index
        template_mappings['test_data_suffix'] = test_data_suffix

        template_filename = os.path.join(template_directory, 'test_data.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

    # Generate a clone, compare and/or free test function if necessary.
    clone_function = None
    compare_function = None
    free_function = None

    for function_prototype in header_file.functions_per_name.values():
      for argument in function_prototype.arguments:
        argument_string = argument.CopyToString()

        if '_clone_function' in argument_string:
          _, _, clone_function = argument_string.partition('*')
          clone_function, _, _ = clone_function.partition(')')

        elif '_compare_function' in argument_string:
          _, _, compare_function = argument_string.partition('*')
          compare_function, _, _ = compare_function.partition(')')

        elif '_free_function' in argument_string:
          _, _, free_function = argument_string.partition('*')
          free_function, _, _ = free_function.partition(')')

    if free_function:
      value_name, _, _ = free_function.rpartition('_free_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'free_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if clone_function:
      value_name, _, _ = clone_function.rpartition('_clone_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'clone_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if compare_function:
      value_name, _, _ = compare_function.rpartition('_compare_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'compare_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: treat external functions as internal when initialize_is_internal
    # except for free.
    have_extern = True

    initialize_is_internal = False
    initialize_number_of_arguments = None

    function_prototype = header_file.GetTypeFunction(type_name, 'initialize')
    if function_prototype:
      initialize_is_internal = not function_prototype.have_extern
      initialize_number_of_arguments = len(function_prototype.arguments)

      if initialize_number_of_arguments == 2:
        function_name, test_function_name, have_extern = self._GenerateTypeTest(
            project_configuration, template_mappings, type_name, 'initialize',
            have_extern, header_file, output_writer, output_filename,
            with_input=with_input)
      else:
        function_name = '{0:s}_{1:s}_initialize'.format(
            project_configuration.library_name, type_name)
        test_function_name = None

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    have_extern = self._GenerateTypeTestWithFreeFunction(
        project_configuration, template_mappings, type_name, 'free',
        have_extern, header_file, output_writer, output_filename,
        function_names, tests_to_run, free_function=free_function)

    function_prototype = header_file.GetTypeFunction(type_name, 'free')
    if function_prototype and initialize_is_internal and have_extern:
      template_filename = os.path.join(
          template_directory, 'define_internal-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    for type_function in ('empty', 'clear'):
      have_extern = self._GenerateTypeTestWithFreeFunction(
          project_configuration, template_mappings, type_name, type_function,
          have_extern, header_file, output_writer, output_filename,
          function_names, tests_to_run, free_function=free_function)

    have_extern = self._GenerateTypeTestWithCloneFunction(
        project_configuration, template_mappings, type_name, 'clone',
        have_extern, header_file, output_writer, output_filename,
        function_names, tests_to_run, clone_function=clone_function,
        free_function=free_function)

    have_extern = self._GenerateTypeTestWithFreeFunction(
        project_configuration, template_mappings, type_name, 'resize',
        have_extern, header_file, output_writer, output_filename,
        function_names, tests_to_run, free_function=free_function)

    if with_input:
      # TODO: fix libbfio having no open wide.
      # TODO: make handling open close more generic for libpff attachment handle.
      for type_function in (
          'open', 'open_wide', 'open_file_io_handle', 'open_file_io_pool'):
        have_extern = self._GenerateTypeTestOpenFunction(
            project_configuration, template_mappings, type_name, type_function,
            test_options, have_extern, header_file, output_writer,
            output_filename, function_names, tests_to_run_with_input)

      function_name, test_function_name, have_extern = self._GenerateTypeTest(
          project_configuration, template_mappings, type_name, 'close',
          have_extern, header_file, output_writer, output_filename,
          initialize_is_internal=initialize_is_internal, with_input=with_input)

      if test_function_name:
        tests_to_run_with_input.append((function_name, test_function_name))
        function_names.remove(function_name)

      self._GenerateTypeTestOpen(
          project_configuration, template_mappings, type_name, 'open_close',
          test_options, output_writer, output_filename)

      function_name = self._GetFunctionName(
          project_configuration, type_name, 'open_close')
      test_function_name = self._GetTestFunctionName(
          project_configuration, type_name, 'open_close')

      tests_to_run_with_input.append((function_name, test_function_name))

    template_mappings['type_size_name'] = type_size_name

    function_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    for function_name in function_names:
      if not function_name.startswith(function_name_prefix):
        continue

      type_function = function_name[function_name_prefix_length:]
      test_function_name = None

      # TODO: improve can currently only handle simple initialize functions.
      if initialize_number_of_arguments == 2:
        _, test_function_name, have_extern = self._GenerateTypeTest(
            project_configuration, template_mappings, type_name, type_function,
            have_extern, header_file, output_writer, output_filename,
            initialize_is_internal=initialize_is_internal, with_input=with_input)

      if with_input:
        tests_to_run_with_args.append((function_name, test_function_name))
      else:
        tests_to_run.append((function_name, test_function_name))

    del template_mappings['type_size_name']

    if initialize_is_internal or not have_extern:
      template_filename = os.path.join(
          template_directory, 'define_internal-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: create generic test for get_number_of_X API functions.
    # TODO: generate run test macros.

    if with_input:
      test_getopt_string = []
      test_options_variable_declarations = []
      for option, argument in test_options:
        getopt_string = option
        if argument:
          getopt_string = '{0:s}:'.format(getopt_string)

        test_getopt_string.append(getopt_string)

        if argument == 'offset': 
          test_options_variable_declarations.extend([
              '\tsystem_character_t *option_{0:s} = NULL;'.format(argument),
              '\toff64_t {0:s}_offset = 0;'.format(type_name)])

        else:
          variable_declaration = (
              '\tsystem_character_t *option_{0:s} = NULL;').format(argument)
          test_options_variable_declarations.append(variable_declaration)

      if needs_glob:
        test_options_variable_declarations.extend([
            '\tlibbfio_handle_t *file_io_handle = NULL;',
            '\tsystem_character_t **filenames = NULL;',
            '\tint filename_index = 0;',
            '\tint number_of_filenames = 0;'])

      variable_declaration = '\tsystem_character_t *source = NULL;'
      test_options_variable_declarations.append(variable_declaration)

      template_mappings['test_getopt_string'] = ''.join(test_getopt_string)
      template_mappings['test_options_variable_declarations'] = '\n'.join(
          sorted(test_options_variable_declarations))

      template_filename = os.path.join(
          template_directory, 'main-start_with_input-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['test_getopt_string']
      del template_mappings['test_options_variable_declarations']

      for option, argument in test_options:
        template_mappings['test_option'] = option
        template_mappings['test_option_argument'] = argument

        template_filename = os.path.join(
            template_directory, 'main-start_with_input-switch_case.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

        del template_mappings['test_option']
        del template_mappings['test_option_argument']

      template_filename = os.path.join(
          template_directory, 'main-start_with_input-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = os.path.join(
            template_directory, 'main-option_offset.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

      template_filename = os.path.join(template_directory, 'main-notify_set.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    else:
      template_filename = os.path.join(template_directory, 'main-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name, test_options,
        tests_to_run, header_file, output_writer, output_filename,
        initialize_is_internal=initialize_is_internal)

    if with_input:
      if needs_glob:
        template_filename = 'main-with_glob-start.c'
      elif 'offset' in [argument for _, argument in test_options]:
        template_filename = 'main-with_offset-start.c'
      else:
        template_filename = 'main-with_input-start.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      self._GenerateTypeTestsMainTestsToRun(
          project_configuration, template_mappings, type_name, test_options,
          tests_to_run_with_input, header_file, output_writer, output_filename,
          initialize_is_internal=initialize_is_internal, with_input=True)

      if needs_glob:
        open_source_arguments = ['\t\t          file_io_pool']
      else:
        open_source_arguments = ['\t\t          file_io_handle']
      for _, argument in test_options:
        if argument != 'offset':
          open_source_arguments.append(
              '\t\t          option_{0:s}'.format(argument))

      template_mappings['test_options_open_source_arguments'] = ',\n'.join(
          open_source_arguments)

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = 'main-with_input-tests_with_offset.c'
      else:
        template_filename = 'main-with_input-tests.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      del template_mappings['test_options_open_source_arguments']

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name, test_options,
        tests_to_run_with_args, header_file, output_writer, output_filename,
        initialize_is_internal=initialize_is_internal, with_args=True)

    if with_input:
      if needs_glob:
        template_filename = 'main-with_glob-end.c'
      else:
        template_filename = 'main-with_input-end.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if needs_glob:
      template_filename = 'main-end-with_glob.c'
    elif with_input:
      template_filename = 'main-end-with_input.c'
    else:
      template_filename = 'main-end.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['bfio_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

    return True

  def _GenerateTypeTestsMainTestsToRun(
      self, project_configuration, template_mappings, type_name, test_options,
      tests_to_run, header_file, output_writer, output_filename,
      initialize_is_internal=False, with_args=False, with_input=False):
    """Generates a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_options (list[tuple[str, str]]): test options.
      tests_to_run (list[tuple[str, str]]): names of the library type function
          and its corresponding test function.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      initialize_is_internal (Optional[bool]): True if the initialize function
          is not externally available.
      with_args (Optional[bool]): True if the tests to run have arguments.
      with_input (Optional[bool]): True if the tests to run have input.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    library_name_suffix = project_configuration.library_name_suffix.upper()

    last_have_extern = not initialize_is_internal
    last_have_wide_character_type = False

    if not last_have_extern:
      template_filename = os.path.join(
          template_directory, 'define_internal-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

    tests_to_run_mappings = []
    for function_name, test_function_name in tests_to_run:
      function_prototype = header_file.functions_per_name.get(
          function_name, None)

      if not function_prototype:
        have_wide_character_type = False
        have_extern = last_have_extern
      else:
        have_wide_character_type = function_prototype.have_wide_character_type
        if function_prototype.name.endswith('_free'):
          have_extern = function_prototype.have_extern
        else:
          have_extern = (
              not initialize_is_internal and function_prototype.have_extern)

      if (have_wide_character_type != last_have_wide_character_type or
          have_extern != last_have_extern):

        if tests_to_run_mappings:
          template_mappings['tests_to_run'] = '\n'.join(tests_to_run_mappings)
          tests_to_run_mappings = []

          template_filename = os.path.join(
              template_directory, 'main-tests_to_run.c')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

          if not have_wide_character_type and last_have_wide_character_type:
            template_filename = os.path.join(
                template_directory, 'define_wide_character_type-end.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer,
                output_filename, access_mode='ab')

          if have_extern and not last_have_extern:
            template_filename = os.path.join(
                template_directory, 'define_internal-end.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer,
                output_filename, access_mode='ab')

          if not have_extern and last_have_extern:
            template_filename = os.path.join(
                template_directory, 'define_internal-start.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer,
                output_filename, access_mode='ab')

          if have_wide_character_type and not last_have_wide_character_type:
            template_filename = os.path.join(
                template_directory, 'define_wide_character_type-start.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer,
                output_filename, access_mode='ab')

        last_have_wide_character_type = have_wide_character_type
        last_have_extern = have_extern

      if tests_to_run_mappings:
        tests_to_run_mappings.append('')

      if not test_function_name:
        if with_args:
          tests_to_run_mappings.append(
              '\t\t/* TODO: add tests for {0:s} */'.format(function_name))
        else:
          tests_to_run_mappings.append(
              '\t/* TODO: add tests for {0:s} */'.format(function_name))

      else:
        if with_args:
          test_to_run_mappings = [
              '\t\t{0:s}_TEST_RUN_WITH_ARGS('.format(library_name_suffix),
              '\t\t "{0:s}",'.format(function_name),
              '\t\t {0:s},'.format(test_function_name),
              '\t\t {0:s} );'.format(type_name)]

        elif with_input:
          if (function_name.endswith('_close') and
              not function_name.endswith('_open_close')):
            test_to_run_mappings = [
                '\t\t{0:s}_TEST_RUN('.format(library_name_suffix),
                '\t\t "{0:s}",'.format(function_name),
                '\t\t {0:s} );'.format(test_function_name)]

          else:
            test_to_run_mappings = [
                '\t\t{0:s}_TEST_RUN_WITH_ARGS('.format(library_name_suffix),
                '\t\t "{0:s}",'.format(function_name),
                '\t\t {0:s},'.format(test_function_name),
                '\t\t source' ]

            for _, argument in test_options:
              if argument != 'offset':
                test_to_run_mappings[-1] = '{0:s},'.format(test_to_run_mappings[-1])
                test_to_run_mappings.append('\t\t option_{0:s}'.format(argument))

            test_to_run_mappings[-1] = '{0:s} );'.format(test_to_run_mappings[-1])

        else:
          test_to_run_mappings = [
              '\t{0:s}_TEST_RUN('.format(library_name_suffix),
              '\t "{0:s}",'.format(function_name),
              '\t {0:s} );'.format(test_function_name)]

        tests_to_run_mappings.extend(test_to_run_mappings)

    if tests_to_run_mappings:
      template_mappings['tests_to_run'] = '\n'.join(tests_to_run_mappings)
      tests_to_run_mappings = []

      template_filename = os.path.join(
          template_directory, 'main-tests_to_run.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if not have_wide_character_type and last_have_wide_character_type:
        template_filename = os.path.join(
            template_directory, 'define_wide_character_type-end.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='ab')

    if not last_have_extern:
      template_filename = os.path.join(
          template_directory, 'define_internal-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

  def _GetFunctionName(
      self, project_configuration, type_name, type_function):
    """Retrieves the function name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      type_function (str): type function.

    Returns:
      str: function name.
    """
    return '{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, type_name, type_function)

  def _GetLibraryTypes(self, project_configuration, makefile_am_file):
    """Determines the types defined in the library sources.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      makefile_am_file (MainMakefileAMFile): project main Makefile.am file.

    Returns:
      types (list[str]): type names.
    """
    library_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name)

    type_name_prefix = '{0:s}_'.format(project_configuration.library_name)
    type_name_prefix_length = len(type_name_prefix)

    types = []
    for source_file in makefile_am_file.sources:
      if not source_file.endswith('.h'):
        continue

      header_file_path = os.path.join(library_path, source_file)
      header_file = LibraryHeaderFile(header_file_path)
      header_file.Read(project_configuration)

      for type_name in header_file.types:
        if not type_name.startswith(type_name_prefix):
          continue

        type_name = type_name[type_name_prefix_length:]
        types.append(type_name)

    return types

  def _GetTemplateMappings(
      self, project_configuration, api_functions, api_functions_with_input,
      api_types, api_types_with_input, api_pseudo_types, internal_types,
      python_functions, python_functions_with_input):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      api_pseudo_types (list[str]): names of API pseudo types to test.
      internal_types (list[str]): names of internal types to test.
      python_functions (list[str]): names of Python functions to test.
      python_functions_with_input (list[str]): names of Python functions to
          test with input data.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = super(
        TestsSourceFileGenerator, self)._GetTemplateMappings(
            project_configuration)

    test_api_types = set(api_types).union(set(internal_types))
    library_tests = sorted(set(api_functions).union(test_api_types))
    library_tests_with_input = sorted(
        set(api_functions_with_input).union(set(api_types_with_input)))

    template_mappings['library_tests'] = ' '.join(library_tests)
    template_mappings['library_tests_with_input'] = ' '.join(
        library_tests_with_input)

    template_mappings['test_python_functions'] = ' '.join(
        sorted(python_functions))
    template_mappings['test_python_functions_with_input'] = ' '.join(
        sorted(python_functions_with_input))

    template_mappings['tests_option_sets'] = ' '.join(
        sorted(project_configuration.tests_option_sets))

    template_mappings['alignment_padding'] = (
        ' ' * len(project_configuration.library_name_suffix))

    return template_mappings

  def _GetTestFunctionName(
      self, project_configuration, type_name, type_function):
    """Retrieves the test function name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      type_function (str): type function.

    Returns:
      str: test function name.
    """
    return '{0:s}_test_{1:s}_{2:s}'.format(
        project_configuration.library_name_suffix, type_name, type_function)

  def _GetTestOptions(self, project_configuration, type_name):
    """Retrieves the test options.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      list[tuple[str, str]]: test options.
    """
    # TODO: determine test_options based on function prototypes
    test_options = []

    if (type_name == 'volume' and
        project_configuration.library_name == 'libbde'):
      # TODO: add support for startup key option
      # TODO: add support for keys option
      test_options.append(('o', 'offset'))
      test_options.append(('p', 'password'))
      test_options.append(('r', 'recovery_password'))

    elif (type_name == 'volume' and
        project_configuration.library_name == 'libfvde'):
      # TODO: add support for keys option
      test_options.append(('o', 'offset'))
      test_options.append(('p', 'password'))

    elif (type_name == 'volume' and
        project_configuration.library_name == 'libluksde'):
      # TODO: add support for keys option
      test_options.append(('p', 'password'))

    elif (type_name == 'file' and
          project_configuration.library_name == 'libqcow'):
      # TODO: add support for keys option
      test_options.append(('p', 'password'))

    return test_options

  def _NeedsGlob(self, project_configuration, type_name):
    """Determines if the type needs a glob function for source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      bool: True if the type needs a glob function.
    """
    # TODO: determine test_options based on function prototypes
    if (type_name == 'handle' and project_configuration.library_name in (
        'libewf', 'libsmraw')):
      return True

    return False

  def _GetTypeSizeName(self, project_configuration, type_name):
    """Retrieves the test size name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      str: type size name.
    """
    # TODO: determine type_size_name based on function prototypes
    # TODO: add support libfvde and libvslvm
    if (type_name == 'file' and project_configuration.library_name in (
        'libqcow', 'libvhdi')):
      return 'media_size'

    if (type_name == 'handle' and project_configuration.library_name in (
        'libewf', 'libsmraw', 'libvmdk')):
      return 'media_size'

    return 'size'

  def _SortSources(self, output_filename):
    """Sorts the sources.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    sources = None
    in_sources = False

    with open(output_filename, 'wb') as file_object:
      for line in lines:
        stripped_line = line.strip()
        if stripped_line.endswith(b'_SOURCES = \\'):
          file_object.write(line)
          sources = []
          in_sources = True

        elif in_sources:
          if stripped_line:
            if stripped_line.endswith(b' \\'):
              stripped_line = stripped_line[:-2]
            sources.append(stripped_line)

          else:
            sorted_lines = b' \\\n'.join(
                [b'\t{0:s}'.format(filename) for filename in sorted(sources)])

            file_object.writelines(sorted_lines)
            file_object.write(b'\n')
            file_object.write(line)
            in_sources = False

        else:
          file_object.write(line)

  def Generate(self, project_configuration, output_writer):
    """Generates tests source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: compare handle fdata and cdata differences, and includes
    # TODO: weave existing test files?
    # TODO: use data files to generate test data tests/input/.data/<name>
    # TODO: add support for options in configuration file to set option sets.
    # TODO: fix creation of fwsi_test_file_entry_(item) when include header
    # file contains (item).
    # TODO: fix libwrc message-table
    # TODO: handle libfsntfs $attribute_name
    # TODO: detect internal free functions
    # TODO: handle glob, options and options sets in test scripts.

    if not self._HasTests(project_configuration):
      return

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_makefile_am_path))
      return

    api_functions, api_functions_with_input = (
        include_header_file.GetAPIFunctionTestGroups())

    api_types, api_types_with_input = (
        include_header_file.GetAPITypeTestGroups())

    api_pseudo_types = include_header_file.GetAPIPseudoTypeTestGroups()

    # TODO: handle internal functions
    types = self._GetLibraryTypes(project_configuration, makefile_am_file)

    public_functions = set(api_functions).union(set(api_functions_with_input))
    public_types = set(api_types).union(set(api_types_with_input))

    # TODO: handle types in non-matching header files.
    internal_types = []
    for type_name in types:
      if type_name in sorted(public_types):
        continue

      # Ignore internal type that are proxies by API types.
      if type_name.startswith('internal_'):
        continue

      internal_types.append(type_name)

    logging.info('Found public functions: {0:s}'.format(
        ', '.join(public_functions)))
    logging.info('Found public types: {0:s}'.format(', '.join(public_types)))
    logging.info('Found public pseudo types: {0:s}'.format(
        ', '.join(api_pseudo_types)))
    logging.info('Found internal types: {0:s}'.format(
        ', '.join(internal_types)))

    # TODO: handle non-template files differently.
    # TODO: yal_test_open_close.c handle file, handle, volume

    library_header = 'yal_test_{0:s}.h'.format(
        project_configuration.library_name)

    test_python_functions = []
    for function_name in self._PYTHON_FUNCTION_NAMES:
      output_filename = '{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join('tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions.append(function_name)

    test_python_functions_with_input = []
    for function_name in self._PYTHON_FUNCTION_WITH_INPUT_NAMES:
      output_filename = '{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join('tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions_with_input.append(function_name)

    template_mappings = self._GetTemplateMappings(
        project_configuration, api_functions, api_functions_with_input,
        api_types, api_types_with_input, api_pseudo_types, internal_types,
        test_python_functions, test_python_functions_with_input)

    for directory_entry in os.listdir(self._template_directory):
      # Ignore yal_test_library.h in favor of yal_test_libyal.h
      if directory_entry == library_header:
        continue

      # For libcerror skip generating yal_test_error.c.
      if (directory_entry == 'yal_test_error.c' and
          project_configuration.library_name == 'libcerror'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      is_script = (
          directory_entry.endswith('.ps1') or directory_entry.endswith('.sh'))

      if directory_entry == 'yal_test_libyal.h':
        output_filename = '{0:s}_test_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      elif directory_entry.startswith('yal_test_'):
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[4:])

      elif directory_entry.startswith('pyyal_test_'):
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.python_module_name, directory_entry[6:])

      elif directory_entry.startswith('test_yal') and is_script:
        output_filename = 'test_{0:s}{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[8:])

      elif directory_entry.startswith('test_pyyal') and is_script:
        output_filename = 'test_{0:s}{1:s}'.format(
            project_configuration.python_module_name, directory_entry[10:])

      else:
        output_filename = directory_entry

      if directory_entry in ('test_library.ps1', 'test_library.sh'):
        force_create = bool(public_functions) or bool(public_types)

      elif directory_entry in ('test_yalinfo.ps1', 'test_yalinfo.sh'):
        tool_name = '{0:s}info'.format(
            project_configuration.library_name_suffix)
        force_create = tool_name in project_configuration.tools_names

      elif directory_entry == 'yal_test_error.c':
        force_create = 'error' in api_functions

      elif directory_entry == 'yal_test_notify.c':
        force_create = 'notify' in api_functions

      else:
        force_create = False

      output_filename = os.path.join('tests', output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if output_filename.endswith('.c'):
        self._SortIncludeHeaders(project_configuration, output_filename)

      elif output_filename.endswith('.sh'):
        # Set x-bit for .sh scripts.
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

    self._GenerateAPISupportTests(
        project_configuration, template_mappings, include_header_file,
        output_writer)

    if project_configuration.HasPythonModule():
      self._GeneratePythonModuleSupportTests(
          project_configuration, template_mappings, include_header_file,
          output_writer)

    python_module_types = []

    for type_name in api_types:
      if (type_name == 'error' and
          project_configuration.library_name == 'libcerror'):
        continue

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer)
      if not result:
        api_types.remove(type_name)

      if project_configuration.HasPythonModule():
        python_module_types.append(type_name)
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer)

    for type_name in api_types_with_input:
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          with_input=True)
      if not result:
        api_types_with_input.remove(type_name)

      if project_configuration.HasPythonModule():
        python_module_types.append(type_name)
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer,
            with_input=True)

    for type_name in api_pseudo_types:
      if (type_name == 'error' and
          project_configuration.library_name == 'libcerror'):
        continue

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer)
      if not result:
        api_pseudo_types.remove(type_name)

      if project_configuration.HasPythonModule():
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer)

    for type_name in internal_types:
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          is_internal=True)
      if not result:
        internal_types.remove(type_name)

    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, api_functions, api_functions_with_input, api_types,
        api_types_with_input, api_pseudo_types, internal_types,
        python_module_types, output_writer)


class ToolsSourceFileGenerator(SourceFileGenerator):
  """Tools source files generator."""

  def _GenerateMountHandleHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount handle header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'mount_handle')

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'includes.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)

    for template_name in (
        'struct.h', 'initialize.h', 'free.h', 'signal_abort.h'):
      template_filename = os.path.join(template_directory, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.mount_tool_has_keys_option:
      template_filename = os.path.join(template_directory, 'set_keys.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.mount_tool_has_password_option:
      template_filename = os.path.join(template_directory, 'set_password.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'open.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: improve this check.
    if project_configuration.library_name == 'libvhdi':
      template_filename = os.path.join(template_directory, 'open_parent.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    for template_name in ('close.h', 'read.h', 'seek.h'):
      template_filename = os.path.join(template_directory, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: split in individual functions.
    template_filename = os.path.join(template_directory, 'body.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['mount_tool_source_type']

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateMountHandleSourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount handle source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'mount_handle')

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'includes.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)

    template_filename = os.path.join(template_directory, 'initialize.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.mount_tool_has_keys_option:
      template_filename = os.path.join(template_directory, 'free_with_keys.c')
    else:
      template_filename = os.path.join(template_directory, 'free.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'signal_abort.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if project_configuration.mount_tool_has_keys_option:
      template_filename = os.path.join(template_directory, 'set_keys.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.mount_tool_has_password_option:
      template_filename = os.path.join(template_directory, 'set_password.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: improve this check.
    if project_configuration.library_name == 'libvhdi':
      template_filename = os.path.join(template_directory, 'open_with_parent.c')
    else:
      template_filename = os.path.join(template_directory, 'open.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: improve this check.
    if project_configuration.library_name == 'libvhdi':
      template_filename = os.path.join(template_directory, 'open_parent.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    for template_name in ('close.c', 'read.c', 'seek.c'):
      template_filename = os.path.join(template_directory, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: split in individual functions.
    template_filename = os.path.join(template_directory, 'body.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'set_basename.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['mount_tool_source_type']

  def _GenerateMountToolSourceFile(
      self, project_configuration, template_mappings, mount_tool_name,
      output_writer, output_filename):
    """Generates a mount tool source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yalmount')

    mount_tool_options = self._GetMountToolOptions(
        project_configuration, mount_tool_name)

    template_mappings['mount_tool_name'] = mount_tool_name
    template_mappings['mount_tool_source_description'] = (
        project_configuration.mount_tool_source_description)
    template_mappings['mount_tool_source_description_long'] = (
        project_configuration.mount_tool_source_description_long)
    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'includes.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._GenerateMountToolSourceUsageFunction(
        project_configuration, template_mappings, mount_tool_name,
        mount_tool_options, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'signal_handler.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'fuse.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'dokan.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._GenerateMountToolSourceMainFunction(
        project_configuration, template_mappings, mount_tool_name,
        mount_tool_options, output_writer, output_filename)

    del template_mappings['mount_tool_name']
    del template_mappings['mount_tool_source_description']
    del template_mappings['mount_tool_source_description_long']
    del template_mappings['mount_tool_source_type']

  def _GenerateMountToolSourceMainFunction(
      self, project_configuration, template_mappings, mount_tool_name,
      mount_tool_options, output_writer, output_filename):
    """Generates a mount tool source main function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      mount_tool_options (list[tuple[str, str, st]])): mount tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yalmount')

    mount_tool_getopt_string = []
    mount_tool_options_variable_declarations = []
    # TODO: move mount_tool_options_switch into templates.
    mount_tool_options_switch = []
    for option, argument, _ in mount_tool_options:
      if mount_tool_options_switch:
        mount_tool_options_switch.append('')

      getopt_string = option
      if argument:
        getopt_string = '{0:s}:'.format(getopt_string)

      mount_tool_getopt_string.append(getopt_string)

      if argument:
        alignment_padding = ' ' * (len('extended_options') - len(argument))
        variable_declaration = (
            '\tsystem_character_t *option_{0:s}{1:s} = NULL;').format(
                argument, alignment_padding)
        mount_tool_options_variable_declarations.append(variable_declaration)

        mount_tool_options_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\toption_{0:s} = optarg;'.format(argument),
            '',
            '\t\t\t\tbreak;'])

      elif option == 'h':
        mount_tool_options_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\tusage_fprint(',
            '\t\t\t\t stdout );',
            '',
            '\t\t\t\treturn( EXIT_SUCCESS );'])

      elif option == 'v':
        mount_tool_options_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\tverbose = 1;',
            '',
            '\t\t\t\tbreak;'])

      elif option == 'V':
        mount_tool_options_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\t{0:s}_output_copyright_fprint('.format(
                project_configuration.tools_directory),
            '\t\t\t\t stdout );',
            '',
            '\t\t\t\treturn( EXIT_SUCCESS );'])

    template_mappings['mount_tool_getopt_string'] = ''.join(mount_tool_getopt_string)
    template_mappings['mount_tool_options_variable_declarations'] = '\n'.join(
        sorted(mount_tool_options_variable_declarations))
    template_mappings['mount_tool_options_switch'] = '\n'.join(
        mount_tool_options_switch)

    template_filename = os.path.join(template_directory, 'main-start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['mount_tool_getopt_string']
    del template_mappings['mount_tool_options_variable_declarations']
    del template_mappings['mount_tool_options_switch']

    if project_configuration.mount_tool_has_keys_option:
      template_filename = os.path.join(template_directory, 'main-option_keys.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if project_configuration.mount_tool_has_password_option:
      template_filename = os.path.join(
          template_directory, 'main-option_password.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, 'main-open.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'main-fuse.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'main-dokan.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, 'main-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateMountToolSourceUsageFunction(
      self, project_configuration, template_mappings, mount_tool_name,
      mount_tool_options, output_writer, output_filename):
    """Generates a mount tool source usage function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      mount_tool_options (list[tuple[str, str, st]])): mount tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yalmount')

    alignment_padding = '          '
    width = 80 - len(alignment_padding)
    text_wrapper = textwrap.TextWrapper(width=width)

    options_details = []
    options_usage = []
    options_without_arguments = []
    for option, argument, description in mount_tool_options:
      description_lines = text_wrapper.wrap(description)

      description_line = description_lines.pop(0)
      details = '\tfprintf( stream, "\\t-{0:s}:{1:s}{2:s}\\n"'.format(
          option, alignment_padding, description_line)

      for description_line in description_lines:
        options_details.append(details)
        details = '\t                 "\\t   {0:s}{1:s}\\n"'.format(
            alignment_padding, description_line)

      details = '{0:s} );'.format(details)
      options_details.append(details)

      if not argument:
        options_without_arguments.append(option)
      else:
        usage = '[ -{0:s} {1:s} ]'.format(option, argument)
        options_usage.append(usage)

    usage = '[ -{0:s} ]'.format(''.join(options_without_arguments))
    options_usage.append(usage)

    options_usage.extend([
        project_configuration.mount_tool_source_type, 'mount_point'])

    mount_tool_source_alignment = ' ' *(
        len('mount_point') - len(project_configuration.mount_tool_source_type))

    usage = 'Usage: {0:s} '.format(mount_tool_name)
    usage_length = len(usage)
    alignment_padding = ' ' * usage_length
    options_usage = ' '.join(options_usage)

    width = 80 - usage_length
    text_wrapper = textwrap.TextWrapper(width=width)

    usage_lines = text_wrapper.wrap(options_usage)

    mount_tool_usage = []
    usage_line = usage_lines.pop(0)
    usage = '\tfprintf( stream, "{0:s}{1:s}\\n"'.format(usage, usage_line)

    for usage_line in usage_lines:
      mount_tool_usage.append(usage)
      usage = '\t                 "{0:s}{1:s}\\n"'.format(
          alignment_padding, usage_line)

    usage = '{0:s}\\n" );'.format(usage[:-1])
    mount_tool_usage.append(usage)

    template_mappings['mount_tool_options'] = '\n'.join(options_details)
    template_mappings['mount_tool_source_alignment'] = mount_tool_source_alignment
    template_mappings['mount_tool_usage'] = '\n'.join(mount_tool_usage)

    template_filename = os.path.join(template_directory, 'usage.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    del template_mappings['mount_tool_options']
    del template_mappings['mount_tool_source_alignment']
    del template_mappings['mount_tool_usage']

  def _GetMountToolOptions(self, project_configuration, mount_tool_name):
    """Retrieves the mount tool option.s

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      mount_tool_name (str): name of the mount tool.

    Returns:
      list[tuple[str, str, str]]: mount tool options.
    """
    # TODO: sort options with lower case before upper case.
    mount_tool_options = [('h', '', 'shows this help')]

    if project_configuration.mount_tool_has_keys_option:
      mount_tool_options.append(
          ('k', 'keys', 'the key formatted in base16'))

    if project_configuration.mount_tool_has_password_option:
      mount_tool_options.append(
          ('p', 'password', 'specify the password/passphrase'))

    mount_tool_options.extend([
        ('v', '', ('verbose output to stderr, while {0:s} will remain '
                    'running in the foreground').format(mount_tool_name)),
        ('V', '', 'print version'),
        ('X', 'extended_options', 'extended options to pass to sub system')])

    return mount_tool_options

  def Generate(self, project_configuration, output_writer):
    """Generates tools source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    tools_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.tools_directory)

    library_header = 'yaltools_{0:s}.h'.format(
        project_configuration.library_name)

    if not os.path.exists(tools_path):
      return

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    # TODO: add support for ouput.[ch]

    for directory_entry in os.listdir(self._template_directory):
      # Ignore yaltools_library.h in favor of yaltools_libyal.h
      if directory_entry == library_header:
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == 'yaltools_libyal.h':
        output_filename = '{0:s}tools_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      else:
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.tools_directory, directory_entry[9:])

      output_filename = os.path.join(
          project_configuration.tools_directory, output_filename)

      if not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    mount_tool_name = '{0:s}mount'.format(
        project_configuration.library_name_suffix)

    mount_tool_filename = '{0:s}.c'.format(mount_tool_name)
    mount_tool_filename = os.path.join(
        project_configuration.tools_directory, mount_tool_filename)

    if os.path.exists(mount_tool_filename):
      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_handle.h')
      self._GenerateMountHandleHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_handle.c')
      self._GenerateMountHandleSourceFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      self._GenerateMountToolSourceFile(
          project_configuration, template_mappings, mount_tool_name,
          output_writer, mount_tool_filename)


class FileWriter(object):
  """File output writer."""

  def __init__(self, output_directory):
    """Initialize an output writer.

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
  """Stdout output writer."""

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
    print('-' * 80)
    print('{0: ^80}'.format(file_path))
    print('-' * 80)
    print('')
    print(file_data, end='')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates source files of the libyal libraries.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='CONFIGURATION_FILE',
      default='source.conf', help='The source generation configuration file.')

  argument_parser.add_argument(
      '-e', '--experimental', dest='experimental', action='store_true',
      default=False, help='enable experimental functionality.')

  argument_parser.add_argument(
      '-g', '--generators', dest='generators', action='store', default='all',
      help='names of the generators to run.')

  argument_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='path of the output files to write to.')

  argument_parser.add_argument(
      '-p', '--projects', dest='projects_directory', action='store',
      metavar='PROJECTS_DIRECTORY', default=None,
      help='path of the projects.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print('Config file missing.')
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

  project_configuration = configuration.ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_directory = options.projects_directory
  if not projects_directory:
    projects_directory = os.path.dirname(libyal_directory)

  # TODO: generate more source files.
  # AUTHORS, NEWS
  # include headers
  # yal.net files

  if options.generators == 'all':
    generators = []
  else:
    generators = options.generators.split(',')

  SOURCE_GENERATORS = [
      ('common', CommonSourceFileGenerator),
      ('config', ConfigurationFileGenerator),
      ('include', IncludeSourceFileGenerator),
      ('libyal', LibrarySourceFileGenerator),
      ('pyyal', PythonModuleSourceFileGenerator),
      ('scripts', ScriptFileGenerator),
      ('tests', TestsSourceFileGenerator),
      ('yaltools', ToolsSourceFileGenerator),
  ]

  sources_directory = os.path.join(
      libyal_directory, 'data', 'source')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(sources_directory, source_category,)
    source_file = source_generator_class(
        projects_directory, template_directory,
        experimental=options.experimental)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: dpkg handle dependencies

  # TODO: add support for Unicode templates.

  # TODO: generate manuals/Makefile.am

  source_files = [
      ('libyal.3', LibraryManPageGenerator),
  ]

  manuals_directory = os.path.join(
      libyal_directory, 'data', 'source', 'manuals')
  for source_category, source_generator_class in source_files:
    if generators and source_category not in generators:
      continue

    template_directory = os.path.join(manuals_directory, source_category)
    source_file = source_generator_class(
        projects_directory, template_directory,
        experimental=options.experimental)

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
