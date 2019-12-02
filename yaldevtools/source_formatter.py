# -*- coding: utf-8 -*-
"""The libyal source formatter classes."""

from __future__ import print_function
from __future__ import unicode_literals


# TODO: have the SourceFormatter use the GroupModifier to detect a group
# of lines it applies to and then make the necessary changes.
class GroupModifier(object):
  """Group of lines modifier."""


# TODO: have the SourceFormatter use the LineModifier to detect a line
# it applies to and then make the necessary changes.
class LineModifier(object):
  """Line modifier."""


class Variable(object):
  """C variable."""

  _TYPE_SORT_RANKING = [
      'FILE',
      'size64_t',
      'size32_t',
      'size_t',
      'ssize_t',
      'off64_t',
      'off_t',
      'uint64_t',
      'int64_t',
      'uint32_t',
      'int32_t',
      'uint16_t',
      'int16_t',
      'uint8_t',
      'int8_t',
      'double',
      'float',
      'intptr_t',
      'int',
      'wchar_t',
      'char',
      'void']

  def __init__(self, declaration):
    """Initializes a C variable.

    Args:
      declaration (str): C variable declaration.
    """
    prefix, _, _ = declaration.partition('=')
    prefix = prefix.strip()
    prefix, _, name = prefix.rpartition(' ')
    modifiers, _, variable_type = prefix.rpartition(' ')

    is_pointer = name.startswith('*')
    if is_pointer:
      _, _, name = name.rpartition('*')

    try:
      variable_type_sort_ranking = (
          1 + self._TYPE_SORT_RANKING.index(variable_type))
    except ValueError:
      variable_type_sort_ranking = 0

    super(Variable, self).__init__()
    self.is_pointer = is_pointer
    self.name = name
    self.modifiers = modifiers
    self.type = variable_type
    self.type_sort_ranking = variable_type_sort_ranking

  def __eq__(self, other):
    """Checks if the variable equals another variable.

    Returns:
      bool: True if the variable equals another variable.
    """
    return self.Compare(other) == 0

  def __ge__(self, other):
    """Checks if the variable greater equals another variable.

    Returns:
      bool: True if the variable greater equals another variable.
    """
    return self.Compare(other) >= 0

  def __gt__(self, other):
    """Checks if the variable is greater than another variable.

    Returns:
      bool: True if the variable is greater than another variable.
    """
    return self.Compare(other) > 0

  def __le__(self, other):
    """Checks if the variable less equals another variable.

    Returns:
      bool: True if the variable less equals another variable.
    """
    return self.Compare(other) <= 0

  def __lt__(self, other):
    """Checks if the variable is less than another variable.

    Returns:
      bool: True if the variable is less than another variable.
    """
    return self.Compare(other) < 0

  def __ne__(self, other):
    """Checks if the variable not equals another variable.

    Returns:
      bool: True if the variable not equals another variable.
    """
    return self.Compare(other) != 0

  def Compare(self, variable):
    """Compares the variable with another variable.

    Returns:
      int: -1 if self should be ranked earlier, 0 if both variables are
          ranked equally, 1 if self should be ranked later
    """
    if self.is_pointer and not variable.is_pointer:
      return -1

    if not self.is_pointer and variable.is_pointer:
      return 1

    if self.type_sort_ranking < variable.type_sort_ranking:
      return -1

    if self.type_sort_ranking > variable.type_sort_ranking:
      return 1

    # If no specific sort ranking use alphabetically ordering without
    # the trailing '_t'.
    self_type, _, _ = self.type.rpartition('_t')
    variable_type, _, _ = variable.type.rpartition('_t')

    # (a > b) - (a < b) is a Python 3 compatable variant of cmp(a, b)
    variable_type_sort_ranking = (
        (self_type > variable_type) - (self_type < variable_type))

    if variable_type_sort_ranking != 0:
      return variable_type_sort_ranking

    # TODO: handle modifiers like const, static

    # (a > b) - (a < b) is a Python 3 compatable variant of cmp(a, b)
    return (self.name > variable.name) - (self.name < variable.name)


