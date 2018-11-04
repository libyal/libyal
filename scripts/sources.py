
            # -*- coding: utf-8 -*-
"""The C sources classes."""

from __future__ import unicode_literals

import collections

import definitions


class EnumDeclaration(object):
  """Enumeration type declaration.

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
  """Function argument."""

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

    argument_string = ''
    if number_of_strings == 1:
      argument_string = self._strings[0]

    elif number_of_strings > 1:
      argument_string = '{0:s}{1:s}'.format(
          self._strings[0], ', '.join(self._strings[1:]))

    return argument_string


class FunctionPrototype(object):
  """Function prototype.

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
    return_values (set[str]): return values or None if the function does not
        return values.
    value_description (str): description of the value.
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
    self.return_values = None
    self.value_description = None

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

    return ', '.join(argument_strings)


class PythonTypeObjectFunctionPrototype(object):
  """Python type object function prototype.

  Attributes:
    arguments (list[str]): arguments.
    data_type (str): data type.
    function_type (str): function type.
    object_type (str): object type.
    return_values (set[str]): return values or None if the function does not
        return values.
    value_description (str): description of the value.
    value_type (str): value type.
  """

  def __init__(self, python_module_name, type_name, type_function):
    """Initializes a Python type object function prototype.

    Args:
      python_module_name (str): python module name.
      type_name (str): type name.
      type_function (str): type function.
    """
    super(PythonTypeObjectFunctionPrototype, self).__init__()
    self._name = None
    self._python_module_name = python_module_name
    self._type_function = type_function
    self._type_name = type_name
    self._value_name = None
    self.arguments = []
    self.data_type = definitions.DATA_TYPE_NONE
    self.function_type = None
    self.object_type = None
    self.return_values = None
    self.value_description = None
    self.value_type = None

  @property
  def name(self):
    """str: name."""
    if self._name is None:
      self._name = '{0:s}_{1:s}_{2:s}'.format(
          self._python_module_name, self._type_name, self.type_function)

    return self._name

  @property
  def type_function(self):
    """str: type function."""
    # TODO: make overrides more generic.
    if self._type_function == 'set_parent_file':
      return 'set_parent'

    if (self._type_function.startswith('copy_') and
        not self._type_function.startswith('copy_from_')):
      return 'get_{0:s}'.format(self._type_function[5:])

    if (self._type_function.startswith('get_utf8_') or
        self._type_function.startswith('set_utf8_')):
      return ''.join([self._type_function[:4], self._type_function[9:]])

    if self._type_function.startswith('get_data_as_'):
      _, _, type_function_suffix = self._type_function.partition('_data_as_')

      if type_function_suffix in (
          '16bit_integer', '32bit_integer', '64bit_integer'):
        return 'get_data_as_integer'

      elif type_function_suffix in ('filetime', 'floatingtime'):
        return 'get_data_as_datetime'

      elif type_function_suffix == 'utf8_string':
        return 'get_data_as_string'

      else:
        return self._type_function

    if self._type_function.startswith('get_'):
      type_function_prefix, _, type_function_suffix = (
          self._type_function.partition('_by_'))

      if type_function_suffix in ('entry', 'index'):
        return type_function_prefix

      if type_function_suffix in ('utf8_name', 'utf8_path'):
        return ''.join([self._type_function[:-10], self._type_function[-5:]])

      if self._type_function.endswith('_utf8_string'):
        return ''.join([self._type_function[:-12], self._type_function[-7:]])

      if self._type_function.endswith('_utf8_string_size'):
        return ''.join([self._type_function[:-17], self._type_function[-12:]])

    return self._type_function

  @property
  def value_name(self):
    """str: value name."""
    if self._value_name is None:
      # TODO: make overrides more generic.
      if self.function_type == definitions.FUNCTION_TYPE_COPY:
        if self._type_function.startswith('copy_'):
          self._value_name = self._type_function[5:]

      elif self.function_type == definitions.FUNCTION_TYPE_COPY_FROM:
        if self._type_function.startswith('copy_from_'):
          self._value_name = self._type_function[10:]

      elif self.function_type == definitions.FUNCTION_TYPE_COPY_TO:
        if self._type_function.startswith('get_'):
          self._value_name = self._type_function[4:]

      elif self.function_type in (
          definitions.FUNCTION_TYPE_GET,
          definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
          definitions.FUNCTION_TYPE_GET_BY_INDEX,
          definitions.FUNCTION_TYPE_GET_BY_NAME,
          definitions.FUNCTION_TYPE_GET_BY_PATH):
        type_function_prefix, _, _ = self._type_function.partition('_by_')

        if type_function_prefix.startswith('get_'):
          type_function_prefix = type_function_prefix[4:]

        if type_function_prefix.startswith('utf8_'):
          type_function_prefix = type_function_prefix[5:]

        self._value_name = type_function_prefix

      elif self.function_type == definitions.FUNCTION_TYPE_IS:
        if self._type_function.startswith('is_'):
          self._value_name = self._type_function[3:]

      elif self.function_type == definitions.FUNCTION_TYPE_SET:
        if self._type_function.startswith('set_utf8_'):
          self._value_name = self._type_function[9:]

        elif self._type_function.startswith('set_'):
          self._value_name = self._type_function[4:]

    return self._value_name

  def DataTypeIsDatetime(self):
    """Determines if the data type is a datetime type.

    Returns:
      bool: True if the data type is a datetime type.
    """
    return self.data_type in (
        definitions.DATA_TYPE_FAT_DATE_TIME,
        definitions.DATA_TYPE_FILETIME,
        definitions.DATA_TYPE_FLOATINGTIME,
        definitions.DATA_TYPE_POSIX_TIME)

  def DataTypeIsFloat(self):
    """Determines if the data type is a floating-point type.

    Returns:
      bool: True if the data type is a floating-point type.
    """
    return self.data_type in (
        definitions.DATA_TYPE_FLOAT, 
        definitions.DATA_TYPE_DOUBLE)

  def DataTypeIsInteger(self):
    """Determines if the data type is an integer type.

    Returns:
      bool: True if the data type is an integer type.
    """
    return self.data_type in (
        definitions.DATA_TYPE_INT,
        definitions.DATA_TYPE_INT32,
        definitions.DATA_TYPE_OFF64,
        definitions.DATA_TYPE_SIZE32,
        definitions.DATA_TYPE_SIZE64,
        definitions.DATA_TYPE_UINT8,
        definitions.DATA_TYPE_UINT16,
        definitions.DATA_TYPE_UINT32,
        definitions.DATA_TYPE_UINT64)

  def GetAttributeDescription(self):
    """Retrieves the fuction as attribute description.

    Returns:
      str: function as attribute description.
    """
    description = ''

    type_function = self.type_function
    value_name = self.value_name
    if value_name:
      value_name = value_name.replace('_', ' ')

    if type_function == 'get_ascii_codepage':
      description = (
          'The codepage used for ASCII strings in the {0:s}.').format(
              self._type_name)

    elif type_function == 'get_data_as_boolean':
      description = 'The data as a boolean.'

    elif type_function == 'get_data_as_datetime':
      description = 'The data as a datetime object.'

    elif type_function == 'get_data_as_integer':
      description = 'The data as an integer.'

    elif type_function == 'get_data_as_floating_point':
      description = 'The data as a floating point.'

    elif type_function == 'get_data_as_string':
      description = 'The data as a string.'

    elif self.function_type == definitions.FUNCTION_TYPE_IS:
      type_name = self._type_name
      if type_name:
        type_name = type_name.replace('_', ' ')

      description = 'Indicates the {0:s} is {1:s}.'.format(
          type_name, value_name)

    elif self.value_description:
      description = 'The {0:s}.'.format(self.value_description)

    elif value_name:
      description = 'The {0:s}.'.format(value_name)

    return description

  def GetDataTypeDescription(self):
    """Retrieves the data type description.

    Returns:
      str: data type description.
    """
    if self.data_type == definitions.DATA_TYPE_BINARY_DATA:
      data_type_description = 'Binary string'

    elif self.data_type == definitions.DATA_TYPE_BOOLEAN:
      data_type_description = 'Boolean'

    elif self.DataTypeIsDatetime():
      data_type_description = 'Datetime'

    elif self.data_type == definitions.DATA_TYPE_OBJECT:
      data_type_description = 'Object'

    elif self.DataTypeIsFloat():
      data_type_description = 'Float'

    elif self.DataTypeIsInteger():
      data_type_description = 'Integer'

    elif self.data_type in (
        definitions.DATA_TYPE_GUID,
        definitions.DATA_TYPE_STRING,
        definitions.DATA_TYPE_UUID):
      data_type_description = 'Unicode string'

    elif self.data_type == definitions.DATA_TYPE_NARROW_STRING:
      data_type_description = 'String'

    elif self.data_type == definitions.DATA_TYPE_NONE:
      data_type_description = 'None'

    else:
      data_type_description = self.data_type

    if (data_type_description != 'None' and self.return_values and
        'None' in self.return_values):
      data_type_description = '{0:s} or None'.format(data_type_description)

    return data_type_description

  def GetDescription(self):
    """Retrieves the description.

    Returns:
      list[str]: lines of the description.
    """
    description = ['']

    type_function = self.type_function

    type_name = self._type_name
    if type_name:
      type_name = type_name.replace('_', ' ')

    value_name = self.value_name
    if value_name:
      value_name = value_name.replace('_', ' ')

    if type_function == 'close':
      description = ['Closes a {0:s}.'.format(type_name)]

    elif type_function == 'get_ascii_codepage':
      description = [(
          'Retrieves the codepage for ASCII strings used in '
          'the {0:s}.').format(type_name)]

    elif type_function == 'get_data_as_boolean':
      description = ['Retrieves the data as a boolean.']

    elif type_function == 'get_data_as_datetime':
      description = ['Retrieves the data as a datetime object.']

    elif type_function == 'get_data_as_integer':
      description = ['Retrieves the data as an integer.']

    elif type_function == 'get_data_as_floating_point':
      description = ['Retrieves the data as a floating point.']

    elif type_function == 'get_data_as_string':
      description = ['Retrieves the data as a string.']

    elif type_function == 'get_string':
      description = ['Retrieves the {0:s} formatted as a string.'.format(
          type_name)]

    elif type_function == 'open':
      description = ['Opens a {0:s}.'.format(type_name)]

    elif type_function == 'open_file_object':
      description = [(
          'Opens a {0:s} using a file-like object.').format(type_name)]

    elif type_function == 'read_buffer':
      description = ['Reads a buffer of data.']

    elif type_function == 'read_buffer_at_offset':
      description = ['Reads a buffer of data at a specific offset.']

    elif type_function == 'seek_offset':
      description = ['Seeks an offset within the data.']

    elif type_function == 'set_ascii_codepage':
      description = [
          ('Sets the codepage for ASCII strings used in the '
           '{0:s}.').format(type_name),
          ('Expects the codepage to be a string containing a Python '
           'codec definition.')]

    elif type_function == 'set_parent':
      description = ['Sets the parent file.']

    elif type_function == 'signal_abort':
      description = ['Signals the {0:s} to abort the current activity.'.format(
          type_name)]

    elif self.function_type == definitions.FUNCTION_TYPE_GET_BY_INDEX:
      _, _, argument_suffix = self.arguments[0].rpartition('_')
      if self.value_description:
        description = ['Retrieves the {0:s} specified by the {1:s}.'.format(
            self.value_description, argument_suffix)]
      else:
        description = ['Retrieves the {0:s} specified by the {1:s}.'.format(
            value_name, argument_suffix)]

    elif self.function_type in (
        definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
        definitions.FUNCTION_TYPE_GET_BY_NAME,
        definitions.FUNCTION_TYPE_GET_BY_PATH):
      _, _, type_function_suffix = type_function.partition('_by_')
      if self.value_description:
        description = ['Retrieves the {0:s} specified by the {1:s}.'.format(
            self.value_description, type_function_suffix)]
      else:
        description = ['Retrieves the {0:s} specified by the {1:s}.'.format(
            value_name, type_function_suffix)]

    elif self.function_type == definitions.FUNCTION_TYPE_COPY_FROM:

      # TODO: fix value name.
      description = ['Copies the {0:s} from the {1:s}.'.format(
          type_name, value_name)]

    elif self.function_type in (
        definitions.FUNCTION_TYPE_COPY, definitions.FUNCTION_TYPE_GET):
      if self.value_description:
        description = ['Retrieves the {0:s}.'.format(self.value_description)]
      else:
        description = ['Retrieves the {0:s}.'.format(value_name)]

    elif self.function_type == definitions.FUNCTION_TYPE_IS:
      description = ['Determines if the {0:s} is {1:s}.'.format(
          type_name, value_name)]

    elif self.function_type == definitions.FUNCTION_TYPE_SET:
      description = ['Sets the {0:s}.'.format(value_name)]

    return description

  def GetValueNameAndPrefix(self):
    """Determines the value name and its prefix.

    Returns:
      tuple[str, str]: value name and prefix.
    """
    if self.value_name:
      value_name_prefix, _, value_name = self.value_name.partition('_')
      if value_name_prefix in ('root', 'sub'):
        return value_name, value_name_prefix

    return self.value_name, None
