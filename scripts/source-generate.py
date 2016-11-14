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

import source_formatter


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
    self.tools_names = None

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
    self.tools_names = self._GetOptionalConfigValue(
        config_parser, u'tools', u'names', default_value=[])

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
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.

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


class EnumDeclaration(object):
  """Class that defines an enumeration type declaration.

  Attributes:
    name (str): name.
    constants (dict[str, str]): constant values per name.
  """

  def __init__(self, name):
    """Initializes an enumeration type declaration.

    Args:
      name (str): name.
    """
    super(EnumDeclaration, self).__init__()
    self.constants = collections.OrderedDict()
    self.name = name


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
    arguments (list[FunctionArgument]): function arguments.
    have_bfio (bool): True if the function prototype is defined if BFIO is
        defined.
    have_debug_output (bool): True if the function prototype is defined if
        debug output is defined.
    have_extern (bool): True if the function prototype is defined as
        externally available (API).
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
    self.arguments = []
    self.have_bfio = False
    self.have_debug_output = False
    self.have_extern = False
    self.have_wide_character_type = False
    self.name = name
    self.return_type = return_type

  def AddArgument(self, argument):
    """Adds an argument to the function prototype.

    Args:
      argument (FunctionArgument): function argument.
    """
    self.arguments.append(argument)

  def AddArgumentString(self, argument_string):
    """Adds an argument string to the function prototype.

    Args:
      argument_string (str): function argument.
    """
    function_argument = FunctionArgument(argument_string)
    self.arguments.append(function_argument)

  def CopyToString(self):
    """Copies the function prototype to a string.

    Returns:
      str: function prototype.
    """
    argument_strings = []
    for function_argument in self.arguments:
      argument_string = function_argument.CopyToString()
      argument_strings.append(argument_string)

    return u', '.join(argument_strings)


class PythonTypeObjectFunctionPrototype(object):
  """Class that defines a Python type object function prototype.

  Attributes:
    arguments (list[str]): arguments.
    name (str): name.
    return_type (str): return type.
  """
  FUNCTION_TYPE_CLOSE = u'close'
  FUNCTION_TYPE_COPY = u'copy'
  FUNCTION_TYPE_FREE = u'free'
  FUNCTION_TYPE_GET = u'get'
  FUNCTION_TYPE_INITIALIZE = u'initialize'
  FUNCTION_TYPE_OPEN = u'open'
  FUNCTION_TYPE_READ = u'read'
  FUNCTION_TYPE_SEEK = u'seek'
  FUNCTION_TYPE_SET = u'set'
  FUNCTION_TYPE_UTILITY = u'utility'
  FUNCTION_TYPE_WRITE = u'write'

  RETURN_TYPE_BINARY_DATA = u'binary_data'
  RETURN_TYPE_FILETIME = u'filetime'
  RETURN_TYPE_GUID = u'guid'
  RETURN_TYPE_NONE = u'none'
  RETURN_TYPE_INT = u'int'
  RETURN_TYPE_INT32 = u'int32'
  RETURN_TYPE_OBJECT = u'object'
  RETURN_TYPE_OFF64 = u'off64'
  RETURN_TYPE_POSIX_TIME = u'posix_time'
  RETURN_TYPE_SIZE32 = u'size32'
  RETURN_TYPE_SIZE64 = u'size64'
  RETURN_TYPE_STRING = u'string'
  RETURN_TYPE_UINT16 = u'uint16'
  RETURN_TYPE_UINT32 = u'uint32'
  RETURN_TYPE_UINT64 = u'uint64'

  def __init__(self, python_module_name, type_name, type_function):
    """Initializes a Python type object function prototype.

    Args:
      python_module_name (str): python module name.
      type_name (str): type name.
      type_function (str): type function.
    """
    if type_function == u'open_file_io_handle':
      type_function = u'open_file_object'

    super(PythonTypeObjectFunctionPrototype, self).__init__()
    self._function_type = None
    self._name = None
    self._python_module_name = python_module_name
    self._type_function = type_function
    self._type_name = type_name
    self._value_name = None
    self.arguments = u''
    self.return_type = self.RETURN_TYPE_NONE

  @property
  def function_type(self):
    """str: function type."""
    if self._function_type is None:
      if self._type_function == u'close':
        self._function_type = self.FUNCTION_TYPE_CLOSE

      elif self._type_function.startswith(u'copy_'):
        self._function_type = self.FUNCTION_TYPE_COPY

      elif self._type_function == u'free':
        self._function_type = self.FUNCTION_TYPE_FREE

      elif self._type_function.startswith(u'get_'):
        self._function_type = self.FUNCTION_TYPE_GET

      elif self._type_function == u'initialize':
        self._function_type = self.FUNCTION_TYPE_INITIALIZE

      elif (self._type_function == u'open' or
          self._type_function.startswith(u'open_')):
        self._function_type = self.FUNCTION_TYPE_OPEN

      elif self._type_function.startswith(u'read_'):
        self._function_type = self.FUNCTION_TYPE_READ

      elif self._type_function.startswith(u'seek_'):
        self._function_type = self.FUNCTION_TYPE_SEEK

      elif self._type_function.startswith(u'set_'):
        self._function_type = self.FUNCTION_TYPE_SET

      elif self._type_function == u'signal_abort':
        self._function_type = self.FUNCTION_TYPE_UTILITY

      # elif self._type_function.startswith(u'write_'):
      #   self._function_type = self.FUNCTION_TYPE_WRITE

    return self._function_type

  @property
  def name(self):
    """str: name."""
    if self._name is None:
      self._name = u'{0:s}_{1:s}_{2:s}'.format(
          self._python_module_name, self._type_name, self.type_function)

    return self._name

  @property
  def type_function(self):
    """str: type function."""
    if self._type_function.startswith(u'copy_'):
      return u'get_{0:s}'.format(self._type_function[5:])

    if (self._type_function.startswith(u'get_utf8_') or
        self._type_function.startswith(u'set_utf8_')):
      return u''.join([self._type_function[:4], self._type_function[9:]])

    # TODO: make more generic.
    if self._type_function == u'set_parent_file':
      return u'set_parent'

    return self._type_function

  def GetAttributeDescription(self):
    """Retrieves the fuction as attribute description.

    Returns:
      str: function as attribute description.
    """
    description = u''
    if self.function_type in (
        self.FUNCTION_TYPE_COPY, self.FUNCTION_TYPE_GET):
      if self._type_function == u'get_ascii_codepage':
        description = (
            u'The codepage used for ASCII strings in the {0:s}.').format(
                self._type_name)

      else:
        value_name = self.GetValueName()
        if value_name:
          value_name = value_name.replace(u'_', u' ')
          description = u'The {0:s}.'.format(value_name)

    return description

  def GetDescription(self):
    """Retrieves the description.

    Returns:
      list[str]: lines of the description.
    """
    description = [u'']
    if self.function_type == self.FUNCTION_TYPE_CLOSE:
      description = [u'Closes a {0:s}.'.format(self._type_name)]

    elif self.function_type in (
        self.FUNCTION_TYPE_COPY, self.FUNCTION_TYPE_GET):
      if self._type_function == u'get_ascii_codepage':
        description = [(
            u'Retrieves the codepage for ASCII strings used in '
            u'the {0:s}.').format(self._type_name)]

      elif self._type_function == u'get_offset':
        description = [u'Retrieves the current offset within the data.']

      else:
        value_name = self.GetValueName()
        if value_name:
          value_name = value_name.replace(u'_', u' ')
          description = [u'Retrieves the {0:s}.'.format(value_name)]

    elif self.function_type == self.FUNCTION_TYPE_OPEN:
      if self._type_function == u'open_file_object':
        description = [(
            u'Opens a {0:s} using a file-like object.').format(self._type_name)]
      else:
        description = [u'Opens a {0:s}.'.format(self._type_name)]

    elif self.function_type == self.FUNCTION_TYPE_READ:
      if self._type_function == u'read_buffer':
        description = [u'Reads a buffer of data.']

      elif self._type_function == u'read_buffer_at_offset':
        description = [u'Reads a buffer of data at a specific offset.']

    elif self.function_type == self.FUNCTION_TYPE_SEEK:
      if self._type_function == u'seek_offset':
        description = [u'Seeks an offset within the data.']

    elif self.function_type == self.FUNCTION_TYPE_SET:
      if self._type_function == u'set_ascii_codepage':
        description = [
            (u'Sets the codepage for ASCII strings used in the '
             u'{0:s}.').format(self._type_name),
            (u'Expects the codepage to be a string containing a Python '
             u'codec definition.')]

      elif self._type_function == u'set_parent':
        description = [u'Sets the parent file.']

      else:
        value_name = self.GetValueName()
        if value_name:
          value_name = value_name.replace(u'_', u' ')
          description = [u'Sets the {0:s}.'.format(value_name)]

    elif self.function_type == self.FUNCTION_TYPE_UTILITY:
      if self._type_function == u'signal_abort':
        description = [
            u'Signals the {0:s} to abort the current activity.'.format(
                self._type_name)]

    return description

  def GetReturnTypeDescription(self):
    """Retrieves the return type description.

    Returns:
      str: return type description.
    """
    if self.return_type == self.RETURN_TYPE_BINARY_DATA:
      return u'Binary string or None'

    if self.return_type in (
        self.RETURN_TYPE_FILETIME, self.RETURN_TYPE_POSIX_TIME):
      return u'Datetime or None'

    if self.return_type == self.RETURN_TYPE_OBJECT:
      return u'Object or None'

    if self.return_type in (
        self.RETURN_TYPE_INT, self.RETURN_TYPE_INT32, self.RETURN_TYPE_OFF64,
        self.RETURN_TYPE_SIZE32, self.RETURN_TYPE_SIZE64,
        self.RETURN_TYPE_UINT16, self.RETURN_TYPE_UINT32,
        self.RETURN_TYPE_UINT64):
      return u'Integer or None'

    if self.return_type in (
        self.RETURN_TYPE_GUID, self.RETURN_TYPE_STRING):
      return u'Unicode string or None'

    if self.return_type == self.RETURN_TYPE_NONE:
      return u'None'

    return self.return_type

  def GetValueName(self):
    """Retrieve the value name.

    Returns:
      str: value name or None.
    """
    if self._value_name is None:
      if self.function_type == self.FUNCTION_TYPE_COPY:
        if self._type_function.startswith(u'copy_'):
          self._value_name = self._type_function[5:]

      elif self.function_type == self.FUNCTION_TYPE_GET:
        if self._type_function.startswith(u'get_utf8_'):
          self._value_name = self._type_function[9:]

        elif self._type_function.startswith(u'get_'):
          self._value_name = self._type_function[4:]

      elif self.function_type == self.FUNCTION_TYPE_SET:
        if self._type_function.startswith(u'set_utf8_'):
          self._value_name = self._type_function[9:]

        elif self._type_function.startswith(u'set_'):
          self._value_name = self._type_function[4:]

    return self._value_name


