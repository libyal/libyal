#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to generate source based on dtFabric format definitions."""

import argparse
import datetime
import logging
import os
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

from yaldevtools import configuration
from yaldevtools import source_formatter
from yaldevtools.source_generators import interface


# TODO: put signature into constants: libyal_constants.[ch]


class TemplateRuntimeStructureMember(object):
  """Runtime structure member.

  Attributes:
    data_size (str): data size.
    data_type (str): data type.
    description (str): description.
    name (str): name.
    value_type (str): value type.
  """

  def __init__(self):
    """Initializes a runtime structure member."""
    super(TemplateRuntimeStructureMember, self).__init__()
    self.data_size = None
    self.data_type = None
    self.description = None
    self.name = None
    self.value_type = None


class SourceGenerator(interface.BaseSourceFileGenerator):
  """Generates source based on dtFabric format definitions."""

  _DEBUG_FORMAT_DECIMAL = 'decimal'
  _DEBUG_FORMAT_HEXADECIMAL = 'hexadecimal'

  # The member is used for debugging.
  _USAGE_DEBUG = 'debug'
  # The member is used in the read_data function.
  _USAGE_IN_FUNCTION = 'in_function'
  # The member is used in the runtime struct.
  _USAGE_IN_STRUCT = 'in_struct'

  _CHARACTER_DATA_TYPES = {
      1: 'char',
  }

  _CHARACTER_FORMAT_INDICATORS = {
      1: '%c',
  }

  _FLOATING_POINT_DATA_TYPES = {
      4: 'float',
      8: 'double',
  }

  _FLOATING_POINT_FORMAT_INDICATORS = {
      4: '%f',
      8: '%f',
  }

  _HEXADECIMAL_FORMAT_INDICATORS = {
      1: '0x%02" PRIx8 "',
      2: '0x%04" PRIx16 "',
      4: '0x%08" PRIx32 "',
      8: '0x%08" PRIx64 "',
  }

  _SIGNED_INTEGER_DATA_TYPES = {
      1: 'int8_t',
      2: 'int16_t',
      4: 'int32_t',
      8: 'int64_t',
  }

  _SIGNED_INTEGER_FORMAT_INDICATORS = {
      1: '%" PRIi8 "',
      2: '%" PRIi16 "',
      4: '%" PRIi32 "',
      8: '%" PRIi64 "',
  }

  _UNSIGNED_INTEGER_DATA_TYPES = {
      1: 'uint8_t',
      2: 'uint16_t',
      4: 'uint32_t',
      8: 'uint64_t',
  }

  _UNSIGNED_INTEGER_FORMAT_INDICATORS = {
      1: '%" PRIu8 "',
      2: '%" PRIu16 "',
      4: '%" PRIu32 "',
      8: '%" PRIu64 "',
  }

  _NON_PRINTABLE_CHARACTERS = list(range(0, 0x20)) + list(range(0x7f, 0xa0))
  _ESCAPE_CHARACTERS = str.maketrans({
      value: f'\\x{value:02x}'
      for value in _NON_PRINTABLE_CHARACTERS})

  def __init__(self, templates_path):
    """Initializes a source generator.

    Args:
      templates_path (str): path of the directory containing the template files.
    """
    super(SourceGenerator, self).__init__(templates_path)
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._generate_structure_member_contents_hint = True
    self._generate_structure_member_size_hint = False
    self._prefix = None

  def _FormatTestData(self, data):
    """Formats the test data as a C byte array.

    Args:
      data (bytes): data.

    Returns:
      str: data as a C byte array.
    """
    # TODO: print text as text?

    hexadecimal_lines = []
    data_size = len(data)
    for block_index in range(0, data_size, 16):
      data_string = data[block_index:block_index + 16]

      hexadecimal_string = ', '.join([
          f'0x{byte_value:02x}' for byte_value in data_string[0:16]])

      if len(data_string) < 16 or block_index + 16 == data_size:
        hexadecimal_lines.append(f'\t{hexadecimal_string:s}')
      else:
        hexadecimal_lines.append(f'\t{hexadecimal_string:s},')

    return '\n'.join(hexadecimal_lines)

  def _GenerateRuntimeStructureHeaderFile(
      self, data_type_definition, members_configuration):
    """Generates a runtime structure header file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.h')

    template_mappings = self._GetTemplateMappings(
        library_name=f'lib{self._prefix:s}',
        structure_name=data_type_definition.name)

    if not self._prefix:
      output_filename = 'runtime_structure.h'
    else:
      output_filename = os.path.join(
          f'lib{self._prefix:s}',
          f'lib{self._prefix:s}_{data_type_definition.name:s}.h')

    logging.info(f'Writing: {output_filename:s}')

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = ''.join([
        structure_description[0].upper(), structure_description[1:]])

    structure_members = self._GetTemplateRuntimeStructureMembers(
        data_type_definition, members_configuration)

    template_mappings['structure_description_title'] = (
        structure_description_title)
    template_mappings['structure_members'] = structure_members
    template_mappings['structure_options'] = members_configuration.get(
         '__options__', {})

    self._GenerateSectionsFromOperationsFile(
        'runtime_structure.h.yaml', 'main', None, template_mappings,
        output_filename)

    del template_mappings['structure_description_title']
    del template_mappings['structure_members']
    del template_mappings['structure_options']

  def _GenerateRuntimeStructureSourceFile(
      self, data_type_definition, members_configuration):
    """Generates a runtime structure source file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.
    """
    structure_options = members_configuration.get('__options__', {})

    has_datetime_member = False
    has_string_member = False
    has_uuid_member = False

    for member_definition in data_type_definition.members:
      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_STRING:
        has_string_member = True

      elif type_indicator == definitions.TYPE_INDICATOR_UUID:
        has_uuid_member = True

      member_data_type = getattr(member_definition, 'member_data_type', None)
      if member_data_type in ('filetime', 'posix_time'):
        has_datetime_member = True

    template_mappings = self._GetTemplateMappings(
        library_name=f'lib{self._prefix:s}',
        structure_name=data_type_definition.name)

    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    if not self._prefix:
      output_filename = 'runtime_structure.c'
    else:
      output_filename = os.path.join(
          f'lib{self._prefix:s}',
          f'lib{self._prefix:s}_{data_type_definition.name:s}.c')

    logging.info(f'Writing: {output_filename:s}')

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = ''.join([
        structure_description[0].upper(), structure_description[1:]])

    # TODO: refactor move into sub method - start

    check_signature_structure_members = []

    for member_definition in data_type_definition.members:
      member_name = member_definition.name

      # data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      supported_values = getattr(member_definition, 'values', None)
      if not supported_values:
        continue

      member_value_type = self._GetRuntimeStructureMemberValueType(
          member_data_type_definition)

      member_value = None
      member_value_size = None

      if member_value_type == 'integer':
        data_type_size = member_definition.GetByteSize()

        member_value = supported_values[0]
        member_value_size = data_type_size * 8

      elif member_value_type in ('stream', 'stream_fixed_size'):
        member_value = supported_values[0].decode('ascii')
        member_value = member_value.translate(self._ESCAPE_CHARACTERS)
        member_value_size = len(supported_values[0])

      elif member_value_type == 'uuid':
        member_value = supported_values[0].decode('ascii')
        member_value = member_value.translate(self._ESCAPE_CHARACTERS)
        member_value_size = 16

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_name.replace('_', ' ')

      structure_member = TemplateRuntimeStructureMember()
      structure_member.description = ''.join([
          description[0].lower(), description[1:]])
      structure_member.name = member_name
      structure_member.value = member_value
      structure_member.value_size = member_value_size
      structure_member.value_type = member_value_type

      check_signature_structure_members.append(structure_member)

    # TODO: refactor move into sub method - end

    template_mappings['check_signature_structure_members'] = (
        check_signature_structure_members)

    template_mappings['has_datetime_member'] = has_datetime_member
    template_mappings['has_string_member'] = has_string_member
    template_mappings['has_uuid_member'] = has_uuid_member

    # Indentation needs to account for "*name = ".
    template_mappings['initialize_memory_allocate_indentation'] = ' ' * (
        len(data_type_definition.name) + 4)

    template_mappings['read_data_debug_variables'] = (
        self._GetRuntimeStructureSourceFunctionReadDataDebugVariables(
            data_type_definition, members_configuration))
    template_mappings['read_data_variables'] = (
        self._GetRuntimeStructureSourceFunctionReadDataVariables(
            data_type_definition, members_configuration))

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = (
        structure_description_title)
    template_mappings['structure_options'] = members_configuration.get(
         '__options__', {})

    self._GenerateSectionsFromOperationsFile(
        'runtime_structure.c.yaml', 'main', None, template_mappings,
        output_filename)

    del template_mappings['check_signature_structure_members']

    del template_mappings['has_datetime_member']
    del template_mappings['has_string_member']
    del template_mappings['has_uuid_member']

    del template_mappings['initialize_memory_allocate_indentation']

    del template_mappings['read_data_debug_variables']
    del template_mappings['read_data_variables']

    del template_mappings['structure_description']
    del template_mappings['structure_description_title']
    del template_mappings['structure_options']

    # TODO: refactor move to operations file

    structure_members = []

    for member_definition in data_type_definition.members:
      member_name = member_definition.name

      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      member_configuration = members_configuration.get(
          structure_member.name, {})

      member_byte_order = None
      member_data_type = None
      member_element_data_size = None
      member_usage = member_configuration.get('usage', self._USAGE_DEBUG)
      member_value_type = self._GetRuntimeStructureMemberValueType(
          member_data_type_definition)

      if member_value_type == 'filetime':
        # TODO: get byte order from member_data_type_definition.
        member_byte_order = 'little_endian'
        member_data_type = 'uint64'

      elif member_value_type == 'posix_time':
        # TODO: get byte order from member_data_type_definition.
        member_byte_order = 'little_endian'
        member_data_type = 'uint32'

      elif (member_value_type == 'integer' and
            data_type_size and data_type_size > 1):
        # TODO: get byte order from member_data_type_definition.
        member_byte_order = 'little_endian'
        member_data_type = data_type

      elif member_value_type in ('string', 'string_fixed_size'):
        elements_terminator = getattr(
            member_data_type_definition, 'elements_terminator', None)
        if elements_terminator is not None:
          element_data_type_definition = (
              member_data_type_definition.element_data_type_definition)
          member_element_data_size = element_data_type_definition.GetByteSize()

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_name.replace('_', ' ')

      description = ''.join([description[0].lower(), description[1:]])

      structure_member = TemplateRuntimeStructureMember()
      structure_member.byte_order = member_byte_order
      structure_member.data_type = member_data_type
      structure_member.description = description
      structure_member.element_data_size = member_element_data_size
      structure_member.name = member_name
      structure_member.usage = member_usage
      structure_member.value_type = member_value_type

      structure_members.append(structure_member)

    for structure_member in structure_members:
      if structure_member.usage != self._USAGE_IN_STRUCT:
        continue

      template_mappings['structure_member'] = structure_member

      data_offset_is_set = False
      template_filename = 'read_data-unsupported.c'

      if structure_member.value_type in ('filetime', 'integer', 'posix_time'):
        if structure_member.data_type.startswith('int'):
          template_filename = 'read_data-integer.c'
        else:
          template_filename = 'read_data-unsigned_integer.c'

      elif structure_member.value_type in ('string', 'string_fixed_size'):
        if structure_member.element_data_size in (1, 2):
          if not data_offset_is_set:
            template_filename = os.path.join(
                template_directory, 'read_data-data_offset.c')
            self._GenerateSection(
                template_filename, template_mappings, output_filename,
                access_mode='a')

            template_filename = 'read_data-unsupported.c'
            data_offset_is_set = True

          if structure_member.element_data_size == 1:
            template_filename = 'read_data-string_8bit.c'
          elif structure_member.element_data_size == 2:
            template_filename = 'read_data-string_16bit.c'

      elif structure_member.value_type == 'uuid':
        template_filename = 'read_data-guid.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

      del template_mappings['structure_member']

    template_filename = os.path.join(
        template_directory, 'read_data-debug_start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    # TODO: refactor move to operations file

    # TODO: add support for debug output of trailing units, such as "X bytes"

    function_name = (
        f'lib{self._prefix:s}_{data_type_definition.name:s}_read_data')

    # Default alignment is 9 tabs.
    tab_alignment = 9 * 8
    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      debug_line = f'{function_name:s}: {member_name:s}'
      debug_line_length = len(debug_line)
      if debug_line_length > tab_alignment:
        tab_alignment = debug_line_length

    _, remainder = divmod(tab_alignment, 8)
    if remainder > 0:
      tab_alignment += 8 - remainder

    structure_members = []

    for member_definition in data_type_definition.members:
      member_name = member_definition.name

      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      member_value_type = self._GetRuntimeStructureMemberValueType(
          member_data_type_definition)

      member_configuration = members_configuration.get(
          structure_member.name, {})

      member_byte_order = None
      member_format_indicator = None
      member_usage = member_configuration.get('usage', self._USAGE_DEBUG)
      member_value_size = data_type_size

      if member_value_type == 'integer':
        # TODO: get byte order from member_data_type_definition.
        member_byte_order = 'little_endian'
        member_value_size *= 8

        debug_format = member_configuration.get(
            'debug_format', self._DEBUG_FORMAT_DECIMAL)
        member_format_indicator = self._GetRuntimePrintfFormatIndicator(
            member_definition, debug_format)

      # Use the member name as the debug description.
      description = member_name.replace('_', ' ')

      structure_member = TemplateRuntimeStructureMember()
      structure_member.byte_order = member_byte_order
      structure_member.data_type = data_type
      structure_member.description = description
      structure_member.name = member_name
      structure_member.format_indicator = member_format_indicator
      structure_member.usage = member_usage
      structure_member.value_size = member_value_size
      structure_member.value_type = member_value_type

      structure_members.append(structure_member)

    for structure_member in structure_members:
      template_filename = 'read_data-debug-unsupported.c'

      if structure_member.value_type == 'filetime':
        template_filename = 'read_data-debug-filetime.c'

      elif structure_member.value_type == 'integer':
        if structure_member.usage == self._USAGE_IN_FUNCTION:
          template_filename = 'read_data-debug-integer-in_function.c'

        elif structure_member.usage == self._USAGE_IN_STRUCT:
          if structure_member.name.endswith('_flags'):
            template_filename = 'read_data-debug-integer-in_struct-as_flags.c'
          else:
            template_filename = 'read_data-debug-integer-in_struct.c'

        elif structure_member.usage == self._USAGE_IN_FUNCTION:
          # TODO: improve.
          template_filename = 'read_data-debug-integer.c'

        else:
          template_filename = 'read_data-debug-integer.c'

      elif structure_member.value_type == 'padding':
        template_filename = 'read_data-debug-padding.c'

      elif structure_member.value_type == 'posix_time':
        template_filename = 'read_data-debug-posix_time.c'

      elif structure_member.value_type in ('stream', 'stream_fixed_size'):
        supported_values = getattr(member_definition, 'values', None)

        if supported_values:
          format_indicator = ['%c'] * len(supported_values[0])
          for supported_value in supported_values:
            if isinstance(supported_value, str):
              for index, character in enumerate(supported_value):
                if not character.isalnum():
                  format_indicator[index] = '\\x%02" PRIx8 "'

          member_data_arguments = []
          for byte_index in range(len(supported_values[0])):
            argument = '\t\t ( ({0:s}_{1:s}_t *) data )->{2:s}[ {3:d} ]'.format(
                self._prefix, data_type_definition_name, structure_member.name,
                byte_index)
            member_data_arguments.append(argument)

          template_filename = 'read_data-debug-signature.c'

          template_mappings['format_indicator'] = ''.join(format_indicator)
          template_mappings['member_data_arguments'] = ',\n'.join(
              member_data_arguments)

        elif structure_member.value_size:
          template_filename = 'read_data-debug-stream_with_data_size.c'

        else:
          template_filename = 'read_data-debug-stream.c'

      elif structure_member.value_type in ('string', 'string_fixed_size'):
        # TODO: handle evt "data_size - 4"
        elements_terminator = getattr(
            member_data_type_definition, 'elements_terminator', None)
        if elements_terminator is not None:
          element_data_type_definition = (
              member_data_type_definition.element_data_type_definition)
          element_data_size = element_data_type_definition.GetByteSize()
          if element_data_size == 2:
            template_filename = 'read_data-debug-string_16bit.c'

      elif structure_member.value_type == 'uuid':
        template_filename = 'read_data-debug-guid.c'

      template_filename = os.path.join(template_directory, template_filename)

      # Determine the number of tabs for alignment.
      debug_line = f'{function_name:s}: {structure_member.description:s}'
      debug_line_length = len(debug_line)

      number_of_tabs, remainder = divmod(tab_alignment - debug_line_length, 8)
      if remainder > 0:
        number_of_tabs += 1

      template_mappings['format_indicator'] = structure_member.format_indicator
      template_mappings['structure_member'] = structure_member
      template_mappings['tab_alignment'] = '\\t' * number_of_tabs

      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

      del template_mappings['structure_member']
      del template_mappings['tab_alignment']

    template_filename = os.path.join(
        template_directory, 'read_data-debug_end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_filename = os.path.join(template_directory, 'read_data-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if 'file_io_handle' in structure_options:
      template_mappings['structure_description'] = structure_description

      template_filename = os.path.join(
          template_directory, 'read_file_io_handle.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

      del template_mappings['structure_description']

    self._SortIncludeHeaders(output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignAssignmentStatements(output_filename)

  def _GenerateRuntimeStructureTestSourceFile(
      self, project_configuration, data_type_definition, members_configuration):
    """Generates a runtime structure test source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.
    """
    # TODO: handle multiple data file.
    test_data = self._ReadTestDataFile(data_type_definition.name)

    if not self._prefix:
      output_filename = 'runtime_structure_test.c'
    else:
      output_filename = os.path.join(
          'tests', f'{self._prefix:s}_test_{data_type_definition.name:s}.c')

    logging.info(f'Writing: {output_filename:s}')

    template_mappings = self._GetTemplateMappings(
        library_name=f'lib{self._prefix:s}',
        structure_name=data_type_definition.name)

    template_mappings['test_data'] = self._FormatTestData(test_data)
    template_mappings['test_data_size'] = len(test_data)

    # TODO: add support for get functions.

    self._GenerateSectionsFromOperationsFile(
        'runtime_structure_test.c.yaml', 'main', project_configuration,
        template_mappings, output_filename)

    del template_mappings['test_data']
    del template_mappings['test_data_size']

  def _GenerateStoredStructureHeader(
      self, data_type_definition, members_configuration, output_filename):
    """Generates a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.
      output_filename (str): name of the output file.
    """
    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition.name)

    structure_members = self._GetStoredStructureHeaderMembers(
        data_type_definition, members_configuration)

    template_mappings['structure_members'] = structure_members

    template_filename = os.path.join(
        self._templates_path, 'stored_structure.h', 'structure.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['structure_members']

  def _GenerateStoredStructureHeaderFile(
      self, data_type_definition, members_configuration):
    """Generates a stored structure header file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.
    """
    template_directory = os.path.join(
        self._templates_path, 'stored_structure.h')

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition.name)

    if not self._prefix:
      output_filename = 'stored_structure.h'
    else:
      output_filename = os.path.join(
          f'lib{self._prefix:s}',
          f'{self._prefix:s}_{data_type_definition.name:s}.h')

    logging.info(f'Writing: {output_filename:s}')

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description = ''.join([
        structure_description[0].upper(), structure_description[1:]])

    format_definition = self._GetFormatDefinitions()
    if format_definition.description:
      structure_description = (
          f'{structure_description:s} of the {format_definition.description:s}')

    template_mappings['structure_description'] = structure_description

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    del template_mappings['structure_description']

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definitions = data_type_definition.members
    else:
      structure_definitions = [data_type_definition]

    for structure_definition in structure_definitions:
      self._GenerateStoredStructureHeader(
          structure_definition, members_configuration, output_filename)

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._SortIncludeHeaders(output_filename)

  def _GetFormatDefinitions(self):
    """Retrieves the format definition.

    Returns:
      FormatDefinition: format definition.

    Raises:
      RuntimeError: if the format definition is mission or more than 1
          format definition is defined.
    """
    # pylint: disable=protected-access

    if not self._definitions_registry._format_definitions:
      raise RuntimeError('Missing format definition.')

    if len(self._definitions_registry._format_definitions) > 1:
      raise RuntimeError('Unsupported multiple format definitions.')

    return self._definitions_registry.GetDefinitionByName(
        self._definitions_registry._format_definitions[0])

  def _GetRuntimeDataType(self, data_type_definition):
    """Retrieves a runtime data type.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: runtime data type or None if not available.
    """
    type_indicator = data_type_definition.TYPE_INDICATOR

    if type_indicator == definitions.TYPE_INDICATOR_CHARACTER:
      return self._CHARACTER_DATA_TYPES.get(data_type_definition.size, None)

    if type_indicator == definitions.TYPE_INDICATOR_FLOATING_POINT:
      return self._FLOATING_POINT_DATA_TYPES.get(
          data_type_definition.size, None)

    if type_indicator in (definitions.TYPE_INDICATOR_BOOLEAN,
                          definitions.TYPE_INDICATOR_INTEGER):
      if data_type_definition.format == definitions.FORMAT_SIGNED:
        return self._SIGNED_INTEGER_DATA_TYPES.get(
            data_type_definition.size, None)

      return self._UNSIGNED_INTEGER_DATA_TYPES.get(
          data_type_definition.size, None)

    return None

  def _GetRuntimePrintfFormatIndicator(
      self, data_type_definition, debug_format):
    """Retrieves a runtime printf format indicator.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      debug_format (str): debug format as defined by the member configuration.

    Returns:
      str: C runtime data type or None if not available.
    """
    data_type_definition = getattr(
        data_type_definition, 'member_data_type_definition',
        data_type_definition)

    format_indicator = None
    if debug_format == self._DEBUG_FORMAT_HEXADECIMAL:
      format_indicator = self._HEXADECIMAL_FORMAT_INDICATORS.get(
          data_type_definition.size, None)

    elif debug_format == self._DEBUG_FORMAT_DECIMAL:
      type_indicator = data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_CHARACTER:
        format_indicator = self._CHARACTER_FORMAT_INDICATORS.get(
            data_type_definition.size, None)

      elif type_indicator == definitions.TYPE_INDICATOR_FLOATING_POINT:
        format_indicator = self._FLOATING_POINT_FORMAT_INDICATORS.get(
            data_type_definition.size, None)

      elif type_indicator in (
          definitions.TYPE_INDICATOR_BOOLEAN,
          definitions.TYPE_INDICATOR_INTEGER):
        if data_type_definition.format == definitions.FORMAT_SIGNED:
          format_indicator = self._SIGNED_INTEGER_FORMAT_INDICATORS.get(
              data_type_definition.size, None)
        else:
          format_indicator = self._UNSIGNED_INTEGER_FORMAT_INDICATORS.get(
              data_type_definition.size, None)

    return format_indicator

  def _GetRuntimeStructureMemberValueType(self, member_data_type_definition):
    """Retrieves a runtime structure member value type.

    Args:
      member_data_type_definition (dtfabric.DataTypeDefinition): member data
          type definition.

    Returns:
      str: member value type or None if unknown.
    """
    if member_data_type_definition.name == 'filetime':
      return 'filetime'

    if member_data_type_definition.name == 'posix_time':
      return 'posix_time'

    type_indicator = member_data_type_definition.TYPE_INDICATOR

    if type_indicator == definitions.TYPE_INDICATOR_INTEGER:
      return 'integer'

    if type_indicator == definitions.TYPE_INDICATOR_PADDING:
      return 'padding'

    if type_indicator == definitions.TYPE_INDICATOR_STREAM:
      if 'fixed_size' in member_options:
        return 'stream_fixed_size'
      else:
        return 'stream'

    if type_indicator == definitions.TYPE_INDICATOR_STRING:
      if 'fixed_size' in member_options:
        return 'string_fixed_size'
      else:
        return 'string'

    if type_indicator == definitions.TYPE_INDICATOR_UUID:
      return 'uuid'

    return None

  def _GetRuntimeStructureSourceFunctionReadDataDebugVariables(
      self, data_type_definition, members_configuration):
    """Retrieves the debug variables part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.

    Returns:
      str: debug variables part of a read_data function.
    """
    debug_variables = set()

    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      member_usage = members_configuration.get(member_name, {}).get(
          'usage', self._USAGE_DEBUG)
      if member_usage != self._USAGE_DEBUG:
        continue

      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_INTEGER:
        data_bit_size = data_type_size * 8
        debug_variables.add(
            f'\tuint{data_bit_size:d}_t value_{data_bit_size:d}bit = 0;')

      elif type_indicator == definitions.TYPE_INDICATOR_PADDING:
        debug_variables.add(f'\tconst uint8_t *{member_name:s} = NULL;')
        debug_variables.add(f'\tsize_t {member_name:s}_size = 0;')

    return '\n'.join(sorted(debug_variables))

  def _GetRuntimeStructureSourceFunctionReadDataVariables(
      self, data_type_definition, members_configuration):
    """Retrieves the variables part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.

    Returns:
      str: variables part of a read_data function.
    """
    variables = set()

    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      member_usage = members_configuration.get(member_name, {}).get(
          'usage', self._USAGE_DEBUG)

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_INTEGER:
        if member_usage == self._USAGE_IN_FUNCTION:
          data_type_size = member_definition.GetByteSize()
          variable = '\tuint{0:d}_t {1:s} = 0;'.format(
              data_type_size * 8, member_name)
          variables.add(variable)

      # TODO: add support for padding type?

      elif type_indicator == definitions.TYPE_INDICATOR_STREAM:
        if member_usage in (self._USAGE_IN_FUNCTION, self._USAGE_IN_STRUCT):
          variable = '\tsize_t data_offset = 0;'
          variables.add(variable)

        if member_usage == self._USAGE_IN_FUNCTION:
          variable = '\tconst uint8_t *{0:s} = NULL;'.format(member_name)
          variables.add(variable)

      elif type_indicator == definitions.TYPE_INDICATOR_STRING:
        elements_terminator = getattr(
            member_data_type_definition, 'elements_terminator', None)
        if elements_terminator is not None:
          if member_usage in (self._USAGE_IN_FUNCTION, self._USAGE_IN_STRUCT):
            variable = '\tsize_t data_offset = 0;'
            variables.add(variable)

            variable = '\tconst uint8_t *{0:s} = NULL;'.format(member_name)
            variables.add(variable)

            variable = '\tsize_t {0:s}_size = 0;'.format(member_name)
            variables.add(variable)

    variables = list(sorted(variables))
    variables.append('')

    return '\n'.join(variables)

  def _GetStoredStructureHeaderMembers(
      self, data_type_definition, members_configuration):
    """Generates the member definitions of a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.

    Returns:
      str: member definitions of the stored structure header.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      member_name = member_definition.name
      data_type_size = member_definition.GetByteSize()

      description = members_configuration.get(member_name, {}).get(
          'description', member_definition.description)
      if not description:
        description = member_name.replace('_', ' ')

      if description[0] == '(':
        line = '\t/* ({0:s}{1:s}'.format(
            description[1].upper(), description[2:])
      else:
        line = '\t/* {0:s}{1:s}'.format(description[0].upper(), description[1:])

      lines.append(line)

      if self._generate_structure_member_size_hint:
        if not data_type_size:
          line = '\t * TODO: unknown size'
        elif data_type_size == 1:
          line = '\t * Consists of 1 byte'
        else:
          line = '\t * Consists of {0:d} bytes'.format(data_type_size)

        lines.append(line)

      if self._generate_structure_member_contents_hint:
        type_indicator = data_type_definition.TYPE_INDICATOR
        if type_indicator == definitions.TYPE_INDICATOR_UUID:
          lines.append('\t * Contains a UUID')

      lines.append('\t */')

      if not data_type_size:
        line = '\t/* TODO: unknown size */'
      elif data_type_size == 1:
        line = '\tuint8_t {0:s};'.format(member_name)
      else:
        line = '\tuint8_t {0:s}[ {1:d} ];'.format(member_name, data_type_size)

      lines.append(line)

      if index != last_index:
        lines.append('')

    return '\n'.join(lines)

  def _GetStructureDescription(self, data_type_definition):
    """Retrieves the structure description.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: structure description.
    """
    if data_type_definition.description:
      structure_description = data_type_definition.description
    else:
      structure_description = data_type_definition.name

    return structure_description.lower()

  def _GetTemplateMappings(self, library_name=None, structure_name=None):
    """Retrieves the template mappings.

    Args:
      library_name (Optional[str]): library name.
      structure_name (Optional[str]): structure name.

    Returns:
      dict[str, str]: template mappings.
    """
    format_definition = self._GetFormatDefinitions()

    template_mappings = {}

    authors = format_definition.metadata.get('authors', None)
    if authors:
      template_mappings['authors'] = ', '.join(authors)

    date = datetime.date.today()
    year = format_definition.metadata.get('year', date.year)
    if year:
      if year != date.year:
        copyright_years = '{0:d}-{1:d}'.format(year, date.year)
      else:
        copyright_years = '{0:d}'.format(year)

      template_mappings['copyright'] = copyright_years

    template_mappings['prefix'] = self._prefix

    if library_name:
      template_mappings['library_name'] = library_name

    if structure_name:
      template_mappings['structure_name'] = structure_name

    return template_mappings

  def _GetTemplateRuntimeStructureMembers(
      self, data_type_definition, members_configuration):
    """Retrieves the template runtime struture members.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (dict[dict[str: str]]): code generation
          configuration of the structure members.

    Returns:
      list[TemplateRuntimeStructureMember]: template runtime struture members.
    """
    structure_members = []

    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      member_configuration = members_configuration.get(member_name, {})

      member_usage = member_configuration.get('usage', self._USAGE_DEBUG)
      if member_usage != self._USAGE_IN_STRUCT:
        continue

      member_options = member_configuration.get('__options__', [])

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_name.replace('_', ' ')

      # TODO: remove leading "The", kept for testing purposed for now.
      # description = '{0:s}{1:s}'.format(
      #     description[0].upper(), description[1:])
      description = 'The {0:s}{1:s}'.format(
          description[0].lower(), description[1:])

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR

      member_value_type = self._GetRuntimeStructureMemberValueType(
          member_data_type_definition)

      if member_value_type in ('stream_fixed_size', 'string_fixed_size'):
        member_data_size = member_data_type_definition.GetByteSize() + 1
      else:
        member_data_size = 0

      structure_member = TemplateRuntimeStructureMember()
      structure_member.data_size = member_data_size
      structure_member.data_type = self._GetRuntimeDataType(
          member_data_type_definition)
      structure_member.description = description
      structure_member.name = member_name
      structure_member.value_type = member_value_type

      structure_members.append(structure_member)

    return structure_members

  def _ReadTestDataFile(self, type_name, sequence_number=1):
    """Reads a test data file.

    Args:
      type_name (str): name of type.
      sequence_number (int): sequence number.

    Returns:
      bytes: contents of test data file.
    """
    test_data_filename = '{0:s}.{1:d}'.format(type_name, sequence_number)
    test_data_file = os.path.join('tests', 'data', test_data_filename)

    test_data = b''
    if os.path.exists(test_data_file):
      with open(test_data_file, 'rb') as file_object:
        test_data = file_object.read()

    return test_data

  def _SortIncludeHeaders(self, output_filename):
    """Sorts the include headers within a source file.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    library_include_header_start = '#include "lib{0:s}_'.format(self._prefix)

    include_headers = []
    in_include_headers = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if line.startswith(library_include_header_start):
          include_headers.append(line)
          in_include_headers = True

        elif in_include_headers:
          file_object.writelines(sorted(include_headers))
          file_object.write(line)
          in_include_headers = False

        else:
          file_object.write(line)

  def _SortVariableDeclarations(self, output_filename):
    """Sorts the variable declarations within a source file.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    formatter = source_formatter.SourceFormatter()
    variable_declarations = None
    in_variable_declarations = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        stripped_line = line.rstrip()
        if stripped_line == '{':
          file_object.write(line)
          variable_declarations = []
          in_variable_declarations = True

        elif in_variable_declarations:
          if ('(' not in stripped_line or
              stripped_line.startswith('#if defined(')):
            variable_declarations.append(line)

          else:
            # TODO: remove the need for FormatSourceOld.
            sorted_lines = formatter.FormatSourceOld(variable_declarations)

            file_object.writelines(sorted_lines)
            file_object.write(line)
            in_variable_declarations = False

        else:
          file_object.write(line)

  def _VerticalAlignAssignmentStatements(self, output_filename):
    """Vertically aligns assignment statements.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    assigment_statements = []
    in_assigment_statements_block = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if ' = ' in line:
          if not in_assigment_statements_block:
            in_assigment_statements_block = True

          assigment_statements.append(line)
          continue

        if in_assigment_statements_block:
          if len(assigment_statements) == 1:
            file_object.write(assigment_statements[0])

          else:
            alignment_offset = 0
            for assigment_statement in assigment_statements:
              prefix, _, _ = assigment_statement.rpartition('=')
              prefix = prefix.rstrip()
              alignment_offset = max(alignment_offset, len(prefix) + 1)

            for assigment_statement in assigment_statements:
              prefix, _, suffix = assigment_statement.rpartition('=')
              prefix = prefix.rstrip()
              alignment_length = alignment_offset - len(prefix)

              assigment_statement_line = '{0:s}{1:s}={2:s}'.format(
                  prefix, ' ' * alignment_length, suffix)
              file_object.write(assigment_statement_line)

          in_assigment_statements_block = False
          assigment_statements = []

        file_object.write(line)

  def Generate(self, project_configuration):
    """Generates source code from the data type definitions.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if successful, False otherwise.
    """
    format_definition = self._GetFormatDefinitions()
    self._prefix = format_definition.name

    result = True

    dtfabric_configuration = project_configuration.dtfabric_configuration
    for name, members_configuration in (
        dtfabric_configuration.data_types.items()):
      definition = self._definitions_registry.GetDefinitionByName(name)
      if not definition:
        logging.error('Missing data type: {0:s}'.format(name))
        result = False
        continue

      if definition.TYPE_INDICATOR not in (
          definitions.TYPE_INDICATOR_STRUCTURE,
          definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
        logging.error('Unsupported data type: {0:s}'.format(name))
        result = False
        continue

      # if definition.TYPE_INDICATOR == (
      #     definitions.TYPE_INDICATOR_STRUCTURE):

      #   Skip structures that are part of a type family.
      #   if definition.family_definition:
      #     logging.info('Skipping data type: {0:s}'.format(name))
      #     continue

      #   byte_size = definition.GetByteSize()
      #   if byte_size is None:
      #     continue

      logging.info('Generating data type: {0:s}'.format(name))

      self._GenerateRuntimeStructureHeaderFile(
          definition, members_configuration)
      self._GenerateRuntimeStructureSourceFile(
          definition, members_configuration)
      self._GenerateRuntimeStructureTestSourceFile(
          project_configuration, definition, members_configuration)
      self._GenerateStoredStructureHeaderFile(definition, members_configuration)

    return result

  def ReadDefinitions(self, definitions_file):
    """Reads the definitions form file or directory.

    Args:
      definitions_file (str): path to the data format definition file.
    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    definitions_reader.ReadFile(
        self._definitions_registry, definitions_file)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description='Generates source based on dtFabric format definitions.')

  argument_parser.add_argument(
      '--definitions-file', '--definitions_file', dest='definitions_file',
      action='store', metavar='PATH', default='dtfabric.yaml', help=(
          'Path to the dtFabric definitions file.'))

  argument_parser.add_argument(
      '--templates-path', '--templates_path', dest='templates_path',
      action='store', metavar='PATH', default=None, help=(
          'Path to the template files.'))

  argument_parser.add_argument(
      'configuration_file', action='store', metavar='PATH',
      default='libyal.ini', help='path of the configuration file.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print('Configuration file value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not os.path.isfile(options.configuration_file):
    print('No such configuration file: {0:s}.'.format(
        options.configuration_file))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  templates_path = options.templates_path
  if not templates_path:
    templates_path = os.path.dirname(__file__)
    templates_path = os.path.dirname(templates_path)
    templates_path = os.path.join(templates_path, 'data', 'dtfabric')

  project_configuration = configuration.ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  source_generator = SourceGenerator(templates_path)

  try:
    source_generator.ReadDefinitions(options.definitions_file)
  except errors.FormatError as exception:
    print((
        'Unable to read data format definitions from file: {0:s} with error: '
        '{1!s}').format(options.definitions_file, exception))
    return False

  return source_generator.Generate(project_configuration)


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
