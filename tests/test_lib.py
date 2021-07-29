# -*- coding: utf-8 -*-
"""Shared test case."""

import io
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
