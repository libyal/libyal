#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate source based on dtFabric format definitions."""

from __future__ import print_function
from __future__ import unicode_literals
import argparse
import datetime
import logging
import os
import string
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

import template_string


class SourceGenerator(object):
  """Generates source based on dtFabric format definitions."""

  _RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE = 'runtime_structure.h'
  _RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE = 'runtime_structure.c'
  _STORED_STRUCTURE_HEADER_TEMPLATE_FILE = 'stored_structure.h'

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
      8: '%" PRIi16 "',
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
      8: '%" PRIu16 "',
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

  def _GenerateStoredStructureHeader(self, data_type_definition):
    """Generates a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    format_definition = self._GetFormatDefinitions()

    template_mappings = self._GetTemplateMappings()

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    if format_definition.description:
      structure_description = '{0:s} of a {1:s}'.format(
          structure_description_title, format_definition.description)

    structure_members = self._GetStoredStructureHeaderMembers(
        data_type_definition)

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = structure_description_title
    template_mappings['structure_members'] = structure_members
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._STORED_STRUCTURE_HEADER_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          '{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._STORED_STRUCTURE_HEADER_TEMPLATE_FILE

    logging.info('Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureHeader(self, data_type_definition):
    """Generates a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_mappings = self._GetTemplateMappings()

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    structure_members = self._GetRuntimeStructureHeaderMembers(
        data_type_definition)

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = structure_description_title
    template_mappings['structure_members'] = structure_members
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE

    logging.info('Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureSource(self, data_type_definition):
    """Generates a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_mappings = self._GetTemplateMappings()

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    structure_members_copy_from_byte_stream = (
        self._GetRuntimeStructureSourceMembersCopyFromByteStream(
            data_type_definition))

    structure_members_debug_print = (
        self._GetRuntimeStructureSourceMembersDebugPrint(
            data_type_definition))

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = structure_description_title
    template_mappings['structure_members_copy_from_byte_stream'] = (
        structure_members_copy_from_byte_stream)
    template_mappings['structure_members_debug_print'] = (
        structure_members_debug_print)
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.c'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE

    logging.info('Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GetRuntimeDataType(self, data_type_definition):
    """Retrieves a runtime data type.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: C runtime data type or None if not available.
    """
    data_type_definition = getattr(
        data_type_definition, 'member_data_type_definition',
        data_type_definition)

    data_type = None

    type_indicator = data_type_definition.TYPE_INDICATOR
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

    return data_type

  def _GetRuntimePrintfFormatIndicator(self, data_type_definition):
    """Retrieves a runtime printf format indicator.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: C runtime data type or None if not available.
    """
    data_type_definition = getattr(
        data_type_definition, 'member_data_type_definition',
        data_type_definition)

    data_type = None

    type_indicator = data_type_definition.TYPE_INDICATOR
    if type_indicator == definitions.TYPE_INDICATOR_CHARACTER:
      data_type = self._CHARACTER_FORMAT_INDICATORS.get(
          data_type_definition.size, None)

    elif type_indicator == definitions.TYPE_INDICATOR_FLOATING_POINT:
      data_type = self._FLOATING_POINT_FORMAT_INDICATORS.get(
          data_type_definition.size, None)

    elif type_indicator in (
        definitions.TYPE_INDICATOR_BOOLEAN, definitions.TYPE_INDICATOR_INTEGER):
      if data_type_definition.format == definitions.FORMAT_SIGNED:
        data_type = self._SIGNED_INTEGER_FORMAT_INDICATORS.get(
            data_type_definition.size, None)
      else:
        data_type = self._UNSIGNED_INTEGER_FORMAT_INDICATORS.get(
            data_type_definition.size, None)

    return data_type

  def _GetFormatDefinitions(self):
    """Retrieves the format definition.

    Returns:
      FormatDefinition: format definition.
    """
    # pylint: disable=protected-access

    if not self._definitions_registry._format_definitions:
      raise RuntimeError('Missing format definition.')

    if len(self._definitions_registry._format_definitions) > 1:
      raise RuntimeError('Unsupported multiple format definitions.')

    format_definition = self._definitions_registry.GetDefinitionByName(
        self._definitions_registry._format_definitions[0])

    self._prefix = format_definition.name

    return format_definition

  def _GetRuntimeStructureHeaderMembers(self, data_type_definition):
    """Generates the member definitions of a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure header.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      description = '{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      data_type = self._GetRuntimeDataType(member_definition)
      if data_type:
        lines.extend([
            '\t/* {0:s}'.format(description),
            '\t */',
            '\t{1:s} {0:s};'.format(name, data_type)
        ])

      else:
        lines.append('\t/* TODO: {1:s} {0:s} */'.format(name, data_type))

      if index != last_index:
        lines.append('')

    return '\n'.join(lines)

  def _GetRuntimeStructureSourceMembersCopyFromByteStream(
      self, data_type_definition):
    """Generates the member definitions of a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure source.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      description = '{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      data_type = getattr(member_definition, 'member_data_type', None)
      if data_type:
        lines.extend([
            '\tbyte_stream_copy_to_{0:s}_little_endian('.format(data_type),
            '\t ( ({0:s}_{1:s}_t *) data )->{2:s},'.format(
                self._prefix, data_type_definition.name, name),
            '\t {0:s}->{1:s} );'.format(data_type_definition.name, name)
        ])

      else:
        lines.append('\t/* TODO: {1:s} {0:s} */'.format(name, data_type))

      if index != last_index:
        lines.append('')

    return '\n'.join(lines)

  def _GetRuntimeStructureSourceMembersDebugPrint(self, data_type_definition):
    """Generates the member definitions of a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure source.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = data_type_definition.TYPE_INDICATOR
      if type_indicator in (
          definitions.TYPE_INDICATOR_BOOLEAN,
          definitions.TYPE_INDICATOR_CHARACTER,
          definitions.TYPE_INDICATOR_FLOATING_POINT,
          definitions.TYPE_INDICATOR_INTEGER):

        printf_format_indicator = self._GetRuntimePrintfFormatIndicator(
            member_definition)
        # TODO: detemine number of tabs for alignment.
        lines.extend([
            '\t\tlibcnotify_printf(',
            '\t\t "%s: {0:s}\\t: {1:s}\\n",'.format(
                description, printf_format_indicator),
            '\t\t function,',
            '\t\t {0:s}->{1:s} );'.format(data_type_definition.name, name)
        ])

      elif type_indicator == definitions.TYPE_INDICATOR_STREAM:
        data_type_size = member_definition.GetByteSize()

        lines.extend([
            '\t\tlibcnotify_printf(',
            '\t\t "%s: {0:s}\\n",'.format(description),
            '\t\t function );',
            '\t\tlibcnotify_print_data(',
            '\t\t {0:s}->{1:s},'.format(data_type_definition.name, name),
            '\t\t {0:d},'.format(data_type_size),
            '\t\t 0 );'
        ])

      else:
        lines.append('\t\t/* TODO: {1:s} {0:s} */'.format(name, type_indicator))

      if index != last_index:
        lines.append('')

    return '\n'.join(lines)

  def _GetStoredStructureHeaderMembers(self, data_type_definition):
    """Generates the member definitions of a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the stored structure header.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      description = '{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      if data_type_size == 1:
        lines.extend([
            '\t/* {0:s}'.format(description),
            '\t * Consists of {0:d} byte'.format(data_type_size),
            '\t */',
            '\tuint8_t {0:s};'.format(name)
        ])

      else:
        lines.extend([
            '\t/* {0:s}'.format(description),
            '\t * Consists of {0:d} bytes'.format(data_type_size),
            '\t */',
            '\tuint8_t {0:s}[ {1:d} ];'.format(name, data_type_size)
        ])

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

  def _GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      dict[str, str]: template mappings.
    """
    format_definition = self._GetFormatDefinitions()

    template_mappings = {}

    authors = format_definition.metadata.get('authors', None)
    if authors:
      template_mappings['authors'] = ', '.join(authors)

    year = format_definition.metadata.get('year', None)
    if year:
      date = datetime.date.today()
      if year != date.year:
        copyright_years = '{0:d}-{1:d}'.format(year, date.year)
      else:
        copyright_years = '{0:d}'.format(year)

      template_mappings['copyright'] = copyright_years

    template_mappings['prefix'] = self._prefix
    template_mappings['prefix_upper_case'] = self._prefix.upper()

    return template_mappings

  def Generate(self):
    """Generates source code from the data type definitions."""
    for data_type_definition in self._definitions_registry.GetDefinitions():
      if data_type_definition.TYPE_INDICATOR != (
          definitions.TYPE_INDICATOR_STRUCTURE):
        continue

      byte_size = data_type_definition.GetByteSize()
      if byte_size is None:
        continue

      self._GenerateRuntimeStructureHeader(data_type_definition)
      self._GenerateRuntimeStructureSource(data_type_definition)
      self._GenerateStoredStructureHeader(data_type_definition)

  def ReadDefinitions(self, path):
    """Reads the definitions form file or directory.

    Args:
      path (str): path of the definition file or directory.
    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    definitions_reader.ReadFile(self._definitions_registry, path)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description='Generates source based on dtFabric format definitions.')

  argument_parser.add_argument(
      '--templates-path', '--templates_path', dest='templates_path',
      action='store', metavar='PATH', default=None, help=(
          'Path to the template files.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help='name of the file containing the dtFabric format definitions.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not os.path.isfile(options.source):
    print('No such file: {0:s}'.format(options.source))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  templates_path = options.templates_path
  if not templates_path:
    templates_path = os.path.dirname(__file__)
    templates_path = os.path.dirname(templates_path)
    templates_path = os.path.join(templates_path, 'data', 'dtfabric')

  source_generator = SourceGenerator(templates_path)

  try:
    source_generator.ReadDefinitions(options.source)
  except errors.FormatError as exception:
    print('Unable to read definitions with error: {0:s}'.format(exception))
    return False

  source_generator.Generate()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
