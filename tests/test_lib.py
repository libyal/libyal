# -*- coding: utf-8 -*-
"""Shared test case."""

import os
import unittest

from dtfabric import reader
from dtfabric import registry


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  _TEST_DATA_PATH = os.path.join(os.getcwd(), 'test_data')

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

    Raises:
      SkipTest: if the data definition file does not exist and the test should
          be skipped.
    """
    self._SkipIfPathNotExists(path)

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

    with open(path, 'rb') as file_object:
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

  def _SkipIfPathNotExists(self, path):
    """Skips the test if the path does not exist.

    Args:
      path (str): path of a test file.

    Raises:
      SkipTest: if the path does not exist and the test should be skipped.
    """
    if not os.path.exists(path):
      filename = os.path.basename(path)
      raise unittest.SkipTest(f'missing test file: {filename:s}')
