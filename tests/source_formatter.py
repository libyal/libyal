# -*- coding: utf-8 -*-
"""Tests for the libyal source formatter classes."""

from __future__ import unicode_literals

import unittest

from yaldevtools import source_formatter

from tests import test_lib


class SourceFormatterTest(test_lib.BaseTestCase):
  """Libyal C source formatter tests."""

  # TODO: add tests for FormatLineIndentation

  def testFormatSource(self):
    """Tests the FormatSource function."""
    test_formatter = source_formatter.SourceFormatter()

    expected_lines = """
int myfunction(
     int *argument )
{
	int first  = 0;
	int second = 0;

	if( argument == NULL )
	{
		return( -1 );
	}
	first = anotherfunction(
	         argument );

	return( first );
}
"""

    lines = """
int myfunction(
     int *argument )
{
	int first = 0;
	int second = 0;

	if( argument == NULL )
	{
                return( -1 );
	}
	first = anotherfunction(
		 argument );

	return( first );
}
"""

    lines = test_formatter.FormatSource(lines.split('\n'))
    lines = '\n'.join(lines)

    self.assertEqual(lines, expected_lines)

  def testVerticalAlignEqualSigns(self):
    """Tests the VerticalAlignEqualSigns function."""
    test_formatter = source_formatter.SourceFormatter()

    expected_lines = [
        'int first  = NULL;',
        'int second = NULL;',
        '']

    lines = [
        'int first = NULL;',
        'int second = NULL;',
        '']

    lines = test_formatter.VerticalAlignEqualSigns(lines, 11)
    self.assertEqual(lines, expected_lines)

  def testVerticalAlignEqualSignsDetermineOffset(self):
    """Tests the VerticalAlignEqualSignsDetermineOffset function."""
    test_formatter = source_formatter.SourceFormatter()

    lines = [
        'int first = NULL;',
        'int second = NULL;',
        '']

    offset = test_formatter.VerticalAlignEqualSignsDetermineOffset(lines)
    self.assertEqual(offset, 11)


if __name__ == '__main__':
  unittest.main()
