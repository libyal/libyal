# -*- coding: utf-8 -*-
"""Tests for the template string generator."""

import unittest

from yaldevtools import template_string

from tests import test_lib


class TemplateStringGeneratorTest(test_lib.BaseTestCase):
  """Template string generator tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    generator = template_string.TemplateStringGenerator()
    self.assertIsNotNone(generator)


if __name__ == '__main__':
  unittest.main()
