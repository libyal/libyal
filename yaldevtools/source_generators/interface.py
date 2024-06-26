# -*- coding: utf-8 -*-
"""The source file generator interface."""

import abc
import datetime
import logging
import os
import re
import string
import time

from yaldevtools import source_file
from yaldevtools import source_formatter
from yaldevtools import yaml_operations_file


class TemplateString(string.Template):
  """Template string."""

  idpattern = r'(?a:[_a-z][_a-z0-9.]*(|:[_a-z][_a-z0-9]*))'

  def substitute(self, mapping=None):
    """Substitutes placeholders in the template string.

    Args:
      mapping (dict[str, str]): values of placeholders.
    """
    def convert_placeholder(match):
      """Converts a placeholder into a mapped value.

      Args:
        match (re.Match): expression match.

      Returns:
        str: mapped value.

      Raises:
        ValueError: if the pattern is not supported.
      """
      identifier = match.group('named') or match.group('braced')
      if identifier is not None:
        identifier, _, modifier = identifier.partition(':')

        identifiers = identifier.split('.')
        try:
          value = mapping[identifiers[0]]
        except KeyError:
          raise ValueError(f'No mapping for placeholder: {identifiers[0]:s}')

        for attribute_name in identifiers[1:]:
          value = getattr(value, attribute_name, None)
        value = str(value)

        if modifier == 'camel_case':
          value = ''.join([word.title() for word in value.split('_')])
        elif modifier == 'lower_case':
          value = value.lower()
        elif modifier == 'upper_case':
          value = value.upper()
        elif modifier:
          raise ValueError('Unrecognized modifier in pattern', self.pattern)

        return value

      if match.group('escaped') is not None:
        return self.delimiter

      if match.group('invalid') is not None:
        self._invalid(match)

      raise ValueError('Unrecognized named group in pattern', self.pattern)

    return self.pattern.sub(convert_placeholder, self.template)


