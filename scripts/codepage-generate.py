#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to generate libuna source files base on a codepage definition."""

import argparse
import datetime
import logging
import os
import re
import sys

from yaldevtools import source_formatter
from yaldevtools import template_string


class SourceGenerator(object):
  """Generates libuna source files based on a codepage definition."""

  _CODEPAGE_MAPPINGS_REGEX = re.compile(
      '([0-9A-F]{2,4}) = U\+([0-9A-F]{4}) : ', re.IGNORECASE)

  def __init__(self, templates_path):
    """Initializes a source generator.

    Args:
      templates_path (str): templates path.
    """
    super(SourceGenerator, self).__init__()
    self._codepage_name = None
    self._codepage_mappings = {}
    self._codepage_values = {}
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()
    self._unicode_mappings = {}

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

  def _GenerateSourceFile(self):
    """Generates a source file."""
    templates_path = os.path.join(self._templates_path, 'libuna_codepage.c')

    output_filename = os.path.join(
        'libuna', 'libuna_codepage_{0:s}.c'.format(self._codepage_name))

    template_mappings = self._GetTemplateMappings()

    template_filename = os.path.join(templates_path, 'header.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename)

    template_filename = os.path.join(templates_path, 'includes.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    number_of_table_values = 0
    first_codepage_value = None
    last_codepage_value = None
    lines = []
    table_values = []

    # TODO: group values in small tables
    # TODO: add suport for undefined codepage values
    # TODO: add suport for MSC
    for codepage_value, unicode_value in sorted(
        self._codepage_mappings.items()):

      if last_codepage_value is not None:
        while last_codepage_value < codepage_value - 1:
          last_codepage_value += 1
          table_values.append('0x{0:04x}'.format(last_codepage_value))
          number_of_table_values += 1

          if last_codepage_value % 8 == 7:
            lines.append('\t{0:s},'.format(', '.join(table_values)))
            table_values = []

      table_values.append('0x{0:04x}'.format(unicode_value))
      number_of_table_values += 1

      if codepage_value % 8 == 7:
        lines.append('\t{0:s},'.format(', '.join(table_values)))
        table_values = []

      if first_codepage_value is None:
        first_codepage_value = codepage_value
      last_codepage_value = codepage_value

    if table_values:
      lines.append('\t{0:s}'.format(', '.join(table_values)))
      table_values = []
    else:
      lines[-1] = lines[-1][:-1]

    lines.insert(0, (
        'const uint16_t libuna_codepage_{0:s}_byte_stream_to_unicode_base_'
        '0x{1:02x}[ {2:d} ] = {{').format(
            self._codepage_name, first_codepage_value, number_of_table_values))
    lines.append('};')

    template_mappings['codepage_to_unicode_table'] = '\n'.join(lines)

    template_filename = os.path.join(
        templates_path, 'codepage_to_unicode_table.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    del template_mappings['codepage_to_unicode_table']

    template_filename = os.path.join(
        templates_path, 'unicode_to_codepage_tables-start.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    first_unicode_value = None
    last_unicode_value = None

    groups = {}
    for unicode_value in sorted(self._unicode_mappings):
      if first_unicode_value is None:
        first_unicode_value = unicode_value
      elif (last_unicode_value is not None and
            last_unicode_value + 16 < unicode_value):
        first_unicode_value = unicode_value

      group_base_value = first_unicode_value & ~( 0x0007 )
      if group_base_value not in groups:
        groups[group_base_value] = [unicode_value]
      else:
        groups[group_base_value].append(unicode_value)

      last_unicode_value = unicode_value

    for group_base_value, unicode_values in sorted(groups.items()):
      if len(unicode_values) < 8:
        continue

      number_of_table_values = 0
      last_unicode_value = group_base_value - 1
      lines = []
      table_values = []

      for unicode_value in sorted(unicode_values):
        codepage_value = self._unicode_mappings[unicode_value]

        while last_unicode_value < unicode_value - 1:
          last_unicode_value += 1
          table_values.append('0x1a')
          number_of_table_values += 1

          if last_unicode_value % 8 == 7:
            lines.append('\t{0:s},'.format(', '.join(table_values)))
            table_values = []

        table_values.append('0x{0:02x}'.format(codepage_value))
        number_of_table_values += 1

        if unicode_value % 8 == 7:
          lines.append('\t{0:s},'.format(', '.join(table_values)))
          table_values = []

        last_unicode_value = unicode_value

      if table_values:
        lines.append('\t{0:s}'.format(', '.join(table_values)))
      else:
        lines[-1] = lines[-1][:-1]

      template_mappings['entries_base_offset'] = '0x{0:04x}'.format(
          group_base_value)
      template_mappings['number_of_entries'] = number_of_table_values
      template_mappings['table_entries'] = '\n'.join(lines)

      template_filename = os.path.join(
          templates_path, 'unicode_to_codepage_table.c')

      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

      del template_mappings['entries_base_offset']
      del template_mappings['number_of_entries']
      del template_mappings['table_entries']

    template_filename = os.path.join(
        templates_path, 'copy_from_byte_stream-start.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    template_filename = os.path.join(
        templates_path, 'copy_from_byte_stream-body.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    template_filename = os.path.join(
        templates_path, 'copy_from_byte_stream-end.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    template_filename = os.path.join(
        templates_path, 'copy_to_byte_stream-start.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    template_filename = os.path.join(
        templates_path, 'copy_to_byte_stream-body.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

    template_filename = os.path.join(
        templates_path, 'copy_to_byte_stream-end.c')

    self._GenerateSection(
        template_filename, template_mappings, output_filename,
        access_mode='a')

  def _GenerateSourceHeaderFile(self):
    """Generates a source header file."""
    output_filename = os.path.join(
        'libuna', 'libuna_codepage_{0:s}.h'.format(self._codepage_name))

    template_mappings = self._GetTemplateMappings()

    template_filename = os.path.join(
        self._templates_path, 'libuna_codepage.h')

    self._GenerateSection(
        template_filename, template_mappings, output_filename)

  def _GenerateTestHeaderFile(self):
    """Generates a test header file."""
    output_filename = os.path.join(
        'tests', 'una_test_codepage_{0:s}.h'.format(self._codepage_name))

    number_of_test_mappings = 0
    test_mappings = []
    last_codepage_value = -1
    for codepage_value, unicode_value in sorted(self._codepage_values.items()):
      if codepage_value == 0:
        byte_stream = ['0x00']
      else:
        byte_stream = []
        byte_value = codepage_value
        while byte_value > 0:
          byte_stream_value = '0x{0:02x}'.format(byte_value & 0xff)
          byte_value >>= 8

          byte_stream.insert(0, byte_stream_value)

      # Add an empty line between non-consecutive values.
      if codepage_value > last_codepage_value + 1:
        test_mappings.append('')

      test_mappings.append(
          '\t{{ {{ {0:s} }}, {1:d}, 0x{2:04x}, 0 }},'.format(
              ', '.join(byte_stream), len(byte_stream), unicode_value))
      number_of_test_mappings += 1

      last_codepage_value = codepage_value

    if test_mappings:
      # Remove the trailing comma in the last test mapping.
      test_mappings[-1] = test_mappings[-1][:-1]

    template_mappings = self._GetTemplateMappings()
    template_mappings['number_of_test_mappings'] = number_of_test_mappings
    template_mappings['test_mappings'] = '\n'.join(test_mappings)

    template_filename = os.path.join(
        self._templates_path, 'una_test_codepage.h')

    self._GenerateSection(
        template_filename, template_mappings, output_filename)

    del template_mappings['number_of_test_mappings']
    del template_mappings['test_mappings']

  def _GetTemplateMappings(self):
    """Retrieves the template mappings.

    Args:
      library_name (Optional[str]): library name.
      structure_name (Optional[str]): structure name.

    Returns:
      dict[str, str]: template mappings.
    """
    template_mappings = {}

    date = datetime.date.today()
    template_mappings['copyright'] = '2008-{0:d}'.format(date.year)

    codepage_description = self._codepage_name.replace('_', ' ')
    template_mappings['codepage_description'] = codepage_description.title()
    template_mappings['codepage_name'] = self._codepage_name
    template_mappings['codepage_name_upper_case'] = self._codepage_name.upper()

    return template_mappings

  def Generate(self):
    """Generates source code from the codepage definitions.

    Returns:
      bool: True if successful, False otherwise.
    """
    self._GenerateSourceFile()
    self._GenerateSourceHeaderFile()
    self._GenerateTestHeaderFile()

  def ReadDefinitions(self, definitions_file):
    """Reads the definitions form file or directory.

    Args:
      definitions_file (str): path to the codepage definition file.
    """
    codepage_name = os.path.basename(definitions_file)
    codepage_name, _, _ = codepage_name.rpartition('.')
    self._codepage_name = codepage_name.replace('-', '_')

    # TODO: add support for multi-byte characters

    self._codepage_values = {}
    with open(definitions_file, 'r', encoding='utf-8') as file_object:
      for line in file_object.readlines():
        match_groups = self._CODEPAGE_MAPPINGS_REGEX.match(line)
        if match_groups:
          try:
            codepage_value = int(match_groups[1], 16)
            unicode_value = int(match_groups[2], 16)
            self._codepage_values[codepage_value] = unicode_value
          except (ValueError, TypeError):
            pass

    self._codepage_mappings = {}
    self._unicode_mappings = {}
    for codepage_value, unicode_value in sorted(self._codepage_values.items()):
      if codepage_value != unicode_value:
        self._codepage_mappings[codepage_value] = unicode_value
        self._unicode_mappings[unicode_value] = codepage_value


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates libuna source files base on a codepage definition.'))

  argument_parser.add_argument(
      'definitions_file', action='store', metavar='PATH',
      default='windows-1252.txt', help='Path to the codepage definition file.')

  argument_parser.add_argument(
      '-o', '--output', dest='output_directory', action='store',
      metavar='OUTPUT_DIRECTORY', default=None,
      help='Path of the output files to write to.')

  argument_parser.add_argument(
      '--templates-path', '--templates_path', dest='templates_path',
      action='store', metavar='PATH', default=None, help=(
          'Path to the template files.'))

  options = argument_parser.parse_args()

  if not options.definitions_file:
    print('Missing codepage definition file.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not os.path.exists(options.definitions_file):
    print('No such codepage definition file: {0:s}.'.format(
        options.definitions_file))
    print('')
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print('No such output directory: {0:s}.'.format(options.output_directory))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  templates_path = options.templates_path
  if not templates_path:
    templates_path = os.path.dirname(__file__)
    templates_path = os.path.dirname(templates_path)
    templates_path = os.path.join(templates_path, 'data', 'codepage')

  source_generator = SourceGenerator(templates_path)
  source_generator.ReadDefinitions(options.definitions_file)
  return source_generator.Generate()


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
