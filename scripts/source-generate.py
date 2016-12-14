#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of the libyal libraries."""

from __future__ import print_function
import abc
import argparse
import collections
import datetime
import difflib
import json
import logging
import os
import shutil
import stat
import string
import sys
import time

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error

import source_formatter


DATA_TYPE_BINARY_DATA = u'binary_data'
DATA_TYPE_DOUBLE = u'double'
DATA_TYPE_FAT_DATE_TIME = u'fat_date_time'
DATA_TYPE_FILETIME = u'filetime'
DATA_TYPE_FLOAT = u'float'
DATA_TYPE_FLOATINGTIME = u'floatingtime'
DATA_TYPE_GUID = u'guid'
DATA_TYPE_INT = u'int'
DATA_TYPE_INT32 = u'int32'
DATA_TYPE_NARROW_STRING = u'narrow_string'
DATA_TYPE_NONE = u'none'
DATA_TYPE_OBJECT = u'object'
DATA_TYPE_OFF64 = u'off64'
DATA_TYPE_POSIX_TIME = u'posix_time'
DATA_TYPE_SIZE32 = u'size32'
DATA_TYPE_SIZE64 = u'size64'
DATA_TYPE_STRING = u'string'
DATA_TYPE_UINT8 = u'uint8'
DATA_TYPE_UINT16 = u'uint16'
DATA_TYPE_UINT32 = u'uint32'
DATA_TYPE_UINT64 = u'uint64'