class BaseSourceFileGenerator(object):
  """Source file generator."""

  _PLACEHOLDER_VALUE_CALLBACKS = {}

  _SUPPORTED_MODIFIERS = frozenset([
      'remove_trailing_empty_lines',
      'sort_lines'])

  def __init__(self, templates_path):
    """Initializes a source file generator.

    Args:
      templates_path (str): path of the directory containing the template files.
    """
    super(BaseSourceFileGenerator, self).__init__()
    self._templates_path = templates_path

  def _GenerateSection(
      self, template_file_path, template_mappings, output_file_path,
      access_mode='w'):
    """Generates a section from template filename.

    Args:
      template_file_path (str): path of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_file_path (str): path of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    template_string = self._ReadTemplateFile(template_file_path)

    try:
      output_data = template_string.substitute(mapping=template_mappings)
    except (KeyError, ValueError) as exception:
      logging.error((
          f'Unable to format template: {template_file_path:s} with error: '
          f'{exception!s}'))
      return

    with open(output_file_path, access_mode, encoding='utf8') as file_object:
      file_object.write(output_data)

  def _GenerateSections(
      self, template_file_paths, template_mappings, output_file_path,
      access_mode='w'):
    """Generates sections from template filenames.

    Args:
      template_file_paths (list[str])): paths of the template files.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_file_path (str): path of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    for template_file_path in template_file_paths:
      self._GenerateSection(
          template_file_path, template_mappings, output_file_path,
          access_mode=access_mode)
      access_mode = 'a'

  def _GenerateSectionsFromGeneratorOperation(
      self, operations_file_name, generator_operation, operations, namespace,
      templates_path):
    """Generates sections based on a generator operation.

    Args:
      operations_file_name (str): name of the operations file.
      generator_operation (GeneratorOperation): generator operation.
      operations (dict[str, GeneratorOperation]): operations per identifier.
      namespace (dict[str, object])): expression namespace.
      templates_path (str): path of the directory containing the template files.

    Return:
      str: output data.
    """
    if generator_operation.type == 'group':
      output_data = self._GenerateSectionsFromGroupOperation(
          operations_file_name, generator_operation, operations, namespace,
          templates_path)

    elif generator_operation.type == 'selection':
      output_data = self._GenerateSectionsFromSelectionOperation(
          operations_file_name, generator_operation, operations, namespace,
          templates_path)

    elif generator_operation.type == 'sequence':
      output_data = self._GenerateSectionsFromSequenceOperation(
          operations_file_name, generator_operation, operations, namespace,
          templates_path)

    elif generator_operation.type == 'template':
      output_data = self._GenerateSectionsFromTemplateOperation(
          operations_file_name, generator_operation, operations, namespace,
          templates_path)

    else:
      logging.warning((
          f'Unsupported operation type: {generator_operation.type:s} in file: '
          f'{operations_file_name:s}'))
      output_data = ''

    for modifier in generator_operation.modifiers or []:
      if modifier not in self._SUPPORTED_MODIFIERS:
        logging.error((
            f'Unsupported modifier: {modifier:s} in file: '
            f'{operations_file_name:s}'))
        continue

      if modifier == 'remove_trailing_empty_lines':
        output_data = self._RemoveTrailingEmptyLines(output_data)
      elif modifier == 'sort_lines':
        output_data = self._SortLines(output_data)

    return output_data

  def _GenerateSectionsFromGroupOperation(
      self, operations_file_name, group_operation, operations, namespace,
      templates_path):
    """Generates sections based on a group operation.

    Args:
      operations_file_name (str): name of the operations file.
      group_operation (GeneratorOperation): group operation.
      operations (dict[str, GeneratorOperation]): operations per identifier.
      namespace (dict[str, object])): expression namespace.
      templates_path (str): path of the directory containing the template files.

    Return:
      str: output data.
    """
    if group_operation.condition:
      expression = group_operation.GetConditionExpression()

      try:
        result = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        logging.warning((
            f'Unable to check condition for operation: '
            f'{group_operation.identifier:s} in file: '
            f'{operations_file_name:s} with error: {exception!s}'))
        result = False

      if not result:
        return ''

    output_data = ''

    for operation_name in group_operation.operations:
      operation = operations.get(operation_name, None)
      if not operation:
        logging.warning((
            f'Missing operation: {operation_name:s} in '
            f'{group_operation.identifier:s} in file: '
            f'{operations_file_name:s}'))
        return ''

      operation_output_data = self._GenerateSectionsFromGeneratorOperation(
          operations_file_name, operation, operations, namespace,
          templates_path)

      output_data = ''.join([output_data, operation_output_data])

    return output_data

  def _GenerateSectionsFromOperationsFile(
      self, operations_file_name, main_operation_name, project_configuration,
      template_configuration, output_file_path):
    """Generates sections based on an operations file.

    Args:
      operations_file_name (str): name of the operations file.
      main_operation_name (str): name of the main operations.
      project_configuration (ProjectConfiguration): project configuration.
      template_configuration (dict[str, str]): template configuration.
      output_file_path (str): path of the output file.
    """
    operations_file_path = os.path.join(
        self._templates_path, operations_file_name)

    operations_file = yaml_operations_file.YAMLGeneratorOperationsFile()
    operations = {
         operation.identifier: operation
         for operation in operations_file.ReadFromFile(operations_file_path)}

    main_operation = operations.get(main_operation_name, None)
    if not main_operation:
      logging.warning((
          f'Missing main operation: {main_operation_name:s} in '
          f'{operations_file_path:s}'))
      return

    templates_path = os.path.dirname(operations_file_path)

    namespace = dict()
    if project_configuration:
      namespace.update(project_configuration.__dict__)
    namespace.update(template_configuration)
    # Make sure __builtins__ contains an empty dictionary.
    namespace['__builtins__'] = {}

    output_data = self._GenerateSectionsFromGeneratorOperation(
        operations_file_name, main_operation, operations, namespace,
        templates_path)

    if output_data:
      with open(output_file_path, 'w', encoding='utf8') as file_object:
        file_object.write(output_data)

  def _GenerateSectionsFromSelectionOperation(
      self, operations_file_name, selection_operation, operations, namespace,
      templates_path):
    """Generates sections based on a selection operation.

    Args:
      operations_file_name (str): name of the operations file.
      selection_operation (GeneratorOperation): selection operation.
      operations (dict[str, GeneratorOperation]): operations per identifier.
      namespace (dict[str, object])): expression namespace.
      templates_path (str): path of the directory containing the template files.

    Return:
      str: output data.
    """
    if selection_operation.condition:
      expression = selection_operation.GetConditionExpression()

      try:
        result = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        logging.warning((
            f'Unable to check condition for operation: '
            f'{selection_operation.identifier:s} in file: '
            f'{operations_file_name:s} with error: {exception!s}'))
        result = False

      if not result:
        return ''

    selection_input = self._GetPlaceholderValue(
        namespace, selection_operation.input)

    operation_name = selection_operation.options.get(
        selection_input, selection_operation.default)
    if not operation_name:
      logging.warning((
          f'Unable to determine option {selection_input:s} for operation: '
          f'{selection_operation.identifier:s} in file: '
          f'{operations_file_name:s}'))
      return ''

    operation = operations.get(operation_name, None)
    if not operation:
      logging.warning((
          f'Missing operation: {operation_name:s} in file: '
          f'{operations_file_name:s}'))
      return ''

    output_data = self._GenerateSectionsFromGeneratorOperation(
        operations_file_name, operation, operations, namespace,
        templates_path)

    return output_data

  def _GenerateSectionsFromSequenceOperation(
      self, operations_file_name, sequence_operation, operations, namespace,
      templates_path):
    """Generates sections based on a sequence operation.

    Args:
      operations_file_name (str): name of the operations file.
      sequence_operation (GeneratorOperation): sequence operation.
      operations (dict[str, GeneratorOperation]): operations per identifier.
      namespace (dict[str, object])): expression namespace.
      templates_path (str): path of the directory containing the template files.

    Return:
      str: output data.
    """
    if sequence_operation.condition:
      expression = sequence_operation.GetConditionExpression()

      try:
        result = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        logging.warning((
            f'Unable to check condition for operation: '
            f'{sequence_operation.identifier:s} in file: '
            f'{operations_file_name:s} with error: {exception!s}'))
        result = False

      if not result:
        return ''

    sequence_input = self._GetPlaceholderValue(
        namespace, sequence_operation.input)
    if not sequence_input:
      if sequence_input is None:
        logging.error((
            f'Missing input: {sequence_operation.input} in '
            f'{sequence_operation.identifier:s} in file: '
            f'{operations_file_name:s}'))
      return ''

    output_data = ''

    for value in sequence_input:
      namespace[sequence_operation.placeholder] = value

      for operation_name in sequence_operation.operations:
        operation = operations.get(operation_name, None)
        if not operation:
          logging.warning((
              f'Missing operation: {operation_name:s} in file: '
              f'{operations_file_name:s}'))
          return ''

        operation_output_data = self._GenerateSectionsFromGeneratorOperation(
            operations_file_name, operation, operations, namespace,
            templates_path)

        output_data = ''.join([output_data, operation_output_data])

    del namespace[sequence_operation.placeholder]

    return output_data

  def _GenerateSectionsFromTemplateOperation(
      self, operations_file_name, template_operation, operations, namespace,
      templates_path):
    """Generates sections based on a template operation.

    Args:
      operations_file_name (str): name of the operations file.
      template_operation (GeneratorOperation): template operation.
      operations (dict[str, GeneratorOperation]): operations per identifier.
      namespace (dict[str, object])): expression namespace.
      templates_path (str): path of the directory containing the template files.

    Return:
      str: output data.
    """
    operation_file = template_operation.file

    if template_operation.condition:
      expression = template_operation.GetConditionExpression()

      try:
        result = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        logging.warning((
            f'Unable to check condition for operation: '
            f'{template_operation.identifier:s} in file: '
            f'{operations_file_name:s} with error: {exception!s}'))
        result = False

      if not result:
        if not template_operation.fallback:
          return ''

        operation_file = template_operation.fallback

    template_file_path = os.path.join(templates_path, operation_file)

    template_string = self._ReadTemplateFile(template_file_path)

    template_values = {}
    for identifier in template_operation.placeholders or []:
      value = self._GetPlaceholderValue(namespace, identifier)
      if value is None:
        logging.warning((
            f'Missing template placeholder: {identifier:s} defined in '
            f'operation: {template_operation.identifier:s} in file: '
            f'{operations_file_name:s}'))

      template_values[identifier] = value

    try:
      output_data = template_string.substitute(mapping=template_values)
    except (KeyError, ValueError) as exception:
      logging.error((
          f'Unable to format template: {template_file_path:s} with error: '
          f'{exception!s}'))
      return ''

    return output_data

  def _GetPlaceholderValue(self, namespace, identifier):
    """Retrieves the value of a template placeholder.

    Args:
      namespace (dict[str, object])): expression namespace.
      identifier (str): identifier of the value in the template.

    Returns:
      str: value or None if not available.
    """
    identifiers = identifier.split('.')
    base_identifier = identifiers[0]

    callback = self._PLACEHOLDER_VALUE_CALLBACKS.get(base_identifier, None)
    if not callback:
      value = namespace.get(base_identifier, None)
    else:
      callback_function = getattr(self, callback, None)
      value = callback_function(namespace)

    for attribute_name in identifiers[1:]:
      value = getattr(value, attribute_name, None)

    return value

  def _ReadTemplateFile(self, path):
    """Reads a template string from file.

    Args:
      path (str): path of the file containing the template string.

    Returns:
      TemplateString: template string.
    """
    # Read with binary mode to make sure end of line characters are not
    # converted.
    with open(path, 'rb') as file_object:
      file_data = file_object.read()

    file_data = file_data.decode('utf8')

    return TemplateString(file_data)

  def _RemoveTrailingEmptyLines(self, text):
    """Removes trailing empty lines from text.

    Args:
      text (str): text.

    Returns:
      str: text without trailing empty lines.
    """
    lines = text.split('\n')

    while lines and not lines[-1]:
      lines.pop(-1)

    lines.append('')

    return '\n'.join(lines)

  def _SortLines(self, text):
    """Sorts lines of text.

    Args:
      text (str): text.

    Returns:
      str: text sorted by line.
    """
    lines = text.split('\n')

    if lines[-1] == '':
      last_line = lines.pop(-1)
    else:
      last_line = None

    sorted_lines = sorted(lines)

    if last_line is not None:
      sorted_lines.append(last_line)

    return '\n'.join(sorted_lines)


