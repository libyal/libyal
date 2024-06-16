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
  placeholders:
  - copyright

  Where:
  * identifier, defines the name that identifies the generator operation;
  * TODO: describe additional values.
  """

  _SUPPORTED_KEYS_TYPE_GROUP = frozenset([
      'condition',
      'identifier',
      'modifiers',
      'operations',
      'type'])

  _SUPPORTED_KEYS_TYPE_SELECTION = frozenset([
      'condition',
      'default',
      'identifier',
      'input',
      'modifiers',
      'options',
      'type'])

  _SUPPORTED_KEYS_TYPE_SEQUENCE = frozenset([
      'condition',
      'identifier',
      'input',
      'fallback',
      'modifiers',
      'operations',
      'placeholder',
      'type'])

  _SUPPORTED_KEYS_TYPE_TEMPLATE = frozenset([
      'condition',
      'identifier',
      'fallback',
      'file',
      'modifiers',
      'placeholders',
      'type'])

  _SUPPORTED_KEYS = set(
      _SUPPORTED_KEYS_TYPE_GROUP).union(
      _SUPPORTED_KEYS_TYPE_SELECTION).union(
      _SUPPORTED_KEYS_TYPE_SEQUENCE).union(
      _SUPPORTED_KEYS_TYPE_TEMPLATE)

  _SUPPORTED_TYPES = frozenset([
      'group',
      'selection',
      'sequence',
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
      raise RuntimeError(f'Undefined keys: {different_keys:s}')

    operation_identifier = yaml_generator_operation.get('identifier', None)
    if not operation_identifier:
      raise RuntimeError(
          'Invalid generator operation missing generator identifier.')

    operation_type = yaml_generator_operation.get('type', None)
    if not operation_type:
      raise RuntimeError(f'Missing type in {operation_identifier:s}')

    if operation_type not in self._SUPPORTED_TYPES:
      raise RuntimeError(
          f'Unsupported generator operation type: {operation_type:s}.')

    generator_operation = resources.GeneratorOperation(
        identifier=operation_identifier, type=operation_type)
    generator_operation.condition = yaml_generator_operation.get(
        'condition', None)
    generator_operation.modifiers = yaml_generator_operation.get(
        'modifiers', None)

    if operation_type == 'group':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_GROUP
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError(
            f'Unsupported keys: {different_keys:s} in {operation_identifier:s}')

      operations = yaml_generator_operation.get('operations', None)
      if not operations:
        raise RuntimeError(f'Missing operations in {operation_identifier:s}')

      generator_operation.operations = operations

    elif operation_type == 'selection':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_SELECTION
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError(
            f'Unsupported keys: {different_keys:s} in {operation_identifier:s}')

      operation_input = yaml_generator_operation.get('input', None)
      if not operation_input:
        raise RuntimeError(f'Missing input in {operation_identifier:s}')

      yaml_options = yaml_generator_operation.get('options', None)
      if not yaml_options:
        raise RuntimeError(f'Missing options in {operation_identifier:s}')

      generator_operation.input = operation_input
      generator_operation.options = {
         yaml_option['value']: yaml_option['operation']
         for yaml_option in yaml_options}

    elif operation_type == 'sequence':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_SEQUENCE
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError(
            f'Unsupported keys: {different_keys:s} in {operation_identifier:s}')

      operation_input = yaml_generator_operation.get('input', None)
      if not operation_input:
        raise RuntimeError(f'Missing input in {operation_identifier:s}')

      operations = yaml_generator_operation.get('operations', None)
      if not operations:
        raise RuntimeError(f'Missing operations in {operation_identifier:s}')

      placeholder = yaml_generator_operation.get('placeholder', None)
      if not placeholder:
        raise RuntimeError(f'Missing placeholder in {operation_identifier:s}')

      generator_operation.fallback = yaml_generator_operation.get(
          'fallback', None)
      generator_operation.input = operation_input
      generator_operation.operations = operations
      generator_operation.placeholder = placeholder

    elif operation_type == 'template':
      different_keys = keys - self._SUPPORTED_KEYS_TYPE_TEMPLATE
      if different_keys:
        different_keys = ', '.join(different_keys)
        raise RuntimeError(
            f'Unsupported keys: {different_keys:s} in {operation_identifier:s}')

      file = yaml_generator_operation.get('file', None)
      if not file:
        raise RuntimeError(f'Missing file in {operation_identifier:s}')

      generator_operation.fallback = yaml_generator_operation.get(
          'fallback', None)
      generator_operation.file = file
      generator_operation.placeholders = yaml_generator_operation.get(
          'placeholders', None)

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
