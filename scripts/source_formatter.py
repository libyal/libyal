#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to format source of the libyal libraries."""

from __future__ import print_function
import sys


class Variable(object):
  """Class that defines a C variable."""

  _TYPE_SORT_RANKING = [
      b'FILE',
      b'size64_t',
      b'size32_t',
      b'size_t',
      b'ssize_t',
      b'off64_t',
      b'off_t',
      b'uint64_t',
      b'uint32_t',
      b'uint16_t',
      b'uint8_t',
      b'int64_t',
      b'int32_t',
      b'int16_t',
      b'int8_t',
      b'double',
      b'float',
      b'intptr_t',
      b'int',
      b'wchar_t',
      b'char',
      b'void']
 
  def __init__(self, declaration):
    """Initializes a C variable.

    Args:
      declaration (str): C variable declaration.
    """
    prefix, _, suffix = declaration.partition(b'=')
    prefix = prefix.strip()
    prefix, _, name = prefix.rpartition(b' ')
    modifiers, _, variable_type = prefix.rpartition(b' ')

    is_pointer = name.startswith(b'*')
    if is_pointer:
      _, _, name = name.rpartition(b'*')

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
    self_type, _, _ = self.type.rpartition(b'_t')
    variable_type, _, _ = variable.type.rpartition(b'_t')
    variable_type_sort_ranking = cmp(self_type, variable_type)
    if variable_type_sort_ranking != 0:
      return variable_type_sort_ranking

    # TODO: handle modifiers like const, static

    return cmp(self.name, variable.name)


class SourceFormatter(object):
  """Class that defines a C source formatter."""

  def CompareVariableDeclarations(
      self, first_variable_declaration, second_variable_declaration):
    """Compares two C variable declarations.

    Args:
      first_variable_declaration (str): first C variable declaration.
      second_variable_declaration (str): second C variable declaration.

    Returns:
      int: -1 if the first declaration should be ranked earlier, 0 if both
          declarations are ranked equally, 1 if the first declaration should
          be ranked later
    """
    first_variable = Variable(first_variable_declaration)
    second_variable = Variable(second_variable_declaration)
    return first_variable.Compare(second_variable)

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
      if b'=' in striped_line and not striped_line.endswith(b' = {'):
        prefix, _, suffix = line.rpartition(b'=')
        prefix = prefix.rstrip()
        formatted_prefix = prefix.replace(b'\t', ' ' * 8)

        alignment_size = alignment_offset - len(formatted_prefix)
        alignment = b' ' * alignment_size

        line = b'{0:s}{1:s}={2:s}'.format(prefix, alignment, suffix)

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
      if b'=' not in striped_line or striped_line.endswith(b' = {'):
        continue

      prefix, _, suffix = line.rpartition(b'=')
      prefix = prefix.rstrip()
      formatted_prefix = prefix.replace(b'\t', ' ' * 8)

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
        if striped_line.endswith(b'};'):
          in_declaration_block = False
        formatted_lines.append(line)
        continue

      if striped_line.endswith(b' = {'):
        in_declaration_block = True
        formatted_lines.append(line)
        continue

      if (striped_line and
          not striped_line.startswith(b'#') and
          not striped_line.startswith(b'/*') and
          not striped_line.startswith(b'*/')):
        declaration_lines.append(line)
        continue

      declaration_lines.sort(self.CompareVariableDeclarations)
      declaration_lines = self.VerticalAlignEqualSigns(
          declaration_lines, alignment_offset)

      formatted_lines.extend(declaration_lines)
      formatted_lines.append(line)
      declaration_lines = []

    if declaration_lines:
      declaration_lines.sort(self.CompareVariableDeclarations)
      declaration_lines = self.VerticalAlignEqualSigns(
          declaration_lines, alignment_offset)

      formatted_lines.extend(declaration_lines)
      declaration_lines = []

    return formatted_lines

