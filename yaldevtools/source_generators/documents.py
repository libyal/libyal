# -*- coding: utf-8 -*-
"""The source file generator for document files."""

import os

from yaldevtools.source_generators import interface


class DocumentFileGenerator(interface.SourceFileGenerator):
  """Document file generator."""

  _AUTHORS = 'Joachim Metz <joachim.metz@gmail.com>'
  _AUTHORS_SEPARATOR = ',\n                            '

  def _GenerateAuthors(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates an AUTHORS file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    original_data = []
    if os.path.isfile(output_filename):
      with open(output_filename, 'r', encoding='utf8') as file_object:
        original_data = file_object.readlines()

      original_data = original_data[4:]

    template_directory = os.path.join(self._template_directory, 'AUTHORS')

    template_mappings['authors'] = self._AUTHORS

    template_filename = os.path.join(template_directory, 'header')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['authors']

    if original_data:
      with open(output_filename, 'a', encoding='utf8') as file_object:
        file_object.writelines(original_data)

  def _GenerateReadme(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a README file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    original_data = []
    if os.path.isfile(output_filename):
      with open(output_filename, 'r', encoding='utf8') as file_object:
        original_data = file_object.readlines()

      original_data = original_data[7:-5]

    template_directory = os.path.join(self._template_directory, 'README')

    template_mappings['project_description'] = (
        project_configuration.project_description)
    template_mappings['project_status'] = project_configuration.project_status

    template_filename = os.path.join(template_directory, 'header')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['project_description']
    del template_mappings['project_status']

    if original_data:
      with open(output_filename, 'a', encoding='utf8') as file_object:
        file_object.writelines(original_data)

    template_filename = os.path.join(template_directory, 'footer')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def Generate(self, project_configuration, output_writer):
    """Generates document files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = self._GetTemplateMappings(
        project_configuration, authors_separator=self._AUTHORS_SEPARATOR)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, directory_entry)

    self._GenerateAuthors(
        project_configuration, template_mappings, output_writer, 'AUTHORS')
    self._GenerateReadme(
        project_configuration, template_mappings, output_writer, 'README')
