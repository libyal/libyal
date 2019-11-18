# -*- coding: utf-8 -*-
"""Shared test case."""

import io
import os
import sys
import unittest

from dtfabric import reader
from dtfabric import registry


def skipUnlessHasTestFile(path_segments):
  """Decorator to skip a test if the test file does not exist.

  Args:
    path_segments (list[str]): path segments inside the test data directory.

  Returns:
    function: to invoke.
  """
  fail_unless_has_test_file = getattr(
      unittest, u'fail_unless_has_test_file', False)

  path = os.path.join(u'test_data', *path_segments)
  if fail_unless_has_test_file or os.path.exists(path):
    return lambda function: function

  if sys.version_info[0] < 3:
    path = path.encode(u'utf-8')

  # Note that the message should be of type str which is different for
  # different versions of Python.
  return unittest.skip('missing test file: {0:s}'.format(path))


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  _TEST_DATA_PATH = os.path.join(os.getcwd(), u'test_data')

  # Show full diff results, part of TestCase so does not follow our naming
  # conventions.
  maxDiff = None

  def _CreateDefinitionRegistryFromFile(self, path):
    """Creates a data type definition registry from a file.

    Args:
      path (str): path to the data definition file.

    Returns:
      DataTypeDefinitionsRegistry: data type definition registry or None
          on error.
    """
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    self._FillDefinitionRegistryFromFile(definitions_registry, path)

    return definitions_registry

  def _FillDefinitionRegistryFromFile(self, definitions_registry, path):
    """Fills a data type definition registry from a file.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      path (str): path to the data definition file.

    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    with io.open(path, 'r', encoding='utf8') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def _GetTestFilePath(self, path_segments):
    """Retrieves the path of a test file in the test data directory.

    Args:
      path_segments (list[str]): path segments inside the test data directory.

    Returns:
      str: path of the test file.
    """
    # Note that we need to pass the individual path segments to os.path.join
    # and not a list.
    return os.path.join(self._TEST_DATA_PATH, *path_segments)