class DefinitionsIncludeHeaderFile(object):
  """Class that defines a definitions include header file.

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
          enum_declaration = EnumDeclaration(line[enum_prefix_length:])


class LibraryHeaderFile(object):
  """Class that defines a library header file.

  Attributes:
    functions_per_name (dict[str, list[FunctionPrototype]]): function
        prototypes per name.
    path (str): path of the header file.
    types (list[str]): type names.
  """

  def __init__(self, path):
    """Initializes a library header file.

    Args:
      path (str): path of the header file.
    """
    super(LibraryHeaderFile, self).__init__()
    self.functions_per_name = collections.OrderedDict()
    self.path = path
    self.types = []

  def Read(self, project_configuration):
    """Reads the header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self.functions_per_name = collections.OrderedDict()
    self.types = []

    define_extern = b'{0:s}_EXTERN'.format(
        project_configuration.library_name.upper())

    define_have_debug_output = b'#if defined( HAVE_DEBUG_OUTPUT )'

    define_have_wide_character_type = (
        b'#if defined( HAVE_WIDE_CHARACTER_TYPE )')

    function_argument = None
    function_prototype = None
    have_extern = False
    have_debug_output = False
    have_wide_character_type = False
    in_function_prototype = False

    with open(self.path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_function_prototype:
          line = line.decode(u'ascii')

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
            self.functions_per_name[function_prototype.name] = (
                function_prototype)

            function_prototype = None
            in_function_prototype = False
            have_extern = False

        elif line.endswith(b'('):
          # Get the part of the line before the library name.
          return_type, _, _ = line.partition(
              project_configuration.library_name)

          # Get the part of the line after the return type.
          line = line[len(return_type):]
          return_type = return_type.strip()

          # Get the part of the remainder of the line before the '('.
          name, _, _ = line.partition(u'(')

          function_prototype = FunctionPrototype(name, return_type)
          function_prototype.have_extern = have_extern
          function_prototype.have_debug_output = have_debug_output
          function_prototype.have_wide_character_type = (
              have_wide_character_type)

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
  """Class that defines a library include header file.

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

  _SIGNATURE_TYPES = (u'file', u'volume')

  def __init__(self, path):
    """Initializes a library include header file.

    Args:
      path (str): path library include header file.
    """
    super(LibraryIncludeHeaderFile, self).__init__()
    self._api_functions = []
    self._api_functions_with_input = []
    self._api_types = []
    self._api_types_with_input = []
    self._check_signature_type = None
    self._path = path

    self.functions_per_name = collections.OrderedDict()
    self.functions_per_section = {}
    self.have_bfio = False
    self.have_wide_character_type = False
    self.name = os.path.basename(path)
    self.section_names = []

  def _AnalyzeTestGroups(self, project_configuration):
    """Analyzes the library include header file for test groups.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._api_functions = []
    self._api_functions_with_input = []
    self._api_types = []
    self._api_types_with_input = []

    signature_type = self.GetCheckSignatureType(project_configuration)
    if signature_type:
      self._api_functions_with_input.append(u'support')
    else:
      self._api_functions.append(u'support')

    for section_name, functions in self.functions_per_section.items():
      if not functions:
        continue

      function_name = None
      for function_prototype in functions:
        if function_prototype.name.endswith(u'_free'):
          function_name = function_prototype.name
          _, _, function_name = function_name.rpartition(
              project_configuration.library_name)
          function_name, _, _ = function_name.rpartition(u'_free')
          break

      section_name = section_name.replace(u' ', u'_')
      section_name = section_name.lower()
      section_name, _, _ = section_name.rpartition(u'_functions')

      function_name_prefix = u'{0:s}_{1:s}_'.format(
          project_configuration.library_name, section_name)

      function_prototype = functions[0]
      if not function_prototype.name.startswith(function_name_prefix):
        # Ignore the section header is just informative.
        continue

      if (section_name == u'error' and
          project_configuration.library_name != u'libcerror'):
        self._api_functions.append(section_name)
        continue

      function_name = u'{0:s}_{1:s}_free'.format(
          project_configuration.library_name, section_name)

      if function_name not in self.functions_per_name:
        self._api_functions.append(section_name)
        continue

      function_name = u'{0:s}_{1:s}_open'.format(
          project_configuration.library_name, section_name)

      if function_name in self.functions_per_name:
        self._api_types_with_input.append(section_name)
      else:
        self._api_types.append(section_name)

  def GetAPIFunctionTestGroups(self, project_configuration):
    """Determines the API function test groups.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      tuple: contains:
        list[str]: names of API function groups without test data.
        list[str]: names of API function groups with test data.
    """
    if not self._api_functions and not self._api_functions_with_input:
      self._AnalyzeTestGroups(project_configuration)

    return self._api_functions, self._api_functions_with_input

  def GetAPITypeTestGroups(self, project_configuration):
    """Determines the API type test groups.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      tuple: contains:
        list[str]: names of API type groups without test data.
        list[str]: names of API type groups with test data.
    """
    if not self._api_types and not self._api_types_with_input:
      self._AnalyzeTestGroups(project_configuration)

    return self._api_types, self._api_types_with_input

  def GetCheckSignatureType(self, project_configuration):
    """Determines the check signature function type.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      str: check signature function type of None if no check signature function
          was found.
    """
    if not self._check_signature_type:
      for signature_type in self._SIGNATURE_TYPES:
        function_name = u'{0:s}_check_{1:s}_signature'.format(
            project_configuration.library_name, signature_type)

        if function_name in self.functions_per_name:
          self._check_signature_type = signature_type
          break

    return self._check_signature_type

  def Read(self, project_configuration):
    """Reads the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self.functions_per_name = collections.OrderedDict()
    self.functions_per_section = {}
    self.have_bfio = False
    self.have_wide_character_type = False
    self.section_names = []

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
              have_extern = False

          elif line.endswith(u';'):
            # The line contains a variable definition.
            have_extern = False

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
  """Class that defines a library Makefile.am file.

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
    self._path = path

    self.cppflags = []
    self.libraries = []
    self.sources = []

  def Read(self, project_configuration):
    """Reads the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self.cppflags = []
    self.libraries = []
    self.sources = []

    library_sources = b'{0:s}_la_SOURCES'.format(
        project_configuration.library_name)

    library_libadd = b'{0:s}_la_LIBADD'.format(
        project_configuration.library_name)

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

          if (in_section == u'cppflags' and line.startswith(b'@') and
              line.endswith(b'_CPPFLAGS@')):
              self.cppflags.append(line[1:-10].lower())

          elif (in_section == u'libadd' and line.startswith(b'@') and
                line.endswith(b'_LIBADD@')):
              self.libraries.append(line[1:-8].lower())

          elif in_section == u'sources':
            sources = line.split(b' ')
            self.sources.extend(sources)

        elif line == b'AM_CPPFLAGS = \\':
          in_section = u'cppflags'

        elif line.startswith(library_libadd):
          in_section = u'libadd'

        elif line.startswith(library_sources):
          in_section = u'sources'

    self.libraries = sorted(self.libraries)


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

  def Read(self, project_configuration):
    """Reads the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
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


class TypesIncludeHeaderFile(object):
  """Class that defines a types include header file.

  Attributes:
    types (list[str]): type names.
  """

  def __init__(self, path):
    """Initializes a types include header file.

    Args:
      path (str): path of the include header file.
    """
    super(TypesIncludeHeaderFile, self).__init__()
    self._path = path

    self.types = []

  def Read(self, project_configuration):
    """Reads the include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self.types = []

    typedef_prefix = b'typedef intptr_t {0:s}_'.format(
        project_configuration.library_name)
    typedef_prefix_length = len(typedef_prefix)

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if line.startswith(typedef_prefix) and line.endswith(b'_t;'):
          self.types.append(line[typedef_prefix_length:-3])


class SourceFileGenerator(object):
  """Class that generates source files."""

  def __init__(
      self, projects_directory, template_directory, experimental=False):
    """Initialize the source file generator.

    Args:
      projects_directory (str): path of the projects directory.
      template_directory (str): path of the template directory.
      experimental (bool): True if experimental features should be enabled.
    """
    super(SourceFileGenerator, self).__init__()
    self._definitions_include_header_file = None
    self._definitions_include_header_path = None
    self._experimental = experimental
    self._has_python_module = None
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
          u'Unable to format template: {0:s} with error: {1:s}'.format(
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
          u'include', project_configuration.library_name, u'definitions.h.in')

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
      self._library_include_header_path = u'{0:s}.h.in'.format(
          project_configuration.library_name)
      self._library_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          u'include', self._library_include_header_path)

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
          project_configuration.library_name, u'Makefile.am')

      if os.path.exists(self._library_makefile_am_path):
        self._library_makefile_am_file = LibraryMakefileAMFile(
            self._library_makefile_am_path)
        self._library_makefile_am_file.Read(project_configuration)

    return self._library_makefile_am_file

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
    header_file_path = u'{0:s}_{1:s}.h'.format(
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
          u'include', project_configuration.library_name, u'types.h.in')

      if os.path.exists(self._types_include_header_path):
        self._types_include_header_file = TypesIncludeHeaderFile(
            self._types_include_header_path)
        self._types_include_header_file.Read(project_configuration)

    return self._types_include_header_file

  def _HasPythonModule(self, project_configuration):
    """Determines if the project has a Python module.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the python module path exits.
    """
    if not self._python_module_path:
      self._python_module_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          project_configuration.python_module_name)

      self._has_python_module = os.path.exists(self._python_module_path)

    return self._has_python_module

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
          u'tests')

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

  def _SortIncludeHeaders(self, project_configuration, output_filename):
    """Sorts the include headers within a source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
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

  def _SortVariableDeclarations(self, output_filename):
    """Sorts the variable declarations within a source file.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = [line for line in file_object.readlines()]

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
      lines = [line for line in file_object.readlines()]

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
      lines = [line for line in file_object.readlines()]

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

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          u'Missing: {0:s} skipping generation of configuration files.'.format(
              self._library_makefile_am_path))
      return

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


class IncludeSourceFileGenerator(SourceFileGenerator):
  """Class that generates the include source files."""

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
        self._template_directory, u'libyal', u'features.h.in')

    template_filename = os.path.join(template_directory, u'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if include_header_file.have_wide_character_type:
      template_filename = os.path.join(
          template_directory, u'wide_character_type.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: improve detection if include is needed.
    if u'libcthreads' in makefile_am_file.libraries:
      template_filename = os.path.join(template_directory, u'multi_thread.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if include_header_file.have_bfio:
      template_filename = os.path.join(template_directory, u'bfio.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

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
        self._template_directory, u'libyal', u'types.h.in')

    type_definitions = []
    for type_name in sorted(project_configuration.library_public_types):
      type_definition = u'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings[u'library_type_definitions'] = u'\n'.join(
        type_definitions)

    template_filename = os.path.join(template_directory, u'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if type_definitions:
      template_filename = os.path.join(template_directory, u'public_types.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.h')
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
          u'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'Makefile.am')

    makefile_am_file = MainMakefileAMFile(makefile_am_path)
    makefile_am_file.Read(project_configuration)

    pkginclude_headers = [
        u'\t{0:s}/definitions.h \\'.format(project_configuration.library_name),
        u'\t{0:s}/error.h \\'.format(project_configuration.library_name),
        u'\t{0:s}/extern.h \\'.format(project_configuration.library_name),
        u'\t{0:s}/features.h \\'.format(project_configuration.library_name),
        u'\t{0:s}/types.h'.format(project_configuration.library_name)]

    function_name = u'{0:s}_get_codepage'.format(
        project_configuration.library_name)
    if function_name in include_header_file.functions_per_name:
      pkginclude_header = u'\t{0:s}/codepage.h \\'.format(
          project_configuration.library_name)
      pkginclude_headers.append(pkginclude_header)

    pkginclude_headers = sorted(pkginclude_headers)

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')
    template_mappings[u'pkginclude_headers'] = u'\n'.join(pkginclude_headers)

    template_filename = os.path.join(self._template_directory, u'Makefile.am')

    output_filename = os.path.join(u'include', u'Makefile.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    output_directory = os.path.join(
        u'include', project_configuration.library_name)
    template_directory = os.path.join(self._template_directory, u'libyal')
    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      if (directory_entry not in (u'definitions.h.in', u'extern.h') and
          not os.path.exists(output_filename)):
        continue

      # Do not overwrite defintions.h.in when it exist.
      if (directory_entry != u'definitions.h.in' and
          os.path.exists(output_filename)):
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in (u'codepage.h', u'definitions.h.in', u'error.h'):
        self._VerticalAlignTabs(output_filename)

    output_filename = os.path.join(output_directory, u'features.h.in')
    self._GenerateFeaturesHeader(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

    output_filename = os.path.join(output_directory, u'types.h.in')
    self._GenerateTypesHeader(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)


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
    # TODO: libsmraw/libsmraw_codepage.h alignment of definitions
    # TODO: libfvalue/libfvalue_codepage.h different

    include_header_file = self._GetTypesIncludeHeaderFile(project_configuration)

    if not include_header_file:
      logging.warning(
          u'Missing: {0:s} skipping generation of library source files.'.format(
              self._types_include_header_path))
      return

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
    type_definitions = []
    for type_name in include_header_file.types:
      library_debug_type_prefix = u'typedef struct {0:s}_{1:s} {{}}'.format(
          project_configuration.library_name, type_name)

      library_debug_type_definition = (
          u'typedef struct {0:s}_{1:s} {{}}\t{0:s}_{1:s}_t;').format(
              project_configuration.library_name, type_name)
      library_debug_type_definitions.append(library_debug_type_definition)

      type_definition = u'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')
    template_mappings[u'library_debug_type_definitions'] = u'\n'.join(
        library_debug_type_definitions)
    template_mappings[u'library_type_definitions'] = u'\n'.join(
        type_definitions)

    authors_template_mapping = template_mappings[u'authors']

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith(u'libyal'):
        continue

      if directory_entry.endswith(u'_{0:s}.h'.format(
          project_configuration.library_name)):
        continue

      if (directory_entry == u'libyal_codepage.h' and (
          not os.path.exists(codepage_header_file) or
          project_configuration.library_name == u'libclocale')):
        continue

      if ((directory_entry == u'libyal_libcerror.h' or
           directory_entry == u'libyal_error.c' or
           directory_entry == u'libyal_error.h') and (
               not os.path.exists(error_header_file) or
               project_configuration.library_name == u'libcerror')):
        continue

      if ((directory_entry == u'libyal_libcnotify.h' or
           directory_entry == u'libyal_notify.c' or
           directory_entry == u'libyal_notify.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == u'libcnotify')):
        continue

      # TODO: improve generation of _types.h file
      if (directory_entry == u'libyal_types.h' and (
              not os.path.exists(types_header_file) or
              project_configuration.library_name in (
                  u'libcerror', u'libcthreads'))):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = u'{0:s}{1:s}'.format(
          project_configuration.library_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.library_name, output_filename)

      if not os.path.exists(output_filename) and not directory_entry in (
          u'libyal.c', u'libyal_extern.h', u'libyal.rc.in', u'libyal_support.c',
          u'libyal_support.h', u'libyal_unused.h'):
        continue

      if directory_entry == u'libyal.rc.in':
        template_mappings[u'authors'] = u', '.join(
            project_configuration.project_authors)
      else:
        template_mappings[u'authors'] = authors_template_mapping

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in (u'libyal_codepage.h', u'libyal_types.h'):
        self._VerticalAlignTabs(output_filename)


class LibraryManPageGenerator(SourceFileGenerator):
  """Class that generates the library man page file (libyal.3)."""

  def Generate(self, project_configuration, output_writer):
    """Generates a library man page file (libyal.3).

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: add support for libcthreads.h - messed up
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
          u'Missing: {0:s} skipping generation of library man page.'.format(
              self._library_include_header_path))
      return

    # TODO: improve method of determining main include header has changed.
    stat_object = os.stat(self._library_include_header_path)
    modification_time = time.gmtime(stat_object.st_mtime)

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
    output_filename = u'{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_definitions')

    template_mappings[u'definitions_name'] = definitions_name
    template_mappings[u'definitions_name_upper_case'] = definitions_name.upper()
    template_mappings[u'definitions_description'] = definitions_name.replace(
        u'_', u' ')

    template_filename = os.path.join(template_directory, u'pyyal_definitions.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

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
    output_filename = u'{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_definitions')

    template_mappings[u'definitions_name'] = definitions_name
    template_mappings[u'definitions_name_upper_case'] = definitions_name.upper()
    template_mappings[u'definitions_description'] = definitions_name.replace(
        u'_', u' ')

    template_mappings[u'definition_name'] = definitions_name[:-1]
    template_mappings[u'definition_name_upper_case'] = (
        definitions_name[:-1].upper())

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    constant_name_prefix = u'{0:s}_{1:s}_'.format(
        project_configuration.library_name, definitions_name[:-1])
    constant_name_prefix_length = len(constant_name_prefix)

    for constant_name in enum_declaration.constants.keys():
      constant_name = constant_name.lower()
      if not constant_name.startswith(constant_name_prefix):
        continue

      constant_name = constant_name[constant_name_prefix_length:]
      template_mappings[u'constant_name'] = constant_name
      template_mappings[u'constant_name_upper_case'] = constant_name.upper()

      template_filename = os.path.join(template_directory, u'constant.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

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
    output_filename = u'{0:s}_{1:s}s.h'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_sequence_type')

    template_filename = os.path.join(
        template_directory, u'pyyal_sequence_type.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateSequenceTypeSourceFile(
      self, project_configuration, template_mappings, type_name, output_writer):
    """Generates a Python sequence type object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
    """
    output_filename = u'{0:s}_{1:s}s.c'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_sequence_type')

    template_filename = os.path.join(
        template_directory, u'pyyal_sequence_type.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: combine vertical align functions.
    self._SortIncludeHeaders(project_configuration, output_filename)
    self._VerticalAlignAssignmentStatements(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateTypeHeaderFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer):
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
    """
    output_filename = u'{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    open_support = u'open' in python_function_prototypes
    with_parent = (
        u'initialize' not in python_function_prototypes and
        u'free' in python_function_prototypes)

    template_directory = os.path.join(self._template_directory, u'pyyal_type')

    template_filename = os.path.join(template_directory, u'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if open_support:
      template_filename = u'includes_with_input.h'
    else:
      template_filename = u'includes.h'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if open_support:
      template_filename = u'typedef_with_input.h'
    elif with_parent:
      template_filename = u'typedef_with_parent.h'
    else:
      template_filename = u'typedef.h'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    python_type_prefix = u'{0:s}_{1:s}'.format(
        project_configuration.python_module_name, type_name)

    if open_support:
      template_filename = u'new_with_input.h'
    elif with_parent:
      template_filename = u'new_with_parent.h'
    else:
      template_filename = u'new.h'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if open_support:
      template_filename = os.path.join(template_directory, u'new_open.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      # TODO: make open with file object object generated conditionally?
      # if u'open_file_object' in python_function_prototypes:

    template_filename = os.path.join(template_directory, u'init.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, u'free.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in (u'free', u'initialize'):
        continue

      if python_function_prototype.function_type in (
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_COPY,
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET,
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_SET):
        value_name = python_function_prototype.GetValueName()
      else:
        value_name = None

      template_filename = u'{0:s}.h'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None
        if python_function_prototype.function_type == (
            PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET):

          if (python_function_prototype.arguments and
              not type_function.endswith(u'_by_name') and
              not type_function.endswith(u'_by_path')):
            template_filename = u'get_{0:s}_value_by_index.h'.format(
                python_function_prototype.return_type)

          elif python_function_prototype.return_type in (
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_FILETIME,
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_POSIX_TIME):
            template_filename = u'get_datetime_value.h'

        if not template_filename:
          if python_function_prototype.arguments:
            template_filename = u'type_object_function_with_args.h'
          else:
            template_filename = u'type_object_function.h'

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning(u'Template missing for type function: {0:s}'.format(
            type_function))
        continue

      template_mappings[u'type_function'] = type_function
      template_mappings[u'type_function_upper_case'] = type_function.upper()

      if value_name:
        template_mappings[u'value_description'] = value_name.replace(u'_', u' ')
        template_mappings[u'value_name'] = value_name

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateTypeSourceFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer):
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
    """
    output_filename = u'{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    bfio_support = u'open_file_object' in python_function_prototypes
    codepage_support = u'get_ascii_codepage' in python_function_prototypes
    datetime_support = False
    guid_support = False
    integer_support = False
    open_support = u'open' in python_function_prototypes
    with_parent = (
        u'initialize' not in python_function_prototypes and
        u'free' in python_function_prototypes)

    for python_function_prototype in python_function_prototypes.values():
      if python_function_prototype.return_type in (
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_FILETIME,
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_POSIX_TIME):
        datetime_support = True
        integer_support = True

      elif python_function_prototype.return_type == (
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_GUID):
        guid_support = True

      elif python_function_prototype.return_type in (
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_SIZE64,
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_OFF64,
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_UINT64):
        integer_support = True

    template_directory = os.path.join(self._template_directory, u'pyyal_type')

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    python_module_include_names = [
        project_configuration.library_name, type_name, u'error', u'libcerror',
        u'python', u'unused']

    # TODO: include header of sub types
    # TODO: include header of sequence types

    if bfio_support:
      python_module_include_names.extend([u'file_object_io_handle', 'libbfio'])
    if codepage_support:
      python_module_include_names.extend([u'codepage', 'libclocale'])
    if datetime_support:
      python_module_include_names.append(u'datetime')
    if guid_support:
      python_module_include_names.append(u'guid')
    if integer_support:
      python_module_include_names.append(u'integer')

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = u'#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    template_mappings[u'python_module_includes'] = u'\n'.join(
        python_module_includes)

    if codepage_support:
      template_filename = u'includes_with_codepage.c'
    else:
      template_filename = u'includes.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if bfio_support:
      template_filename = os.path.join(template_directory, u'have_bfio.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    self._GenerateTypeSourceFileTypeObjectMethods(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    self._GenerateTypeSourceFileTypeObjectGetSetDefinitions(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    template_filename = os.path.join(template_directory, u'type_object.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if with_parent:
      template_filename = u'new_with_parent.c'
    else:
      template_filename = u'new.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if open_support:
      template_filename = os.path.join(template_directory, u'new_open.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if with_parent:
      template_filename = u'init_with_parent.c'
    else:
      template_filename = u'init.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    if with_parent:
      template_filename = u'free_with_parent.c'
    else:
      template_filename = u'free.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in (u'free', u'initialize'):
        continue

      if python_function_prototype.function_type in (
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_COPY,
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET,
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_SET):
        value_name = python_function_prototype.GetValueName()
      else:
        value_name = None

      template_filename = u'{0:s}.c'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None

        if python_function_prototype.function_type == (
            PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_COPY):
          template_filename = u'copy_{0:s}_value.c'.format(
              python_function_prototype.return_type)

        elif python_function_prototype.function_type == (
            PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET):

          if not python_function_prototype.arguments:
            if value_name.startswith(u'number_of_recovered_'):
              value_name = value_name[20:]
              template_filename = u'get_number_of_recovered_{0:s}_value.c'.format(
                  python_function_prototype.return_type)

            else:
              template_filename = u'get_{0:s}_value.c'.format(
                  python_function_prototype.return_type)

          else:
            if type_function.endswith(u'_by_name'):
              template_filename = u'get_{0:s}_value_by_name.c'.format(
                  python_function_prototype.return_type)

            elif type_function.endswith(u'_by_path'):
              template_filename = u'get_{0:s}_value_by_path.c'.format(
                  python_function_prototype.return_type)

            else:
              if value_name.startswith(u'recovered_'):
                value_name = value_name[10:]
                template_filename = u'get_recovered_{0:s}_value_by_index.c'.format(
                    python_function_prototype.return_type)

              else:
                template_filename = u'get_{0:s}_value_by_index.c'.format(
                    python_function_prototype.return_type)

        elif python_function_prototype.function_type == (
            PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_SET):

          # TODO: make more generic.
          if type_function == u'set_password':
            template_filename = u'set_{0:s}_value.c'.format(u'string')

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning(u'Template missing for type function: {0:s}'.format(
            type_function))
        continue

      if value_name:
        template_mappings[u'value_description'] = value_name.replace(u'_', u' ')
        template_mappings[u'value_name'] = value_name

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: combine vertical align functions.
    self._SortIncludeHeaders(project_configuration, output_filename)
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
    template_directory = os.path.join(self._template_directory, u'pyyal_type')

    python_type_object_methods = []
    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in (u'free', u'initialize'):
        continue

      if not python_function_prototype.arguments:
        arguments_flags = u'METH_NOARGS'
      else:
        arguments_flags = u'METH_VARARGS | METH_KEYWORDS'

      return_type = python_function_prototype.GetReturnTypeDescription()
      python_type_object_methods.extend([
          u'',
          u'\t{{ "{0:s}",'.format(type_function),
          u'\t  (PyCFunction) {0:s},'.format(python_function_prototype.name),
          u'\t  {0:s},'.format(arguments_flags),
          u'\t  "{0:s}({1:s}) -> {2:s}\\n"'.format(
              type_function, python_function_prototype.arguments, return_type),
          u'\t  "\\n"'])

      description = python_function_prototype.GetDescription()
      for index, line in enumerate(description):
        if index < len(description) - 1:
          python_type_object_methods.append(u'\t  "{0:s}\\n"'.format(line))
        else:
          python_type_object_methods.append(u'\t  "{0:s}" }},'.format(line))

      if (type_function == u'get_offset' and
          u'read_buffer' in python_function_prototypes and
          u'seek_offset' in python_function_prototypes):

        python_type_object_methods.extend([
            u'',
            u'\t{ "read",',
            u'\t  (PyCFunction) {0:s}_{1:s}_read_buffer,'.format(
                project_configuration.python_module_name, type_name),
            u'\t  METH_VARARGS | METH_KEYWORDS,',
            u'\t  "read(size) -> String\\n"',
            u'\t  "\\n"',
            u'\t  "Reads a buffer of data." },',
            u'',
            u'\t{ "seek",',
            u'\t  (PyCFunction) {0:s}_{1:s}_seek_offset,'.format(
                project_configuration.python_module_name, type_name),
            u'\t  METH_VARARGS | METH_KEYWORDS,',
            u'\t  "seek(offset, whence) -> None\\n"',
            u'\t  "\\n"',
            u'\t  "Seeks an offset within the data." },',
            u'',
            u'\t{ "tell",',
            u'\t  (PyCFunction) {0:s}_{1:s}_get_offset,'.format(
                project_configuration.python_module_name, type_name),
            u'\t  METH_NOARGS,',
            u'\t  "tell() -> Integer\\n"',
            u'\t  "\\n"',
            u'\t  "Retrieves the current offset within the data." },'])

      elif python_function_prototype.return_type in (
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_FILETIME,
          PythonTypeObjectFunctionPrototype.RETURN_TYPE_POSIX_TIME):

        python_type_object_methods.extend([
            u'',
            u'\t{{ "{0:s}_as_integer",'.format(type_function),
            u'\t  (PyCFunction) {0:s}_as_integer,'.format(
                python_function_prototype.name),
            u'\t  METH_NOARGS,',
            u'\t  "{0:s}_as_integer({1:s}) -> Integer or None\\n"'.format(
                type_function,
                python_function_prototype.arguments),
            u'\t  "\\n"'])

        if python_function_prototype.return_type == (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_FILETIME):

          description[0] = (
              u'{0:s} as a 64-bit integer containing a FILETIME value.').format(
                  description[0][:-1])

        elif python_function_prototype.return_type == (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_POSIX_TIME):

          description[0] = (
              u'{0:s} as a 32-bit integer containing a POSIX timestamp '
              u'value.').format(description[0][:-1])

        for index, line in enumerate(description):
          if index < len(description) - 1:
            python_type_object_methods.append(u'\t  "{0:s}\\n"'.format(line))
          else:
            python_type_object_methods.append(u'\t  "{0:s}" }},'.format(line))

      elif (python_function_prototype.arguments and
          python_function_prototype.return_type in (
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_OBJECT,
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_STRING)):
          # TODO: add method for the sequence object.
          pass

    python_type_object_methods.extend([
        u'',
        u'\t/* Sentinel */',
        u'\t{ NULL, NULL, 0, NULL }'])

    template_mappings[u'python_type_object_methods'] = u'\n'.join(
        python_type_object_methods)

    template_filename = os.path.join(
        template_directory, u'type_object_methods.c')
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
    template_directory = os.path.join(self._template_directory, u'pyyal_type')

    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if python_function_prototype.function_type not in (
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_COPY,
          PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET):
        continue

      if (type_function == u'get_offset' and
          u'read_buffer' in python_function_prototypes and
          u'seek_offset' in python_function_prototypes):
        continue

      if type_function != u'get_ascii_codepage':
        setter_function = u'0'
      else:
        setter_function = (
            u'{0:s}_{1:s}_set_ascii_codepage_setter').format(
                project_configuration.python_module_name, type_name)

      description = python_function_prototype.GetAttributeDescription()

      if not python_function_prototype.arguments:
        python_type_object_get_set_definitions.extend([
            u'',
            u'\t{{ "{0:s}",'.format(type_function[4:]),
            u'\t  (getter) {0:s},'.format(python_function_prototype.name),
            u'\t  (setter) {0:s},'.format(setter_function),
            u'\t  "{0:s}",'.format(description),
            u'\t  NULL },'])

      if (python_function_prototype.arguments and
          python_function_prototype.return_type in (
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_OBJECT,
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_STRING)):

        python_type_object_get_set_definitions.extend([
            u'',
            u'\t{{ "{0:s}s",'.format(type_function[4:]),
            u'\t  (getter) {0:s}s,'.format(python_function_prototype.name),
            u'\t  (setter) {0:s},'.format(setter_function),
            u'\t  "{0:s}s.",'.format(description[:-1]),
            u'\t  NULL },'])

    python_type_object_get_set_definitions.extend([
        u'',
        u'\t/* Sentinel */',
        u'\t{ NULL, NULL, NULL, NULL, NULL }'])

    template_mappings[u'python_type_object_get_set_definitions'] = u'\n'.join(
        python_type_object_get_set_definitions)

    template_filename = os.path.join(
        template_directory, u'type_object_get_set_definitions.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GetPythonTypeObjectFunctionPrototypes(
      self, project_configuration, type_name):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

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
      logging.warning(u'Skipping: {0:s}'.format(header_file.path))
      return

    library_type = u'{0:s}_{1:s}_t *'.format(
        project_configuration.library_name, type_name)

    function_name_prefix = u'{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    functions_per_name = header_file.functions_per_name

    python_function_prototypes = collections.OrderedDict()
    for function_name, function_prototype in iter(functions_per_name.items()):
      if not function_prototype.have_extern:
        continue

      if not function_name.startswith(function_name_prefix):
        logging.warning(u'Skipping unsupported API function: {0:s}'.format(
            function_name))
        continue

      type_function = function_name[function_name_prefix_length:]
      if type_function in (u'open_wide', ):
        continue

      elif (type_function.startswith(u'get_utf8_') and
          type_function.endswith(u'_size')):
        continue

      elif (type_function.startswith(u'get_utf16_') or
            type_function.startswith(u'set_utf16_')):
        continue

      elif (type_function.startswith(u'get_') and
          type_function.endswith(u'_data_size')):
        continue

      python_function_prototype = PythonTypeObjectFunctionPrototype(
          project_configuration.python_module_name, type_name, type_function)

      function_arguments = []
      # TODO: add support for glob functions
      # TODO: add support for has, is functions
      # TODO: add support for seek, read, write functions

      if type_function == u'get_ascii_codepage':
        # TODO: replace this by RETURN_TYPE_STRING.
        python_function_prototype.return_type = u'String'

      elif type_function.startswith(u'copy_'):
        python_function_prototype.return_type = (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_BINARY_DATA)

      elif type_function.startswith(u'get_utf8_'):
        python_function_prototype.return_type = (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_STRING)

        for function_argument in function_prototype.arguments:
          function_argument_string = function_argument.CopyToString()
          if (function_argument_string.startswith(library_type) or
              function_argument_string.startswith(u'libcerror_error_t **')):
            continue

          if (function_argument_string != u'uint8_t *utf8_string' and
              function_argument_string != u'size_t utf8_string_size'):
            _, _, argument_name = function_argument_string.rpartition(u' ')
            argument_name = argument_name.lstrip(u'*')
            if not python_function_prototype.arguments:
              python_function_prototype.arguments = argument_name
            else:
              python_function_prototype.arguments = u', '.join([
                  python_function_prototype.arguments, argument_name])

      elif type_function.startswith(u'get_'):
        for function_argument in function_prototype.arguments:
          function_argument_string = function_argument.CopyToString()
          if (function_argument_string.startswith(library_type) or
              function_argument_string.startswith(u'libcerror_error_t **')):
            continue

          if function_argument_string == u'uint64_t *filetime':
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_FILETIME)

          elif function_argument_string == u'uint32_t *posix_time':
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_POSIX_TIME)

          elif function_argument_string == u'uint8_t *data':
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_BINARY_DATA)

          elif function_argument_string == u'uint8_t *guid_data':
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_GUID)

          elif function_argument_string.startswith(u'int *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_INT)

          elif function_argument_string.startswith(u'int32_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_INT32)

          elif function_argument_string.startswith(u'off64_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_OFF64)

          elif function_argument_string.startswith(u'size32_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_SIZE32)

          elif function_argument_string.startswith(u'size64_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_SIZE64)

          elif function_argument_string.startswith(u'uint16_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_UINT16)

          elif function_argument_string.startswith(u'uint32_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_UINT32)

          elif function_argument_string.startswith(u'uint64_t *'):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_UINT64)

          elif function_argument_string.startswith(
              project_configuration.library_name):
            python_function_prototype.return_type = (
                PythonTypeObjectFunctionPrototype.RETURN_TYPE_OBJECT)

          elif (function_argument_string != u'size_t data_size' and
              function_argument_string != u'size_t guid_data_size'):
            _, _, argument_name = function_argument_string.rpartition(u' ')
            argument_name = argument_name.lstrip(u'*')
            if not python_function_prototype.arguments:
              python_function_prototype.arguments = argument_name
            else:
              python_function_prototype.arguments = u', '.join([
                  python_function_prototype.arguments, argument_name])

      elif type_function == u'open':
        python_function_prototype.arguments = u'filename, mode=\'r\''

      elif type_function == u'open_file_io_handle':
        python_function_prototype.arguments = u'file_object, mode=\'r\''

      elif type_function == u'read_buffer':
        python_function_prototype.return_type = (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_BINARY_DATA)
        python_function_prototype.arguments = u'size'

      elif type_function == u'read_buffer_at_offset':
        python_function_prototype.return_type = (
            PythonTypeObjectFunctionPrototype.RETURN_TYPE_BINARY_DATA)
        python_function_prototype.arguments = u'size, offset'

      elif type_function == u'seek_offset':
        python_function_prototype.arguments = u'offset, whence'

      elif type_function == u'set_ascii_codepage':
        python_function_prototype.arguments = u'codepage'

      # TODO: make more generic.
      elif type_function == u'set_parent_file':
        python_function_prototype.arguments = u'parent_file'

      elif type_function == u'set_password':
        python_function_prototype.arguments = u'password'

      if not python_function_prototype.function_type:
        logging.warning(u'Skipping unsupported type function: {0:s}'.format(
            function_name))
        continue

      type_function = python_function_prototype.type_function
      python_function_prototypes[type_function] = python_function_prototype

    return python_function_prototypes

  def _GetTemplateMappings(self, project_configuration):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')

    # TODO: have source formatter take care of the alignment.
    # Used to align source in pyyal/pyyal_file_object_io_handle.c
    alignment_padding = len(project_configuration.library_name) - 6
    template_mappings[u'alignment_padding'] = u' ' * alignment_padding

    return template_mappings

  def _VerticalAlignFunctionArguments(self, output_filename):
    """Vertically aligns function arguments.

    Note this is a very basic approach that should suffice for the Python
    module source files.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = [line for line in file_object.readlines()]

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
    # TODO: handle get_X_by_utf8_name
    # TODO: generate pyyal/Makefile.am
    # TODO: generate pyyal-python2/Makefile.am
    # TODO: generate pyyal-python3/Makefile.am
    # TODO: align assiment statements =

    if not self._HasPythonModule(project_configuration):
      return

    template_mappings = self._GetTemplateMappings(project_configuration)

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith(u'pyyal_'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      force_create = False

      output_filename = u'{0:s}_{1:s}'.format(
          project_configuration.python_module_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.python_module_name, output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry == u'pyyal_file_object_io_handle.c':
        self._SortVariableDeclarations(output_filename)

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning((
          u'Missing: {0:s} skipping generation of Python type object '
          u'source and header files.').format(
              self._library_include_header_path))
    else:
      api_types, api_types_with_input = (
          include_header_file.GetAPITypeTestGroups(project_configuration))

      sequence_types = []

      api_types.extend(api_types_with_input)
      for type_name in list(api_types):
        template_mappings[u'type_name'] = type_name
        template_mappings[u'type_name_upper_case'] = type_name.upper()
        template_mappings[u'type_description'] = type_name.replace(u'_', u' ')

        python_function_prototypes = self._GetPythonTypeObjectFunctionPrototypes(
            project_configuration, type_name)

        for type_function, python_function_prototype in iter(
            python_function_prototypes.items()):

          if python_function_prototype.function_type != (
              PythonTypeObjectFunctionPrototype.FUNCTION_TYPE_GET):
            continue

          if not python_function_prototype.arguments:
            continue

          if python_function_prototype.return_type in (
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_OBJECT,
              PythonTypeObjectFunctionPrototype.RETURN_TYPE_STRING):

            # TODO: check if base type of sequence type exists.
            sequence_type = type_function[4:]
            if not sequence_type.startswith(u'recovered_'):
              sequence_types.append(type_function[4:])

        self._GenerateTypeSourceFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer)

        self._GenerateTypeHeaderFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer)

      for type_name in list(sequence_types):
        template_mappings[u'type_name'] = type_name
        template_mappings[u'type_name_upper_case'] = type_name.upper()
        template_mappings[u'type_description'] = type_name.replace(u'_', u' ')

        self._GenerateSequenceTypeSourceFile(
            project_configuration, template_mappings, type_name, output_writer)

        self._GenerateSequenceTypeHeaderFile(
            project_configuration, template_mappings, type_name, output_writer)

    include_header_file = self._GetDefinitionsIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning((
          u'Missing: {0:s} skipping generation of Python definitions object '
          u'source and header files.').format(
              self._definitions_include_header_path))
    else:
      definitions_name_prefix = u'{0:s}_'.format(
          project_configuration.library_name)
      definitions_name_prefix_length = len(definitions_name_prefix)

      for enum_declaration in include_header_file.enum_declarations:
        definitions_name = enum_declaration.name.lower()
        if not definitions_name.startswith(definitions_name_prefix):
          continue

        # TODO: skip flags definitions
        definitions_name = definitions_name[definitions_name_prefix_length:]
        if definitions_name == u'access_flags':
          continue

        self._GenerateDefinitionsSourceFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)

        self._GenerateDefinitionsHeaderFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)


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
    makefile_am_file.Read(project_configuration)

    template_mappings = project_configuration.GetTemplateMappings()
    template_mappings[u'local_libs'] = u' '.join(makefile_am_file.libraries)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = directory_entry

      if (directory_entry in (u'syncwinflexbison.ps1', u'synczlib.ps1') and
          not os.path.exists(output_filename)):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class TestsSourceFileGenerator(SourceFileGenerator):
  """Class that generates the tests source files."""

  _PYTHON_FUNCTION_NAMES = (
      u'get_version', )

  _PYTHON_FUNCTION_WITH_INPUT_NAMES = (
      u'open_close', u'seek', u'read')

  def _GenerateAPISupportTests(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates an API type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, u'yal_test_support')

    output_filename = u'{0:s}_test_support.c'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join(u'tests', output_filename)

    function_name = u'{0:s}_get_codepage'.format(
        project_configuration.library_name)
    codepage_support = function_name in include_header_file.functions_per_name

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    signature_type = include_header_file.GetCheckSignatureType(
        project_configuration)

    if signature_type:
      template_filename = os.path.join(
          template_directory, u'includes_with_input.c')

      template_mappings[u'signature_type'] = signature_type
    else:
      template_filename = os.path.join(template_directory, u'includes.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for support_function in (
        u'get_version', u'get_access_flags_read', u'get_codepage',
        u'set_codepage'):
      function_name = u'{0:s}_{1:s}'.format(
          project_configuration.library_name, support_function)
      if function_name not in include_header_file.functions_per_name:
        continue

      template_filename = u'{0:s}.c'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if signature_type:
      template_filename = os.path.join(template_directory, u'check_signature.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      template_filename = os.path.join(template_directory, u'main_with_input.c')
    else:
      template_filename = os.path.join(template_directory, u'main.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMakefileAM(
      self, project_configuration, template_mappings, makefile_am_file,
      api_functions, api_functions_with_input, api_types, api_types_with_input,
      internal_types, output_writer):
    """Generates a tests Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      makefile_am_file (LibraryMakefileAMFile): library Makefile.am file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      internal_types (list[str]): names of internal types to test.
      output_writer (OutputWriter): output writer.
    """
    tests = set(api_functions).union(set(api_functions_with_input))
    tests = tests.union(set(api_types).union(set(api_types_with_input)))
    tests = sorted(tests.union(set(internal_types)))

    has_python_module = self._HasPythonModule(project_configuration)

    template_directory = os.path.join(
        self._template_directory, u'Makefile.am')
    output_filename = os.path.join(u'tests', u'Makefile.am')

    test_scripts = []
    if api_functions or api_functions_with_input:
      test_script = u'test_api_functions.sh'
      test_scripts.append(test_script)

    if api_types or api_types_with_input:
      test_script = u'test_api_types.sh'
      test_scripts.append(test_script)

    tool_name = u'{0:s}info'.format(
        project_configuration.library_name_suffix)
    if tool_name in project_configuration.tools_names:
      test_script = u'test_{0:s}.sh'.format(tool_name)
      test_scripts.append(test_script)

    tool_name = u'{0:s}export'.format(
        project_configuration.library_name_suffix)
    if tool_name in project_configuration.tools_names:
      test_script = u'test_{0:s}.sh'.format(tool_name)
      test_scripts.append(test_script)

    python_scripts = []
    python_test_scripts = [
        u'test_python_functions.sh',
        u'test_{0:s}_set_ascii_codepage.sh'.format(
            project_configuration.python_module_name)]

    check_scripts = [u'test_runner.sh']
    check_scripts.extend(test_scripts)
    if has_python_module:
      check_scripts.extend(python_scripts)
      check_scripts.extend(python_test_scripts)
      check_scripts.extend([
          u'{0:s}_test_get_version.py'.format(
              project_configuration.python_module_name),
          u'{0:s}_test_open_close.py'.format(
              project_configuration.python_module_name),
          u'{0:s}_test_set_ascii_codepage.py'.format(
              project_configuration.python_module_name)])

    check_scripts = sorted(check_scripts)

    if has_python_module:
      test_script = u'$(TESTS_{0:s})'.format(
          project_configuration.python_module_name.upper())
      test_scripts.append(test_script)

    check_programs = []
    for test in tests:
      check_program = u'{0:s}_test_{1:s}'.format(
          project_configuration.library_name_suffix, test)
      check_programs.append(check_program)

    cppflags = list(makefile_am_file.cppflags)
    if api_functions_with_input or api_types_with_input:
      # TODO: add libcsystem before non libyal cppflags.
      cppflags.append(u'libcsystem')

    template_mappings[u'cppflags'] = u' \\\n'.join(
        [u'\t@{0:s}_CPPFLAGS@'.format(name.upper()) for name in cppflags])
    template_mappings[u'python_tests'] = u' \\\n'.join(
        [u'\t{0:s}'.format(filename) for filename in python_test_scripts])
    template_mappings[u'tests'] = u' \\\n'.join(
        [u'\t{0:s}'.format(filename) for filename in test_scripts])
    template_mappings[u'check_scripts'] = u' \\\n'.join(
        [u'\t{0:s}'.format(filename) for filename in check_scripts])
    template_mappings[u'check_programs'] = u' \\\n'.join(
        [u'\t{0:s}'.format(filename) for filename in check_programs])

    template_filename = os.path.join(template_directory, u'header.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if has_python_module:
      template_filename = os.path.join(template_directory, u'python.am')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'body.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for test in tests:
      if test in api_functions:
        template_filename = u'yal_test_function.am'
        template_mappings[u'library_function'] = test

      elif test in api_functions_with_input:
        template_filename = u'yal_test_function_with_input.am'
        template_mappings[u'library_function'] = test

      elif test in api_types or test in internal_types:
        template_filename = u'yal_test_type.am'
        template_mappings[u'type_name'] = test
        template_mappings[u'type_name_upper_case'] = test.upper()
        template_mappings[u'type_description'] = test.replace(u'_', u' ')

      elif test in api_types_with_input:
        template_filename = u'yal_test_type_with_input.am'
        template_mappings[u'type_name'] = test
        template_mappings[u'type_name_upper_case'] = test.upper()
        template_mappings[u'type_description'] = test.replace(u'_', u' ')

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._SortSources(output_filename)

  def _GenerateTypeTest(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, output_writer, output_filename):
    """Generates a type test within the type tests source file.

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

    Returns:
      tuple: contains:
        str: name of library type function.
        str: name of the test function corresponding to the library type function.
        bool: True if the function prototype was externally available.
    """
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, type_name, type_function)
    if function_name not in header_file.functions_per_name:
      return function_name, None, last_have_extern

    template_directory = os.path.join(
        self._template_directory, u'yal_test_type')

    template_filename = u'{0:s}.c'.format(type_function)
    template_filename = os.path.join(template_directory, template_filename)
    if not os.path.exists(template_filename):
      return function_name, None, last_have_extern

    function_prototype = header_file.functions_per_name.get(function_name, None)

    if not function_prototype.have_extern and last_have_extern:
      internal_template_filename = os.path.join(
          template_directory, u'define_internal_start.c')
      self._GenerateSection(
          internal_template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

    elif function_prototype.have_extern and not last_have_extern:
      internal_template_filename = os.path.join(
          template_directory, u'define_internal_end.c')
      self._GenerateSection(
          internal_template_filename, template_mappings, output_writer,
          output_filename, access_mode='ab')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    test_function_name = u'{0:s}_test_{1:s}_{2:s}'.format(
        project_configuration.library_name_suffix, type_name,
        type_function)

    return function_name, test_function_name, function_prototype.have_extern

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
    output_filename = u'{0:s}_test_{1:s}.c'.format(
        project_configuration.library_name_suffix, type_name)
    output_filename = os.path.join(u'tests', output_filename)

    if os.path.exists(output_filename) and not self._experimental:
      return False

    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)

    # TODO: handle types in non-matching header files.
    try:
      header_file.Read(project_configuration)
    except IOError:
      logging.warning(u'Skipping: {0:s}'.format(header_file.path))
      return False

    template_directory = os.path.join(
        self._template_directory, u'yal_test_type')

    function_names = list(header_file.functions_per_name.keys())
    tests_to_run = []
    tests_to_run_with_args = []

    template_mappings[u'type_name'] = type_name
    template_mappings[u'type_name_upper_case'] = type_name.upper()
    template_mappings[u'type_description'] = type_name.replace(u'_', u' ')

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if with_input:
      template_filename = u'includes_with_input.c'
    else:
      template_filename = u'includes.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    function_name = u'{0:s}_{1:s}_initialize'.format(
        project_configuration.library_name, type_name)
    function_prototype = header_file.functions_per_name.get(function_name, None)

    have_extern = True
    initialize_is_internal = (
        function_prototype and not function_prototype.have_extern)

    if is_internal or initialize_is_internal:
      template_filename = os.path.join(
          template_directory, u'includes_internal.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    for type_function in (u'initialize', u'free'):
      function_name, test_function_name, have_extern = self._GenerateTypeTest(
          project_configuration, template_mappings, type_name, type_function,
          have_extern, header_file, output_writer, output_filename)
      if test_function_name:
        tests_to_run.append((function_name, test_function_name))
        function_names.remove(function_name)

    # TODO: fix libbfio having no open wide.
    if with_input:
      for type_function in (u'open', u'get_ascii_codepage'):
        function_name, test_function_name, have_extern = self._GenerateTypeTest(
            project_configuration, template_mappings, type_name, type_function,
            have_extern, header_file, output_writer, output_filename)

        if test_function_name:
          function_names.remove(function_name)

          # The open, close and open-close functions are defined in the template
          # so no need to add them to tests_to_run or tests_to_run_with_args.
          if type_function == u'open':
            function_name = u'{0:s}_{1:s}_open_wide'.format(
                project_configuration.library_name, type_name, type_function)
            function_names.remove(function_name)

            function_name = u'{0:s}_{1:s}_open_file_io_handle'.format(
                project_configuration.library_name, type_name, type_function)
            function_names.remove(function_name)

            function_name = u'{0:s}_{1:s}_close'.format(
                project_configuration.library_name, type_name, type_function)
            function_names.remove(function_name)

            # TODO: remove open_read?
          else:
            tests_to_run_with_args.append((function_name, test_function_name))

    function_name, test_function_name, have_extern = self._GenerateTypeTest(
        project_configuration, template_mappings, type_name,
        u'set_ascii_codepage', have_extern, header_file, output_writer,
        output_filename)
    if test_function_name:
      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    function_name_prefix = u'{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    for function_name in function_names:
      if not function_name.startswith(function_name_prefix):
        continue

      type_function = function_name[function_name_prefix_length:]
      test_function_name = None

      template_filename = os.path.join(template_directory, template_filename)
      if os.path.exists(template_filename):
        _, test_function_name, have_extern = self._GenerateTypeTest(
            project_configuration, template_mappings, type_name, type_function,
            have_extern, header_file, output_writer, output_filename)

      if with_input:
        tests_to_run_with_args.append((function_name, test_function_name))
      else:
        tests_to_run.append((function_name, test_function_name))

    if not have_extern:
      template_filename = os.path.join(
          template_directory, u'define_internal_end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    # TODO: create generic test for get_number_of_X API functions.
    # TODO: generate run test macros.

    if with_input:
      template_filename = u'main_start_with_input.c'
    else:
      template_filename = u'main_start.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name, tests_to_run,
        header_file, output_writer, output_filename)

    if with_input:
      template_filename = os.path.join(
          template_directory, u'main_with_input_start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name,
        tests_to_run_with_args, header_file, output_writer, output_filename,
        with_args=True)

    if with_input:
      template_filename = os.path.join(
          template_directory, u'main_with_input_end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      template_filename = u'main_end_with_input.c'
    else:
      template_filename = u'main_end.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

    return True

  def _GenerateTypeTestsMainTestsToRun(
      self, project_configuration, template_mappings, type_name, tests_to_run,
      header_file, output_writer, output_filename, with_args=False):
    """Generates a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      tests_to_run (list[tuple[str, str]]): names of the library type function
          and its corresponding test function.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      with_args (Optional[bool]): True if the tests to run have arguments.
    """
    template_directory = os.path.join(
        self._template_directory, u'yal_test_type')

    library_name_suffix = project_configuration.library_name_suffix.upper()

    last_have_extern = True
    tests_to_run_mappings = []
    for function_name, test_function_name in tests_to_run:
      function_prototype = header_file.functions_per_name.get(
          function_name, None)

      if function_prototype.have_extern != last_have_extern:
        if tests_to_run_mappings:
          if not last_have_extern:
            template_filename = os.path.join(
                template_directory, u'define_internal_start.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer, output_filename,
                access_mode='ab')

          template_mappings[u'tests_to_run'] = u'\n'.join(tests_to_run_mappings)
          tests_to_run_mappings = []

          template_filename = os.path.join(
              template_directory, u'main_tests_to_run.c')
          self._GenerateSection(
              template_filename, template_mappings, output_writer, output_filename,
              access_mode='ab')

          if not last_have_extern:
            template_filename = os.path.join(
                template_directory, u'define_internal_end.c')
            self._GenerateSection(
                template_filename, template_mappings, output_writer, output_filename,
                access_mode='ab')

        last_have_extern = function_prototype.have_extern

      if tests_to_run_mappings:
        tests_to_run_mappings.append(u'')

      if not test_function_name:
        if with_args:
          tests_to_run_mappings.append(
              u'\t\t/* TODO: add tests for {0:s} */'.format(function_name))
        else:
          tests_to_run_mappings.append(
              u'\t/* TODO: add tests for {0:s} */'.format(function_name))

      else:
        if with_args:
          test_to_run_mappings = [
              u'\t\t{0:s}_TEST_RUN_WITH_ARGS('.format(library_name_suffix),
              u'\t\t "{0:s}",'.format(function_name),
              u'\t\t {0:s},'.format(test_function_name),
              u'\t\t {0:s} );'.format(type_name)]

        else:
          test_to_run_mappings = [
              u'\t{0:s}_TEST_RUN('.format(library_name_suffix),
              u'\t "{0:s}",'.format(function_name),
              u'\t {0:s} );'.format(test_function_name)]

        tests_to_run_mappings.extend(test_to_run_mappings)

    if tests_to_run_mappings:
      if not last_have_extern:
        template_filename = os.path.join(
            template_directory, u'define_internal_start.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

      template_mappings[u'tests_to_run'] = u'\n'.join(tests_to_run_mappings)
      tests_to_run_mappings = []

      template_filename = os.path.join(
          template_directory, u'main_tests_to_run.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      if not last_have_extern:
        template_filename = os.path.join(
            template_directory, u'define_internal_end.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

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

    type_name_prefix = u'{0:s}_'.format(project_configuration.library_name)
    type_name_prefix_length = len(type_name_prefix)

    types = []
    for source_file in makefile_am_file.sources:
      if not source_file.endswith(u'.h'):
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
      api_types, api_types_with_input, internal_types, python_functions,
      python_functions_with_input):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      internal_types (list[str]): names of internal types to test.
      python_functions (list[str]): names of Python functions to test.
      python_functions_with_input (list[str]): names of Python functions to
          test with input data.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = project_configuration.GetTemplateMappings()

    template_mappings[u'test_api_functions'] = u' '.join(sorted(api_functions))
    template_mappings[u'test_api_functions_with_input'] = u' '.join(
        sorted(api_functions_with_input))

    test_api_types = set(api_types).union(set(internal_types))
    template_mappings[u'test_api_types'] = u' '.join(sorted(test_api_types))
    template_mappings[u'test_api_types_with_input'] = u' '.join(
        sorted(api_types_with_input))

    template_mappings[u'test_python_functions'] = u' '.join(
        sorted(python_functions))
    template_mappings[u'test_python_functions_with_input'] = u' '.join(
        sorted(python_functions_with_input))

    template_mappings[u'alignment_padding'] = (
        u' ' * len(project_configuration.library_name_suffix))

    return template_mappings

  def _SortSources(self, output_filename):
    """Sorts the sources.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'rb') as file_object:
      lines = [line for line in file_object.readlines()]

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
    # TODO: deprecate project_configuration.library_public_types ?

    if not self._HasTests(project_configuration):
      return

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          u'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          u'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_makefile_am_path))
      return

    api_functions, api_functions_with_input = (
        include_header_file.GetAPIFunctionTestGroups(project_configuration))

    api_types, api_types_with_input = (
        include_header_file.GetAPITypeTestGroups(project_configuration))

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
      if type_name.startswith(u'internal_'):
        continue

      internal_types.append(type_name)

    # TODO: handle non-template files differently.
    # TODO: yal_test_open_close.c handle file, handle, volume

    library_header = u'yal_test_{0:s}.h'.format(
        project_configuration.library_name)

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

    template_mappings = self._GetTemplateMappings(
        project_configuration, api_functions, api_functions_with_input,
        api_types, api_types_with_input, internal_types, test_python_functions,
        test_python_functions_with_input)

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

      is_script = (
          directory_entry.endswith(u'.ps1') or directory_entry.endswith(u'.sh'))

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

      elif directory_entry.startswith(u'test_yal') and is_script:
        output_filename = u'test_{0:s}{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[8:])

      elif directory_entry.startswith(u'test_pyyal') and is_script:
        output_filename = u'test_{0:s}{1:s}'.format(
            project_configuration.python_module_name, directory_entry[10:])

      else:
        output_filename = directory_entry

      if directory_entry in (
          u'test_api_functions.ps1', u'test_api_functions.sh'):
        force_create = bool(public_functions)

      elif directory_entry in (u'test_api_types.ps1', u'test_api_types.sh'):
        force_create = bool(public_types)

      elif directory_entry in (u'test_yalinfo.ps1', u'test_yalinfo.sh'):
        tool_name = u'{0:s}info'.format(
            project_configuration.library_name_suffix)
        force_create = tool_name in project_configuration.tools_names

      elif directory_entry == 'yal_test_error.c':
        force_create = u'error' in api_functions

      elif directory_entry == 'yal_test_notify.c':
        force_create = u'notify' in api_functions

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

    self._GenerateAPISupportTests(
        project_configuration, template_mappings, include_header_file,
        output_writer)

    for type_name in list(api_types):
      if (type_name == u'error' and
          project_configuration.library_name == u'libcerror'):
        continue

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer)
      if not result:
        api_types.remove(type_name)

    for type_name in list(api_types_with_input):
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          with_input=True)
      if not result:
        api_types_with_input.remove(type_name)

    for type_name in list(internal_types):
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          is_internal=True)
      if not result:
        internal_types.remove(type_name)

    self._GenerateMakefileAM(
        project_configuration, template_mappings, makefile_am_file,
        api_functions, api_functions_with_input, api_types,
        api_types_with_input, internal_types, output_writer)


