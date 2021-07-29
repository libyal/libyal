#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to generate documenation based on dtFabric format definitions."""

import argparse
import datetime
import logging
import os
import sys

from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

from yaldevtools import template_string


class AsciidocFormatDocumentGenerator(object):
  """Asciidoc format document generator."""

  _APPENDICES_TEMPLATE_FILE = 'appendices.asciidoc'
  _BODY_TEMPLATE_FILE = 'body.asciidoc'
  _OVERVIEW_TEMPLATE_FILE = 'overview.asciidoc'
  _PREFACE_TEMPLATE_FILE = 'preface.asciidoc'

  def __init__(self, templates_path):
    """Initializes a generator.

    Args:
      templates_path (str): templates path.
    """
    super(AsciidocFormatDocumentGenerator, self).__init__()
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()

  def _GenerateAppendices(self):
    """Generates appendices."""
    template_mappings = {}

    template_filename = os.path.join(
        self._templates_path, self._APPENDICES_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    print(output_data)

    # TODO: generate references
    # TODO: generate GFDL

  def _GenerateBody(self):
    """Generates a body."""
    template_mappings = {}

    template_filename = os.path.join(
        self._templates_path, self._BODY_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    print(output_data)

    self._GenerateOverview()

    # TODO: generate chapter per structure

  def _GetFormatDefinitions(self):
    """Retrieves the format definition.

    Returns:
      FormatDefinition: format definition.

    Raises:
      RuntimeError: if the format definition is missing or if there are more
          than 1 format definitions.
    """
    # pylint: disable=protected-access

    if not self._definitions_registry._format_definitions:
      raise RuntimeError('Missing format definition.')

    if len(self._definitions_registry._format_definitions) > 1:
      raise RuntimeError('Unsupported multiple format definitions.')

    return self._definitions_registry.GetDefinitionByName(
        self._definitions_registry._format_definitions[0])

  def _GenerateOverview(self):
    """Generates the overview chapter."""
    format_definition = self._GetFormatDefinitions()

    template_mappings = {}

    summary = format_definition.metadata.get('summary', None)
    if summary:
      template_mappings['summary'] = summary

    template_filename = os.path.join(
        self._templates_path, self._OVERVIEW_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    print(output_data)

    # TODO: generate characteristics table
    # TODO: generate overview description

  def _GeneratePreface(self):
    """Generates a preface."""
    format_definition = self._GetFormatDefinitions()

    template_mappings = {
        'title': format_definition.description}

    if format_definition.description:
      template_mappings['abstract'] = (
          'This document contains information about the {0:s}'.format(
              format_definition.description))

    summary = format_definition.metadata.get('summary', None)
    if summary:
      template_mappings['summary'] = summary

    authors = format_definition.metadata.get('authors', None)
    if authors:
      template_mappings['authors'] = ', '.join(authors)

    keywords = format_definition.metadata.get('keywords', None)
    if authors:
      template_mappings['keywords'] = ', '.join(keywords)

    year = format_definition.metadata.get('year', None)
    if year:
      date = datetime.date.today()
      if year != date.year:
        copyright_years = '{0:d}-{1:d}'.format(year, date.year)
      else:
        copyright_years = '{0:d}'.format(year)

      template_mappings['copyright'] = copyright_years

    template_filename = os.path.join(
        self._templates_path, self._PREFACE_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    print(output_data)

  def Generate(self):
    """Generates a format document."""
    self._GeneratePreface()
    self._GenerateBody()
    self._GenerateAppendices()

  def ReadDefinitions(self, path):
    """Reads the definitions form file or directory.

    Args:
      path (str): path of the definition file.
    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    definitions_reader.ReadFile(self._definitions_registry, path)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Generates documentation based on dtFabric format definitions.'))

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
    templates_path = os.path.join(templates_path, 'data')

  source_generator = AsciidocFormatDocumentGenerator(templates_path)

  try:
    source_generator.ReadDefinitions(options.source)
  except errors.FormatError as exception:
    print('Unable to read definitions with error: {0!s}'.format(exception))
    return False

  source_generator.Generate()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
