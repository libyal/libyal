# -*- coding: utf-8 -*-
"""The source file generator for library source files."""

from __future__ import unicode_literals

import logging
import os

from yaldevtools.source_generators import interface


class LibrarySourceFileGenerator(interface.SourceFileGenerator):
  """Library source file generator."""

  def Generate(self, project_configuration, output_writer):
    """Generates library source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: libcsplit skip wide_string.[ch]
    # TODO: add support for libuna/libuna_types.h
    # TODO: types.h alingment of debug types?
    # TODO: libsmraw/libsmraw_codepage.h alignment of definitions
    # TODO: libfvalue/libfvalue_codepage.h different

    include_header_file = self._GetTypesIncludeHeaderFile(project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of library source files.'.format(
              self._types_include_header_path))
      return

    library_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name)

    codepage_header_file = os.path.join(
        library_path, '{0:s}_codepage.h'.format(
            project_configuration.library_name))
    error_header_file = os.path.join(
        library_path, '{0:s}_error.h'.format(
            project_configuration.library_name))
    notify_header_file = os.path.join(
        library_path, '{0:s}_notify.h'.format(
            project_configuration.library_name))
    types_header_file = os.path.join(
        library_path, '{0:s}_types.h'.format(
            project_configuration.library_name))

    if include_header_file.types:
      longest_type_name = max(include_header_file.types, key=len)
      longest_library_debug_type_prefix = (
          'typedef struct {0:s}_{1:s} {{}}').format(
              project_configuration.library_name, longest_type_name)

    library_debug_type_definitions = []
    type_definitions = []
    for type_name in include_header_file.types:
      library_debug_type_prefix = 'typedef struct {0:s}_{1:s} {{}}'.format(
          project_configuration.library_name, type_name)

      library_debug_type_definition = (
          'typedef struct {0:s}_{1:s} {{}}\t{0:s}_{1:s}_t;').format(
              project_configuration.library_name, type_name)
      library_debug_type_definitions.append(library_debug_type_definition)

      type_definition = 'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')
    template_mappings['library_debug_type_definitions'] = '\n'.join(
        library_debug_type_definitions)
    template_mappings['library_type_definitions'] = '\n'.join(
        type_definitions)

    authors_template_mapping = template_mappings['authors']

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith('libyal'):
        continue

      if directory_entry.endswith('_{0:s}.h'.format(
          project_configuration.library_name)):
        continue

      if (directory_entry == 'libyal_codepage.h' and (
          not os.path.exists(codepage_header_file) or
          project_configuration.library_name == 'libclocale')):
        continue

      if ((directory_entry == 'libyal_libcerror.h' or
           directory_entry == 'libyal_error.c' or
           directory_entry == 'libyal_error.h') and (
               not os.path.exists(error_header_file) or
               project_configuration.library_name == 'libcerror')):
        continue

      if ((directory_entry == 'libyal_libcnotify.h' or
           directory_entry == 'libyal_notify.c' or
           directory_entry == 'libyal_notify.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == 'libcnotify')):
        continue

      if ((directory_entry == 'libyal_wide_string.c' or
           directory_entry == 'libyal_wide_string.h') and (
               not os.path.exists(notify_header_file) or
               project_configuration.library_name == 'libcsplit')):
        continue

      # TODO: improve generation of _types.h file
      if (directory_entry == 'libyal_types.h' and (
          not os.path.exists(types_header_file) or
          project_configuration.library_name in (
              'libcerror', 'libcthreads'))):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = '{0:s}{1:s}'.format(
          project_configuration.library_name, directory_entry[6:])
      output_filename = os.path.join(
          project_configuration.library_name, output_filename)

      if not os.path.exists(output_filename) and not directory_entry in (
          'libyal.c', 'libyal_extern.h', 'libyal.rc.in', 'libyal_support.c',
          'libyal_support.h', 'libyal_unused.h'):
        continue

      if directory_entry == 'libyal.rc.in':
        template_mappings['authors'] = ', '.join(
            project_configuration.project_authors)
      else:
        template_mappings['authors'] = authors_template_mapping

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in ('libyal_codepage.h', 'libyal_types.h'):
        self._VerticalAlignTabs(output_filename)
