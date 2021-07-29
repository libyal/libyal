# -*- coding: utf-8 -*-
"""The source file generator for python module source files."""

import collections
import io
import logging
import os

from yaldevtools import definitions
from yaldevtools import source_code
from yaldevtools.source_generators import interface


class PythonModuleSourceFileGenerator(interface.SourceFileGenerator):
  """Python module source files generator."""

  def _CopyFunctionToOutputFile(self, lines, search_string, output_filename):
    """Copies a function to the output file.

    Args:
      lines (list[bytes]): lines of the input file to copy from.
      search_string (bytes): string to search the input for.
      output_filename (str): path of the output file.

    Returns:
      bool: True if the function was found and copied, False otherwise.
    """
    function_index = None
    for index, line in enumerate(lines):
      if line.startswith(search_string):
        # TODO: improve this to determine start of comment based on lines.
        function_index = index - 3
        break

    if function_index is None:
      return False

    with io.open(output_filename, 'a', encoding='utf8') as file_object:
      line = lines[function_index]
      while not line.startswith('}'):
        file_object.write(line)

        function_index += 1
        line = lines[function_index]

      file_object.write(line)
      file_object.write(lines[function_index + 1])

    return True

  def _FormatHeaderFile(self, project_configuration, output_filename):
    """Formats a header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_filename (str): path of the output file.
    """
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _FormatSourceFile(self, project_configuration, output_filename):
    """Formats a source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_filename (str): path of the output file.
    """
    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)
    # TODO: combine vertical align functions.
    self._VerticalAlignAssignmentStatements(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)

  def _GenerateDefinitionsHeaderFile(
      self, project_configuration, template_mappings, definitions_name,
      enum_declaration, output_writer):
    """Generates a Python definitions object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      definitions_name (str): name of definitions.
      enum_declaration (EnumDeclaration): enumeration type declaration.
      output_writer (OutputWriter): output writer.
    """
    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_definitions')

    template_mappings['definitions_name'] = definitions_name
    template_mappings['definitions_name_upper_case'] = definitions_name.upper()
    template_mappings['definitions_description'] = definitions_name.replace(
        '_', ' ')

    template_filename = os.path.join(template_directory, 'pyyal_definitions.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(definitions_name, output_filename)

    self._FormatHeaderFile(project_configuration, output_filename)

  def _GenerateDefinitionsSourceFile(
      self, project_configuration, template_mappings, definitions_name,
      enum_declaration, output_writer):
    """Generates a Python definitions object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      definitions_name (str): name of definitions.
      enum_declaration (EnumDeclaration): enumeration type declaration.
      output_writer (OutputWriter): output writer.
    """
    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, definitions_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_definitions')

    template_mappings['definitions_name'] = definitions_name
    template_mappings['definitions_name_upper_case'] = definitions_name.upper()
    template_mappings['definitions_description'] = definitions_name.replace(
        '_', ' ')

    template_mappings['definition_name'] = definitions_name[:-1]
    template_mappings['definition_name_upper_case'] = (
        definitions_name[:-1].upper())

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    constant_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, definitions_name[:-1])
    constant_name_prefix_length = len(constant_name_prefix)

    for constant_name in enum_declaration.constants.keys():
      constant_name = constant_name.lower()
      if not constant_name.startswith(constant_name_prefix):
        continue

      constant_name = constant_name[constant_name_prefix_length:]

      if constant_name in ('undefined', 'unknown'):
        continue

      template_mappings['constant_name'] = constant_name
      template_mappings['constant_name_upper_case'] = constant_name.upper()

      template_filename = os.path.join(template_directory, 'constant.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')
      self._CorrectDescriptionSpelling(constant_name, output_filename)

    template_filename = os.path.join(template_directory, 'footer.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(definitions_name, output_filename)

    self._FormatSourceFile(project_configuration, output_filename)

  def _GenerateModuleHeaderFile(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates a Python module header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    signature_type = include_header_file.GetCheckSignatureType()

    has_glob = self._HasGlob(project_configuration, signature_type)

    template_directory = os.path.join(self._template_directory, 'pyyal_module')

    output_filename = '{0:s}.h'.format(project_configuration.python_module_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    if signature_type:
      template_mappings['signature_type'] = signature_type

    template_names = ['header.h', 'includes.h', 'get_version.h']

    if signature_type:
      template_names.append('check_signature.h')

    if has_glob:
      template_names.append('glob.h')

    if signature_type:
      template_names.append('open_new.h')

    template_names.extend(['init.h', 'footer.h'])

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    if signature_type:
      del template_mappings['signature_type']

    self._FormatHeaderFile(project_configuration, output_filename)

  def _GenerateModuleSourceFile(
      self, project_configuration, template_mappings, include_header_file,
      python_module_types, definition_types, output_writer):
    """Generates a Python module source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      python_module_types (list[str]): names of Python module types.
      definition_types (list[str]): names of Python module definition types.
      output_writer (OutputWriter): output writer.
    """
    signature_type = include_header_file.GetCheckSignatureType()

    has_glob = self._HasGlob(project_configuration, signature_type)

    template_directory = os.path.join(self._template_directory, 'pyyal_module')

    output_filename = '{0:s}.c'.format(project_configuration.python_module_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    if signature_type:
      signature_desription = (
          project_configuration.project_data_format or 'TODO')

      if signature_type.lower() not in signature_desription.lower():
        signature_desription = '{0:s} {1:s}'.format(
            signature_desription, signature_type)

      template_mappings['signature_type'] = signature_type
      template_mappings['signature_desription'] = signature_desription

    template_names = ['header.c', 'includes-start.c']

    if signature_type:
      template_names.append('includes-file_object_io_handle.c')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    for type_name in sorted(python_module_types):
      self._SetTypeNameInTemplateMappings(template_mappings, type_name)

      template_filename = os.path.join(
          template_directory, 'includes-type_object.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_names = ['includes-end.c']

    if signature_type:
      template_names.append('bfio.c')

    template_names.append('module_methods-start.c')

    if signature_type:
      template_names.append('module_methods-check_signature.c')

    if has_glob:
      template_names.append('module_methods-glob.c')

    # TODO: add multi-file open support if glob is present.
    if signature_type:
      template_names.append('module_methods-open_new.c')

    template_names.extend(['module_methods-end.c', 'get_version.c'])

    if signature_type:
      template_names.append('check_signature.c')

    # TODO: add condition
    # template_names.append('glob.c')

    if signature_type:
      template_names.append('open_new.c')

    template_names.extend(['module_definition.c', 'init-start.c'])

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    for type_name in sorted(python_module_types):
      self._SetTypeNameInTemplateMappings(template_mappings, type_name)

      if type_name in definition_types:
        template_filename = 'init-definitions_type_object.c'
      else:
        template_filename = 'init-type_object.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'init-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if signature_type:
      del template_mappings['signature_type']
      del template_mappings['signature_desription']

    self._FormatSourceFile(project_configuration, output_filename)

  def _GenerateSequenceTypeHeaderFile(
      self, project_configuration, template_mappings, type_name, output_writer):
    """Generates a Python sequence type object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
    """
    sequence_type_name = self._GetSequenceName(type_name)

    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_sequence_type')

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_filename = os.path.join(
        template_directory, 'pyyal_sequence_type.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(sequence_type_name, output_filename)
    self._CorrectDescriptionSpelling(type_name, output_filename)

    self._FormatHeaderFile(project_configuration, output_filename)

  def _GenerateSequenceTypeSourceFile(
      self, project_configuration, template_mappings, type_name, output_writer,
      type_is_object=False):
    """Generates a Python sequence type object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
      type_is_object (Optional[bool]): True if the type is an object.
    """
    sequence_type_name = self._GetSequenceName(type_name)

    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, sequence_type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'pyyal_sequence_type')

    python_module_include_names = set([
        project_configuration.library_name, sequence_type_name, 'libcerror',
        'python'])

    if type_is_object:
      python_module_include_names.add(type_name)

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = '#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    self._SetSequenceTypeNameInTemplateMappings(
        template_mappings, sequence_type_name)

    template_mappings['python_module_includes'] = '\n'.join(
        python_module_includes)

    template_filename = os.path.join(
        template_directory, 'pyyal_sequence_type.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)
    self._CorrectDescriptionSpelling(sequence_type_name, output_filename)

    self._FormatSourceFile(project_configuration, output_filename)

  def _GenerateTypeHeaderFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, has_pseudo_sub_types=False,
      is_pseudo_type=False):
    """Generates a Python type object header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      has_pseudo_sub_types (Optional[bool]): True if type has pseudo sub types.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.
    """
    output_filename = '{0:s}_{1:s}.h'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    open_support = 'open' in python_function_prototypes
    without_initialize_and_with_free = (
        'initialize' not in python_function_prototypes and
        'free' in python_function_prototypes)

    # TODO: make check more generic based on the source itself.
    if (project_configuration.library_name == 'libfwnt' and
        type_name == 'security_identifier'):
      with_parent = True
    else:
      with_parent = without_initialize_and_with_free

    if is_pseudo_type:
      template_directory = os.path.join(
          self._template_directory, 'pyyal_pseudo_type')
    else:
      template_directory = os.path.join(self._template_directory, 'pyyal_type')

    if is_pseudo_type:
      base_type_name = 'item'
      base_type_indicator = '{0:s}_{1:s}_TYPE_{2:s}'.format(
          project_configuration.library_name, base_type_name, type_name)
      base_type_indicator = base_type_indicator.upper()

      template_mappings['base_type_name'] = base_type_name
      template_mappings['base_type_description'] = base_type_name
      template_mappings['base_type_indicator'] = base_type_indicator

    template_names = ['header.h']

    if open_support:
      template_names.append('includes_with_input.h')
    else:
      template_names.append('includes.h')

    if open_support:
      template_names.append('typedef_with_input.h')
    elif with_parent:
      template_names.append('typedef_with_parent.h')
    else:
      template_names.append('typedef.h')

    if not is_pseudo_type:
      if has_pseudo_sub_types:
        template_names.append('new-with_type_object.h')

      elif with_parent:
        template_names.append('new-with_parent.h')

      template_names.extend(['init.h', 'free.h'])

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      value_name = python_function_prototype.value_name

      template_filename = '{0:s}.h'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None
        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET):

          if python_function_prototype.DataTypeIsDatetime():
            template_filename = 'get_datetime_value.h'

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):

          value_name_prefix = ''
          if value_name.startswith('recovered_'):
            value_name_prefix = 'recovered_'
            value_name = value_name[10:]

          template_filename = 'get_{0:s}{1:s}_value_by_index.h'.format(
              value_name_prefix, python_function_prototype.data_type)

          sequence_value_name = self._GetSequenceName(value_name)
          self._SetSequenceValueNameInTemplateMappings(
              template_mappings, sequence_value_name)

        if not template_filename:
          if python_function_prototype.arguments:
            template_filename = 'type_object_function_with_args.h'
          else:
            template_filename = 'type_object_function.h'

        if template_filename:
          template_filename = os.path.join(
              template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            'Unable to generate Python type object header for: {0:s}.{1:s} '
            'missing template: {2:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetTypeFunctionInTemplateMappings(template_mappings, type_function)
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')
      self._CorrectDescriptionSpelling(value_name, output_filename)

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)

    self._FormatHeaderFile(project_configuration, output_filename)

  def _GenerateTypeSourceFile(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, has_pseudo_sub_types=False,
      is_pseudo_type=False):
    """Generates a Python type object source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      has_pseudo_sub_types (Optional[bool]): True if type has pseudo sub types.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.
    """
    output_filename = '{0:s}_{1:s}.c'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join(
        project_configuration.python_module_name, output_filename)

    lines = []
    if os.path.exists(output_filename):
      with io.open(output_filename, 'r', encoding='utf8') as file_object:
        lines = file_object.readlines()

    bfio_support = 'open_file_object' in python_function_prototypes
    codepage_support = 'get_ascii_codepage' in python_function_prototypes
    open_support = 'open' in python_function_prototypes

    without_initialize_and_with_free = (
        'initialize' not in python_function_prototypes and
        'free' in python_function_prototypes)

    # TODO: make check more generic based on the source itself.
    if (project_configuration.library_name == 'libfwnt' and
        type_name == 'security_identifier'):
      with_parent = True
    else:
      with_parent = without_initialize_and_with_free

    python_module_include_names = set([
        project_configuration.library_name, type_name, 'error', 'libcerror',
        'python', 'unused'])

    if bfio_support:
      python_module_include_names.update(
          set(['file_object_io_handle', 'libbfio']))

    if codepage_support:
      python_module_include_names.update(set(['codepage', 'libclocale']))

    for python_function_prototype in python_function_prototypes.values():
      if python_function_prototype.data_type in (
          definitions.DATA_TYPE_FAT_DATE_TIME,
          definitions.DATA_TYPE_POSIX_TIME):
        python_module_include_names.update(set(['datetime']))

      if python_function_prototype.data_type in (
          definitions.DATA_TYPE_FILETIME,
          definitions.DATA_TYPE_FLOATINGTIME):
        python_module_include_names.update(set(['datetime', 'integer']))

      elif python_function_prototype.data_type == definitions.DATA_TYPE_GUID:
        python_module_include_names.add('guid')

      elif python_function_prototype.data_type == definitions.DATA_TYPE_UUID:
        python_module_include_names.add('uuid')

      elif python_function_prototype.data_type in (
          definitions.DATA_TYPE_SIZE64,
          definitions.DATA_TYPE_OFF64,
          definitions.DATA_TYPE_UINT64):
        python_module_include_names.add('integer')

      elif python_function_prototype.data_type == definitions.DATA_TYPE_OBJECT:
        python_module_include_names.add(python_function_prototype.object_type)

        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = self._GetSequenceName(
              python_function_prototype.object_type)
          python_module_include_names.add(sequence_type_name)

      elif python_function_prototype.data_type == definitions.DATA_TYPE_STRING:
        if python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_GET_BY_INDEX):
          sequence_type_name = python_function_prototype.arguments[0]

          sequence_type_prefix, _, sequence_type_suffix = (
              sequence_type_name.rpartition('_'))

          if sequence_type_suffix in ('entry', 'index'):
            sequence_type_name = sequence_type_prefix

          sequence_type_name = self._GetSequenceName(sequence_type_name)
          python_module_include_names.add(sequence_type_name)

    if is_pseudo_type:
      template_directory = os.path.join(
          self._template_directory, 'pyyal_pseudo_type')
    else:
      template_directory = os.path.join(self._template_directory, 'pyyal_type')

    if is_pseudo_type:
      base_type_name = 'item'
      base_type_indicator = '{0:s}_{1:s}_TYPE_{2:s}'.format(
          project_configuration.library_name, base_type_name, type_name)
      base_type_indicator = base_type_indicator.upper()

      template_mappings['base_type_name'] = base_type_name
      template_mappings['base_type_description'] = base_type_name
      template_mappings['base_type_indicator'] = base_type_indicator

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    # TODO: include header of sub types

    python_module_includes = []
    for include_name in sorted(python_module_include_names):
      include = '#include "{0:s}_{1:s}.h"'.format(
          project_configuration.python_module_name, include_name)
      python_module_includes.append(include)

    template_mappings['python_module_includes'] = '\n'.join(
        python_module_includes)

    if codepage_support:
      template_filename = 'includes_with_codepage.c'
    else:
      template_filename = 'includes.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if bfio_support:
      template_filename = os.path.join(template_directory, 'have_bfio.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    self._GenerateTypeSourceFileTypeObjectMethods(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    self._GenerateTypeSourceFileTypeObjectGetSetDefinitions(
        project_configuration, template_mappings, type_name,
        python_function_prototypes, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'type_object.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if not is_pseudo_type:
      if has_pseudo_sub_types:
        template_filename = os.path.join(
            template_directory, 'new-with_type_object.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

      elif with_parent:
        template_filename = os.path.join(
            template_directory, 'new-with_parent.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

      if bfio_support:
        template_filename = 'init-with_file_io_handle.c'
      elif with_parent and without_initialize_and_with_free:
        template_filename = 'init-with_parent.c'
      else:
        template_filename = 'init.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      if with_parent:
        template_filename = 'free_with_parent.c'
      else:
        template_filename = 'free.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    generate_get_value_type_object = False
    value_type_objects = set([])

    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      # TODO: use prefix in template?
      value_name, value_name_prefix = (
          python_function_prototype.GetValueNameAndPrefix())

      # TODO: add get_cache_directory template

      if type_function == 'get_format_version':
        self._SetValueTypeInTemplateMappings(
            template_mappings, python_function_prototype.value_type)

      template_filename = '{0:s}.c'.format(type_function)
      template_filename = os.path.join(template_directory, template_filename)
      if not os.path.exists(template_filename):
        template_filename = None

        # TODO: make more generic.
        if type_function == 'set_key':
          template_filename = 'set_key_with_mode.c'

        elif type_function == 'set_keys':
          template_filename = 'set_keys_with_mode.c'

        elif type_function == 'set_password':
          template_filename = 'set_{0:s}_value.c'.format('string')

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_COPY):
          template_filename = 'copy_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_COPY_FROM):
          template_filename = 'copy_from_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_COPY_TO):
          template_filename = 'copy_to_{0:s}_value.c'.format(
              python_function_prototype.data_type)

        elif python_function_prototype.function_type in (
            definitions.FUNCTION_TYPE_GET,
            definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
            definitions.FUNCTION_TYPE_GET_BY_INDEX,
            definitions.FUNCTION_TYPE_GET_BY_NAME,
            definitions.FUNCTION_TYPE_GET_BY_PATH):

          if value_name.startswith('recovered_'):
            value_name_prefix = 'recovered_'
            value_name = value_name[10:]

          elif value_name_prefix:
            value_name_prefix = '{0:s}_'.format(value_name_prefix)

          else:
            value_name_prefix = ''

          if python_function_prototype.function_type == (
              definitions.FUNCTION_TYPE_GET):
            if not python_function_prototype.arguments:
              if value_name.startswith('number_of_recovered_'):
                value_name = value_name[20:]
                template_filename = (
                    'get_number_of_recovered_{0:s}_value.c').format(
                        python_function_prototype.data_type)

              else:
                if (python_function_prototype.return_values and
                    'None' in python_function_prototype.return_values):
                  template_filename = 'get_{0:s}{1:s}_value-with_none.c'.format(
                      value_name_prefix, python_function_prototype.data_type)

                elif has_pseudo_sub_types:
                  template_filename = (
                      'get_{0:s}{1:s}_value-with_type_object.c').format(
                          value_name_prefix, python_function_prototype.data_type)

                else:
                  template_filename = 'get_{0:s}{1:s}_value.c'.format(
                      value_name_prefix, python_function_prototype.data_type)

          elif python_function_prototype.function_type == (
              definitions.FUNCTION_TYPE_GET_BY_INDEX):

            template_filename = 'get_{0:s}{1:s}_value_by_index.c'.format(
                value_name_prefix, python_function_prototype.data_type)

            if python_function_prototype.object_type:
              sequence_type_name = self._GetSequenceName(
                  python_function_prototype.object_type)
              self._SetSequenceTypeNameInTemplateMappings(
                  template_mappings, sequence_type_name)

            sequence_value_name = self._GetSequenceName(value_name)
            self._SetSequenceValueNameInTemplateMappings(
                template_mappings, sequence_value_name)

          elif python_function_prototype.function_type in (
              definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
              definitions.FUNCTION_TYPE_GET_BY_NAME,
              definitions.FUNCTION_TYPE_GET_BY_PATH):

            _, _, type_function_suffix = type_function.partition('_by_')

            template_filename = 'get_{0:s}{1:s}_value_by_{2:s}.c'.format(
                value_name_prefix, python_function_prototype.data_type,
                type_function_suffix)

          if python_function_prototype.data_type == (
              definitions.DATA_TYPE_OBJECT):
            if value_name_prefix != 'root_':
              value_name_prefix = ''

            if (has_pseudo_sub_types and
                python_function_prototype.value_type not in value_type_objects):
              generate_get_value_type_object = True
              value_type_objects.add(python_function_prototype.value_type)

          if python_function_prototype.object_type:
            self._SetValueTypeInTemplateMappings(
                template_mappings, python_function_prototype.object_type)

        elif python_function_prototype.function_type == (
            definitions.FUNCTION_TYPE_IS):
          template_filename = 'is_value.c'

        if template_filename:
          template_filename = os.path.join(
              template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            'Unable to generate Python type object source code for: '
            '{0:s}.{1:s} missing template: {2:s}').format(
                type_name, type_function, template_filename))
        continue

      self._SetValueNameInTemplateMappings(template_mappings, value_name)
      if python_function_prototype.value_description:
        value_description_long = python_function_prototype.value_description
        value_description, _, _ = value_description_long.partition('(')
        value_description = value_description.strip()
      else:
        value_description = ''
        value_description_long = ''

      template_mappings['value_description'] = value_description
      template_mappings['value_description_long'] = value_description_long

      if generate_get_value_type_object:
        search_string = (
            'PyTypeObject *{0:s}_{1:s}_get_{2:s}_type_object(').format(
                project_configuration.python_module_name, type_name,
                value_name)

        result = self._CopyFunctionToOutputFile(
            lines, search_string, output_filename)

        if not result:
          additional_template_filename = 'get_value_type_object.c'
          additional_template_filename = os.path.join(
              template_directory, additional_template_filename)
          self._GenerateSection(
              additional_template_filename, template_mappings, output_writer,
              output_filename, access_mode='a')

        generate_get_value_type_object = False

      result = False
      if type_function in (
          'get_data_as_datetime', 'get_data_as_floating_point',
          'get_data_as_integer'):
        search_string = (
            'PyObject *{0:s}_{1:s}_{2:s}(').format(
                project_configuration.python_module_name, type_name,
                type_function)

        result = self._CopyFunctionToOutputFile(
            lines, search_string, output_filename)

      if not result:
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='a')

    # TODO: change to a generic line modifiers approach.
    self._CorrectDescriptionSpelling(type_name, output_filename)

    self._FormatSourceFile(project_configuration, output_filename)

  def _GenerateTypeSourceFileTypeObjectMethods(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, output_filename):
    """Generates the type object methods for a Python type source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'pyyal_type')

    python_type_object_methods = []
    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if type_function in ('free', 'initialize'):
        continue

      if not python_function_prototype.arguments:
        arguments_flags = 'METH_NOARGS'
      else:
        arguments_flags = 'METH_VARARGS | METH_KEYWORDS'

      arguments_string = ', '.join([
          argument.lstrip('*')
          for argument in python_function_prototype.arguments])
      data_type = python_function_prototype.GetDataTypeDescription()

      if type_function == 'copy_from_byte_stream':
        python_type_object_method = [
            '',
            '\t{{ "{0:s}",'.format(type_function),
            '\t  (PyCFunction) {0:s},'.format(python_function_prototype.name),
            '\t  {0:s},'.format(arguments_flags),
            '\t  "{0:s}({1:s})\\n"'.format(type_function, arguments_string),
            '\t  "\\n"']
      else:
        python_type_object_method = [
            '',
            '\t{{ "{0:s}",'.format(type_function),
            '\t  (PyCFunction) {0:s},'.format(python_function_prototype.name),
            '\t  {0:s},'.format(arguments_flags),
            '\t  "{0:s}({1:s}) -> {2:s}\\n"'.format(
                type_function, arguments_string, data_type),
            '\t  "\\n"']

      python_type_object_methods.extend(python_type_object_method)

      description = python_function_prototype.GetDescription()
      for index, line in enumerate(description):
        # Correct xml => XML in description for pyevtx.
        line = line.replace(' xml ', ' XML ')

        if index < len(description) - 1:
          python_type_object_methods.append('\t  "{0:s}\\n"'.format(line))
        else:
          python_type_object_methods.append('\t  "{0:s}" }},'.format(line))

      if (type_function == 'get_offset' and
          'read_buffer' in python_function_prototypes and
          'seek_offset' in python_function_prototypes):

        read_buffer_description = (
            python_function_prototypes['read_buffer'].GetDescription())
        seek_offset_description = (
            python_function_prototypes['seek_offset'].GetDescription())

        python_type_object_methods.extend([
            '',
            '\t{ "read",',
            '\t  (PyCFunction) {0:s}_{1:s}_read_buffer,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_VARARGS | METH_KEYWORDS,',
            '\t  "read(size) -> Binary string\\n"',
            '\t  "\\n"',
            '\t  "{0:s}." }},'.format(read_buffer_description[0][:-1]),
            '',
            '\t{ "seek",',
            '\t  (PyCFunction) {0:s}_{1:s}_seek_offset,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_VARARGS | METH_KEYWORDS,',
            '\t  "seek(offset, whence) -> None\\n"',
            '\t  "\\n"',
            '\t  "{0:s}." }},'.format(seek_offset_description[0][:-1]),
            '',
            '\t{ "tell",',
            '\t  (PyCFunction) {0:s}_{1:s}_get_offset,'.format(
                project_configuration.python_module_name, type_name),
            '\t  METH_NOARGS,',
            '\t  "tell() -> Integer\\n"',
            '\t  "\\n"',
            '\t  "{0:s}." }},'.format(description[0][:-1])])

      elif (python_function_prototype.DataTypeIsDatetime() and
            type_function != 'get_data_as_datetime'):
        python_type_object_methods.extend([
            '',
            '\t{{ "{0:s}_as_integer",'.format(type_function),
            '\t  (PyCFunction) {0:s}_as_integer,'.format(
                python_function_prototype.name),
            '\t  METH_NOARGS,',
            '\t  "{0:s}_as_integer({1:s}) -> Integer or None\\n"'.format(
                type_function, arguments_string),
            '\t  "\\n"'])

        if python_function_prototype.data_type == (
            definitions.DATA_TYPE_FAT_DATE_TIME):
          description[0] = (
              '{0:s} as a 32-bit integer containing a FAT date time '
              'value.').format(description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_FILETIME):
          description[0] = (
              '{0:s} as a 64-bit integer containing a FILETIME value.').format(
                  description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_FLOATINGTIME):
          description[0] = (
              '{0:s} as a 64-bit integer containing a floatingtime '
              'value.').format(description[0][:-1])

        elif python_function_prototype.data_type == (
            definitions.DATA_TYPE_POSIX_TIME):
          description[0] = (
              '{0:s} as a 32-bit integer containing a POSIX timestamp '
              'value.').format(description[0][:-1])

        for index, line in enumerate(description):
          if index < len(description) - 1:
            python_type_object_methods.append('\t  "{0:s}\\n"'.format(line))
          else:
            python_type_object_methods.append('\t  "{0:s}" }},'.format(line))

      elif (python_function_prototype.arguments and
            python_function_prototype.data_type in (
                definitions.DATA_TYPE_OBJECT,
                definitions.DATA_TYPE_STRING)):
          # TODO: add method for the sequence object.
        pass

    python_type_object_methods.extend([
        '',
        '\t/* Sentinel */',
        '\t{ NULL, NULL, 0, NULL }'])

    template_mappings['python_type_object_methods'] = '\n'.join(
        python_type_object_methods)

    template_filename = os.path.join(
        template_directory, 'type_object_methods.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GenerateTypeSourceFileTypeObjectGetSetDefinitions(
      self, project_configuration, template_mappings, type_name,
      python_function_prototypes, output_writer, output_filename):
    """Generates the type object definitions for a Python type source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      python_function_prototypes
          (dict[str, PythonTypeObjectFunctionPrototype]): Python type object
          function prototypes per name.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'pyyal_type')

    python_type_object_get_set_definitions = []
    for type_function, python_function_prototype in iter(
        python_function_prototypes.items()):

      if python_function_prototype.function_type not in (
          definitions.FUNCTION_TYPE_COPY,
          definitions.FUNCTION_TYPE_COPY_TO,
          definitions.FUNCTION_TYPE_GET,
          definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
          definitions.FUNCTION_TYPE_GET_BY_INDEX,
          definitions.FUNCTION_TYPE_GET_BY_NAME,
          definitions.FUNCTION_TYPE_GET_BY_PATH):
        continue

      if (type_function.endswith('_by_name') or
          type_function.endswith('_by_path')):
        continue

      if (type_function == 'get_offset' and
          'read_buffer' in python_function_prototypes and
          'seek_offset' in python_function_prototypes):
        continue

      if type_function != 'get_ascii_codepage':
        setter_function = '0'
      else:
        setter_function = (
            '{0:s}_{1:s}_set_ascii_codepage_setter').format(
                project_configuration.python_module_name, type_name)

      description = python_function_prototype.GetAttributeDescription()

      # Correct xml => XML in description for pyevtx.
      description = description.replace(' xml ', ' XML ')

      # TODO: fix libcreg getter name keies instead of keys.

      if not python_function_prototype.arguments:
        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(type_function[4:]),
            '\t  (getter) {0:s},'.format(python_function_prototype.name),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}",'.format(description),
            '\t  NULL },'])

      if (python_function_prototype.arguments and
          python_function_prototype.data_type in (
              definitions.DATA_TYPE_OBJECT,
              definitions.DATA_TYPE_STRING)):

        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(sequence_type_function),
            '\t  (getter) {0:s},'.format(sequence_type_getter),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}.",'.format(sequence_type_description),
            '\t  NULL },'])

      if type_function == 'get_cache_directory':
        sequence_type_function = self._GetSequenceName(type_function[4:])
        sequence_type_getter = self._GetSequenceName(
            python_function_prototype.name)
        sequence_type_description = self._GetSequenceName(description[:-1])

        python_type_object_get_set_definitions.extend([
            '',
            '\t{{ "{0:s}",'.format(sequence_type_function),
            '\t  (getter) {0:s},'.format(sequence_type_getter),
            '\t  (setter) {0:s},'.format(setter_function),
            '\t  "{0:s}.",'.format(sequence_type_description),
            '\t  NULL },'])

    python_type_object_get_set_definitions.extend([
        '',
        '\t/* Sentinel */',
        '\t{ NULL, NULL, NULL, NULL, NULL }'])

    template_mappings['python_type_object_get_set_definitions'] = '\n'.join(
        python_type_object_get_set_definitions)

    template_filename = os.path.join(
        template_directory, 'type_object_get_set_definitions.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GetPythonTypeObjectFunctionPrototype(
      self, project_configuration, type_name, type_function, function_prototype,
      is_pseudo_type=False):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): type name.
      type_function (str): type function.
      function_prototype (FunctionPrototype): C function prototype.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.

    Returns:
      PythonTypeObjectFunctionPrototype: Python type object function prototype
          or None.
    """
    if len(function_prototype.arguments) < 2:
      logging.warning('Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return None

    if type_function in ('free', 'initialize'):
      self_argument = '{0:s}_{1:s}_t **{1:s}'.format(
          project_configuration.library_name, type_name)

    elif is_pseudo_type:
      base_type_name = 'item'
      self_argument = '{0:s}_{1:s}_t *{2:s}'.format(
          project_configuration.library_name, base_type_name, type_name)

    else:
      self_argument = '{0:s}_{1:s}_t *{1:s}'.format(
          project_configuration.library_name, type_name)

    function_argument = function_prototype.arguments[0]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != self_argument:
      logging.warning((
          'Unsupported function prototype: {0:s} - unsupported self '
          'argument: {1:s}').format(
              function_prototype.name, function_argument_string))
      return None

    function_argument = function_prototype.arguments[-1]
    function_argument_string = function_argument.CopyToString()
    if function_argument_string != 'libcerror_error_t **error':
      logging.warning('Unsupported function prototype: {0:s}'.format(
          function_prototype.name))
      return None

    # TODO: add support for glob functions
    # TODO: add support for has, is functions

    arguments = []
    function_type = None
    python_type_function = type_function
    object_type = None
    data_type = definitions.DATA_TYPE_NONE
    return_values = None
    value_description = function_prototype.value_description
    value_type = None

    # TODO: add override for
    # if (type_function == 'copy_link_target_identifier_data' and
    #    project_configuration.library_name == 'liblnk'):

    if type_function == 'get_string_size':
      return None

    if (type_function == 'get_cache_directory_name' and
        project_configuration.library_name == 'libmsiecf'):
      type_function = 'get_cache_directory'

      arguments = ['cache_directory_index']
      function_type = definitions.FUNCTION_TYPE_GET_BY_INDEX
      data_type = definitions.DATA_TYPE_NARROW_STRING

    elif type_function == 'close':
      function_type = definitions.FUNCTION_TYPE_CLOSE

    elif type_function.startswith('copy_from'):
      function_type = definitions.FUNCTION_TYPE_COPY_FROM

      value_argument_index = 1

      function_argument = function_prototype.arguments[value_argument_index]
      value_argument_string = function_argument.CopyToString()

      _, _, argument_name = value_argument_string.rpartition(' ')
      argument_name.lstrip('*')
      arguments.append(argument_name)

      function_argument = function_prototype.arguments[
          value_argument_index + 1]
      value_size_argument_string = function_argument.CopyToString()

      if (value_argument_string == 'const uint8_t *byte_stream' and
          value_size_argument_string == 'size_t byte_stream_size'):
        data_type = definitions.DATA_TYPE_BINARY_DATA

      elif (value_argument_string == 'const uint8_t *data' and
            value_size_argument_string == 'size_t data_size'):
        data_type = definitions.DATA_TYPE_BINARY_DATA

    elif type_function.startswith('copy_to_utf'):
      if 'utf16' in type_function or 'utf32' in type_function:
        return None

      function_type = definitions.FUNCTION_TYPE_COPY_TO
      python_type_function = 'get_string'
      data_type = definitions.DATA_TYPE_STRING
      value_description = 'string'

    elif type_function.startswith('copy_'):
      function_type = definitions.FUNCTION_TYPE_COPY
      data_type = definitions.DATA_TYPE_BINARY_DATA

    elif type_function == 'free':
      function_type = definitions.FUNCTION_TYPE_FREE

    elif type_function.startswith('get_'):
      function_type = definitions.FUNCTION_TYPE_GET

      if type_function == 'get_ascii_codepage':
        # TODO: replace this by definitions.DATA_TYPE_NARROW_STRING ?
        data_type = 'String'

      elif type_function == 'get_format_version':
        function_argument = function_prototype.arguments[1]
        value_argument_string = function_argument.CopyToString()

        data_type = definitions.DATA_TYPE_STRING
        value_type, _, _ = value_argument_string.partition(' ')

      else:
        type_function_prefix, _, type_function_suffix = (
            type_function.partition('_by_'))

        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, value_argument_suffix = value_argument_string.rpartition('_')

        # Not all get_by_index functions have the suffix _by_index so we need
        # to detect them based on the function arguments.
        if (value_argument_string.startswith('int ') and
            value_argument_suffix in ('entry', 'index')):
          function_type = definitions.FUNCTION_TYPE_GET_BY_INDEX

          _, _, argument_name = value_argument_string.rpartition(' ')

          arguments.append(argument_name)
          value_argument_index = 2

        elif type_function_suffix == 'identifier':
          function_type = definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER

          arguments.append(type_function_suffix)
          value_argument_index = 2

        elif type_function_suffix in ('utf8_name', 'utf8_path'):
          type_function_suffix = type_function_suffix[5:]

          if value_argument_string != 'const uint8_t *utf8_string':
            logging.warning('Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return None

          function_argument = function_prototype.arguments[2]
          function_argument_string = function_argument.CopyToString()

          if function_argument_string != 'size_t utf8_string_length':
            logging.warning('Unsupported function prototype: {0:s}'.format(
                function_prototype.name))
            return None

          if type_function_suffix == 'name':
            function_type = definitions.FUNCTION_TYPE_GET_BY_NAME
          else:
            function_type = definitions.FUNCTION_TYPE_GET_BY_PATH

          arguments.append(type_function_suffix)
          value_argument_index = 3

        if value_argument_index != 1:
          function_argument = function_prototype.arguments[value_argument_index]
          value_argument_string = function_argument.CopyToString()

        if value_argument_index + 1 < len(function_prototype.arguments):
          function_argument = function_prototype.arguments[
              value_argument_index + 1]
          value_size_argument_string = function_argument.CopyToString()

          if value_argument_string == 'uint64_t *filetime':
            data_type = definitions.DATA_TYPE_FILETIME

          elif value_argument_string == 'uint64_t *floatingtime':
            data_type = definitions.DATA_TYPE_FLOATINGTIME

          elif value_argument_string == 'uint32_t *fat_date_time':
            data_type = definitions.DATA_TYPE_FAT_DATE_TIME

          elif value_argument_string == 'uint32_t *hfs_time':
            data_type = definitions.DATA_TYPE_HFS_TIME

          elif value_argument_string == 'uint32_t *posix_time':
            data_type = definitions.DATA_TYPE_POSIX_TIME

          elif (value_argument_string == 'uint8_t *data' and
                value_size_argument_string == 'size_t data_size'):
            data_type = definitions.DATA_TYPE_BINARY_DATA

          elif (value_argument_string == 'uint8_t *guid_data' and
                value_size_argument_string == 'size_t guid_data_size'):
            data_type = definitions.DATA_TYPE_GUID

          elif (value_argument_string == 'uint8_t *utf8_string' and
                value_size_argument_string == 'size_t utf8_string_size'):
            data_type = definitions.DATA_TYPE_STRING

          elif (value_argument_string == 'uint8_t *uuid_data' and
                value_size_argument_string == 'size_t uuid_data_size'):
            data_type = definitions.DATA_TYPE_UUID

          elif (value_argument_string == 'char *string' and
                value_size_argument_string == 'size_t string_size'):
            data_type = definitions.DATA_TYPE_NARROW_STRING

          elif value_argument_string.startswith('double *'):
            data_type = definitions.DATA_TYPE_DOUBLE

          elif value_argument_string.startswith('float *'):
            data_type = definitions.DATA_TYPE_FLOAT

          elif value_argument_string.startswith('int *'):
            data_type = definitions.DATA_TYPE_INT

          elif value_argument_string.startswith('int32_t *'):
            data_type = definitions.DATA_TYPE_INT32

          elif value_argument_string.startswith('off64_t *'):
            data_type = definitions.DATA_TYPE_OFF64

          elif value_argument_string.startswith('size32_t *'):
            data_type = definitions.DATA_TYPE_SIZE32

          elif value_argument_string.startswith('size64_t *'):
            data_type = definitions.DATA_TYPE_SIZE64

          elif value_argument_string.startswith('uint8_t *'):
            data_type = definitions.DATA_TYPE_UINT8

          elif value_argument_string.startswith('uint16_t *'):
            data_type = definitions.DATA_TYPE_UINT16

          elif value_argument_string.startswith('uint32_t *'):
            data_type = definitions.DATA_TYPE_UINT32

          elif value_argument_string.startswith('uint64_t *'):
            data_type = definitions.DATA_TYPE_UINT64

          elif value_argument_string.startswith(
              project_configuration.library_name):
            data_type = definitions.DATA_TYPE_OBJECT

            object_type, _, _ = value_argument_string.partition(' ')
            _, _, object_type = object_type.partition('_')
            object_type = object_type[:-2]

    elif type_function == 'initialize':
      function_type = definitions.FUNCTION_TYPE_INITIALIZE

    elif type_function.startswith('is_'):
      function_type = definitions.FUNCTION_TYPE_IS
      data_type = definitions.DATA_TYPE_BOOLEAN

    elif type_function == 'open' or type_function.startswith('open_'):
      function_type = definitions.FUNCTION_TYPE_OPEN

      if type_function == 'open':
        arguments = ['filename', 'mode=\'r\'']

      elif type_function == 'open_file_io_handle':
        python_type_function = 'open_file_object'
        arguments = ['file_object', 'mode=\'r\'']

    elif type_function.startswith('read_'):
      function_type = definitions.FUNCTION_TYPE_READ

      if type_function == 'read_buffer':
        data_type = definitions.DATA_TYPE_BINARY_DATA
        arguments = ['size']

      elif type_function == 'read_buffer_at_offset':
        data_type = definitions.DATA_TYPE_BINARY_DATA
        arguments = ['size', 'offset']

    elif type_function.startswith('seek_'):
      function_type = definitions.FUNCTION_TYPE_SEEK

      if type_function == 'seek_offset':
        arguments = ['offset', 'whence']

    elif type_function.startswith('set_'):
      function_type = definitions.FUNCTION_TYPE_SET

      # TODO: make more generic.
      if type_function == 'set_ascii_codepage':
        arguments = ['codepage']

      elif type_function == 'set_parent_file':
        arguments = ['parent_file']

      elif type_function == 'set_key':
        arguments = ['mode', 'key']

      elif type_function == 'set_keys':
        arguments = ['mode', 'key', 'tweak_key']

      elif type_function in (
          'set_password', 'set_recovery_password',
          'set_utf8_password', 'set_utf8_recovery_password'):
        arguments = ['password']

      else:
        value_argument_index = 1

        function_argument = function_prototype.arguments[value_argument_index]
        value_argument_string = function_argument.CopyToString()

        _, _, argument_name = value_argument_string.rpartition(' ')
        argument_name.lstrip('*')
        arguments.append(argument_name)

        function_argument = function_prototype.arguments[
            value_argument_index + 1]
        value_size_argument_string = function_argument.CopyToString()

        if (value_argument_string == 'uint8_t *data' and
            value_size_argument_string == 'size_t data_size'):
          data_type = definitions.DATA_TYPE_BINARY_DATA

        elif (value_argument_string == 'uint8_t *utf8_string' and
              value_size_argument_string == 'size_t utf8_string_size'):
          data_type = definitions.DATA_TYPE_STRING

        elif (value_argument_string == 'char *string' and
              value_size_argument_string == 'size_t string_size'):
          data_type = definitions.DATA_TYPE_NARROW_STRING

        elif value_argument_string.startswith(
            project_configuration.library_name):
          data_type = definitions.DATA_TYPE_OBJECT

          object_type, _, _ = value_argument_string.partition(' ')
          _, _, object_type = object_type.partition('_')
          object_type = object_type[:-2]

    elif type_function == 'signal_abort':
      function_type = definitions.FUNCTION_TYPE_UTILITY

    # elif type_function.startswith('write_'):
    #   function_type = definitions.FUNCTION_TYPE_WRITE

    if function_prototype.return_values:
      return_values = set()
      if ('0' in function_prototype.return_values or
          'NULL' in function_prototype.return_values):
        return_values.add('None')

    python_function_prototype = source_code.PythonTypeObjectFunctionPrototype(
        project_configuration.python_module_name, type_name,
        python_type_function)

    python_function_prototype.arguments = arguments
    python_function_prototype.data_type = data_type
    python_function_prototype.function_type = function_type
    python_function_prototype.object_type = object_type
    python_function_prototype.return_values = return_values
    python_function_prototype.value_description = value_description
    python_function_prototype.value_type = value_type

    return python_function_prototype

  def _GetPythonTypeObjectFunctionPrototypes(
      self, project_configuration, type_name, is_pseudo_type=False):
    """Determines the Python type object function prototypes.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      is_pseudo_type (Optional[bool]): True if type is a pseudo type.

    Returns:
      dict[str, PythonTypeObjectFunctionPrototype]: Python type object
          function prototypes per name.
    """
    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)
    if not header_file:
      return

    function_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    functions_per_name = header_file.functions_per_name

    python_function_prototypes = collections.OrderedDict()
    for function_name, function_prototype in iter(functions_per_name.items()):
      if not function_prototype.have_extern:
        continue

      if not function_name.startswith(function_name_prefix):
        logging.warning('Skipping unsupported API function: {0:s}'.format(
            function_name))
        continue

      type_function = function_name[function_name_prefix_length:]
      # Skip functions that are a wide character variant of another function.
      if type_function.endswith('_wide'):
        continue

      # Skip functions that retrieves the size of binary data.
      if (type_function.startswith('get_') and
          type_function.endswith('_data_size')):
        continue

      # Skip functions that retrieve the size of an UTF-8 string.
      if (type_function.startswith('get_utf8_') and
          type_function.endswith('_size')):
        continue

      if (type_function.startswith('get_') and
          type_function.endswith('_utf8_string_size')):
        continue

      # Skip functions that are a UTF-16 variant of another function.
      if (type_function.startswith('get_utf16_') or
          type_function.startswith('set_utf16_') or
          (type_function.startswith('get_') and (
              type_function.endswith('_by_utf16_name') or
              type_function.endswith('_by_utf16_path') or
              type_function.endswith('_utf16_string') or
              type_function.endswith('_utf16_string_size')))):
        continue

      # TODO: ignore these functions for now.
      if (type_function == 'get_flags' and
          project_configuration.library_name not in (
              'libfwnt', )):
        continue

      # TODO: improve check only to apply for types with pseudo types.
      if (type_function == 'get_type' and
          project_configuration.library_name in (
              'libmsiecf', 'libolecf', 'libpff')):
        continue

      # TODO: remove when removed after deprecation.
      if (type_function.startswith('get_value_') and
          type_function != 'get_value_type' and
          project_configuration.library_name in (
              'libolecf', )):
        continue

      if (type_function == 'get_version' and
          project_configuration.library_name in (
              'libevt', 'libevtx')):
        continue

      if (type_function.startswith('write_buffer') and
          project_configuration.library_name not in (
              'libewf', )):
        continue

      if type_function in (
          'get_offset_range', 'get_number_of_unallocated_blocks',
          'get_unallocated_block'):
        continue

      python_function_prototype = self._GetPythonTypeObjectFunctionPrototype(
          project_configuration, type_name, type_function, function_prototype,
          is_pseudo_type=is_pseudo_type)

      if (not python_function_prototype or
          not python_function_prototype.function_type):
        logging.warning('Skipping unsupported type function: {0:s}'.format(
            function_name))
        continue

      # TODO: Skip functions that retrieve the size of a narrow string.

      type_function = python_function_prototype.type_function
      python_function_prototypes[type_function] = python_function_prototype

    return python_function_prototypes

  def _GetSequenceName(self, name):
    """Determines the sequence type or value name.

    Args:
      name (str): name of type or value.

    Returns:
      str: sequence type or value name.
    """
    if name == 'key':
      return '{0:s}s'.format(name)

    if (name[-1] in ('s', 'x', 'z') or (
        name[-1] == 'h'  and name[-2] in ('c', 's'))):
      return '{0:s}es'.format(name)

    if name[-1] == 'y':
      return '{0:s}ies'.format(name[:-1])

    return '{0:s}s'.format(name)

  def _GetSequenceType(self, python_function_prototype):
    """Determines if the function prototype implies a sequence type.

    Args:
      python_function_prototype (PythonTypeObjectFunctionPrototype): Python
          type object function prototype.

    Returns:
      tuple: contains:
        str: sequence type name or None.
        bool: True if the sequence type is an object type or None.
    """
    if not python_function_prototype.arguments:
      return None, None

    if python_function_prototype.function_type not in (
        definitions.FUNCTION_TYPE_GET,
        definitions.FUNCTION_TYPE_GET_BY_IDENTIFIER,
        definitions.FUNCTION_TYPE_GET_BY_INDEX,
        definitions.FUNCTION_TYPE_GET_BY_NAME,
        definitions.FUNCTION_TYPE_GET_BY_PATH):
      return None, None

    if python_function_prototype.data_type == definitions.DATA_TYPE_OBJECT:
      return python_function_prototype.object_type, True

    if python_function_prototype.data_type == definitions.DATA_TYPE_STRING:
      return python_function_prototype.value_name, False

    return None, None

  def _GetTemplateMappings(self, project_configuration):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = super(
        PythonModuleSourceFileGenerator, self)._GetTemplateMappings(
            project_configuration,
            authors_separator=',\n *                          ')

    # TODO: have source formatter take care of the alignment.
    # Used to align source in pyyal/pyyal_file_object_io_handle.c
    alignment_padding = len(project_configuration.library_name) - 6
    template_mappings['alignment_padding'] = ' ' * alignment_padding

    return template_mappings

  def Generate(self, project_configuration, output_writer):
    """Generates Python module source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: pycaes add support for object without parent and file_io_handle
    # TODO: add tests configuration e.g. test data, libfwnt or use in-line
    # generator hints
    # TODO: add support for get_object_by_type
    # TODO: add support for get_object_by_identifier
    # TODO: add support for copy from
    # TODO: add support for definitions without "definition prefix"
    # TODO: add support for pyolecf_property_value
    # TODO: sequence object rename ${type_name}_index to item_index
    # TODO: generate non type files.
    # TODO: generate pyyal/Makefile.am
    # TODO: generate pyyal-python2/Makefile.am
    # TODO: generate pyyal-python3/Makefile.am

    if not project_configuration.HasPythonModule():
      return

    template_mappings = self._GetTemplateMappings(project_configuration)

    if project_configuration.python_module_name == 'pyluksde':
      template_mappings['guid_byte_order'] = 'BIG'
    else:
      template_mappings['guid_byte_order'] = 'LITTLE'

    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith('pyyal_'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      force_create = False

      if directory_entry == 'pyyal_libyal.h':
        output_filename = '{0:s}_{1:s}.h'.format(
            project_configuration.python_module_name,
            project_configuration.library_name)

      else:
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.python_module_name, directory_entry[6:])

      output_filename = os.path.join(
          project_configuration.python_module_name, output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if directory_entry == 'pyyal_file_object_io_handle.c':
        self._SortVariableDeclarations(output_filename)

    del template_mappings['guid_byte_order']

    library_include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    python_module_types = []

    if not library_include_header_file:
      logging.warning((
          'Missing: {0:s} skipping generation of Python type object '
          'source and header files.').format(
              self._library_include_header_path))
    else:
      api_types, api_types_with_input = (
          library_include_header_file.GetAPITypeTestGroups())

      api_pseudo_types = (
          library_include_header_file.GetAPIPseudoTypeTestGroups())

      api_types.extend(api_types_with_input)
      python_module_types.extend(api_types)
      api_types.extend(api_pseudo_types)

      types_with_sequence_types = set([])

      for type_name in api_types:
        self._SetTypeNameInTemplateMappings(template_mappings, type_name)

        is_pseudo_type = type_name in api_pseudo_types

        python_function_prototypes = (
            self._GetPythonTypeObjectFunctionPrototypes(
                project_configuration, type_name,
                is_pseudo_type=is_pseudo_type))

        if not python_function_prototypes:
          logging.warning((
              'Missing function prototypes for type: {0:s} skipping '
              'generation of Python type object source and header '
              'files.').format(type_name))
          continue

        for type_function, python_function_prototype in iter(
            python_function_prototypes.items()):

          sequence_type_name, type_is_object = self._GetSequenceType(
              python_function_prototype)
          if sequence_type_name:
            types_with_sequence_types.add((sequence_type_name, type_is_object))

        # TODO: determine value based on actual code.
        has_pseudo_sub_types = type_name == 'item' and api_pseudo_types

        self._GenerateTypeSourceFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer,
            has_pseudo_sub_types=has_pseudo_sub_types,
            is_pseudo_type=is_pseudo_type)

        self._GenerateTypeHeaderFile(
            project_configuration, template_mappings, type_name,
            python_function_prototypes, output_writer,
            has_pseudo_sub_types=has_pseudo_sub_types,
            is_pseudo_type=is_pseudo_type)

      for sequence_type_name, type_is_object in types_with_sequence_types:
        self._SetTypeNameInTemplateMappings(
            template_mappings, sequence_type_name)

        self._GenerateSequenceTypeSourceFile(
            project_configuration, template_mappings, sequence_type_name,
            output_writer, type_is_object=type_is_object)

        self._GenerateSequenceTypeHeaderFile(
            project_configuration, template_mappings, sequence_type_name,
            output_writer)

        module_type_name = self._GetSequenceName(sequence_type_name)
        python_module_types.append(module_type_name)

    definition_types = []

    definitions_include_header_file = self._GetDefinitionsIncludeHeaderFile(
        project_configuration)

    if not definitions_include_header_file:
      logging.warning((
          'Missing: {0:s} skipping generation of Python definitions object '
          'source and header files.').format(
              self._definitions_include_header_path))
    else:
      definitions_name_prefix = '{0:s}_'.format(
          project_configuration.library_name)
      definitions_name_prefix_length = len(definitions_name_prefix)

      for enum_declaration in definitions_include_header_file.enum_declarations:
        definitions_name = enum_declaration.name.lower()
        if not definitions_name.startswith(definitions_name_prefix):
          continue

        # TODO: skip flags definitions
        definitions_name = definitions_name[definitions_name_prefix_length:]
        if definitions_name in ('access_flags', 'endian'):
          continue

        self._GenerateDefinitionsSourceFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)

        self._GenerateDefinitionsHeaderFile(
            project_configuration, template_mappings, definitions_name,
            enum_declaration, output_writer)

        definition_types.append(definitions_name)

    python_module_types.extend(definition_types)

    self._GenerateModuleHeaderFile(
        project_configuration, template_mappings, library_include_header_file,
        output_writer)

    self._GenerateModuleSourceFile(
        project_configuration, template_mappings, library_include_header_file,
        python_module_types, definition_types, output_writer)