class SourceFileGenerator(BaseSourceFileGenerator):
  """Source file generator."""

  def __init__(
      self, projects_directory, data_directory, templates_path,
      experimental=False):
    """Initializes a source file generator.

    Args:
      projects_directory (str): path of the projects directory.
      data_directory (str): path of the data directory.
      templates_path (str): path of the directory containing the template files.
      experimental (bool): True if experimental features should be enabled.
    """
    super(SourceFileGenerator, self).__init__(templates_path)
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
    description = f' a {name:s}'
    corrected_description = f' an {name:s}'

    with open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        line = line.replace(description, corrected_description)
        file_object.write(line)

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
      self._library_include_header_path = os.path.join(
          self._projects_directory, project_configuration.library_name,
          'include', f'{project_configuration.library_name:s}.h.in')

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

    project_copyright = f'{project_configuration.project_year_of_creation:d}'
    if project_configuration.project_year_of_creation != date.year:
      project_copyright = f'{project_copyright:s}-{date.year:d}'

    python_module_copyright = (
        f'{project_configuration.python_module_year_of_creation:d}')
    if project_configuration.python_module_year_of_creation != date.year:
      python_module_copyright = f'{python_module_copyright:s}-{date.year:d}'

    authors = authors_separator.join(project_configuration.project_authors)
    python_module_authors = authors_separator.join(
        project_configuration.python_module_authors)
    tools_authors = authors_separator.join(project_configuration.tools_authors)
    tests_authors = authors_separator.join(project_configuration.tests_authors)

    library_version = time.strftime('%Y%m%d', time.gmtime())

    template_mappings = {
        'authors': authors,
        'copyright': project_copyright,

        'library_name': project_configuration.library_name,
        'library_name_suffix': project_configuration.library_name_suffix,
        'library_description': project_configuration.library_description,
        'library_version': library_version,

        'python_module_authors': python_module_authors,
        'python_module_name': project_configuration.python_module_name,
        'python_module_copyright': python_module_copyright,

        'tools_authors': tools_authors,
        'tools_name': project_configuration.tools_directory,
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

      header_file_path = os.path.join(
          self._library_path,
          f'{project_configuration.library_name:s}_{type_name:s}.h')
      header_file = source_file.LibraryHeaderFile(header_file_path)

      # TODO: handle types in non-matching header files.
      try:
        header_file.Read(project_configuration)
      except IOError:
        logging.warning(
            f'Unable to read library header file: {header_file.path:s}')
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

  # TODO: remove _HasGlob if no longer used, replace with library_features
  def _HasGlob(self, project_configuration, type_name):
    """Determines if the type has a glob function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      bool: True if the type needs a glob function.
    """
    # TODO: determine needs_glob based on function prototypes
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

  # TODO: remove if no longer used
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
    else:
      template_mappings['sequence_type_description'] = type_name.replace(
          '_', ' ')
      template_mappings['sequence_type_name'] = type_name

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
    else:
      template_mappings['sequence_value_description'] = value_name.replace(
          '_', ' ')
      template_mappings['sequence_value_name'] = value_name

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
    else:
      template_mappings['type_function'] = type_function

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
    else:
      template_mappings['type_description'] = type_name.replace('_', ' ')
      template_mappings['type_name'] = type_name

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
    else:
      template_mappings['value_description'] = value_name.replace('_', ' ')
      template_mappings['value_name'] = value_name

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
    else:
      template_mappings['value_type'] = value_type
      template_mappings['value_type_description'] = value_type.replace(
          '_', ' ')

  def _SortIncludeHeaders(self, project_configuration, output_filename):
    """Sorts the include headers within a source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_filename (str): path of the output file.
    """
    with open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    library_include_header_start = (
        f'#include "{project_configuration.library_name:s}_')
    python_module_include_header_start = (
        f'#include "{project_configuration.python_module_name:s}_')
    test_include_header_start = (
        f'#include "{project_configuration.library_name_suffix:s}_test_')
    tools_include_header_start = (
        f'#include "{project_configuration.library_name_suffix:s}tools_')

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

              assigment_statement_line = ''.join([
                  prefix, ' ' * alignment_length, '=', suffix])
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
          line = ''.join([
              '\t' * alignment_number_of_tabs, ' ' * alignment_number_of_spaces,
              stripped_line])

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

          line = ''.join([prefix, '\t' * alignment_size, suffix])

        file_object.write(line)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
