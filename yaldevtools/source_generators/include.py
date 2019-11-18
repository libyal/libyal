# -*- coding: utf-8 -*-
"""The source file generator for include source files."""

import os

from yaldevtools.source_generators import interface


class IncludeSourceFileGenerator(interface.SourceFileGenerator):
  """Include source file generator."""

  def _GenerateFeaturesHeader(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, output_writer, output_filename):
    """Generates a features header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (MainMakefileAMFile): project main Makefile.am file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(
        self._template_directory, 'libyal', 'features.h.in')

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: fix check for libsigscan.
    if include_header_file.have_wide_character_type:
      template_filename = os.path.join(
          template_directory, 'wide_character_type.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    # TODO: improve detection if include is needed.
    if 'libcthreads' in makefile_am_file.libraries:
      template_filename = os.path.join(template_directory, 'multi_thread.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if include_header_file.have_bfio:
      template_filename = os.path.join(template_directory, 'bfio.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GenerateMakefileAM(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, output_writer, output_filename):
    """Generates a tests Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (LibraryMakefileAMFile): library Makefile.am file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    library_name = project_configuration.library_name

    pkginclude_headers = [
        '\t{0:s}/definitions.h \\'.format(library_name),
        '\t{0:s}/extern.h \\'.format(library_name),
        '\t{0:s}/features.h \\'.format(library_name),
        '\t{0:s}/types.h'.format(library_name)]

    # TODO: detect if header file exits.
    if library_name != 'libcerror':
      pkginclude_header = '\t{0:s}/error.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    if include_header_file.HasFunction('get_codepage'):
      pkginclude_header = '\t{0:s}/codepage.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name in ('libnk2', 'libpff'):
      pkginclude_header = '\t{0:s}/mapi.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    # TODO: detect if header file exits.
    if library_name == 'libolecf':
      pkginclude_header = '\t{0:s}/ole.h \\'.format(library_name)
      pkginclude_headers.append(pkginclude_header)

    pkginclude_headers = sorted(pkginclude_headers)

    template_mappings['pkginclude_headers'] = '\n'.join(pkginclude_headers)

    template_filename = os.path.join(self._template_directory, 'Makefile.am')

    output_filename = os.path.join('include', 'Makefile.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

  def _GenerateTypesHeader(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates a types header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(
        self._template_directory, 'libyal', 'types.h.in')

    type_definitions = []
    # TODO: deprecate project_configuration.library_public_types ?
    for type_name in sorted(project_configuration.library_public_types):
      type_definition = 'typedef intptr_t {0:s}_{1:s}_t;'.format(
          project_configuration.library_name, type_name)
      type_definitions.append(type_definition)

    template_mappings['library_type_definitions'] = '\n'.join(
        type_definitions)

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if type_definitions:
      template_filename = os.path.join(template_directory, 'public_types.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def Generate(self, project_configuration, output_writer):
    """Generates include source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    output_filename = os.path.join('include', 'Makefile.am')
    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

    output_directory = os.path.join(
        'include', project_configuration.library_name)
    template_directory = os.path.join(self._template_directory, 'libyal')
    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      if (directory_entry not in ('definitions.h.in', 'extern.h') and
          not os.path.exists(output_filename)):
        continue

      # Do not overwrite defintions.h.in when it exist.
      if (directory_entry != 'definitions.h.in' and
          os.path.exists(output_filename)):
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename)

      if directory_entry in ('codepage.h', 'definitions.h.in', 'error.h'):
        self._VerticalAlignTabs(output_filename)

    output_filename = os.path.join(output_directory, 'features.h.in')
    self._GenerateFeaturesHeader(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, output_writer, output_filename)

    output_filename = os.path.join(output_directory, 'types.h.in')
    self._GenerateTypesHeader(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)
