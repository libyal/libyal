#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the YAML-based properties operations file."""

import unittest

from yaldevtools import yaml_operations_file

from tests import test_lib


class YAMLGeneratorOperationsFileTest(test_lib.BaseTestCase):
  """Tests for the YAML-based properties operations file."""

  # pylint: disable=protected-access

  _TEST_YAML = {
      'identifier': 'header',
      'type': 'template',
      'file': 'mount_fuse.h/header.h'}

  def testReadGeneratorOperation(self):
    """Tests the _ReadGeneratorOperation function."""
    test_operations_file = (
        yaml_operations_file.YAMLGeneratorOperationsFile())

    operations = test_operations_file._ReadGeneratorOperation(self._TEST_YAML)

    self.assertIsNotNone(operations)
    self.assertEqual(operations.identifier, 'header')

    with self.assertRaises(RuntimeError):
      test_operations_file._ReadGeneratorOperation({})

    with self.assertRaises(RuntimeError):
      test_operations_file._ReadGeneratorOperation({
          'type': 'template',
          'file': 'mount_fuse.h/header.h'})

    with self.assertRaises(RuntimeError):
      test_operations_file._ReadGeneratorOperation({
          'identifier': 'header',
          'file': 'mount_fuse.h/header.h'})

    with self.assertRaises(RuntimeError):
      test_operations_file._ReadGeneratorOperation({
          'identifier': 'header',
          'type': 'bogus',
          'file': 'mount_fuse.h/header.h'})

  def testReadFromFileObject(self):
    """Tests the _ReadFromFileObject function."""
    test_file_path = self._GetTestFilePath(['operations.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    test_operations_file = (
        yaml_operations_file.YAMLGeneratorOperationsFile())

    with open(test_file_path, 'r', encoding='utf-8') as file_object:
      operations = list(test_operations_file._ReadFromFileObject(file_object))

    self.assertEqual(len(operations), 5)

  def testReadFromFile(self):
    """Tests the ReadFromFile function."""
    test_file_path = self._GetTestFilePath(['operations.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    test_operations_file = (
        yaml_operations_file.YAMLGeneratorOperationsFile())

    operations = list(test_operations_file.ReadFromFile(test_file_path))

    self.assertEqual(len(operations), 5)

    self.assertEqual(operations[0].identifier, 'mount_fuse.h')
    self.assertEqual(operations[4].identifier, 'listxattr')


if __name__ == '__main__':
  unittest.main()