FUNCTION_TYPE_CLOSE = u'close'
FUNCTION_TYPE_COPY = u'copy'
FUNCTION_TYPE_COPY_FROM = u'copy_from'
FUNCTION_TYPE_COPY_TO = u'copy_to'
FUNCTION_TYPE_FREE = u'free'
FUNCTION_TYPE_GET = u'get'
FUNCTION_TYPE_GET_BY_INDEX = u'get_by_index'
FUNCTION_TYPE_GET_BY_IDENTIFIER = u'get_by_identifier'
FUNCTION_TYPE_GET_BY_NAME = u'get_by_name'
FUNCTION_TYPE_GET_BY_PATH = u'get_by_path'
FUNCTION_TYPE_INITIALIZE = u'initialize'
FUNCTION_TYPE_OPEN = u'open'
FUNCTION_TYPE_READ = u'read'
FUNCTION_TYPE_SEEK = u'seek'
FUNCTION_TYPE_SET = u'set'
FUNCTION_TYPE_UTILITY = u'utility'
FUNCTION_TYPE_WRITE = u'write'


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
    self.tests_options = None

    self.msvscpp_build_dependencies = None

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
    self.tools_names = self._GetOptionalConfigValue(
        config_parser, u'tests', u'options', default_value=[])

    self.msvscpp_build_dependencies = self._GetOptionalConfigValue(
        config_parser, u'msvscpp', u'build_dependencies', default_value=[])

    self.msvscpp_build_dependencies = [
        name.split(u' ')[0] for name in self.msvscpp_build_dependencies]

    if config_parser.has_section(u'mount_tool'):
      self.msvscpp_build_dependencies.append(u'dokan')

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
    data_type (str): data type.
    function_type (str): function type.
    object_type (str): object type.
    value_type (str): value type.
  """

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
    self._name = None
    self._python_module_name = python_module_name
    self._type_function = type_function
    self._type_name = type_name
    self._value_name = None
    self.arguments = []
    self.data_type = DATA_TYPE_NONE
    self.function_type = None
    self.object_type = None
    self.value_type = None

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
    # TODO: make overrides more generic.
    if self._type_function == u'set_parent_file':
      return u'set_parent'

    if (self._type_function.startswith(u'copy_') and
       not self._type_function.startswith(u'copy_from_')):
      return u'get_{0:s}'.format(self._type_function[5:])

    if (self._type_function.startswith(u'get_utf8_') or
        self._type_function.startswith(u'set_utf8_')):
      return u''.join([self._type_function[:4], self._type_function[9:]])

    if self._type_function.startswith(u'get_data_as_'):
      _, _, type_function_suffix = self._type_function.partition(u'_data_as_')

      if type_function_suffix in (
          u'16bit_integer', u'32bit_integer', u'64bit_integer'):
        return u'get_data_as_integer'

      elif type_function_suffix in (u'filetime', u'floatingtime'):
       return u'get_data_as_datetime'

      elif type_function_suffix == u'utf8_string':
        return u'get_data_as_string'

      else:
        return self._type_function

    if self._type_function.startswith(u'get_'):
      type_function_prefix, _, type_function_suffix = (
          self._type_function.partition(u'_by_'))

      if type_function_suffix in (u'entry', u'index'):
        return type_function_prefix

      if type_function_suffix in (u'utf8_name', u'utf8_path'):
        return u''.join([self._type_function[:-10], self._type_function[-5:]])

      if self._type_function.endswith(u'_utf8_string'):
        return u''.join([self._type_function[:-12], self._type_function[-7:]])

      if self._type_function.endswith(u'_utf8_string_size'):
        return u''.join([self._type_function[:-17], self._type_function[-12:]])

    return self._type_function

  @property
  def value_name(self):
    """str: value name."""
    if self._value_name is None:
      # TODO: make overrides more generic.
      if self.function_type == FUNCTION_TYPE_COPY:
        if self._type_function.startswith(u'copy_'):
          self._value_name = self._type_function[5:]

      elif self.function_type == FUNCTION_TYPE_COPY_FROM:
        if self._type_function.startswith(u'copy_from_'):
          self._value_name = self._type_function[10:]

      elif self.function_type in (
          FUNCTION_TYPE_GET, FUNCTION_TYPE_GET_BY_IDENTIFIER,
          FUNCTION_TYPE_GET_BY_INDEX, FUNCTION_TYPE_GET_BY_NAME,
          FUNCTION_TYPE_GET_BY_PATH):
        type_function_prefix, _, _ = self._type_function.partition(u'_by_')

        if type_function_prefix.startswith(u'get_'):
          type_function_prefix = type_function_prefix[4:]

        if type_function_prefix.startswith(u'utf8_'):
          type_function_prefix = type_function_prefix[5:]

        self._value_name = type_function_prefix

      elif self.function_type == FUNCTION_TYPE_SET:
        if self._type_function.startswith(u'set_utf8_'):
          self._value_name = self._type_function[9:]

        elif self._type_function.startswith(u'set_'):
          self._value_name = self._type_function[4:]

    return self._value_name

  def DataTypeIsDatetime(self):
    """Determines if the data type is a datetime type.

    Returns:
      bool: True if the data type is a datetime type.
    """
    return self.data_type in (
        DATA_TYPE_FAT_DATE_TIME, DATA_TYPE_FILETIME,
        DATA_TYPE_FLOATINGTIME, DATA_TYPE_POSIX_TIME)

  def DataTypeIsFloat(self):
    """Determines if the data type is a floating-point type.

    Returns:
      bool: True if the data type is a floating-point type.
    """
    return self.data_type in (DATA_TYPE_FLOAT, DATA_TYPE_DOUBLE)

  def DataTypeIsInteger(self):
    """Determines if the data type is an integer type.

    Returns:
      bool: True if the data type is an integer type.
    """
    return self.data_type in (
        DATA_TYPE_INT, DATA_TYPE_INT32, DATA_TYPE_OFF64,
        DATA_TYPE_SIZE32, DATA_TYPE_SIZE64, DATA_TYPE_UINT8,
        DATA_TYPE_UINT16, DATA_TYPE_UINT32, DATA_TYPE_UINT64)

  def GetAttributeDescription(self):
    """Retrieves the fuction as attribute description.

    Returns:
      str: function as attribute description.
    """
    description = u''

    type_function = self.type_function
    value_name = self.value_name
    if value_name:
      value_name = value_name.replace(u'_', u' ')

    if type_function == u'get_ascii_codepage':
      description = (
          u'The codepage used for ASCII strings in the {0:s}.').format(
              self._type_name)

    elif type_function == u'get_data_as_boolean':
      description = u'The data as a boolean.'

    elif type_function == u'get_data_as_datetime':
      description = u'The data as a datetime object.'

    elif type_function == u'get_data_as_integer':
      description = u'The data as an integer.'

    elif type_function == u'get_data_as_floating_point':
      description = u'The data as a floating point.'

    elif type_function == u'get_data_as_string':
      description = u'The data as a string.'

    elif value_name:
      description = u'The {0:s}.'.format(value_name)

    return description

  def GetDataTypeDescription(self):
    """Retrieves the data type description.

    Returns:
      str: data type description.
    """
    if self.data_type == DATA_TYPE_BINARY_DATA:
      return u'Binary string or None'

    if self.DataTypeIsDatetime():
      return u'Datetime or None'

    if self.data_type == DATA_TYPE_OBJECT:
      return u'Object or None'

    if self.DataTypeIsFloat():
      return u'Float or None'

    if self.DataTypeIsInteger():
      return u'Integer or None'

    if self.data_type in (DATA_TYPE_GUID, DATA_TYPE_STRING):
      return u'Unicode string or None'

    if self.data_type == DATA_TYPE_NARROW_STRING:
      return u'String or None'

    if self.data_type == DATA_TYPE_NONE:
      return u'None'

    return self.data_type

  def GetDescription(self):
    """Retrieves the description.

    Returns:
      list[str]: lines of the description.
    """
    description = [u'']

    type_function = self.type_function
    value_name = self.value_name
    if value_name:
      value_name = value_name.replace(u'_', u' ')

    if type_function == u'close':
      description = [u'Closes a {0:s}.'.format(self._type_name)]

    elif type_function == u'get_ascii_codepage':
      description = [(
          u'Retrieves the codepage for ASCII strings used in '
          u'the {0:s}.').format(self._type_name)]

    elif type_function == u'get_data_as_boolean':
      description = [u'Retrieves the data as a boolean.']

    elif type_function == u'get_data_as_datetime':
      description = [u'Retrieves the data as a datetime object.']

    elif type_function == u'get_data_as_integer':
      description = [u'Retrieves the data as an integer.']

    elif type_function == u'get_data_as_floating_point':
      description = [u'Retrieves the data as a floating point.']

    elif type_function == u'get_data_as_string':
      description = [u'Retrieves the data as a string.']

    elif type_function == u'open':
      description = [u'Opens a {0:s}.'.format(self._type_name)]

    elif type_function == u'open_file_object':
      description = [(
          u'Opens a {0:s} using a file-like object.').format(self._type_name)]

    elif type_function == u'read_buffer':
      description = [u'Reads a buffer of data.']

    elif type_function == u'read_buffer_at_offset':
      description = [u'Reads a buffer of data at a specific offset.']

    elif type_function == u'seek_offset':
      description = [u'Seeks an offset within the data.']

    elif type_function == u'set_ascii_codepage':
      description = [
          (u'Sets the codepage for ASCII strings used in the '
           u'{0:s}.').format(self._type_name),
          (u'Expects the codepage to be a string containing a Python '
           u'codec definition.')]

    elif type_function == u'set_parent':
      description = [u'Sets the parent file.']

    elif type_function == u'signal_abort':
      description = [u'Signals the {0:s} to abort the current activity.'.format(
          self._type_name)]

    elif self.function_type == FUNCTION_TYPE_GET_BY_INDEX:
      _, _, argument_suffix = self.arguments[0].rpartition(u'_')
      description = [u'Retrieves the {0:s} specified by the {1:s}.'.format(
          value_name, argument_suffix)]

    elif self.function_type in (
        FUNCTION_TYPE_GET_BY_IDENTIFIER, FUNCTION_TYPE_GET_BY_NAME,
        FUNCTION_TYPE_GET_BY_PATH):
      _, _, type_function_suffix = type_function.partition(u'_by_')
      description = [u'Retrieves the {0:s} specified by the {1:s}.'.format(
          value_name, type_function_suffix)]

    elif self.function_type == FUNCTION_TYPE_COPY_FROM:
      type_name = self._type_name
      if type_name:
        type_name = type_name.replace(u'_', u' ')

      # TODO: fix value name.
      description = [u'Copies the the {0:s} from the {1:s}'.format(
          type_name, value_name)]

    elif self.function_type in (FUNCTION_TYPE_COPY, FUNCTION_TYPE_GET):
      description = [u'Retrieves the {0:s}.'.format(value_name)]

    elif self.function_type == FUNCTION_TYPE_SET:
      value_name = value_name.replace(u'_', u' ')
      description = [u'Sets the {0:s}.'.format(value_name)]

    return description

  def GetValueNameAndPrefix(self):
    """Determines the value name and its prefix.

    Returns:
      tuple[str, str]: value name and prefix.
    """
    if self.value_name:
      value_name_prefix, _, value_name = self.value_name.partition(u'_')
      if value_name_prefix in (u'root', u'sub'):
        return value_name, value_name_prefix

    return self.value_name, None


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
    self._library_name = None
    self.functions_per_name = collections.OrderedDict()
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
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
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
          data_type, _, _ = line.partition(self._library_name)

          # Get the part of the line after the data type.
          line = line[len(data_type):]
          data_type = data_type.strip()

          # Get the part of the remainder of the line before the '('.
          name, _, _ = line.partition(u'(')

          function_prototype = FunctionPrototype(name, data_type)
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
    self._api_functions_group = {}
    self._api_functions_with_input_group = {}
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

      group_name = section_name.replace(u' ', u'_')
      group_name = group_name.lower()
      group_name, _, _ = group_name.rpartition(u'_functions')

      function_name_prefix = u'{0:s}_{1:s}_'.format(
          self._library_name, group_name)

      found_match = False
      for function_prototype in functions:
        if function_prototype.name.startswith(function_name_prefix):
          found_match = True
          break

      # Ignore the section header is just informative.
      if not found_match:
        if group_name == u'support':
          signature_type = self.GetCheckSignatureType()
          if signature_type:
            self._api_functions_with_input_group[group_name] = section_name
          else:
            self._api_functions_group[group_name] = section_name

      elif self._library_name != u'libcerror' and group_name == u'error':
        self._api_functions_group[group_name] = section_name

      elif (not self.HasTypeFunction(group_name, u'create') and
          not self.HasTypeFunction(group_name, u'free')):
        self._api_functions_group[group_name] = section_name

      elif not self.HasTypeFunction(group_name, u'open'):
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
        function_name = u'{0:s}_check_{1:s}_signature'.format(
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
    error_type = u'{0:s}_error_t '.format(self._library_name)

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
    function_name = u'{0:s}_{1:s}'.format(self._library_name, function_name)
    return function_name in self.functions_per_name

  def HasTypeFunction(self, type_name, type_function):
    """Determines if the include header defines a specific type function.

    Args:
      type_name (str): type name.
      type_function (str): type function.

    Returns:
      bool: True if function is defined, False otherwise.
    """
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
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
            data_type, _, _ = line.partition(self._library_name)

            # Get the part of the line after the data type.
            line = line[len(data_type):]
            data_type = data_type.strip()

            # Get the part of the remainder of the line before the '('.
            name, _, _ = line.partition(u'(')

            function_prototype = FunctionPrototype(name, data_type)
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
    self._library_name = None
    self._path = path
    self.libraries = []

  def Read(self, project_configuration):
    """Reads the Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    self._library_name = project_configuration.library_name

    in_subdirs = False

    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()

        if in_subdirs:
          if line.endswith(b'\\'):
            line = line[:-1].strip()

          if not line:
            in_subdirs = False

          elif line.startswith(b'lib') and line != self._library_name:
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

  def _SetSequenceTypeNameInTemplateMappings(
      self, template_mappings, type_name):
    """Sets the sequence type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): sequence type name.
    """
    if not type_name:
      template_mappings[u'sequence_type_description'] = u''
      template_mappings[u'sequence_type_name'] = u''
      template_mappings[u'sequence_type_name_camel_case'] = u''
      template_mappings[u'sequence_type_name_upper_case'] = u''
    else:
      template_mappings[u'sequence_type_description'] = type_name.replace(
          u'_', u' ')
      template_mappings[u'sequence_type_name'] = type_name
      template_mappings[u'sequence_type_name_camel_case'] = u''.join([
          word.title() for word in type_name.split(u'_')])
      template_mappings[u'sequence_type_name_upper_case'] = type_name.upper()

  def _SetSequenceValueNameInTemplateMappings(
      self, template_mappings, value_name):
    """Sets the sequence value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): sequence value name.
    """
    if not value_name:
      template_mappings[u'sequence_value_description'] = u''
      template_mappings[u'sequence_value_name'] = u''
      template_mappings[u'sequence_value_name_upper_case'] = u''
    else:
      template_mappings[u'sequence_value_description'] = value_name.replace(
          u'_', u' ')
      template_mappings[u'sequence_value_name'] = value_name
      template_mappings[u'sequence_value_name_upper_case'] = value_name.upper()

  def _SetTypeFunctionInTemplateMappings(
      self, template_mappings, type_function):
    """Sets the type function in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_function (str): type function.
    """
    if not type_function:
      template_mappings[u'type_function'] = u''
      template_mappings[u'type_function_upper_case'] = u''
    else:
      template_mappings[u'type_function'] = type_function
      template_mappings[u'type_function_upper_case'] = type_function.upper()

  def _SetTypeNameInTemplateMappings(self, template_mappings, type_name):
    """Sets the type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): type name.
    """
    if not type_name:
      template_mappings[u'type_description'] = u''
      template_mappings[u'type_name'] = u''
      template_mappings[u'type_name_camel_case'] = u''
      template_mappings[u'type_name_upper_case'] = u''
    else:
      template_mappings[u'type_description'] = type_name.replace(u'_', u' ')
      template_mappings[u'type_name'] = type_name
      template_mappings[u'type_name_camel_case'] = u''.join([
          word.title() for word in type_name.split(u'_')])
      template_mappings[u'type_name_upper_case'] = type_name.upper()

  def _SetValueNameInTemplateMappings(self, template_mappings, value_name):
    """Sets value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): value name.
    """
    if not value_name:
      template_mappings[u'value_description'] = u''
      template_mappings[u'value_name'] = u''
      template_mappings[u'value_name_upper_case'] = u''
    else:
      template_mappings[u'value_description'] = value_name.replace(u'_', u' ')
      template_mappings[u'value_name'] = value_name
      template_mappings[u'value_name_upper_case'] = value_name.upper()

  def _SetValueTypeInTemplateMappings(self, template_mappings, value_type):
    """Sets value type in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the type of a template variable.
      value_type (str): value type.
    """
    if not value_type:
      template_mappings[u'value_type'] = u''
      template_mappings[u'value_type_description'] = u''
      template_mappings[u'value_type_upper_case'] = u''
    else:
      template_mappings[u'value_type'] = value_type
      template_mappings[u'value_type_description'] = value_type.replace(
          u'_', u' ')
      template_mappings[u'value_type_upper_case'] = value_type.upper()

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
    template_directory = os.path.join(self._template_directory, u'appveyor.yml')

    template_filename = os.path.join(template_directory, u'header.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: add the right condition.
    if False:
      template_filename = os.path.join(template_directory, u'winflexbison.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if u'zlib' in project_configuration.msvscpp_build_dependencies:
      template_filename = os.path.join(template_directory, u'zlib.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    if u'dokan' in project_configuration.msvscpp_build_dependencies:
      template_filename = os.path.join(template_directory, u'dokan.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def Generate(self, project_configuration, output_writer):
    """Generates configuration files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: generate spec file, what about Python versus non-Python?
    # TODO: generate dpkg files, what about Python versus non-Python?

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

    self._GenerateAppVeyorYML(
        project_configuration, template_mappings, output_writer,
        u'appveyor.yml')


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

    # TODO: fix check for libsigscan.
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
        u'\t{0:s}/definitions.h \\'.format(library_name),
        u'\t{0:s}/extern.h \\'.format(library_name),
        u'\t{0:s}/features.h \\'.format(library_name),
        u'\t{0:s}/types.h'.format(library_name)]

    # TODO: detect if header file exits.
    if library_name != u'libcerror':
      pkginclude_header = u'\t{0:s}/error.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    if include_header_file.HasFunction(u'get_codepage'):
      pkginclude_header = u'\t{0:s}/codepage.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name in (u'libnk2', u'libpff'):
      pkginclude_header = u'\t{0:s}/mapi.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name == u'libolecf':
      pkginclude_header = u'\t{0:s}/ole.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    pkginclude_headers = sorted(pkginclude_headers)

    template_mappings[u'pkginclude_headers'] = u'\n'.join(pkginclude_headers)

    template_filename = os.path.join(self._template_directory, u'Makefile.am')

    output_filename = os.path.join(u'include', u'Makefile.am')
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

    template_mappings = project_configuration.GetTemplateMappings(
        authors_separator=u',\n *                          ')

    output_filename = os.path.join(u'include', u'Makefile.am')
    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

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
    # TODO: libcsplit skip wide_string.[ch]
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

      if ((directory_entry == u'libyal_wide_string.c' or
           directory_entry == u'libyal_wide_string.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == u'libcsplit')):
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
    stat_object = os.stat(self._library_include_header_path)
    modification_time = time.gmtime(stat_object.st_mtime)

    backup_filename = u'{0:s}.{1:d}'.format(output_filename, os.getpid())
    shutil.copyfile(output_filename, backup_filename)

    template_mappings[u'date'] = time.strftime(
        u'%B %d, %Y', modification_time).replace(u' 0', u'  ')

    template_filename = os.path.join(self._template_directory, u'header.txt')
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
          u'Missing: {0:s} skipping generation of library man page.'.format(
              self._library_include_header_path))
      return

    template_mappings = project_configuration.GetTemplateMappings()

    output_filename = u'{0:s}.3'.format(project_configuration.library_name)
    output_filename = os.path.join(u'manuals', output_filename)

    self._GenerateLibraryManPage(project_configuration, template_mappings, include_header_file,
      output_writer, output_filename)



class PythonModuleSourceFileGenerator(SourceFileGenerator):
  """Class that generates the Python module source files."""

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
    if not name or name[0] not in (u'a', u'e', u'i', u'o', u'u'):
      return

    with open(output_filename, 'rb') as file_object:
      lines = file_object.readlines()

    name = name.replace(u'_', u' ')
    description = u' a {0:s}'.format(name)
    corrected_description = u' an {0:s}'.format(name)

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

      if constant_name in (u'undefined', u'unknown'):
        continue

      template_mappings[u'constant_name'] = constant_name
      template_mappings[u'constant_name_upper_case'] = constant_name.upper()

      template_filename = os.path.join(template_directory, u'constant.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')
      self._CorrectDescriptionSpelling(constant_name, output_filename)

    template_filename = os.path.join(template_directory, u'footer.c')
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

    output_filename = u'{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_sequence_type')

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_filename = os.path.join(
        template_directory, u'pyyal_sequence_type.h')
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

    output_filename = u'{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, u'pyyal_sequence_type')

    python_module_include_names = set([
        project_configuration.library_name, sequence_type_name, u'libcerror',
        u'python'])

    if type_is_object:
      python_module_include_names.add(type_name)

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = u'#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_mappings[u'python_module_includes'] = u'\n'.join(
        python_module_includes)

    template_filename = os.path.join(
        template_directory, u'pyyal_sequence_type.c')
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

    if with_parent:
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

      value_name = python_function_prototype.value_name

      template_filename = u'{0:s}.h'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None
        if python_function_prototype.function_type == FUNCTION_TYPE_GET:

          if python_function_prototype.DataTypeIsDatetime():
            template_filename = u'get_datetime_value.h'

        elif python_function_prototype.function_type == (
            FUNCTION_TYPE_GET_BY_INDEX):

          value_name_prefix = u''
          if value_name.startswith(u'recovered_'):
            value_name_prefix = u'recovered_'
            value_name = value_name[10:]

          template_filename = u'get_{0:s}{1:s}_value_by_index.h'.format(
              value_name_prefix, python_function_prototype.data_type)

          sequence_value_name = self._GetSequenceName(value_name)
          self._SetSequenceValueNameInTemplateMappings(
              template_mappings, sequence_value_name)

        if not template_filename:
          if python_function_prototype.arguments:
            template_filename = u'type_object_function_with_args.h'
          else:
            template_filename = u'type_object_function.h'

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            u'Unable to generate Python type object header for: {0:s}.{1:s} '
            u'missing template: {1:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetTypeFunctionInTemplateMappings(template_mappings, type_function)
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')
      self._CorrectDescriptionSpelling(value_name, output_filename)

    template_filename = os.path.join(template_directory, u'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)
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

    if os.path.exists(output_filename):
      with open(output_filename, 'rb') as file_object:
        lines = file_object.readlines()

    bfio_support = u'open_file_object' in python_function_prototypes
    codepage_support = u'get_ascii_codepage' in python_function_prototypes
    open_support = u'open' in python_function_prototypes
    with_parent = (
        u'initialize' not in python_function_prototypes and
        u'free' in python_function_prototypes)

    python_module_include_names = set([
        project_configuration.library_name, type_name, u'error', u'libcerror',
        u'python', u'unused'])

    if bfio_support:
      python_module_include_names.update(
          set([u'file_object_io_handle', 'libbfio']))

    if codepage_support:
      python_module_include_names.update(set([u'codepage', 'libclocale']))

    for python_function_prototype in python_function_prototypes.values():
      if python_function_prototype.data_type in (
          DATA_TYPE_FAT_DATE_TIME, DATA_TYPE_POSIX_TIME):
        python_module_include_names.update(set([u'datetime']))

      if python_function_prototype.data_type in (
          DATA_TYPE_FILETIME, DATA_TYPE_FLOATINGTIME):
        python_module_include_names.update(set([u'datetime', u'integer']))

      elif python_function_prototype.data_type == DATA_TYPE_GUID:
        python_module_include_names.add(u'guid')

      elif python_function_prototype.data_type in (
          DATA_TYPE_SIZE64, DATA_TYPE_OFF64, DATA_TYPE_UINT64):
        python_module_include_names.add(u'integer')

      elif python_function_prototype.data_type == DATA_TYPE_OBJECT:
        python_module_include_names.add(python_function_prototype.object_type)

        if python_function_prototype.function_type == (
            FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = self._GetSequenceName(
              python_function_prototype.object_type)
          python_module_include_names.add(sequence_type_name)

      elif python_function_prototype.data_type == DATA_TYPE_STRING:
        if python_function_prototype.function_type == (
            FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = python_function_prototype.arguments[0]

          sequence_type_prefix, _, sequence_type_suffix = (
              sequence_type_name.rpartition(u'_'))

          if sequence_type_suffix in (u'entry', u'index'):
            sequence_type_name = sequence_type_prefix

          sequence_type_name = self._GetSequenceName(sequence_type_name)
          python_module_include_names.add(sequence_type_name)

    template_directory = os.path.join(self._template_directory, u'pyyal_type')

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: include header of sub types

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
    elif open_support:
      template_filename = u'init_with_input.c'
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

    generate_get_value_type_object = False
    value_type_objects = set([])

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in (u'free', u'initialize'):
        continue

      # TODO: use prefix in template?
      value_name, value_name_prefix = (
          python_function_prototype.GetValueNameAndPrefix())

      # TODO: add get_cache_directory template

      if type_function == u'get_format_version':
        self._SetValueTypeInTemplateMappings(
            template_mappings, python_function_prototype.value_type)

      template_filename = u'{0:s}.c'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None

        # TODO: make more generic.
        if type_function == u'set_key':
          template_filename = u'set_key_with_mode.c'

        elif type_function == u'set_keys':
          template_filename = u'set_keys_with_mode.c'

        elif type_function == u'set_password':
          template_filename = u'set_{0:s}_value.c'.format(u'string')

        elif python_function_prototype.function_type == FUNCTION_TYPE_COPY_FROM:
          template_filename = u'copy_from_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type == FUNCTION_TYPE_COPY:
          template_filename = u'copy_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type in (
            FUNCTION_TYPE_GET, FUNCTION_TYPE_GET_BY_IDENTIFIER,
            FUNCTION_TYPE_GET_BY_INDEX, FUNCTION_TYPE_GET_BY_NAME,
            FUNCTION_TYPE_GET_BY_PATH):

          if value_name.startswith(u'recovered_'):
            value_name_prefix = u'recovered_'
            value_name = value_name[10:]

          elif value_name_prefix:
            value_name_prefix = u'{0:s}_'.format(value_name_prefix)

          else:
            value_name_prefix = u''

          if python_function_prototype.function_type == FUNCTION_TYPE_GET:
            if not python_function_prototype.arguments:
              if value_name.startswith(u'number_of_recovered_'):
                value_name = value_name[20:]
                template_filename = u'get_number_of_recovered_{0:s}_value.c'.format(
                    python_function_prototype.data_type)

              else:
                template_filename = u'get_{0:s}{1:s}_value.c'.format(
                    value_name_prefix, python_function_prototype.data_type)

          elif python_function_prototype.function_type == (
              FUNCTION_TYPE_GET_BY_INDEX):

            template_filename = u'get_{0:s}{1:s}_value_by_index.c'.format(
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
              FUNCTION_TYPE_GET_BY_IDENTIFIER, FUNCTION_TYPE_GET_BY_NAME,
              FUNCTION_TYPE_GET_BY_PATH):

            _, _, type_function_suffix = type_function.partition(u'_by_')

            template_filename = u'get_{0:s}{1:s}_value_by_{2:s}.c'.format(
                value_name_prefix, python_function_prototype.data_type,
                  type_function_suffix)

          if python_function_prototype.data_type == DATA_TYPE_OBJECT:
            if value_name_prefix != u'root_':
              value_name_prefix = u''

            if python_function_prototype.value_type not in value_type_objects:
              generate_get_value_type_object = True
              value_type_objects.add(python_function_prototype.value_type)

          if python_function_prototype.object_type:
            self._SetValueTypeInTemplateMappings(
                template_mappings, python_function_prototype.object_type)

        if template_filename:
          template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            u'Unable to generate Python type object source code for: '
            u'{0:s}.{1:s} missing template: {1:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      if generate_get_value_type_object:
        search_string = (
            u'PyTypeObject *{0:s}_{1:s}_get_{2:s}_type_object(').format(
                project_configuration.python_module_name, type_name,
                value_name)

        search_string = search_string.encode(u'ascii')
        result = self._CopyFunctionToOutputFile(
            lines, search_string, output_filename)

        if not result:
          additional_template_filename = u'get_value_type_object.c'
          additional_template_filename = os.path.join(
              template_directory, additional_template_filename)
          self._GenerateSection(
              additional_template_filename, template_mappings, output_writer,
              output_filename, access_mode='ab')

        generate_get_value_type_object = False

      result = False
      if type_function in (
          u'get_data_as_datetime', u'get_data_as_floating_point',
          u'get_data_as_integer'):
        search_string = (
            u'PyObject *{0:s}_{1:s}_{2:s}(').format(
                project_configuration.python_module_name, type_name,
                type_function)

        search_string = search_string.encode(u'ascii')
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

      arguments_string = u', '.join(python_function_prototype.arguments)
      data_type = python_function_prototype.GetDataTypeDescription()
      python_type_object_methods.extend([
          u'',
          u'\t{{ "{0:s}",'.format(type_function),
          u'\t  (PyCFunction) {0:s},'.format(python_function_prototype.name),
          u'\t  {0:s},'.format(arguments_flags),
          u'\t  "{0:s}({1:s}) -> {2:s}\\n"'.format(
              type_function, arguments_string, data_type),
          u'\t  "\\n"'])

      if (type_function == u'get_offset' and
          u'read_buffer' in python_function_prototypes and
          u'seek_offset' in python_function_prototypes):

        description = [u'Retrieves the current offset within the data.']
      else:
        description = python_function_prototype.GetDescription()

      for index, line in enumerate(description):
        # Correct xml => XML in description for pyevtx.
        line = line.replace(u' xml ', u' XML ')

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

      elif (python_function_prototype.DataTypeIsDatetime() and
          type_function != u'get_data_as_datetime'):
        python_type_object_methods.extend([
            u'',
            u'\t{{ "{0:s}_as_integer",'.format(type_function),
            u'\t  (PyCFunction) {0:s}_as_integer,'.format(
                python_function_prototype.name),
            u'\t  METH_NOARGS,',
            u'\t  "{0:s}_as_integer({1:s}) -> Integer or None\\n"'.format(
                type_function, arguments_string),
            u'\t  "\\n"'])

        if python_function_prototype.data_type == DATA_TYPE_FAT_DATE_TIME:
          description[0] = (
              u'{0:s} as a 32-bit integer containing a FAT date time '
              u'value.').format(description[0][:-1])

        elif python_function_prototype.data_type == DATA_TYPE_FILETIME:
          description[0] = (
              u'{0:s} as a 64-bit integer containing a FILETIME value.').format(
                  description[0][:-1])

        elif python_function_prototype.data_type == DATA_TYPE_FLOATINGTIME:
          description[0] = (
              u'{0:s} as a 64-bit integer containing a floatingtime value.').format(
                  description[0][:-1])

        elif python_function_prototype.data_type == DATA_TYPE_POSIX_TIME:
          description[0] = (
              u'{0:s} as a 32-bit integer containing a POSIX timestamp '
              u'value.').format(description[0][:-1])

        for index, line in enumerate(description):
          if index < len(description) - 1:
            python_type_object_methods.append(u'\t  "{0:s}\\n"'.format(line))
          else:
            python_type_object_methods.append(u'\t  "{0:s}" }},'.format(line))

      elif (python_function_prototype.arguments and
          python_function_prototype.data_type in (
              DATA_TYPE_OBJECT, DATA_TYPE_STRING)):
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
          FUNCTION_TYPE_COPY, FUNCTION_TYPE_GET,
          FUNCTION_TYPE_GET_BY_IDENTIFIER, FUNCTION_TYPE_GET_BY_INDEX,
          FUNCTION_TYPE_GET_BY_NAME, FUNCTION_TYPE_GET_BY_PATH):
        continue

      if (type_function.endswith(u'_by_name') or
          type_function.endswith(u'_by_path')):
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

      # Correct xml => XML in description for pyevtx.
      description = description.replace(u' xml ', u' XML ')

      if not python_function_prototype.arguments:
        python_type_object_get_set_definitions.extend([
            u'',
            u'\t{{ "{0:s}",'.format(type_function[4:]),
            u'\t  (getter) {0:s},'.format(python_function_prototype.name),
            u'\t  (setter) {0:s},'.format(setter_function),
            u'\t  "{0:s}",'.format(description),
            u'\t  NULL },'])

      if (python_function_prototype.arguments and
          python_function_prototype.data_type in (
              DATA_TYPE_OBJECT, DATA_TYPE_STRING)):

        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            u'',
            u'\t{{ "{0:s}",'.format(sequence_type_function),
            u'\t  (getter) {0:s},'.format(sequence_type_getter),
            u'\t  (setter) {0:s},'.format(setter_function),
            u'\t  "{0:s}.",'.format(sequence_type_description),
            u'\t  NULL },'])

      if type_function == u'get_cache_directory':
        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            u'',
            u'\t{{ "{0:s}",'.format(sequence_type_function),
            u'\t  (getter) {0:s},'.format(sequence_type_getter),
            u'\t  (setter) {0:s},'.format(setter_function),
            u'\t  "{0:s}.",'.format(sequence_type_description),
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

  def _GetPythonTypeObjectFunctionPrototype(
      self, project_configuration, type_name, type_function, function_prototype):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): type name.
      type_function (str): type function.
      function_prototype (FunctionPrototype): C function prototype.

    Returns:
      PythonTypeObjectFunctionPrototype: Python type object function prototype
          or None.
    """
    if len(function_prototype.arguments) < 2:
      logging.warning(u'Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    if type_function in (u'free', u'initialize'):
      self_argument = u'{0:s}_{1:s}_t **{1:s}'.format(
          project_configuration.library_name, type_name)
    else:
      self_argument = u'{0:s}_{1:s}_t *{1:s}'.format(
          project_configuration.library_name, type_name)

    function_argument = function_prototype.arguments[0]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != self_argument:
      logging.warning(u'Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    function_argument = function_prototype.arguments[-1]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != u'libcerror_error_t **error':
      logging.warning(u'Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return

    # TODO: add support for glob functions
    # TODO: add support for has, is functions

    arguments = []
    function_type = None
    object_type = None
    data_type = DATA_TYPE_NONE
    value_type = None

    # TODO: add override for
    # if (type_function == u'copy_link_target_identifier_data' and
    #    project_configuration.library_name == u'liblnk'):

    if (type_function == u'get_cache_directory_name' and
        project_configuration.library_name == u'libmsiecf'):
      type_function = u'get_cache_directory'

      arguments = [u'cache_directory_index']
      function_type = FUNCTION_TYPE_GET_BY_INDEX
      data_type = DATA_TYPE_NARROW_STRING

    elif type_function == u'close':
      function_type = FUNCTION_TYPE_CLOSE

    elif type_function.startswith(u'copy_from'):
      function_type = FUNCTION_TYPE_COPY_FROM

      value_argument_index = 1

      function_argument = function_prototype.arguments[value_argument_index]
      value_argument_string = function_argument.CopyToString()

      _, _, argument_name = value_argument_string.rpartition(u' ')
      argument_name.lstrip(u'*')
      arguments.append(argument_name)

      function_argument = function_prototype.arguments[
          value_argument_index + 1]
      value_size_argument_string = function_argument.CopyToString()

      if (value_argument_string == u'const uint8_t *byte_stream' and
        value_size_argument_string == u'size_t byte_stream_size'):
        data_type = DATA_TYPE_BINARY_DATA

      elif (value_argument_string == u'const uint8_t *data' and
        value_size_argument_string == u'size_t data_size'):
        data_type = DATA_TYPE_BINARY_DATA

    elif type_function.startswith(u'copy_'):
      function_type = FUNCTION_TYPE_COPY
      data_type = DATA_TYPE_BINARY_DATA

      # TODO: change copy to or add copy_to

    elif type_function == u'free':
      function_type = FUNCTION_TYPE_FREE

    elif type_function.startswith(u'get_'):
      function_type = FUNCTION_TYPE_GET

      if type_function == u'get_ascii_codepage':
        # TODO: replace this by DATA_TYPE_NARROW_STRING ?
        data_type = u'String'

      elif type_function == u'get_format_version':
        function_argument = function_prototype.arguments[1]
        value_argument_string = function_argument.CopyToString()

        data_type = DATA_TYPE_STRING
        value_type, _, _ = value_argument_string.partition(u' ')

      else:
        type_function_prefix, _, type_function_suffix = (
            type_function.partition(u'_by_'))

        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, value_argument_suffix = value_argument_string.rpartition(u'_')

        # Not all get_by_index functions have the suffix _by_index so we need
        # to detect them based on the function arguments. 
        if (value_argument_string.startswith(u'int ') and
            value_argument_suffix in (u'entry', u'index')):
          function_type = FUNCTION_TYPE_GET_BY_INDEX

          _, _, argument_name = value_argument_string.rpartition(u' ')

          arguments.append(argument_name)
          value_argument_index = 2

        elif type_function_suffix == u'identifier':
          function_type = FUNCTION_TYPE_GET_BY_IDENTIFIER

          arguments.append(type_function_suffix)
          value_argument_index = 2

        elif type_function_suffix in (u'utf8_name', u'utf8_path'):
          type_function_suffix = type_function_suffix[5:]

          if value_argument_string != u'const uint8_t *utf8_string':
            logging.warning(u'Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return

          function_argument = function_prototype.arguments[2]
          function_argument_string = function_argument.CopyToString()

          if function_argument_string != u'size_t utf8_string_length':
            logging.warning(u'Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return

          if type_function_suffix == u'name':
            function_type = FUNCTION_TYPE_GET_BY_NAME
          else:
            function_type = FUNCTION_TYPE_GET_BY_PATH

          arguments.append(type_function_suffix)
          value_argument_index = 3

        if value_argument_index != 1:
          function_argument = function_prototype.arguments[value_argument_index]
          value_argument_string = function_argument.CopyToString()

        function_argument = function_prototype.arguments[
            value_argument_index + 1]
        value_size_argument_string = function_argument.CopyToString()

        if value_argument_string == u'uint64_t *filetime':
          data_type = DATA_TYPE_FILETIME

        elif value_argument_string == u'uint64_t *floatingtime':
          data_type = DATA_TYPE_FLOATINGTIME

        elif value_argument_string == u'uint32_t *fat_date_time':
          data_type = DATA_TYPE_FAT_DATE_TIME

        elif value_argument_string == u'uint32_t *posix_time':
          data_type = DATA_TYPE_POSIX_TIME

        elif (value_argument_string == u'uint8_t *data' and
            value_size_argument_string == u'size_t data_size'):
          data_type = DATA_TYPE_BINARY_DATA

        elif (value_argument_string == u'uint8_t *guid_data' and
            value_size_argument_string == u'size_t guid_data_size'):
          data_type = DATA_TYPE_GUID

        elif (value_argument_string == u'uint8_t *utf8_string' and
            value_size_argument_string == u'size_t utf8_string_size'):
          data_type = DATA_TYPE_STRING

        elif (value_argument_string == u'char *string' and
            value_size_argument_string == u'size_t string_size'):
          data_type = DATA_TYPE_NARROW_STRING

        elif value_argument_string.startswith(u'double *'):
          data_type = DATA_TYPE_DOUBLE

        elif value_argument_string.startswith(u'float *'):
          data_type = DATA_TYPE_FLOAT

        elif value_argument_string.startswith(u'int *'):
          data_type = DATA_TYPE_INT

        elif value_argument_string.startswith(u'int32_t *'):
          data_type = DATA_TYPE_INT32

        elif value_argument_string.startswith(u'off64_t *'):
          data_type = DATA_TYPE_OFF64

        elif value_argument_string.startswith(u'size32_t *'):
          data_type = DATA_TYPE_SIZE32

        elif value_argument_string.startswith(u'size64_t *'):
          data_type = DATA_TYPE_SIZE64

        elif value_argument_string.startswith(u'uint8_t *'):
          data_type = DATA_TYPE_UINT8

        elif value_argument_string.startswith(u'uint16_t *'):
          data_type = DATA_TYPE_UINT16

        elif value_argument_string.startswith(u'uint32_t *'):
          data_type = DATA_TYPE_UINT32

        elif value_argument_string.startswith(u'uint64_t *'):
          data_type = DATA_TYPE_UINT64

        elif value_argument_string.startswith(
            project_configuration.library_name):
          data_type = DATA_TYPE_OBJECT

          object_type, _, _ = value_argument_string.partition(u' ')
          _, _, object_type = object_type.partition(u'_')
          object_type = object_type[:-2]

    elif type_function == u'initialize':
      function_type = FUNCTION_TYPE_INITIALIZE

    elif type_function == u'open' or type_function.startswith(u'open_'):
      function_type = FUNCTION_TYPE_OPEN

      if type_function == u'open':
        arguments = [u'filename', u'mode=\'r\'']

      elif type_function == u'open_file_io_handle':
        arguments = [u'file_object', u'mode=\'r\'']

    elif type_function.startswith(u'read_'):
      function_type = FUNCTION_TYPE_READ

      if type_function == u'read_buffer':
        data_type = DATA_TYPE_BINARY_DATA
        arguments = [u'size']

      elif type_function == u'read_buffer_at_offset':
        data_type = DATA_TYPE_BINARY_DATA
        arguments = [u'size', u'offset']

    elif type_function.startswith(u'seek_'):
      function_type = FUNCTION_TYPE_SEEK

      if type_function == u'seek_offset':
        arguments = [u'offset', u'whence']

    elif type_function.startswith(u'set_'):
      function_type = FUNCTION_TYPE_SET

      # TODO: make more generic.
      if type_function == u'set_ascii_codepage':
        arguments = [u'codepage']

      elif type_function == u'set_parent_file':
        arguments = [u'parent_file']
 
      elif type_function == u'set_key':
        arguments = [u'mode', u'key']

      elif type_function == u'set_keys':
        arguments = [u'mode', u'key', u'tweak_key']

      elif type_function in (
          u'set_password', u'set_recovery_password', u'set_utf8_password'):
        arguments = [u'password']

      else:
        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, argument_name = value_argument_string.rpartition(u' ')
        argument_name.lstrip(u'*')
        arguments.append(argument_name)

        function_argument = function_prototype.arguments[
            value_argument_index + 1]
        value_size_argument_string = function_argument.CopyToString()

        if (value_argument_string == u'uint8_t *data' and
          value_size_argument_string == u'size_t data_size'):
          data_type = DATA_TYPE_BINARY_DATA

        elif (value_argument_string == u'uint8_t *utf8_string' and
            value_size_argument_string == u'size_t utf8_string_size'):
          data_type = DATA_TYPE_STRING

        elif (value_argument_string == u'char *string' and
            value_size_argument_string == u'size_t string_size'):
          data_type = DATA_TYPE_NARROW_STRING

        elif value_argument_string.startswith(
            project_configuration.library_name):
          data_type = DATA_TYPE_OBJECT

          object_type, _, _ = value_argument_string.partition(u' ')
          _, _, object_type = object_type.partition(u'_')
          object_type = object_type[:-2]

    elif type_function == u'signal_abort':
      function_type = FUNCTION_TYPE_UTILITY

    # elif type_function.startswith(u'write_'):
    #   function_type = FUNCTION_TYPE_WRITE

    python_function_prototype = PythonTypeObjectFunctionPrototype(
        project_configuration.python_module_name, type_name, type_function)

    python_function_prototype.arguments = arguments
    python_function_prototype.data_type = data_type
    python_function_prototype.function_type = function_type
    python_function_prototype.object_type = object_type
    python_function_prototype.value_type = value_type

    return python_function_prototype

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
      # Skip functions that are a wide character variant of another function.
      if type_function.endswith(u'_wide'):
        continue

      # Skip functions that retrieves the size of binary data.
      if (type_function.startswith(u'get_') and
          type_function.endswith(u'_data_size')):
        continue

      # Skip functions that retrieves the size of an UTF-8 string.
      if (type_function.startswith(u'get_utf8_') and
          type_function.endswith(u'_size')):
        continue

      if (type_function.startswith(u'get_') and
          type_function.endswith(u'_utf8_string_size')):
        continue

      # Skip functions that are a UTF-16 variant of another function.
      if (type_function.startswith(u'get_utf16_') or
          type_function.startswith(u'set_utf16_') or
          (type_function.startswith(u'get_') and (
              type_function.endswith(u'_by_utf16_name') or
              type_function.endswith(u'_by_utf16_path') or
              type_function.endswith(u'_utf16_string') or
              type_function.endswith(u'_utf16_string_size')))):
        continue

      # TODO: ignore these functions for now.
      if (type_function == u'get_type' and ( 
          project_configuration.library_name in (
              u'libmsiecf', u'libolecf', u'libpff'))):
        continue

      # TODO: remove when removed after deprecation.
      if (type_function.startswith(u'get_value_') and
          type_function != u'get_value_type' and
          project_configuration.library_name in (
              u'libolecf', )):
        continue

      if (type_function == u'get_version' and ( 
          project_configuration.library_name in (
              u'libevt', u'libevtx'))):
        continue

      if (type_function.startswith(u'write_buffer') and ( 
          project_configuration.library_name not in (
              u'libewf', ))):
        continue

      if type_function in (
          u'get_flags', u'get_offset_range', 
          u'get_number_of_unallocated_blocks', u'get_unallocated_block'):
        continue

      python_function_prototype = self._GetPythonTypeObjectFunctionPrototype(
          project_configuration, type_name, type_function, function_prototype)

      if (not python_function_prototype or
          not python_function_prototype.function_type):
        logging.warning(u'Skipping unsupported type function: {0:s}'.format(
          function_name))
        continue

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
    if name == u'key':
      return u'{0:s}s'.format(name)

    if (name[-1] in (u's', u'x', u'z') or (
        name[-1] == u'h'  and name[-2] in (u'c', u's'))):
      return u'{0:s}es'.format(name)

    if name[-1] == u'y':
      return u'{0:s}ies'.format(name[:-1])

    return u'{0:s}s'.format(name)

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
        FUNCTION_TYPE_GET, FUNCTION_TYPE_GET_BY_IDENTIFIER,
        FUNCTION_TYPE_GET_BY_INDEX, FUNCTION_TYPE_GET_BY_NAME,
        FUNCTION_TYPE_GET_BY_PATH):
      return None, None

    if python_function_prototype.data_type == DATA_TYPE_OBJECT:
      return python_function_prototype.object_type, True

    elif python_function_prototype.data_type == DATA_TYPE_STRING:
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
          include_header_file.GetAPITypeTestGroups())

      api_types.extend(api_types_with_input)
      types_with_sequence_types = set([])

      for type_name in api_types:
        self._SetTypeNameInTemplateMappings(template_mappings, type_name)

        python_function_prototypes = self._GetPythonTypeObjectFunctionPrototypes(
            project_configuration, type_name)

        for type_function, python_function_prototype in iter(
            python_function_prototypes.items()):

          sequence_type_name, type_is_object = self._GetSequenceType(
              python_function_prototype)
          if sequence_type_name:
            types_with_sequence_types.add((sequence_type_name, type_is_object))

        self._GenerateTypeSourceFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer)

        self._GenerateTypeHeaderFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer)

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
        if definitions_name in (u'access_flags', u'endian'):
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
      u'support', )

  _PYTHON_FUNCTION_WITH_INPUT_NAMES = (
      u'open_close', u'seek', u'read')

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
    template_directory = os.path.join(
        self._template_directory, u'yal_test_support')

    output_filename = u'{0:s}_test_support.c'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join(u'tests', output_filename)

    template_filename = os.path.join(template_directory, u'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    signature_type = include_header_file.GetCheckSignatureType()

    # TODO: add check for has codepage function for libsigscan and include
    # libcerror.
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
      if not include_header_file.HasFunction(support_function):
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
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, api_functions, api_functions_with_input, api_types,
      api_types_with_input, internal_types, output_writer):
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
      internal_types (list[str]): names of internal types to test.
      output_writer (OutputWriter): output writer.
    """
    tests = set(api_functions).union(set(api_functions_with_input))
    tests.update(set(api_types).union(set(api_types_with_input)))
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
    python_test_scripts = [u'test_python_functions.sh']

    check_scripts = [u'test_runner.sh']
    check_scripts.extend(test_scripts)
    if has_python_module:
      check_scripts.extend(python_scripts)
      check_scripts.extend(python_test_scripts)
      check_scripts.extend([
          u'{0:s}_test_support.py'.format(
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
      # Add libcsystem before non libyal cppflags.
      index = 0
      while index < len(cppflags):
        cppflag = cppflags[index]
        if not cppflag.startswith(u'lib') or cppflag == u'libcrypto':
          break
        index += 1

      cppflags.insert(index, u'libcsystem')

    cppflags = [u'@{0:s}_CPPFLAGS@'.format(name.upper()) for name in cppflags]

    cppflag = u'@{0:s}_DLL_IMPORT@'.format(
        project_configuration.library_name.upper())
    cppflags.append(cppflag)

    template_mappings[u'cppflags'] = u' \\\n'.join(
        [u'\t{0:s}'.format(name) for name in cppflags])
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

    for group_name in tests:
      if group_name in api_functions:
        has_error_argument = include_header_file.HasErrorArgument(group_name)
        if (project_configuration.library_name != u'libcerror' and
            group_name not in (u'error', u'notify') and has_error_argument):
          template_filename = u'yal_test_function.am'
        else:
          template_filename = u'yal_test_function_no_error.am'

        template_mappings[u'library_function'] = group_name

      elif group_name in api_functions_with_input:
        if group_name == u'support':
          template_filename = u'yal_test_support_with_input.am'
        else:
          template_filename = u'yal_test_function_with_input.am'

        template_mappings[u'library_function'] = group_name

      elif group_name in api_types or group_name in internal_types:
        if project_configuration.library_name == u'libcerror':
          template_filename = u'yal_test_type_no_error.am'
        else:
          template_filename = u'yal_test_type.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      elif group_name in api_types_with_input:
        template_filename = u'yal_test_type_with_input.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'footer.am')
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
        self._template_directory, u'pyyal_test_support')

    output_filename = u'{0:s}_test_support.py'.format(
        project_configuration.python_module_name)
    output_filename = os.path.join(u'tests', output_filename)

    template_filename = os.path.join(template_directory, u'header.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, u'imports.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, u'test_case.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    for support_function in (
        u'get_version', ):
      if not include_header_file.HasFunction(support_function):
        continue

      template_filename = u'{0:s}.py'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'main.py')
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
    template_directory = os.path.join(
        self._template_directory, u'pyyal_test_type')

    output_filename = u'{0:s}_test_{1:s}.py'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(u'tests', output_filename)

    template_filename = os.path.join(template_directory, u'header.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, u'imports.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    template_filename = os.path.join(template_directory, u'test_case.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

    # TODO: implement.
    for type_function in (
        u'open', u'set_ascii_codepage'):
      template_filename = u'{0:s}.py'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    template_filename = os.path.join(template_directory, u'main.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')

  def _GenerateTypeTest(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, output_writer, output_filename,
      initialize_is_internal=False, with_input=False):
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
    function_name = u'{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, type_name, type_function)

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return function_name, None, last_have_extern

    template_directory = os.path.join(
        self._template_directory, u'yal_test_type')

    template_filename = None
    value_name = None
    value_type = None

    if (type_function.startswith(u'get_utf8_') or
        type_function.startswith(u'get_utf16_')):
      function_argument = function_prototype.arguments[1]
      function_argument_string = function_argument.CopyToString()

      value_name = type_function[4:]
      value_type, _, _ = function_argument_string.partition(u' ')

      if type_function.endswith(u'_size'):
        if len(function_prototype.arguments) == 3:
          if with_input:
            template_filename = u'get_value_with_input.c'
          else:
            template_filename = u'get_value.c'

      else:
        if len(function_prototype.arguments) == 4:
          if with_input:
            template_filename = u'get_string_value_with_input.c'
          else:
            template_filename = u'get_string_value.c'

    elif (type_function.startswith(u'get_') and
        len(function_prototype.arguments) in (3, 4)):
      function_argument = function_prototype.arguments[1]
      function_argument_string = function_argument.CopyToString()

      value_name = type_function[4:]
      value_type, _, _ = function_argument_string.partition(u' ')

      if len(function_prototype.arguments) == 3:
        if value_type.startswith(project_configuration.library_name):
          value_type = value_type[:-2]

          if with_input:
            template_filename = u'get_type_value_with_input.c'
          else:
            template_filename = u'get_type_value.c'
        else:
          if with_input:
            template_filename = u'get_value_with_input.c'
          else:
            template_filename = u'get_value.c'

      elif function_argument_string == u'uint8_t *guid_data':
        if with_input:
          template_filename = u'get_guid_value_with_input.c'
        else:
          template_filename = u'get_guid_value.c'

    if not template_filename:
      template_filename = u'{0:s}.c'.format(type_function)

    self._SetValueNameInTemplateMappings(template_mappings, value_name)
    self._SetValueTypeInTemplateMappings(template_mappings, value_type)

    template_filename = os.path.join(template_directory, template_filename)
    if not os.path.exists(template_filename):
      logging.warning((
          u'Unable to generate test type source code for type function: '
          u'{0:s} with error: missing template').format(type_function))
      return function_name, None, last_have_extern

    if not initialize_is_internal:
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

    self._SetTypeNameInTemplateMappings(template_mappings, type_name)

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

    # TODO: treat external functions as internal when initialize_is_internal
    # except for free.
    have_extern = True
    initialize_is_internal = False
    initialize_number_of_arguments = None

    function_prototype = header_file.GetTypeFunction(type_name, u'initialize')
    if function_prototype:
      initialize_is_internal = not function_prototype.have_extern
      initialize_number_of_arguments = len(function_prototype.arguments)

      if is_internal or initialize_is_internal:
        template_filename = os.path.join(
            template_directory, u'includes_internal.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

      if initialize_number_of_arguments == 2:
        function_name, test_function_name, have_extern = self._GenerateTypeTest(
            project_configuration, template_mappings, type_name, u'initialize',
            have_extern, header_file, output_writer, output_filename,
            with_input=with_input)
      else:
        function_name = u'{0:s}_{1:s}_initialize'.format(
            project_configuration.library_name, type_name)
        test_function_name = None

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

    function_prototype = header_file.GetTypeFunction(type_name, u'free')
    if function_prototype:
      function_name, test_function_name, have_extern = self._GenerateTypeTest(
          project_configuration, template_mappings, type_name, u'free',
          have_extern, header_file, output_writer, output_filename,
          with_input=with_input)

      tests_to_run.append((function_name, test_function_name))
      function_names.remove(function_name)

      if initialize_is_internal and have_extern:
        template_filename = os.path.join(
            template_directory, u'define_internal_start.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='ab')

    # TODO: fix libbfio having no open wide.
    # TODO: make handling open close more generic for libpff attachment handle.
    for type_function in (u'open', u'open_wide', u'close'):
      function_name, test_function_name, have_extern = self._GenerateTypeTest(
          project_configuration, template_mappings, type_name, type_function,
          have_extern, header_file, output_writer, output_filename,
          initialize_is_internal=initialize_is_internal, with_input=with_input)

      if test_function_name:
        function_names.remove(function_name)

    if with_input:
      template_filename = os.path.join(template_directory, u'open_close.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

      # The open, close and open-close functions are defined in the template
      # so no need to add them to tests_to_run or tests_to_run_with_args.
      function_name = u'{0:s}_{1:s}_open_file_io_handle'.format(
          project_configuration.library_name, type_name)

      if function_name in function_names:
        function_names.remove(function_name)

      # TODO: remove open_read?

    function_name_prefix = u'{0:s}_{1:s}_'.format(
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

    if initialize_is_internal or not have_extern:
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
        header_file, output_writer, output_filename,
        initialize_is_internal=initialize_is_internal)

    if with_input:
      template_filename = os.path.join(
          template_directory, u'main_with_input_start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='ab')

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name,
        tests_to_run_with_args, header_file, output_writer, output_filename,
        initialize_is_internal=initialize_is_internal, with_args=True)

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
      header_file, output_writer, output_filename, initialize_is_internal=False,
      with_args=False):
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
      initialize_is_internal (Optional[bool]): True if the initialize function
          is not externally available.
      with_args (Optional[bool]): True if the tests to run have arguments.
    """
    template_directory = os.path.join(
        self._template_directory, u'yal_test_type')

    library_name_suffix = project_configuration.library_name_suffix.upper()

    last_have_extern = not initialize_is_internal
    tests_to_run_mappings = []
    for function_name, test_function_name in tests_to_run:
      function_prototype = header_file.functions_per_name.get(
          function_name, None)

      if function_prototype.name.endswith(u'_free'):
        have_extern = function_prototype.have_extern
      else:
        have_extern = (
            not initialize_is_internal and function_prototype.have_extern)

      if have_extern != last_have_extern:
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

        last_have_extern = have_extern

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
    # TODO: deprecate project_configuration.library_public_types ?
    # TODO: weave existing test files?
    # TODO: use data files to generate test data tests/input/.data/<name>
    # TODO: add support for options in configuration file to set option sets.

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
        include_header_file.GetAPIFunctionTestGroups())

    api_types, api_types_with_input = (
        include_header_file.GetAPITypeTestGroups())

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

    logging.info(u'Found public functions: {0:s}'.format(
        u', '.join(public_functions)))
    logging.info(u'Found public types: {0:s}'.format(u', '.join(public_types)))
    logging.info(u'Found internal types: {0:s}'.format(
        u', '.join(internal_types)))

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

    has_python_module = self._HasPythonModule(project_configuration)

    self._GenerateAPISupportTests(
        project_configuration, template_mappings, include_header_file,
        output_writer)

    if has_python_module:
      self._GeneratePythonModuleSupportTests(
          project_configuration, template_mappings, include_header_file,
          output_writer)

    for type_name in api_types:
      if (type_name == u'error' and
          project_configuration.library_name == u'libcerror'):
        continue

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer)
      if not result:
        api_types.remove(type_name)

      if has_python_module:
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer)

    for type_name in api_types_with_input:
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          with_input=True)
      if not result:
        api_types_with_input.remove(type_name)

      if has_python_module:
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer,
            with_input=True)

    for type_name in internal_types:
      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, output_writer,
          is_internal=True)
      if not result:
        internal_types.remove(type_name)

    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, api_functions, api_functions_with_input, api_types,
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

      else:
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

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

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
