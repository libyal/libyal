# -*- coding: utf-8 -*-
"""The source file generator for document files."""

import os

from source_generators import interface


class DocumentFileGenerator(interface.SourceFileGenerator):
  """Document file generator."""

  _AUTHORS = 'Joachim Metz <joachim.metz@gmail.com>'
  _AUTHORS_SEPARATOR = ',\n                            '

  def Generate(self, project_configuration, output_writer):
    """Generates document files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = self._GetTemplateMappings(
        project_configuration, authors_separator=self._AUTHORS_SEPARATOR)
    template_mappings['authors'] = self._AUTHORS
    template_mappings['project_description'] = project_configuration.project_description
    template_mappings['project_status'] = project_configuration.project_status

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, directory_entry)

    del template_mappings['project_description']
    del template_mappings['project_status']
