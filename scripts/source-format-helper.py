#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Libyal CLI source format helper."""

from __future__ import print_function
from __future__ import unicode_literals

import sys


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
  """C source formatter."""

  def VerticalAlignEqualSigns(self, lines, alignment_offset):
    """Vertically aligns the equal signs.

    Args:
      lines (list[str]): C variable declarations.
      alignment_offset (Optional[int]): aligment offset, where None indicates
          the function should determine the alingment offset based on the equal
          signs.

    Returns:
      list[str]: C variable declarations with aligned equal signs.
    """
    aligned_lines = []
    for line in lines:
      striped_line = line.strip()
      if '=' in striped_line and not striped_line.endswith(' = {'):
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
      striped_line = line.strip()
      if '=' not in striped_line or striped_line.endswith(' = {'):
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

  def FormatSource(self, lines):
    """Formats lines of C source.

    Args:
      lines (list[str]): lines of C source.

    Returns:
      list[str]: formatted lines of C source.
    """
    alignment_offset = self.VerticalAlignEqualSignsDetermineOffset(lines)

    in_declaration_block = False
    formatted_lines = []
    declaration_lines = []
    for line in lines:
      striped_line = line.strip()
      if in_declaration_block:
        if striped_line.endswith('};'):
          in_declaration_block = False
        formatted_lines.append(line)
        continue

      if striped_line.endswith(' = {'):
        in_declaration_block = True
        formatted_lines.append(line)
        continue

      if (striped_line and
          not striped_line.startswith('#') and
          not striped_line.startswith('/*') and
          not striped_line.startswith('*/')):
        declaration_lines.append(line)
        continue

      declaration_lines.sort(key=lambda line: Variable(line))
      declaration_lines = self.VerticalAlignEqualSigns(
          declaration_lines, alignment_offset)

      formatted_lines.extend(declaration_lines)
      formatted_lines.append(line)
      declaration_lines = []

    if declaration_lines:
      declaration_lines.sort(key=lambda line: Variable(line))
      declaration_lines = self.VerticalAlignEqualSigns(
          declaration_lines, alignment_offset)

      formatted_lines.extend(declaration_lines)
      declaration_lines = []

    return formatted_lines


if __name__ == '__main__':
  formatter = SourceFormatter()
  lines = formatter.FormatSource(sys.stdin.readlines())

  print(''.join(lines), end='')
