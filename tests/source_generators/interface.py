# -*- coding: utf-8 -*-
"""Tests for the source file generator interface."""

from __future__ import unicode_literals

import os
import unittest

from yaldevtools.source_generators import interface

from tests import test_lib


class SourceFileGeneratorTest(test_lib.BaseTestCase):
  """Source files generator tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    source_directory = os.path.abspath(__file__)
    source_directory = os.path.dirname(source_directory)
    source_directory = os.path.dirname(source_directory)
    source_directory = os.path.dirname(source_directory)

    projects_directory = os.path.dirname(source_directory)
    template_directory = os.path.join(
        source_directory, 'data', 'source', 'common')

    generator = interface.SourceFileGenerator(
        projects_directory, template_directory)
    self.assertIsNotNone(generator)

  # TODO: add tests for _CorrectDescriptionSpelling function.
  # TODO: add tests for _GenerateSection function.
  # TODO: add tests for _GenerateSections function.
  # TODO: add tests for _GetDefinitionsIncludeHeaderFile function.
  # TODO: add tests for _GetLibraryIncludeHeaderFile function.
  # TODO: add tests for _GetLibraryMakefileAM function.
  # TODO: add tests for _GetMainMakefileAM function.
  # TODO: add tests for _GetTemplateMappings function.
  # TODO: add tests for _GetTypeLibraryHeaderFile function.
  # TODO: add tests for _GetTypesIncludeHeaderFile function.
  # TODO: add tests for _HasGlob function.
  # TODO: add tests for _HasTests function.
  # TODO: add tests for _ReadTemplateFile function.
  # TODO: add tests for _SetSequenceTypeNameInTemplateMappings function.
  # TODO: add tests for _SetSequenceValueNameInTemplateMappings function.
  # TODO: add tests for _SetTypeFunctionInTemplateMappings function.
  # TODO: add tests for _SetTypeNameInTemplateMappings function.
  # TODO: add tests for _SetValueNameInTemplateMappings function.
  # TODO: add tests for _SetValueTypeInTemplateMappings function.
  # TODO: add tests for _SortIncludeHeaders function.
  # TODO: add tests for _SortVariableDeclarations function.
  # TODO: add tests for _VerticalAlignAssignmentStatements function.
  # TODO: add tests for _VerticalAlignFunctionArguments function.
  # TODO: add tests for _VerticalAlignTabs function.


if __name__ == '__main__':
  unittest.main()
