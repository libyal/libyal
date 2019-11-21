# -*- coding: utf-8 -*-
"""Tests for the libyal source formatter classes."""

from __future__ import unicode_literals

import unittest

from yaldevtools import source_formatter

from tests import test_lib


class SourceFormatterTest(test_lib.BaseTestCase):
  """Libyal C source formatter tests."""

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

    # TODO: add tests for VerticalAlignEqualSignsDetermineOffset

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
    # TODO: add tests for FormatSource


if __name__ == '__main__':
  unittest.main()
