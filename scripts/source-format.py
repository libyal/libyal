#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to format source of the libyal libraries."""

from __future__ import print_function
import sys


class Variable(object):
  """Class that defines a C variable."""

  _TYPE_SORT_RANKING = [
      'FILE',
      'size64_t',
      'size32_t',
      'size_t',
      'ssize_t',
      'off64_t',
      'off_t',
      'uint64_t',
      'uint32_t',
      'uint16_t',
      'uint8_t',
      'int64_t',
      'int32_t',
      'int16_t',
      'uint8_t',
      'double',
      'float',
      'int',
      'char']
 
  def __init__(self, declaration):
    """Initializes a C variable.

    Args:
      declaration (str): C variable declaration.
    """
    prefix, _, suffix = declaration.partition('=')
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

    # If no specific sort ranking use alphabetically ordering.
    variable_type_sort_ranking = cmp(self.type, variable.type)
    if variable_type_sort_ranking != 0:
      return variable_type_sort_ranking

    # TODO: handle modifiers like const, static

    return cmp(self.name, variable.name)


def CompareVariableDeclarations(
    first_variable_declaration, second_variable_declaration):
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


def VerticalAlignEqualSigns(lines, alignment_offset=None):
  """Vertically aligns the equal signs.

  Args:
    lines (list[str]): C variable declarations.
    alignment_offset (Optional[int]): aligment offset, where None indicates
        the function should determine the alingment offset based on the equal
        signs.

  Returns:
    tuple: contains:
      list[str]: C variable declarations with aligned equal signs.
      int: aligment offset.
  """
  if alignment_offset is None:
    for line in lines:
      if '=' not in line:
        continue

      prefix, _, suffix = line.rpartition(u'=')
      prefix = prefix.rstrip()
      formatted_prefix = prefix.replace(u'\t', ' ' * 8)

      equal_sign_offset = len(formatted_prefix) + 1

      if alignment_offset is None:
        alignment_offset = equal_sign_offset
      else:
        alignment_offset = max(alignment_offset, equal_sign_offset)

  aligned_lines = []
  for line in lines:
    if '=' in line:
      prefix, _, suffix = line.rpartition(u'=')
      prefix = prefix.rstrip()
      formatted_prefix = prefix.replace(u'\t', ' ' * 8)

      alignment_size = alignment_offset - len(formatted_prefix)
      alignment = u' ' * alignment_size

      line = u'{0:s}{1:s}={2:s}'.format(prefix, alignment, suffix)

    aligned_lines.append(line)

  return aligned_lines, alignment_offset


if __name__ == '__main__':
  # TODO: handle conditional declarations (#if ...)

  # TODO: handle if largest declaration is not in first block
  # * determine aligment offset first for all lines

  lines = []
  alignment_offset = None
  declaration_lines = []
  for line in sys.stdin.readlines():
    if line.strip() and not line.startswith('#'):
      declaration_lines.append(line)
      continue

    declaration_lines.sort(CompareVariableDeclarations)
    declaration_lines, alignment_offset = VerticalAlignEqualSigns(
        declaration_lines, alignment_offset=alignment_offset)

    lines.extend(declaration_lines)
    lines.append(line)
    declaration_lines = []

  if declaration_lines:
    declaration_lines.sort(CompareVariableDeclarations)
    declaration_lines, alignment_offset = VerticalAlignEqualSigns(
        declaration_lines, alignment_offset=alignment_offset)

    lines.extend(declaration_lines)
    declaration_lines = []

  print(''.join(lines), end='')
  