class SourceFormatter(object):
  """Libyal C source formatter."""

  def FormatLineIndentation(self, line, indentation_level):
    """Formats the identation for a line of C source.

    Args:
      line (str): line of C source.
      indentation_level (int): the indentation level.

    Returns:
      str: line of C source with formatted indentation.
    """
    index = 0
    line_length = len(line)

    for _ in range(0, indentation_level):
      maximum_end_index = min(index + 8, line_length)

      end_index = index
      while end_index < maximum_end_index:
        if line[end_index] != ' ':
          break
        end_index += 1

      # Merge less than 8 spaces and a tab.
      if end_index < maximum_end_index:
        if line[end_index] != '\t':
          break

        end_index += 1

      indentation = set(line[index:end_index])
      if indentation == set([' ']) or indentation == set([' ', '\t']):
        line = '{0:s}\t{1:s}'.format(line[:index], line[end_index:])
        line_length = len(line)

      index += 1

    while index < line_length:
      if line[index] == '\t':
        line = '{0:s}        {1:s}'.format(line[:index], line[index + 1:])
        line_length = len(line)

      index += 1

    return line

  def FormatSource(self, lines):
    """Formats lines of C source.

    Args:
      lines (list[str]): lines of C source.

    Returns:
      list[str]: formatted lines of C source.
    """
    in_variables_declaration_block = False
    in_function = False
    in_switch_case = False
    indentation_level = 0

    formatted_lines = []
    declaration_lines = []

    # TODO: add support for macro in libcerror/libcerror_system.c

    for line in lines:
      stripped_line = line.strip()

      if in_function:
        if line == '}':
          in_function = False
          indentation_level = 0

        elif in_variables_declaration_block:
          if ('(' not in stripped_line or
              stripped_line.startswith('#') or
              stripped_line.startswith('/*') or
              stripped_line.startswith('*') or
              stripped_line.startswith('*/')):
            declaration_lines.append(line)
            continue

          else:
            in_variables_declaration_block = False

        elif stripped_line == '}':
          indentation_level -= 1

      # TODO: refactor to separate function
      if declaration_lines:
        alignment_offset = self.VerticalAlignEqualSignsDetermineOffset(
            declaration_lines)

        block_of_declaration_lines = []
        for declaration_line in declaration_lines:
          stripped_declaration_line = declaration_line.strip()
          if stripped_declaration_line and not (
                  stripped_declaration_line.startswith('#') or
                  stripped_declaration_line.startswith('/*') or
                  stripped_declaration_line.startswith('*') or
                  stripped_declaration_line.startswith('*/')):
            block_of_declaration_lines.append(declaration_line)
            continue

          if block_of_declaration_lines:
            block_of_declaration_lines.sort(key=lambda line: Variable(line))
            block_of_declaration_lines = self.VerticalAlignEqualSigns(
                block_of_declaration_lines, alignment_offset)

            formatted_lines.extend(block_of_declaration_lines)
            block_of_declaration_lines = []

          formatted_lines.append(declaration_line)

        declaration_lines = []

      line = self.FormatLineIndentation(line, indentation_level)
      formatted_lines.append(line)

      if in_function:
        if stripped_line == '{':
          indentation_level += 1

        # TODO: handle switch case with return.
        elif in_switch_case and (
            stripped_line == 'break;' or
            line == '{0:s}}}'.format('\t' * (indentation_level - 1))):
          in_switch_case = False
          indentation_level -= 1

        elif not in_switch_case and (
            stripped_line.startswith('case ') or stripped_line == 'default:'):
          in_switch_case = True
          indentation_level += 1

      elif line == '{':
        in_function = True
        in_variables_declaration_block = True
        indentation_level = 1

    return formatted_lines

  def VerticalAlignEqualSigns(self, lines, alignment_offset):
    """Vertically aligns the equal signs.

    Args:
      lines (list[str]): C variable declarations.
      alignment_offset (int): aligment offset.

    Returns:
      list[str]: C variable declarations with aligned equal signs.
    """
    aligned_lines = []
    for line in lines:
      stripped_line = line.strip()
      if '=' in stripped_line and not stripped_line.endswith(' = {'):
        prefix, _, suffix = line.rpartition('=')
        prefix = prefix.rstrip()
        formatted_prefix = prefix.replace('\t', ' ' * 8)

        alignment_size = alignment_offset - len(formatted_prefix)
        alignment = ' ' * alignment_size

        line = '{0:s}{1:s}={2:s}'.format(prefix, alignment, suffix)

      aligned_lines.append(line)

    return aligned_lines

  def VerticalAlignEqualSignsDetermineOffset(self, lines):
    """Determines the alignment offset to vertically align the equal signs.

    Args:
      lines (list[str]): C variable declarations.

    Returns:
      int: aligment offset or None if no equal sign was found.
    """
    alignment_offset = None
    for line in lines:
      stripped_line = line.strip()
      if '=' not in stripped_line or stripped_line.endswith(' = {'):
        continue

      prefix, _, _ = line.rpartition('=')
      prefix = prefix.rstrip()
      formatted_prefix = prefix.replace('\t', ' ' * 8)

      equal_sign_offset = len(formatted_prefix) + 1

      if alignment_offset is None:
        alignment_offset = equal_sign_offset
      else:
        alignment_offset = max(alignment_offset, equal_sign_offset)

    return alignment_offset
