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


# TODO: put signature into constants: libyal_constants.[ch]


class SourceGenerator(object):
  """Generates source based on dtFabric format definitions."""

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

  def _GenerateRuntimeStructureHeader(
      self, data_type_definition, data_type_definition_name, output_file):
    """Generates a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      output_file (str): path of the file output file.
    """
    template_mappings = self._GetTemplateMappings()

    structure_members = self._GetRuntimeStructureHeaderMembers(
        data_type_definition)

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_members'] = structure_members
    template_mappings['structure_name'] = data_type_definition_name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition_name.upper())

    template_filename = os.path.join(
        self._templates_path, 'runtime_structure.h', 'structure.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    del template_mappings['structure_members']

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureHeaderFile(self, data_type_definition):
    """Generates a runtime structure header file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.h')

    template_mappings = self._GetTemplateMappings()

    if not self._prefix:
      output_file = 'runtime_structure.h'
    else:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))

    logging.info('Writing: {0:s}'.format(output_file))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_description_title'] = structure_description_title
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(template_directory, 'header.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    del template_mappings['structure_description_title']

    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definition = data_type_definition.runtime
    else:
      structure_definition = data_type_definition

    self._GenerateRuntimeStructureHeader(
        structure_definition, data_type_definition.name, output_file)

    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(template_directory, 'footer.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureSourceFile(self, data_type_definition):
    """Generates a runtime structure source file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_mappings = self._GetTemplateMappings()

    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    if not self._prefix:
      output_file = 'runtime_structure.c'
    else:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          'lib{0:s}_{1:s}.c'.format(self._prefix, data_type_definition.name))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_description_title'] = structure_description_title
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(template_directory, 'header.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    logging.info('Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

    template_filename = os.path.join(template_directory, 'initialize.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

    template_filename = os.path.join(template_directory, 'free.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definition = data_type_definition.runtime
    else:
      structure_definition = data_type_definition

    self._GenerateRuntimeStructureSourceFunctionReadData(
        structure_definition, data_type_definition.name, output_file)

    template_filename = os.path.join(
        template_directory, 'read_file_io_handle.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureSourceFunctionReadData(
      self, data_type_definition, data_type_definition_name, output_file):
    """Generates a runtime structure read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      output_file (str): path of the file output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings()

    structure_description = self._GetStructureDescription(data_type_definition)

    library_name = 'lib{0:s}'.format(self._prefix)

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_name'] = data_type_definition_name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition_name.upper())

    template_filename = os.path.join(template_directory, 'read_data-start.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

    self._GenerateRuntimeStructureSourceFunctionReadDataCopyFromByteStream(
        data_type_definition, data_type_definition_name, output_file)

    template_filename = os.path.join(
        template_directory, 'read_data-debug_start.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

    self._GenerateRuntimeStructureSourceFunctionReadDataDebugPrint(
        data_type_definition, data_type_definition_name, output_file)

    template_filename = os.path.join(
        template_directory, 'read_data-debug_end.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

    template_filename = os.path.join(template_directory, 'read_data-end.c')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureSourceFunctionReadDataCopyFromByteStream(
      self, data_type_definition, data_type_definition_name, output_file):
    """Generates the copy from byte stream part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      output_file (str): path of the file output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings()

    template_mappings['structure_name'] = data_type_definition_name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition_name.upper())

    for member_definition in data_type_definition.members:
      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if (type_indicator == definitions.TYPE_INDICATOR_INTEGER and
          data_type_size and data_type_size > 1):
        template_filename = os.path.join(
            template_directory, 'read_data-integer.c')

        # TODO: get byte order from member_data_type_definition.
        template_mappings['byte_order'] = 'little_endian'
        template_mappings['data_type'] = data_type

      else:
        template_filename = os.path.join(
            template_directory, 'read_data-unsupported.c')

      template_mappings['member_name'] = member_definition.name

      output_data = self._template_string_generator.Generate(
          template_filename, template_mappings)

      with open(output_file, 'ab') as file_object:
        file_object.write(output_data)

  def _GenerateRuntimeStructureSourceFunctionReadDataDebugPrint(
      self, data_type_definition, data_type_definition_name, output_file):
    """Generates the debug print part of a read_data function.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      data_type_definition_name (str): name of the structure data type
          definition.
      output_file (str): path of the file output file.
    """
    template_directory = os.path.join(
        self._templates_path, 'runtime_structure.c')

    template_mappings = self._GetTemplateMappings()

    template_mappings['structure_name'] = data_type_definition_name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition_name.upper())

    for member_definition in data_type_definition.members:
      data_type = getattr(member_definition, 'member_data_type', None)
      data_type_size = member_definition.GetByteSize()

      member_data_type_definition = getattr(
          member_definition, 'member_data_type_definition', member_definition)

      type_indicator = member_data_type_definition.TYPE_INDICATOR
      if type_indicator == definitions.TYPE_INDICATOR_INTEGER:

        printf_format_indicator = self._GetRuntimePrintfFormatIndicator(
            member_definition)

        # TODO: detemine number of tabs for alignment.

        template_filename = os.path.join(
            template_directory, 'read_data-debug-integer.c')

        template_mappings['data_type'] = data_type
        template_mappings['format_indicator'] = printf_format_indicator

      elif (type_indicator == definitions.TYPE_INDICATOR_STREAM and
            data_type_size):
        template_filename = os.path.join(
            template_directory, 'read_data-debug-data.c')

        template_mappings['member_data_size'] = data_type_size

      else:
        template_filename = os.path.join(
            template_directory, 'read_data-debug-unsupported.c')

      if member_definition.description:
        description = member_definition.description
      else:
        description = member_definition.name.replace('_', ' ')

      template_mappings['member_name'] = member_definition.name
      template_mappings['member_name_description'] = description

      output_data = self._template_string_generator.Generate(
          template_filename, template_mappings)

      with open(output_file, 'ab') as file_object:
        file_object.write(output_data)

  def _GenerateStoredStructureHeader(self, data_type_definition, output_file):
    """Generates a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
      output_file (str): path of the file output file.
    """
    template_mappings = self._GetTemplateMappings()

    structure_members = self._GetStoredStructureHeaderMembers(
        data_type_definition)

    template_mappings['structure_members'] = structure_members
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, 'stored_structure.h', 'structure.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    del template_mappings['structure_members']

    with open(output_file, 'ab') as file_object:
      file_object.write(output_data)

  def _GenerateStoredStructureHeaderFile(self, data_type_definition):
    """Generates a stored structure header file.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    format_definition = self._GetFormatDefinitions()

    template_directory = os.path.join(
        self._templates_path, 'stored_structure.h')

    template_mappings = self._GetTemplateMappings()

    if not self._prefix:
      output_file = 'stored_structure.h'
    else:
      output_file = os.path.join(
          'lib{0:s}'.format(self._prefix),
          '{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))

    logging.info('Writing: {0:s}'.format(output_file))

    structure_description = self._GetStructureDescription(data_type_definition)
    structure_description_title = '{0:s}{1:s}'.format(
        structure_description[0].upper(), structure_description[1:])

    if format_definition.description:
      structure_description = '{0:s} of a {1:s}'.format(
          structure_description_title, format_definition.description)

    template_mappings['structure_description'] = structure_description
    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(template_directory, 'header.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    del template_mappings['structure_description']

    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

    if data_type_definition.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
      structure_definitions = data_type_definition.members
    else:
      structure_definitions = [data_type_definition]

    for structure_definition in structure_definitions:
      self._GenerateStoredStructureHeader(structure_definition, output_file)

    template_mappings['structure_name'] = data_type_definition.name
    template_mappings['structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(template_directory, 'footer.h')
    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    with open(output_file, 'ab') as file_object:
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

    elif type_indicator in (
        definitions.TYPE_INDICATOR_STREAM, definitions.TYPE_INDICATOR_STRING):
      data_type = 'uint8_t *'

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

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      description = '{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      data_type = self._GetRuntimeDataType(member_definition)

      lines.extend([
          '\t/* {0:s}'.format(description),
          '\t */'])

      if not data_type:
        lines.append('\t/* TODO: implement */')

      elif data_type.endswith('*'):
        lines.append('\t{0:s}{1:s};'.format(data_type, name))

      else:
        lines.append('\t{0:s} {1:s};'.format(data_type, name))

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

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace('_', ' ')

      lines.append('\t/* {0:s}{1:s}'.format(
          description[0].upper(), description[1:]))

      if data_type_size:
       if data_type_size == 1:
         units = 'byte'
       else:
         units = 'bytes'

       lines.append('\t * Consists of {0:d} {1:s}'.format(
           data_type_size, units))

      if data_type_definition.TYPE_INDICATOR == definitions.TYPE_INDICATOR_UUID:
         lines.append('\t * Contains a UUID')

      lines.append('\t */')

      if not data_type_size:
        lines.append('\t/* TODO: unknown size */')

      elif data_type_size == 1:
        lines.append('\tuint8_t {0:s};'.format(name))

      else:
        lines.append('\tuint8_t {0:s}[ {1:d} ];'.format(name, data_type_size))

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
      if data_type_definition.TYPE_INDICATOR not in (
          definitions.TYPE_INDICATOR_STRUCTURE,
          definitions.TYPE_INDICATOR_STRUCTURE_FAMILY):
        continue

      if data_type_definition.TYPE_INDICATOR == (
          definitions.TYPE_INDICATOR_STRUCTURE):

        # Skip structures that are part of a type family.
        if data_type_definition.family_definition:
          continue

        # byte_size = data_type_definition.GetByteSize()
        # if byte_size is None:
        #   continue

      self._GenerateRuntimeStructureHeaderFile(data_type_definition)
      self._GenerateRuntimeStructureSourceFile(data_type_definition)
      self._GenerateStoredStructureHeaderFile(data_type_definition)

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
