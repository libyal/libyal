# -*- coding: utf-8 -*-
"""The C sources classes."""

from __future__ import unicode_literals

import collections


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

    return ', '.join(argument_strings)
