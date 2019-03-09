# -*- coding: utf-8 -*-
"""The source file generator for common source files."""

import os

from yaldevtools.source_generators import interface


class CommonSourceFileGenerator(interface.SourceFileGenerator):
  """Common source files generator."""

  _AUTHORS = 'Joachim Metz <joachim.metz@gmail.com>'
  _AUTHORS_SEPARATOR = ',\n *                          '

  def Generate(self, project_configuration, output_writer):
    """Generates common source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    template_mappings = self._GetTemplateMappings(
        project_configuration, authors_separator=self._AUTHORS_SEPARATOR)
    template_mappings['authors'] = self._AUTHORS

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join('common', directory_entry)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)
