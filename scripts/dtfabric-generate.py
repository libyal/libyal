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
from yaldevtools import template_string


# TODO: put signature into constants: libyal_constants.[ch]


class SourceGenerator(object):
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

  def __init__(self, templates_path):
    """Initializes a source generator.

    Args:
      templates_path (str): templates path.
    """
    super(SourceGenerator, self).__init__()
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._prefix = None
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()

  def _GenerateRuntimeStructureHeader(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
    """
    library_name = 'lib{0:s}'.format(self._prefix)
    template_mappings = self._GetTemplateMappings(
        library_name=library_name, structure_name=data_type_definition_name)

    structure_members = self._GetRuntimeStructureHeaderMembers(
        data_type_definition, members_configuration)

    template_mappings['structure_members'] = structure_members

    template_filename = os.path.join(
        self._templates_path, 'runtime_structure.h', 'structure.h')

    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['structure_members']

  def _GenerateRuntimeStructureHeaderFile(
      self, data_type_definition, members_configuration):
    """Generates a runtime structure header file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
    """
    structure_options = members_configuration.get('__options__', {})

    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.h')

    library_name = 'lib{0:s}'.format(self._prefix)
    template_mappings = self._GetTemplateMappings(
        library_name=library_name, structure_name=data_type_definition.name)

    if not self._prefix:
      output_filename = 'runtime_structure.h'
    else:
      output_filename = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))

    logging.info('Writing: {0:s}'.format(output_filename))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    template_mappings['structure_description_title'] = (
        structure_description_title)

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    del template_mappings['structure_description_title']

    template_filename = os.path.join(template_directory, 'includes.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if 'file_io_handle' in structure_options:
      template_filename = os.path.join(template_directory, 'includes-libbfio.h')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'extern-start.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definition = data_type_definition.runtime
    else:
      structure_definition = data_type_definition

    self._GenerateRuntimeStructureHeader(
        structure_definition, data_type_definition.name, members_configuration,
        output_filename)

    template_filename = os.path.join(template_directory, 'functions.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if 'file_io_handle' in structure_options:
      template_filename = os.path.join(
          template_directory, 'functions-read_file_io_handle.h')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'extern-end.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._SortIncludeHeaders(output_filename)

  def _GenerateRuntimeStructureSourceFile(
      self, data_type_definition, members_configuration):
    """Generates a runtime structure source file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
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
      if member_data_type in ('filetime', ):
        has_datetime_member = True

    library_name = 'lib{0:s}'.format(self._prefix)
    template_mappings = self._GetTemplateMappings(
        library_name=library_name, structure_name=data_type_definition.name)

    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    if not self._prefix:
      output_filename = 'runtime_structure.c'
    else:
      output_filename = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.c'.format(self._prefix, data_type_definition.name))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = (
        structure_description_title)

    logging.info('Writing: {0:s}'.format(output_filename))

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    template_filename = os.path.join(template_directory, 'includes-start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if has_datetime_member or has_string_member or has_uuid_member:
      template_filename = os.path.join(template_directory, 'includes-debug.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    if has_datetime_member:
      template_filename = os.path.join(
          template_directory, 'includes-libfdatetime.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    if has_uuid_member:
      template_filename = os.path.join(
          template_directory, 'includes-libfguid.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    if has_string_member:
      template_filename = os.path.join(template_directory, 'includes-libuna.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    if 'file_io_handle' in structure_options:
      template_filename = os.path.join(template_directory, 'includes-libbfio.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'includes-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    # Indentation needs to account for "*name = ".
    template_mappings['memory_allocate_indentation'] = ' ' * (
        len(data_type_definition.name) + 4)

    template_filename = os.path.join(template_directory, 'initialize.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['memory_allocate_indentation']

    template_filename = os.path.join(template_directory, 'free.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definition = data_type_definition.runtime
    else:
      structure_definition = data_type_definition

    self._GenerateRuntimeStructureSourceFunctionReadData(
        structure_definition, data_type_definition.name, members_configuration,
        output_filename)

    if 'file_io_handle' in structure_options:
      template_filename = os.path.join(
          template_directory, 'read_file_io_handle.c')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    self._SortIncludeHeaders(output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignAssignmentStatements(output_filename)

  def _GenerateRuntimeStructureSourceFunctionReadData(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates a runtime structure read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition_name)

    structure_description = self._GetStructureDescription(data_type_definition)
    template_mappings['structure_description'] = structure_description

    self._GenerateRuntimeStructureSourceFunctionReadDataVariables(
        data_type_definition, data_type_definition_name, members_configuration,
        output_filename)

    self._GenerateRuntimeStructureSourceFunctionReadDataDebugVariables(
        data_type_definition, data_type_definition_name, members_configuration,
        output_filename)

    template_filename = os.path.join(
        template_directory, 'read_data-check_arguments.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._GenerateRuntimeStructureSourceFunctionReadDataCheckSignature(
        data_type_definition, data_type_definition_name, output_filename)

    self._GenerateRuntimeStructureSourceFunctionReadDataCopyFromByteStream(
        data_type_definition, data_type_definition_name, members_configuration,
        output_filename)

    template_filename = os.path.join(
        template_directory, 'read_data-debug_start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._GenerateRuntimeStructureSourceFunctionReadDataDebugPrint(
        data_type_definition, data_type_definition_name, members_configuration,
        output_filename)

    template_filename = os.path.join(
        template_directory, 'read_data-debug_end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_filename = os.path.join(template_directory, 'read_data-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

  def _GenerateRuntimeStructureSourceFunctionReadDataDebugVariables(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates the debug variables part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
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
        debug_variable = '\tuint{0:d}_t value_{0:d}bit = 0;'.format(
            data_type_size * 8)
        debug_variables.add(debug_variable)

      elif type_indicator == definitions.TYPE_INDICATOR_PADDING:
        debug_variable = '\tconst uint8_t *{0:s} = NULL;'.format(member_name)
        debug_variables.add(debug_variable)

        debug_variable = '\tsize_t {0:s}_size = 0;'.format(member_name)
        debug_variables.add(debug_variable)

    if not debug_variables:
      return

    debug_variables = sorted(debug_variables)

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition_name)

    template_mappings['debug_variables'] = '\n'.join(debug_variables)

    template_filename = os.path.join(
        self._templates_path, 'runtime_structure.c',
        'read_data-debug_variables.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['debug_variables']

  def _GenerateRuntimeStructureSourceFunctionReadDataCheckSignature(
      self, data_type_definition, data_type_definition_name, output_filename):
    """Generates the check signature part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition_name)

    for member_definition in data_type_definition.members:
      member_name = member_definition.name

      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      supported_values = getattr(member_definition, 'values', None)
      if not supported_values:
        continue

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_STREAM:
        template_filename = 'read_data-check_signature-stream.c'

        template_mappings['member_value'] = supported_values[0]
        template_mappings['member_value_size'] = len(supported_values[0])

      else:
        template_filename = 'read_data-check_signature-unsupported.c'

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_name.replace('_', ' ')

      template_mappings['member_name'] = member_name
      template_mappings['member_name_description'] = '{0:s}{1:s}'.format(
          description[0].lower(), description[1:])

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

  def _GenerateRuntimeStructureSourceFunctionReadDataCopyFromByteStream(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates the copy from byte stream part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition_name)

    date_offset_is_set = False

    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      member_usage = members_configuration.get(member_name, {}).get(
          'usage', self._USAGE_DEBUG)
      if member_usage != self._USAGE_IN_STRUCT:
        continue

      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      template_filename = 'read_data-unsupported.c'

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if (type_indicator == definitions.TYPE_INDICATOR_INTEGER and
          data_type_size and data_type_size > 1):
        if data_type.startswith('uint'):
          template_filename = 'read_data-unsigned_integer.c'
        else:
          template_filename = 'read_data-integer.c'

        # TODO: get byte order from member_data_type_definition.
        template_mappings['byte_order'] = 'little_endian'
        template_mappings['data_type'] = data_type

      elif type_indicator == definitions.TYPE_INDICATOR_STRING:
        elements_terminator = getattr(
            member_data_type_definition, 'elements_terminator', None)
        if elements_terminator is not None:
          if not date_offset_is_set:
            template_filename = os.path.join(
                template_directory, 'read_data-data_offset.c')
            self._GenerateSection(
                template_filename, template_mappings, output_filename,
                access_mode='a')

            template_filename = 'read_data-unsupported.c'
            date_offset_is_set = True

          element_data_type_definition = (
              member_data_type_definition.element_data_type_definition)
          element_data_size = element_data_type_definition.GetByteSize()
          if element_data_size == 1:
            template_filename = 'read_data-string_8bit.c'
          elif element_data_size == 2:
            template_filename = 'read_data-string_16bit.c'

      elif type_indicator == definitions.TYPE_INDICATOR_UUID:
        template_filename = 'read_data-guid.c'

      else:
        member_data_type = getattr(member_definition, 'member_data_type', None)
        if member_data_type == 'filetime':
          template_filename = 'read_data-unsigned_integer.c'

          # TODO: get byte order from member_data_type_definition.
          template_mappings['byte_order'] = 'little_endian'
          template_mappings['data_type'] = 'uint64'

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_name.replace('_', ' ')

      template_mappings['member_name'] = member_name
      template_mappings['member_name_description'] = '{0:s}{1:s}'.format(
          description[0].lower(), description[1:])

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

  def _GenerateRuntimeStructureSourceFunctionReadDataDebugPrint(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates the debug print part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    library_name = 'lib{0:s}'.format(self._prefix)
    template_mappings = self._GetTemplateMappings(
        library_name=library_name, structure_name=data_type_definition_name)

    function_name = 'lib{0:s}_{1:s}_read_data'.format(
        self._prefix, data_type_definition_name)

    # Default alignment is 9 tabs.
    tab_alignment = 9 * 8
    for member_definition in data_type_definition.members:
      member_name = member_definition.name
      debug_line = '{0:s}: {1:s}'.format(function_name, member_name)
      debug_line_length = len(debug_line)
      if debug_line_length > tab_alignment:
        tab_alignment = debug_line_length

    _, remainder = divmod(tab_alignment, 8)
    if remainder > 0:
      tab_alignment += 8 - remainder

    for member_definition in data_type_definition.members:
      member_name = member_definition.name

      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      template_filename = 'read_data-debug-unsupported.c'

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_INTEGER:
        debug_format = members_configuration.get(member_name, {}).get(
            'debug_format', self._DEBUG_FORMAT_DECIMAL)

        printf_format_indicator = self._GetRuntimePrintfFormatIndicator(
            member_definition, debug_format)

        member_usage = members_configuration.get(member_name, {}).get(
            'usage', self._USAGE_DEBUG)
        if member_usage == self._USAGE_IN_FUNCTION:
          template_filename = 'read_data-debug-integer-in_function.c'

        elif member_usage == self._USAGE_IN_STRUCT:
          if member_name.endswith('_flags'):
            template_filename = 'read_data-debug-integer-in_struct-as_flags.c'
          else:
            template_filename = 'read_data-debug-integer-in_struct.c'

        elif member_usage == self._USAGE_IN_FUNCTION:
          # TODO: improve.
          template_filename = 'read_data-debug-integer.c'

        else:
          template_filename = 'read_data-debug-integer.c'

        template_mappings['bit_size'] = data_type_size * 8
        # TODO: get byte order from member_data_type_definition.
        template_mappings['byte_order'] = 'little_endian'
        template_mappings['data_type'] = data_type
        template_mappings['format_indicator'] = printf_format_indicator

      elif type_indicator == definitions.TYPE_INDICATOR_PADDING:
        template_filename = 'read_data-debug-padding.c'

      elif type_indicator == definitions.TYPE_INDICATOR_STREAM:
        supported_values = getattr(member_definition, 'values', None)

        if supported_values:
          format_indicator = ['%c'] * len(supported_values[0])
          for supported_value in supported_values:
            for index, character in enumerate(supported_value):
              if not character.isalnum():
                format_indicator[index] = '\\x%02" PRIx8 "'

          member_data_arguments = []
          for byte_index in range(len(supported_values[0])):
            argument = '\t\t ( ({0:s}_{1:s}_t *) data )->{2:s}[ {3:d} ]'.format(
                self._prefix, data_type_definition_name, member_name,
                byte_index)
            member_data_arguments.append(argument)

          template_filename = 'read_data-debug-signature.c'

          template_mappings['format_indicator'] = ''.join(format_indicator)
          template_mappings['member_data_arguments'] = ',\n'.join(
              member_data_arguments)

        elif data_type_size:
          template_filename = 'read_data-debug-stream_with_data_size.c'

          template_mappings['member_data_size'] = data_type_size

        else:
          template_filename = 'read_data-debug-stream.c'

      elif type_indicator == definitions.TYPE_INDICATOR_STRING:
        # TODO: handle evt "data_size - 4"
        elements_terminator = getattr(
            member_data_type_definition, 'elements_terminator', None)
        if elements_terminator is not None:
          element_data_type_definition = (
              member_data_type_definition.element_data_type_definition)
          element_data_size = element_data_type_definition.GetByteSize()
          if element_data_size == 2:
            template_filename = 'read_data-debug-string_16bit.c'

      elif type_indicator == definitions.TYPE_INDICATOR_UUID:
        template_filename = 'read_data-debug-guid.c'

      else:
        member_data_type = getattr(member_definition, 'member_data_type', None)
        if member_data_type == 'filetime':
          template_filename = 'read_data-debug-filetime.c'

      # Use the member name as the debug description.
      description = member_name.replace('_', ' ')

      template_filename = os.path.join(template_directory, template_filename)

      template_mappings['member_name'] = member_name
      template_mappings['member_name_description'] = description

      # Determine the number of tabs for alignment.
      debug_line = '{0:s}: {1:s}'.format(function_name, description)
      debug_line_length = len(debug_line)

      number_of_tabs, remainder = divmod(tab_alignment - debug_line_length, 8)
      if remainder > 0:
        number_of_tabs += 1

      template_mappings['tab_alignment'] = '\\t' * number_of_tabs

      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

  def _GenerateRuntimeStructureSourceFunctionReadDataVariables(
      self, data_type_definition, data_type_definition_name,
      members_configuration, output_filename):
    """Generates the variables part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

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

    variables = sorted(variables)
    variables.append('')

    library_name = 'lib{0:s}'.format(self._prefix)
    template_mappings = self._GetTemplateMappings(
        library_name=library_name, structure_name=data_type_definition_name)

    structure_description = self._GetStructureDescription(data_type_definition)
    template_mappings['structure_description'] = structure_description

    template_mappings['variables'] = '\n'.join(variables)

    template_filename = os.path.join(template_directory, 'read_data-start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['variables']

  def _GenerateSection(
      self, template_filename, template_mappings, output_filename,
      access_mode='w'):
    """Generates a section from template filename.

    Args:
      template_filename (str): name of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_filename (str): name of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_filename, access_mode, encoding='utf8') as file_object:
      file_object.write(output_data)

  def _GenerateStoredStructureHeader(
      self, data_type_definition, members_configuration, output_filename):
    """Generates a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.
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
      members_configuration (list[dict]): code generation configuration of
          the structure members.
    """
    template_directory = os.path.join(
        self._templates_path, 'stored_structure.h')

    template_mappings = self._GetTemplateMappings(
        structure_name=data_type_definition.name)

    if not self._prefix:
      output_filename = 'stored_structure.h'
    else:
      output_filename = os.path.join(
          'lib{0:s}'.format(self._prefix),
          '{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))

    logging.info('Writing: {0:s}'.format(output_filename))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    format_definition = self._GetFormatDefinitions()
    if format_definition.description:
      structure_description = '{0:s} of the {1:s}'.format(
          structure_description, format_definition.description)

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

  def _GetRuntimeStructureHeaderMember(
      self, member_definition, members_configuration):
    """Generates the member definition of a runtime structure header.

    Args:
      member_definition (MemberDataTypeDefinition): member data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.

    Returns:
      list[str]: member definition of a runtime structure header.
    """
    member_name = member_definition.name

    if member_definition.description:
      description = member_definition.description
    else:
      description = member_name.replace('_', ' ')

    # TODO: remove leading "The", kept for testing purposed for now.
    # description = '{0:s}{1:s}'.format(
    #     description[0].upper(), description[1:])
    description = 'The {0:s}{1:s}'.format(
        description[0].lower(), description[1:])

    lines = None

    # TODO: handle stream / string type
    # TODO: handle padding type
    data_type_definition = getattr(
        member_definition, 'member_data_type_definition', member_definition)

    type_indicator = data_type_definition.TYPE_INDICATOR

    if data_type_definition.name == 'filetime':
      lines = [
          '\t/* {0:s}'.format(description),
          '\t * Contains a 64-bit filetime value',
          '\t */',
          '\tuint64_t {0:s};'.format(member_name)]

    elif type_indicator in (
        definitions.TYPE_INDICATOR_STREAM, definitions.TYPE_INDICATOR_STRING):
      lines = [
          '\t/* {0:s}'.format(description),
          '\t */',
          '\tuint8_t *{0:s};'.format(member_name)]

    elif type_indicator == definitions.TYPE_INDICATOR_UUID:
      lines = [
          '\t/* {0:s}'.format(description),
          '\t */',
          '\tuint8_t {0:s}[ 16 ];'.format(member_name)]

    else:
      data_type = None
      if type_indicator == definitions.TYPE_INDICATOR_CHARACTER:
        data_type = self._CHARACTER_DATA_TYPES.get(
            data_type_definition.size, None)

      elif type_indicator == definitions.TYPE_INDICATOR_FLOATING_POINT:
        data_type = self._FLOATING_POINT_DATA_TYPES.get(
            data_type_definition.size, None)

      elif type_indicator in (
          definitions.TYPE_INDICATOR_BOOLEAN, definitions.TYPE_INDICATOR_INTEGER):
        if data_type_definition.format == definitions.FORMAT_SIGNED:
          data_type = self._SIGNED_INTEGER_DATA_TYPES.get(
              data_type_definition.size, None)
        else:
          data_type = self._UNSIGNED_INTEGER_DATA_TYPES.get(
            data_type_definition.size, None)

      if data_type:
        lines = [
            '\t/* {0:s}'.format(description),
            '\t */',
            '\t{0:s} {1:s};'.format(data_type, member_name)]

    if not lines:
      lines = [
          '\t/* {0:s}'.format(description),
          '\t */',
          '\t/* TODO: implement */']

    return lines

  def _GetRuntimeStructureHeaderMembers(
      self, data_type_definition, members_configuration):
    """Generates the member definitions of a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.

    Returns:
      str: member definitions of a runtime structure header.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for member_definition in data_type_definition.members:
      member_usage = members_configuration.get(member_definition.name, {}).get(
          'usage', self._USAGE_DEBUG)
      if member_usage != self._USAGE_IN_STRUCT:
        continue

      if lines:
        lines.append('')

      member_definition_lines = self._GetRuntimeStructureHeaderMember(
          member_definition, members_configuration)
      lines.extend(member_definition_lines)

    if not lines:
      lines = [
          '\t/* Dummy',
          '\t */',
          '\tint dummy;']

    return '\n'.join(lines)

  def _GetStoredStructureHeaderMembers(
      self, data_type_definition, members_configuration):
    """Generates the member definitions of a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      members_configuration (list[dict]): code generation configuration of
          the structure members.

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

      if not data_type_size:
        line = '\t * TODO: unknown size'
      elif data_type_size == 1:
        line = '\t * Consists of 1 byte'
      else:
        line = '\t * Consists of {0:d} bytes'.format(data_type_size)

      lines.append(line)

      if data_type_definition.TYPE_INDICATOR == definitions.TYPE_INDICATOR_UUID:
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
    template_mappings['prefix_upper_case'] = self._prefix.upper()

    if library_name:
      template_mappings['library_name'] = library_name
      template_mappings['library_name_upper_case'] = library_name.upper()

    if structure_name:
      template_mappings['structure_name'] = structure_name
      template_mappings['structure_name_upper_case'] = structure_name.upper()

    return template_mappings

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

      if definition.TYPE_INDICATOR == (
          definitions.TYPE_INDICATOR_STRUCTURE):

        # Skip structures that are part of a type family.
        if definition.family_definition:
          logging.info('Skipping data type: {0:s}'.format(name))
          continue

        # byte_size = definition.GetByteSize()
        # if byte_size is None:
        #   continue

      logging.info('Generating data type: {0:s}'.format(name))

      self._GenerateRuntimeStructureHeaderFile(
          definition, members_configuration)
      self._GenerateRuntimeStructureSourceFile(
          definition, members_configuration)
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
