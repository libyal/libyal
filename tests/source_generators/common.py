# -*- coding: utf-8 -*-
"""Tests for the source file generator for common source files."""

from __future__ import unicode_literals

import os
import unittest

from yaldevtools.source_generators import common

from tests import test_lib


class CommonSourceFileGeneratorTest(test_lib.BaseTestCase):
  """Common source files generator tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    source_directory = os.path.abspath(__file__)
    source_directory = os.path.dirname(source_directory)
    source_directory = os.path.dirname(source_directory)
    source_directory = os.path.dirname(source_directory)

    projects_directory = os.path.dirname(source_directory)
    data_directory = os.path.join(source_directory, 'data')
    template_directory = os.path.join(data_directory, 'source', 'common')

    generator = common.CommonSourceFileGenerator(
        projects_directory, data_directory, template_directory)
    self.assertIsNotNone(generator)

  # TODO: add tests for Generate function.


if __name__ == '__main__':
  unittest.main()
