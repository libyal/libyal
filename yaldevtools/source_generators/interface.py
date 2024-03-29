# -*- coding: utf-8 -*-
"""The source file generator interface."""

import abc
import datetime
import logging
import os
import string
import time

from yaldevtools import source_file
from yaldevtools import source_formatter


class SourceFileGenerator(object):
  """Source file generator."""

  def __init__(
      self, projects_directory, data_directory, template_directory,
      experimental=False):
    """Initializes a source file generator.

    Args:
      projects_directory (str): path of the projects directory.
      data_directory (str): path of the data directory.
      template_directory (str): path of the template directory.
      experimental (bool): True if experimental features should be enabled.
    """
    super(SourceFileGenerator, self).__init__()
    self._data_directory = data_directory
    self._definitions_include_header_file = None
    self._definitions_include_header_path = None
    self._experimental = experimental
    self._has_tests = None
    self._library_include_header_file = None
    self._library_include_header_path = None
    self._library_makefile_am_file = None
    self._library_makefile_am_path = None
    self._library_path = None
    self._library_type_header_files = {}
    self._projects_directory = projects_directory
    self._python_module_path = None
    self._template_directory = template_directory
    self._tests_path = None
    self._tools_path = None
    self._types_include_header_file = None
    self._types_include_header_path = None

  def _CorrectDescriptionSpelling(self, name, output_filename):
    """Corrects the spelling of a type or value decription.

    Args:
      name (str): type or value name.
      output_filename (str): path of the output file.
    """
    if not name or name[0] not in ('a', 'e', 'i', 'o', ''):
      return

    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    name = name.replace('_', ' ')
    description = ' a {0:s}'.format(name)
    corrected_description = ' an {0:s}'.format(name)

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        line = line.replace(description, corrected_description)
        file_object.write(line)

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer,
      output_filename, access_mode='w'):
    """Generates a section from template filename.

    Args:
      template_filename (str): name of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    template_string = self._ReadTemplateFile(template_filename)
    try:
      output_data = template_string.substitute(template_mappings)
    except (KeyError, ValueError) as exception:
      logging.error(
          'Unable to format template: {0:s} with error: {1!s}'.format(
              template_filename, exception))
      return

    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)

  def _GenerateSections(
      self, template_filenames, template_mappings, output_writer,
      output_filename, access_mode='w'):
    """Generates a section from template filenames.

    Args:
      template_filenames (list[str])): names of the template files.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    for template_filename in template_filenames:
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode=access_mode)
      access_mode = 'a'

  def _GetDefinitionsIncludeHeaderFile(self, project_configuration):
    """Retrieves the definitions include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      DefinitionsIncludeHeaderFile: definitions include header file or None if
          the definitions include header file cannot be found.
    """
    if not self._definitions_include_header_file:
      self._definitions_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', project_configuration.library_name, 'definitions.h.in')

      if os.path.exists(self._definitions_include_header_path):
        self._definitions_include_header_file = (
            source_file.DefinitionsIncludeHeaderFile(
                self._definitions_include_header_path))
        self._definitions_include_header_file.Read(project_configuration)

    return self._definitions_include_header_file

  def _GetLibraryIncludeHeaderFile(self, project_configuration):
    """Retrieves the library include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      LibraryIncludeHeaderFile: library include header file or None if
          the library include header file cannot be found.
    """
    if not self._library_include_header_file:
      self._library_include_header_path = '{0:s}.h.in'.format(
          project_configuration.library_name)
      self._library_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', self._library_include_header_path)

      if os.path.exists(self._library_include_header_path):
        self._library_include_header_file = (
            source_file.LibraryIncludeHeaderFile(
                self._library_include_header_path))
        self._library_include_header_file.Read(project_configuration)

    return self._library_include_header_file

  def _GetLibraryMakefileAM(self, project_configuration):
    """Retrieves the library Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      LibraryMakefileAMFile: library Makefile.am file or None if
          the library Makefile.am file cannot be found.
    """
    if not self._library_makefile_am_file:
      self._library_makefile_am_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          project_configuration.library_name, 'Makefile.am')

      if os.path.exists(self._library_makefile_am_path):
        self._library_makefile_am_file = source_file.LibraryMakefileAMFile(
            self._library_makefile_am_path)
        self._library_makefile_am_file.Read(project_configuration)

    return self._library_makefile_am_file

  def _GetMainMakefileAM(self, project_configuration):
    """Retrieves the main Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      MainMakefileAMFile: main Makefile.am file or None if the main
          Makefile.am file cannot be found.
    """
    # TODO: cache MainMakefileAMFile object and makefile_am_path
    makefile_am_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        'Makefile.am')

    makefile_am_file = source_file.MainMakefileAMFile(makefile_am_path)
    makefile_am_file.Read(project_configuration)

    return makefile_am_file

  def _GetTemplateMappings(self, project_configuration, authors_separator=', '):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      authors_separator (Optional[str]): authors separator.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.

    Raises:
      ValueError: if the year of creation value is out of bounds.
    """
    date = datetime.date.today()
    if project_configuration.project_year_of_creation > date.year:
      raise ValueError('Year of creation value out of bounds.')

    if project_configuration.project_year_of_creation == date.year:
      project_copyright = '{0:d}'.format(
          project_configuration.project_year_of_creation)
    else:
      project_copyright = '{0:d}-{1:d}'.format(
          project_configuration.project_year_of_creation, date.year)

    if project_configuration.python_module_year_of_creation == date.year:
      python_module_copyright = '{0:d}'.format(
          project_configuration.python_module_year_of_creation)
    else:
      python_module_copyright = '{0:d}-{1:d}'.format(
          project_configuration.python_module_year_of_creation, date.year)

    authors = authors_separator.join(project_configuration.project_authors)
    python_module_authors = authors_separator.join(
        project_configuration.python_module_authors)
    tools_authors = authors_separator.join(project_configuration.tools_authors)
    tests_authors = authors_separator.join(project_configuration.tests_authors)

    library_description_lower_case = '{0:s}{1:s}'.format(
        project_configuration.library_description[0].lower(),
        project_configuration.library_description[1:])

    library_version = time.strftime('%Y%m%d', time.gmtime())

    template_mappings = {
        'authors': authors,
        'copyright': project_copyright,

        'library_name': project_configuration.library_name,
        'library_name_upper_case': project_configuration.library_name.upper(),
        'library_name_suffix': project_configuration.library_name_suffix,
        'library_name_suffix_upper_case': (
            project_configuration.library_name_suffix.upper()),
        'library_description': project_configuration.library_description,
        'library_description_lower_case': library_description_lower_case,
        'library_version': library_version,

        'python_module_authors': python_module_authors,
        'python_module_name': project_configuration.python_module_name,
        'python_module_name_upper_case': (
            project_configuration.python_module_name.upper()),
        'python_module_copyright': python_module_copyright,

        'tools_authors': tools_authors,
        'tools_name': project_configuration.tools_directory,
        'tools_name_upper_case': project_configuration.tools_directory.upper(),
        'tools_description': project_configuration.tools_description,

        'tests_authors': tests_authors,
    }
    return template_mappings

  def _GetTypeLibraryHeaderFile(self, project_configuration, type_name):
    """Retrieves a type specific library include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of the type.

    Returns:
      LibraryHeaderFile: library header file or None if the library header file
          cannot be found or read.
    """
    header_file = self._library_type_header_files.get(type_name, None)
    if not header_file:
      if not self._library_path:
        self._library_path = os.path.join(
            self._projects_directory, project_configuration.library_name,
            project_configuration.library_name)

      header_file_path = '{0:s}_{1:s}.h'.format(
          project_configuration.library_name, type_name)
      header_file_path = os.path.join(self._library_path, header_file_path)
      header_file = source_file.LibraryHeaderFile(header_file_path)

      # TODO: handle types in non-matching header files.
      try:
        header_file.Read(project_configuration)
      except IOError:
        logging.warning('Unable to read library header file: {0:s}'.format(
            header_file.path))
        return None

      self._library_type_header_files[type_name] = header_file

    return header_file

  def _GetTypesIncludeHeaderFile(self, project_configuration):
    """Retrieves the types include header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      TypesIncludeHeaderFile: types include header file or None if
          the types include header file cannot be found.
    """
    if not self._types_include_header_file:
      self._types_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', project_configuration.library_name, 'types.h.in')

      if os.path.exists(self._types_include_header_path):
        self._types_include_header_file = source_file.TypesIncludeHeaderFile(
            self._types_include_header_path)
        self._types_include_header_file.Read(project_configuration)

    return self._types_include_header_file

  def _HasGlob(self, project_configuration, type_name):
    """Determines if the type has a glob function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      bool: True if the type needs a glob function.
    """
    # TODO: determine needs_glog based on function prototypes
    if (type_name == 'handle' and project_configuration.library_name in (
        'libewf', 'libsmraw')):
      return True

    return False

  def _HasTests(self, project_configuration):
    """Determines if the project has tests.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      bool: True if the tests path exits.
    """
    if not self._tests_path:
      self._tests_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'tests')

      self._has_tests = os.path.exists(self._tests_path)

    return self._has_tests

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename (str): name of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    # Read with binary mode to make sure end of line characters are
    # not converted.
    with open(filename, 'rb') as file_object:
      file_data = file_object.read()

    file_data = file_data.decode('utf8')

    return string.Template(file_data)

  def _SetSequenceTypeNameInTemplateMappings(
      self, template_mappings, type_name):
    """Sets the sequence type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): sequence type name.
    """
    if not type_name:
      template_mappings['sequence_type_description'] = ''
      template_mappings['sequence_type_name'] = ''
      template_mappings['sequence_type_name_camel_case'] = ''
      template_mappings['sequence_type_name_upper_case'] = ''
    else:
      template_mappings['sequence_type_description'] = type_name.replace(
          '_', ' ')
      template_mappings['sequence_type_name'] = type_name
      template_mappings['sequence_type_name_camel_case'] = ''.join([
          word.title() for word in type_name.split('_')])
      template_mappings['sequence_type_name_upper_case'] = type_name.upper()

  def _SetSequenceValueNameInTemplateMappings(
      self, template_mappings, value_name):
    """Sets the sequence value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): sequence value name.
    """
    if not value_name:
      template_mappings['sequence_value_description'] = ''
      template_mappings['sequence_value_name'] = ''
      template_mappings['sequence_value_name_upper_case'] = ''
    else:
      template_mappings['sequence_value_description'] = value_name.replace(
          '_', ' ')
      template_mappings['sequence_value_name'] = value_name
      template_mappings['sequence_value_name_upper_case'] = value_name.upper()

  def _SetTypeFunctionInTemplateMappings(
      self, template_mappings, type_function):
    """Sets the type function in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_function (str): type function.
    """
    if not type_function:
      template_mappings['type_function'] = ''
      template_mappings['type_function_upper_case'] = ''
    else:
      template_mappings['type_function'] = type_function
      template_mappings['type_function_upper_case'] = type_function.upper()

  def _SetTypeNameInTemplateMappings(self, template_mappings, type_name):
    """Sets the type name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): type name.
    """
    if not type_name:
      template_mappings['type_description'] = ''
      template_mappings['type_name'] = ''
      template_mappings['type_name_camel_case'] = ''
      template_mappings['type_name_upper_case'] = ''
    else:
      template_mappings['type_description'] = type_name.replace('_', ' ')
      template_mappings['type_name'] = type_name
      template_mappings['type_name_camel_case'] = ''.join([
          word.title() for word in type_name.split('_')])
      template_mappings['type_name_upper_case'] = type_name.upper()

  def _SetValueNameInTemplateMappings(self, template_mappings, value_name):
    """Sets value name in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      value_name (str): value name.
    """
    if not value_name:
      template_mappings['value_description'] = ''
      template_mappings['value_name'] = ''
      template_mappings['value_name_upper_case'] = ''
    else:
      template_mappings['value_description'] = value_name.replace('_', ' ')
      template_mappings['value_name'] = value_name
      template_mappings['value_name_upper_case'] = value_name.upper()

  def _SetValueTypeInTemplateMappings(self, template_mappings, value_type):
    """Sets value type in template mappings.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the type of a template variable.
      value_type (str): value type.
    """
    if not value_type:
      template_mappings['value_type'] = ''
      template_mappings['value_type_description'] = ''
      template_mappings['value_type_upper_case'] = ''
    else:
      template_mappings['value_type'] = value_type
      template_mappings['value_type_description'] = value_type.replace(
          '_', ' ')
      template_mappings['value_type_upper_case'] = value_type.upper()

  def _SortIncludeHeaders(self, project_configuration, output_filename):
    """Sorts the include headers within a source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    library_include_header_start = '#include "{0:s}_'.format(
        project_configuration.library_name)

    python_module_include_header_start = '#include "{0:s}_'.format(
        project_configuration.python_module_name)

    test_include_header_start = '#include "{0:s}_test_'.format(
        project_configuration.library_name_suffix)

    tools_include_header_start = '#include "{0:s}tools_'.format(
        project_configuration.library_name_suffix)

    include_headers = []
    in_include_headers = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if (line.startswith(library_include_header_start) or
            line.startswith(python_module_include_header_start) or
            line.startswith(test_include_header_start) or
            line.startswith(tools_include_header_start) or
            line.startswith('#include "info_') or
            line.startswith('#include "mount_')):
          include_headers.append(line)
          in_include_headers = True

        elif in_include_headers:
          file_object.writelines(sorted(include_headers))
          file_object.write(line)
          in_include_headers = False

        else:
          file_object.write(line)

  def _SortVariableDeclarations(self, output_filename):
    """Sorts the variable declarations within a source file.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    formatter = source_formatter.SourceFormatter()
    variable_declarations = None
    in_variable_declarations = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        stripped_line = line.rstrip()
        if stripped_line == '{':
          file_object.write(line)
          variable_declarations = []
          in_variable_declarations = True

        elif in_variable_declarations:
          if ('(' not in stripped_line or
              stripped_line.startswith('#if defined(')):
            variable_declarations.append(line)

          else:
            # TODO: remove the need for FormatSourceOld.
            sorted_lines = formatter.FormatSourceOld(variable_declarations)

            file_object.writelines(sorted_lines)
            file_object.write(line)
            in_variable_declarations = False

        else:
          file_object.write(line)

  def _VerticalAlignAssignmentStatements(self, output_filename):
    """Vertically aligns assignment statements.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    assigment_statements = []
    in_assigment_statements_block = False

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if ' = ' in line:
          if not in_assigment_statements_block:
            in_assigment_statements_block = True

          assigment_statements.append(line)
          continue

        if in_assigment_statements_block:
          if len(assigment_statements) == 1:
            file_object.write(assigment_statements[0])

          else:
            alignment_offset = 0
            for assigment_statement in assigment_statements:
              prefix, _, _ = assigment_statement.rpartition('=')
              prefix = prefix.rstrip()
              alignment_offset = max(alignment_offset, len(prefix) + 1)

            for assigment_statement in assigment_statements:
              prefix, _, suffix = assigment_statement.rpartition('=')
              prefix = prefix.rstrip()
              alignment_length = alignment_offset - len(prefix)

              assigment_statement_line = '{0:s}{1:s}={2:s}'.format(
                  prefix, ' ' * alignment_length, suffix)
              file_object.write(assigment_statement_line)

          in_assigment_statements_block = False
          assigment_statements = []

        file_object.write(line)

  def _VerticalAlignFunctionArguments(self, output_filename):
    """Vertically aligns function arguments.

    Note this is a very basic approach that should suffice for the yaltools and
    pyyal Python module source files.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    alignment_number_of_spaces = 0
    alignment_number_of_tabs = 0
    in_function_call = False
    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if not line.startswith('\t'):
          file_object.write(line)
          continue

        stripped_line = line.rstrip()

        if in_function_call:
          if stripped_line.endswith(')') or stripped_line.endswith(');'):
            in_function_call = False

          stripped_line = line.lstrip()
          line = '{0:s}{1:s}{2:s}'.format(
              '\t' * alignment_number_of_tabs,
              ' ' * alignment_number_of_spaces,
              stripped_line)

        elif stripped_line.endswith('('):
          in_function_call = True
          stripped_line = line.lstrip()

          alignment_number_of_spaces = stripped_line.rfind(' ')
          if alignment_number_of_spaces == -1:
            alignment_number_of_spaces = 1
          else:
            alignment_number_of_spaces += 2

          alignment_number_of_tabs = len(line) - len(stripped_line)

        file_object.write(line)

  def _VerticalAlignTabs(self, output_filename):
    """Vertically aligns tabs.

    Args:
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    alignment_offset = 0
    for line in lines:
      if '\t' not in line.lstrip('\t'):
        continue

      prefix, _, suffix = line.rpartition('\t')
      prefix = prefix.rstrip('\t')
      formatted_prefix = prefix.replace('\t', ' ' * 8)

      equal_sign_offset = len(formatted_prefix) + 8
      equal_sign_offset, _ = divmod(equal_sign_offset, 8)
      equal_sign_offset *= 8

      if alignment_offset == 0:
        alignment_offset = equal_sign_offset
      else:
        alignment_offset = max(alignment_offset, equal_sign_offset)

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        if '\t' in line.lstrip('\t'):
          prefix, _, suffix = line.rpartition('\t')
          prefix = prefix.rstrip('\t')
          formatted_prefix = prefix.replace('\t', ' ' * 8)

          alignment_size = alignment_offset - len(formatted_prefix)
          alignment_size, remainder = divmod(alignment_size, 8)
          if remainder > 0:
            alignment_size += 1

          alignment = '\t' * alignment_size

          line = '{0:s}{1:s}{2:s}'.format(prefix, alignment, suffix)

        file_object.write(line)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