class ToolsSourceFileGenerator(SourceFileGenerator):
  """Class that generates the tools source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates tools source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    tools_name = u'{0:s}tools'.format(project_configuration.library_name_suffix)
    tools_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        tools_name)

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

      output_filename = u'{0:s}_{1:s}'.format(tools_name, directory_entry[9:])
      output_filename = os.path.join(tools_name, output_filename)

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
    bool: True if successful or False if not.
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
  # AUTHORS, NEWS
  # configure.ac
  # include headers
  # yal.net files

  SOURCE_GENERATORS = [
      (u'common', CommonSourceFileGenerator),
      (u'config', ConfigurationFileGenerator),
      (u'include', IncludeSourceFileGenerator),
      (u'libyal', LibrarySourceFileGenerator),
      (u'pyyal', PythonModuleSourceFileGenerator),
      (u'scripts', ScriptFileGenerator),
      (u'tests', TestsSourceFileGenerator),
      (u'yaltools', ToolsSourceFileGenerator),
  ]

  sources_directory = os.path.join(
      libyal_directory, u'data', u'source')
  for source_category, source_generator_class in SOURCE_GENERATORS:
    template_directory = os.path.join(sources_directory, source_category,)
    source_file = source_generator_class(
        projects_directory, template_directory,
        experimental=options.experimental)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  # TODO: generate manuals/Makefile.am

  source_files = [
      (u'libyal.3', LibraryManPageGenerator),
  ]

  manuals_directory = os.path.join(
      libyal_directory, u'data', u'source', u'manuals')
  for source_category, source_generator_class in source_files:
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
