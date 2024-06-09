# -*- coding: utf-8 -*-
"""YAML-based generator operations file."""

import yaml

from yaldevtools import resources


class YAMLGeneratorOperationsFile(object):
  """YAML-based generator operations file.

  A YAML-based generator operations file contains one or more generator
  operations. A generator operation consists of:

  identifier: header
  type: template
  file: mount_fuse.h/header.h
  mappings:
  - copyright

  Where:
  * identifier, defines the name that identifies the generator operation;
  * TODO: describe additional values.
  """

  _SUPPORTED_KEYS = frozenset([
      'condition',
      'identifier',
      'fallback_file',
      'file',
      'mappings',
      'modifiers',
      'operations',
      'type'])

  _SUPPORTED_KEYS_TYPE_GROUP = frozenset([
      'condition',
      'identifier',
      'operations',
      'type'])

  _SUPPORTED_KEYS_TYPE_TEMPLATE = frozenset([
      'condition',
      'identifier',
      'fallback_file',
      'file',
      'mappings',
      'modifiers',
      'type'])

  _SUPPORTED_TYPES = frozenset([
      'group',
      'template'])

  def _ReadGeneratorOperation(self, yaml_generator_operation):
    """Reads a generator operation from a dictionary.

    Args:
      yaml_generator_operation (dict[str, object]): YAML generator operation
          values.

    Returns:
      GeneratorOperation: generator operation.

    Raises:
      RuntimeError: if the format of the formatter operation is not set
          or incorrect.
    """
    if not yaml_generator_operation:
      raise RuntimeError('Missing generator operation values.')

    keys = set(yaml_generator_operation)

    different_keys = keys - self._SUPPORTED_KEYS
    if different_keys:
      different_keys = ', '.join(different_keys)
      raise RuntimeError('Undefined keys: {0:s}'.format(different_keys))

    operation_identifier = yaml_generator_operation.get('identifier', None)
    if operation_identifier is None:
      raise RuntimeError(
          'Invalid generator operation missing generator identifier.')

    operation_type = yaml_generator_operation.get('type', None)
    if operation_type is None:
      raise RuntimeError('Invalid generator operation missing generator type.')

    if operation_type not in self._SUPPORTED_TYPES:
      raise RuntimeError(
          'Unsupported generator operation type: {operation_type:s}.')

    generator_operation = resources.GeneratorOperation(
        identifier=operation_identifier, type=operation_type)

    if operation_type == 'group':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_GROUP
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError('Unsupported keys: {0:s}'.format(different_keys))

      generator_operation.condition = yaml_generator_operation.get(
          'condition', None)
      generator_operation.operations = yaml_generator_operation.get(
          'operations', None)

    elif operation_type == 'template':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_TEMPLATE
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError('Unsupported keys: {0:s}'.format(different_keys))

      generator_operation.condition = yaml_generator_operation.get(
          'condition', None)
      generator_operation.fallback_file = yaml_generator_operation.get(
          'fallback_file', None)
      generator_operation.file = yaml_generator_operation.get('file', None)
      generator_operation.mappings = yaml_generator_operation.get(
          'mappings', None)
      generator_operation.modifiers = yaml_generator_operation.get(
          'modifiers', None)

    return generator_operation

  def _ReadFromFileObject(self, file_object):
    """Reads the event formatters from a file-like object.

    Args:
      file_object (file): formatters file-like object.

    Yields:
      GeneratorOperation: generator operation.
    """
    for yaml_generator_operation in yaml.safe_load_all(file_object):
      yield self._ReadGeneratorOperation(yaml_generator_operation)

  def ReadFromFile(self, path):
    """Reads the event formatters from a YAML file.

    Args:
      path (str): path to a formatters file.

    Yields:
      GeneratorOperation: generator operation.
    """
    with open(path, 'r', encoding='utf-8') as file_object:
      yield from self._ReadFromFileObject(file_object)
