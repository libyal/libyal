# -*- coding: utf-8 -*-
"""The source file generator for test source files."""

from __future__ import unicode_literals

import io
import logging
import os
import stat

from yaldevtools import source_file
from yaldevtools.source_generators import interface


class TestSourceFileGenerator(interface.SourceFileGenerator):
  """Test source file generator."""

  _PYTHON_FUNCTION_NAMES = (
      'support', )

  # TODO: replace by type specific test scripts.
  _PYTHON_FUNCTION_WITH_INPUT_NAMES = (
      'file', 'handle', 'volume')

  def _FormatTestData(self, data):
    """Formats the test data as a C byte array.

    Args:
      data (bytes): data.

    Returns:
      str: data as a C byte array.
    """
    # TODO: print text as text?

    hexadecimal_lines = []
    data_size = len(data)
    for block_index in range(0, data_size, 16):
      data_string = data[block_index:block_index + 16]

      hexadecimal_string = ', '.join([
          '0x{0:02x}'.format(byte_value)
          for byte_value in data_string[0:16]])

      if len(data_string) < 16 or block_index + 16 == data_size:
        hexadecimal_lines.append('\t{0:s}'.format(hexadecimal_string))
      else:
        hexadecimal_lines.append('\t{0:s},'.format(hexadecimal_string))

    return '\n'.join(hexadecimal_lines)

  def _GenerateAPISupportTests(
      self, project_configuration, template_mappings, include_header_file,
      test_options, output_writer):
    """Generates an API support tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      test_options (list[tuple[str, str]]): test options.
      output_writer (OutputWriter): output writer.
    """
    signature_type = include_header_file.GetCheckSignatureType()

    template_directory = os.path.join(
        self._template_directory, 'yal_test_support')

    output_filename = '{0:s}_test_support.c'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join('tests', output_filename)

    # TODO: add check for has codepage function for libsigscan and include
    # libcerror.
    if signature_type:
      template_mappings['signature_type'] = signature_type

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if signature_type:
      template_filename = os.path.join(
          template_directory, 'includes-with_input.c')
    else:
      template_filename = os.path.join(template_directory, 'includes.c')

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    for support_function in (
        'get_version', 'get_access_flags_read', 'get_codepage',
        'set_codepage'):
      if not include_header_file.HasFunction(support_function):
        continue

      template_filename = '{0:s}.c'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if signature_type:
      template_filename = os.path.join(template_directory, 'check_signature.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      test_getopt_string = []
      test_options_variable_declarations = []
      for option, argument in test_options:
        getopt_string = option
        if argument:
          getopt_string = '{0:s}:'.format(getopt_string)

        test_getopt_string.append(getopt_string)

        if argument == 'offset': 
          test_options_variable_declarations.extend([
              '\tlibcerror_error_t *error = NULL;',
              '\tsystem_character_t *option_{0:s} = NULL;'.format(argument),
              '\toff64_t {0:s}_offset = 0;'.format(signature_type),
              '\tsize_t string_length = 0;',
              '\tint result = 0;'])

      variable_declaration = '\tsystem_character_t *source = NULL;'
      test_options_variable_declarations.append(variable_declaration)

      template_mappings['test_getopt_string'] = ''.join(test_getopt_string)
      template_mappings['test_options_variable_declarations'] = '\n'.join(
          sorted(test_options_variable_declarations))

      template_filename = os.path.join(
          template_directory, 'main-start-with_source-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['test_getopt_string']
      del template_mappings['test_options_variable_declarations']

      switch_case_unused = []
      for option, argument in test_options:
        if argument == 'offset': 
          template_mappings['test_option'] = option
          template_mappings['test_option_argument'] = argument

          template_filename = os.path.join(
              template_directory, 'main-start-with_source-switch_case.c')
          self._GenerateSection(
              template_filename, template_mappings, output_writer, output_filename,
              access_mode='a')

          del template_mappings['test_option']
          del template_mappings['test_option_argument']

        else:
          switch_case_unused.append(
              '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option))

      if switch_case_unused:
        template_mappings['test_options_switch_case_unused'] = '\n'.join(
            switch_case_unused)

        template_filename = os.path.join(
            template_directory, 'main-start-with_source-switch_case_unused.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='a')

        del template_mappings['test_options_switch_case_unused']

      template_filename = os.path.join(
          template_directory, 'main-start-with_source-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = os.path.join(
            template_directory, 'main-option_offset.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

      template_filename = os.path.join(
          template_directory, 'main-body_with_input.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      if 'offset' in [argument for _, argument in test_options]:
        template_filename = 'main-end_with_offset.c'
      else:
        template_filename = 'main-end_with_input.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    else:
      template_filename = os.path.join(template_directory, 'main.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if signature_type:
      del template_mappings['signature_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateExistingFunction(
      self, test_function_name, test_source_file, output_writer,
      output_filename, access_mode='w'):
    """Writes an existing function to the output.

    Args:
      test_function_name (str): name of the test function.
      test_source_file (TestSourceFile): test source file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      access_mode (Optional[str]): output file access mode.

    Returns:
      bool: True if there was an existing function, False otherwise.
    """
    if not test_source_file:
      return False

    existing_test_function = test_source_file.functions.get(
        test_function_name, None)
    if not existing_test_function:
      return False

    output_data = '\n'.join(existing_test_function)
    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)
    return True

  def _GenerateTestFunctions(
      self, project_configuration, template_mappings, output_writer,
      output_filename, with_input=False, with_offset=False):
    """Generates the test functions.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if tests require input data.
      with_offset (Optional[bool]): True if tests require offset support.
    """
    output_filename = '{0:s}_test_functions.h'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join('tests', output_filename)
    self._GenerateTestFunctionsHeader(
        project_configuration, template_mappings, output_writer, output_filename,
        with_input=with_input, with_offset=with_offset)

    output_filename = '{0:s}_test_functions.c'.format(
        project_configuration.library_name_suffix)
    output_filename = os.path.join('tests', output_filename)
    self._GenerateTestFunctionsSource(
        project_configuration, template_mappings, output_writer, output_filename,
        with_input=with_input, with_offset=with_offset)

  def _GenerateTestFunctionsHeader(
      self, project_configuration, template_mappings, output_writer,
      output_filename, with_input=False, with_offset=False):
    """Generates the test functions header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if tests require input data.
      with_offset (Optional[bool]): True if tests require offset support.
    """
    if not with_input:
      return

    template_directory = os.path.join(
        self._template_directory, 'yal_test_functions')

    template_filename = os.path.join(template_directory, 'header.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if with_offset:
      template_filename = os.path.join(template_directory, 'with_offset.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    # TODO: make check more generic based on the source itself.
    if project_configuration.library_name == 'libcfile':
      template_filename = os.path.join(
          template_directory, 'get_temporary_filename.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    # TODO: make check more generic based on the source itself.
    if project_configuration.library_name not in (
        'libcfile', 'libsmdev', 'libtableau'):
      template_filename = os.path.join(template_directory, 'file_io_handle.h')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GenerateTestFunctionsSource(
      self, project_configuration, template_mappings, output_writer,
      output_filename, with_input=False, with_offset=False):
    """Generates the test functions source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if tests require input data.
      with_offset (Optional[bool]): True if tests require offset support.
    """
    if not with_input:
      return

    template_directory = os.path.join(
        self._template_directory, 'yal_test_functions')

    template_filename = os.path.join(template_directory, 'header.c')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    if with_offset:
      template_filename = os.path.join(template_directory, 'with_offset.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    # TODO: make check more generic based on the source itself.
    if project_configuration.library_name == 'libcfile':
      template_filename = os.path.join(
          template_directory, 'get_temporary_filename.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    # TODO: make check more generic based on the source itself.
    if project_configuration.library_name not in (
        'libcfile', 'libsmdev', 'libtableau'):
      template_filename = os.path.join(template_directory, 'file_io_handle.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

  def _GenerateMakefileAM(
      self, project_configuration, template_mappings, include_header_file,
      makefile_am_file, api_functions, api_functions_with_input, api_types,
      api_types_with_input, api_pseudo_types, internal_functions,
      internal_types, python_module_types, output_writer):
    """Generates a tests Makefile.am file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      makefile_am_file (LibraryMakefileAMFile): library Makefile.am file.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      api_pseudo_types (list[str]): names of API pseudo types to test.
      internal_functions (list[str]): names of internal functions to test.
      internal_types (list[str]): names of internal types to test.
      python_module_types (list[str]): names of Python module types to test.
      output_writer (OutputWriter): output writer.
    """
    tests = set(api_functions)
    tests = tests.union(set(api_functions_with_input))
    tests = tests.union(set(api_types))
    tests = tests.union(set(api_types_with_input))
    tests = tests.union(set(api_pseudo_types))
    tests = tests.union(set(internal_functions))
    tests = tests.union(set(internal_types))
    tests = sorted(tests)

    template_directory = os.path.join(
        self._template_directory, 'Makefile.am')
    output_filename = os.path.join('tests', 'Makefile.am')

    test_scripts = []
    if (api_functions or api_functions_with_input or api_types or
        api_types_with_input or api_pseudo_types):
      test_script = 'test_library.sh'
      test_scripts.append(test_script)

      # TODO: improve test script https://github.com/libyal/libyal/issues/78
      # test_script = 'test_manpage.sh'
      # test_scripts.append(test_script)

    for tool_name_suffix in ('export', 'info', 'verify'):
      tool_name = '{0:s}{1:s}'.format(
          project_configuration.library_name_suffix, tool_name_suffix)
      if tool_name in project_configuration.tools_names:
        test_script = 'test_{0:s}.sh'.format(tool_name)
        test_scripts.append(test_script)

    check_scripts = ['test_manpage.sh', 'test_runner.sh']
    check_scripts.extend(test_scripts)

    python_scripts = []
    python_test_scripts = ['test_python_module.sh']

    if project_configuration.HasPythonModule():
      for python_module_type in python_module_types:
        test_script = '{0:s}_test_{1:s}.py'.format(
            project_configuration.python_module_name, python_module_type)
        python_scripts.append(test_script)

      test_script = '{0:s}_test_support.py'.format(
          project_configuration.python_module_name)
      python_scripts.append(test_script)

      check_scripts.extend(python_scripts)
      check_scripts.extend(python_test_scripts)

    check_scripts = sorted(check_scripts)

    if project_configuration.HasPythonModule():
      test_script = '$(TESTS_{0:s})'.format(
          project_configuration.python_module_name.upper())
      test_scripts.append(test_script)

    check_programs = []
    for test in tests:
      check_program = '{0:s}_test_{1:s}'.format(
          project_configuration.library_name_suffix, test)
      check_programs.append(check_program)

    cppflags = list(makefile_am_file.cppflags)
    if api_functions_with_input or api_types_with_input:
      # Add libcsystem before non libyal cppflags.
      index = 0
      while index < len(cppflags):
        cppflag = cppflags[index]
        if not cppflag.startswith('lib') or cppflag == 'libcrypto':
          break
        index += 1

    cppflags = ['@{0:s}_CPPFLAGS@'.format(name.upper()) for name in cppflags]

    cppflag = '@{0:s}_DLL_IMPORT@'.format(
        project_configuration.library_name.upper())
    cppflags.append(cppflag)

    template_mappings['cppflags'] = ' \\\n'.join([
        '\t{0:s}'.format(name) for name in cppflags])
    template_mappings['python_tests'] = ' \\\n'.join([
        '\t{0:s}'.format(filename) for filename in python_test_scripts])
    template_mappings['tests'] = ' \\\n'.join([
        '\t{0:s}'.format(filename) for filename in test_scripts])
    template_mappings['check_scripts'] = ' \\\n'.join([
        '\t{0:s}'.format(filename) for filename in check_scripts])
    template_mappings['check_programs'] = ' \\\n'.join([
        '\t{0:s}'.format(filename) for filename in check_programs])

    template_names = ['header.am']

    if project_configuration.HasPythonModule():
      template_names.append('python.am')

    template_names.append('body.am')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    # TODO: add support for read_file_io_handle tests
    # TODO: add support for rwlock tests
    for group_name in tests:
      if group_name in api_functions or group_name in internal_functions:
        has_error_argument = include_header_file.HasErrorArgument(group_name)
        if (project_configuration.library_name != 'libcerror' and
            group_name != 'error' and has_error_argument):
          template_filename = 'yal_test_function.am'

        elif (project_configuration.library_name == 'libcerror' and
              group_name == 'system'):
          template_filename = 'yal_test_function_no_error_with_memory.am'

        else:
          template_filename = 'yal_test_function_no_error.am'

        template_mappings['library_function'] = group_name

      elif group_name in api_functions_with_input:
        if group_name == 'support':
          template_filename = 'yal_test_support_with_input.am'
        else:
          template_filename = 'yal_test_function_with_input.am'

        template_mappings['library_function'] = group_name

      elif (group_name in api_types or group_name in api_pseudo_types or
            group_name in internal_types):
        header_file = self._GetTypeLibraryHeaderFile(
            project_configuration, group_name)

        if project_configuration.library_name == 'libcerror':
          template_filename = 'yal_test_type_no_error.am'

        elif (project_configuration.library_name != 'libcthreads' and
              header_file and header_file.has_read_write_lock):
          template_filename = 'yal_test_function_with_rwlock.am'

        else:
          template_filename = 'yal_test_type.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      elif group_name in api_types_with_input:
        if project_configuration.library_name == 'libcdirectory':
          template_filename = 'yal_test_type.am'
        else:
          template_filename = 'yal_test_type_with_input.am'

        self._SetTypeNameInTemplateMappings(template_mappings, group_name)

      else:
        logging.warning((
            'Unable to generate tests Makefile.am entry for: "{0:s}" with '
            'error: missing template').format(group_name))
        continue

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'footer.am')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    self._SortSources(output_filename)

  def _GeneratePythonModuleSupportTests(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates a Python module support tests script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, 'pyyal_test_support')

    output_filename = '{0:s}_test_support.py'.format(
        project_configuration.python_module_name)
    output_filename = os.path.join('tests', output_filename)

    template_filename = os.path.join(template_directory, 'header.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'imports.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    template_filename = os.path.join(template_directory, 'test_case.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    for support_function in (
        'get_version', ):
      if not include_header_file.HasFunction(support_function):
        continue

      template_filename = '{0:s}.py'.format(support_function)
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'main.py')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GeneratePythonModuleTypeTests(
      self, project_configuration, template_mappings, type_name, output_writer,
      with_input=False, with_offset=False):
    """Generates a Python module type tests script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      output_writer (OutputWriter): output writer.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.
      with_offset (Optional[bool]): True if tests require offset support.

    Returns:
      bool: True if successful or False if not.
    """
    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)
    if not header_file:
      return False

    function_prototype = header_file.GetTypeFunction(
        type_name, 'read_buffer')

    with_read_buffer_function = bool(function_prototype)

    test_options = self._GetTestOptions(project_configuration, type_name)
    test_options = [argument for _, argument in test_options]

    template_directory = os.path.join(
        self._template_directory, 'pyyal_test_type')

    output_filename = '{0:s}_test_{1:s}.py'.format(
        project_configuration.python_module_name, type_name)
    output_filename = os.path.join('tests', output_filename)

    template_names = ['header.py', 'imports-start.py']

    if with_read_buffer_function:
      template_names.append('imports-random.py')

    template_names.append('imports-end.py')

    if 'offset' in test_options:
      template_names.append('data_range_file_object.py')

    template_names.append('test_case.py')

    for type_function in (
        'signal_abort', 'open', 'set_ascii_codepage', 'read_buffer',
        'seek_offset'):
      function_prototype = header_file.GetTypeFunction(type_name, type_function)
      if not function_prototype:
        continue

      if type_function == 'open' and 'offset' in test_options:
        template_name = '{0:s}-with_offset.py'.format(type_function)
      else:
        template_name = '{0:s}.py'.format(type_function)

      template_names.append(template_name)

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    type_size_name = self._GetTypeSizeName(project_configuration, type_name)

    template_mappings['type_size_name'] = type_size_name

    self._GenerateSections(
        template_filenames, template_mappings, output_writer,
        output_filename)

    del template_mappings['type_size_name']

    value_names = []
    for function_prototype in header_file.functions_per_name.values():
      if '_utf16_' in function_prototype.name:
        continue

      value_name = function_prototype.GetValueName()
      if value_name:
        value_names.append(value_name)

    for value_name in value_names:
      # Skip value name size getter functions.
      if value_name.endswith('_size') and value_name[:-5] in value_names:
        continue

      template_mappings['value_name'] = value_name

      if with_offset:
        template_filename = 'getter_with_property-with_offset.py'
      else:
        template_filename = 'getter_with_property.py'

      template_filename = os.path.join(template_directory, template_filename)

      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='a')

      del template_mappings['value_name']

    template_names = ['main.py']

    argument_parser_options = []
    unittest_options = []

    if 'offset' in test_options:
      argument_parser_options.extend([
          '  argument_parser.add_argument(',
          ('      "-o", "--offset", dest="offset", action="store", '
           'default=None,'),
          '      type=int, help="offset of the source file.")',
          ''])
      unittest_options.append('  setattr(unittest, "offset", options.offset)')

    if 'password' in test_options:
      argument_parser_options.extend([
          '  argument_parser.add_argument(',
          ('      "-p", "--password", dest="password", action="store", '
           'default=None,'),
          '      type=str, help="password to unlock the source file.")',
          ''])
      unittest_options.append(
          '  setattr(unittest, "password", options.password)')

    if 'recovery_password' in test_options:
      argument_parser_options.extend([
          '  argument_parser.add_argument(',
          '      "-r", "--recovery-password", "--recovery_password",',
          ('      dest="recovery_password", action="store", default=None, '
           'type=str,'),
          '      help="recovery password to unlock the source file.")',
          ''])
      unittest_options.append(
          '  setattr(unittest, "recovery_password", options.recovery_password)')

    if header_file.GetTypeFunction(type_name, 'open'):
      argument_parser_options.extend([
          '  argument_parser.add_argument(',
          '      "source", nargs="?", action="store", metavar="PATH",',
          '      default=None, help="path of the source file.")',
          ''])
      unittest_options.append('  setattr(unittest, "source", options.source)')

    template_mappings['argument_parser_options'] = '\n'.join(
        argument_parser_options)
    template_mappings['unittest_options'] = '\n'.join(unittest_options)

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer,
        output_filename, access_mode='a')

    del template_mappings['argument_parser_options']
    del template_mappings['unittest_options']

  def _GenerateTypeTest(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, test_source_file, output_writer,
      output_filename, with_input=False):
    """Generates a test for a type function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      test_source_file (TestSourceFile): test source file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      tuple: contains:
        str: name of library type function.
        str: name of the test function corresponding to the library type function.
        bool: True if the function prototype was externally available.
    """
    template_filename = '{0:s}.c'.format(type_function)

    return self._GenerateTypeTestFromTemplate(
        project_configuration, template_mappings, template_filename, type_name,
        type_function, last_have_extern, header_file, test_source_file,
        output_writer, output_filename, with_input=with_input)

  def _GenerateTypeTestFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, test_source_file, output_writer,
      output_filename, with_input=False):
    """Generates a test for a type function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      test_source_file (TestSourceFile): test source file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      tuple: contains:
        str: name of library type function.
        str: name of the test function corresponding to the library type
            function or None if no test function could be generated.
        bool: True if the function prototype was externally available.
    """
    function_name = self._GetFunctionName(
        project_configuration, type_name, type_function)

    test_function_name = self._GetTestFunctionName(
        project_configuration, type_name, type_function)

    library_type_prefix = '{0:s}_'.format(project_configuration.library_name)

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return function_name, None, last_have_extern

    have_extern = function_prototype.have_extern

    number_of_arguments = len(function_prototype.arguments)

    initialize_number_of_arguments = None
    initialize_value_name = None
    initialize_value_type = None
    initialize_function_prototype = header_file.GetTypeFunction(
        type_name, 'initialize')
    if initialize_function_prototype:
      initialize_number_of_arguments = len(
          initialize_function_prototype.arguments)

    if initialize_number_of_arguments not in (2, 3):
      if self._GenerateExistingFunction(
          test_function_name, test_source_file, output_writer,
          output_filename, access_mode='a'):
        return function_name, test_function_name, last_have_extern
      else:
        return function_name, None, last_have_extern

    if initialize_number_of_arguments == 3:
      function_argument = initialize_function_prototype.arguments[1]

      initialize_value_type, initialize_value_name = (
          self._GetValueTypeFromFunctionArgument(function_argument))

      if not initialize_value_type.startswith(library_type_prefix):
        initialize_value_type = None
        initialize_value_name = None

    function_template = None
    value_name = None
    value_type = None

    codepage_argument = function_prototype.arguments[-2]
    codepage_argument_string = codepage_argument.CopyToString()

    with_codepage = False
    if (codepage_argument_string.startswith('int ') and
        codepage_argument_string.endswith('codepage')):
      with_codepage = True

    index_argument = function_prototype.arguments[1]
    index_argument_string = index_argument.CopyToString()

    with_index = False
    if (index_argument_string.startswith('int ') and
        index_argument_string.endswith('_index')):
      with_index = True

    if with_index:
      function_argument_index = 2
    else:
      function_argument_index = 1

    file_offset_argument = function_prototype.arguments[-2]
    file_offset_argument_string = codepage_argument.CopyToString()

    with_file_offset = False
    if (file_offset_argument_string.startswith('off64_t ') and
        file_offset_argument_string.endswith('_offset')):
      with_file_offset = True

    if (type_function.startswith('get_utf8_') or
        type_function.startswith('get_utf16_')):
      function_argument = function_prototype.arguments[function_argument_index]
      function_argument_string = function_argument.CopyToString()

      value_name = type_function[4:]
      value_type, _, _ = function_argument_string.partition(' ')

      if (number_of_arguments == function_argument_index + 2 and
          type_function.endswith('_size')):
        function_template = 'get_value'
      elif number_of_arguments == function_argument_index + 3:
        function_template = 'get_string_value'

    elif type_function.startswith('get_'):
      function_argument = function_prototype.arguments[function_argument_index]
      function_argument_string = function_argument.CopyToString()

      function_value_name = type_function[4:]

      if with_index:
        value_type, value_name = self._GetValueTypeFromFunctionArgument(
            function_argument)

      else:
        value_name = function_value_name
        value_type, _, _ = function_argument_string.partition(' ')

      if function_argument_string == 'uint8_t *guid_data':
        function_template = 'get_guid_value'

      if function_argument_string == 'uint8_t *uuid_data':
        function_template = 'get_uuid_value'

      elif number_of_arguments == function_argument_index + 2:
        if not value_type.startswith(library_type_prefix):
          function_template = 'get_value'
        else:
          function_template = 'get_type_value'

          value_type = value_type[:-2]

    if function_template and with_index:
      function_template = '{0:s}-with_index'.format(function_template)

    if type_function in ('copy_from_byte_stream', 'read_data'):
      # TODO: add support for read data with value.
      if (number_of_arguments == 4 or (
         number_of_arguments == 5 and with_codepage)):
        function_template = type_function

    elif type_function == 'read_file_io_handle':
      # TODO: add support for io_handle argument
      if (number_of_arguments == 3 or (
         number_of_arguments == 4 and with_file_offset)):
        function_template = type_function

    elif not function_template:
      function_template = type_function

    clone_function = None
    compare_function = None
    free_function = None
    pointer_type_argument_name = None
    pointer_type_argument_type = None

    for argument in function_prototype.arguments:
      argument_string = argument.CopyToString()

      if argument_string.startswith(library_type_prefix):
        argument_type, _, argument_name = argument_string.partition(' ')
        if argument_name.startswith('**'):
          pointer_type_argument_type = argument_type[
              len(library_type_prefix):-2]
          pointer_type_argument_name = argument_name[2:]

      if '_clone_function' in argument_string:
        _, _, clone_function = argument_string.partition('*')
        clone_function, _, _ = clone_function.partition(')')

      elif '_compare_function' in argument_string:
        _, _, compare_function = argument_string.partition('*')
        compare_function, _, _ = compare_function.partition(')')

      elif '_free_function' in argument_string:
        _, _, free_function = argument_string.partition('*')
        free_function, _, _ = free_function.partition(')')

    if free_function:
      value_name, _, _ = free_function.rpartition('_free_function')

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    # TODO: add support for functions that don't return 0 to not use is_set in tests.
    # if function_prototype.return_values:

    with_is_set = bool(function_prototype.return_values == set(['-1', '0', '1']))

    body_template_name = None
    if function_template:
      if clone_function:
        body_template_name = 'function-body-{0:s}-with_clone_function.c'.format(
            function_template)
      elif free_function:
        body_template_name = 'function-body-{0:s}-with_free_function.c'.format(
            function_template)
      elif with_codepage:
        body_template_name = 'function-body-{0:s}-with_codepage.c'.format(
            function_template)
      elif with_is_set:
        body_template_name = 'function-body-{0:s}-with_is_set.c'.format(
            function_template)
      else:
        body_template_name = 'function-body-{0:s}.c'.format(function_template)

    body_template_filename = None
    if body_template_name:
      body_template_filename = os.path.join(
          template_directory, body_template_name)

    if not body_template_filename or not os.path.exists(body_template_filename):
      template_filename = None
      if function_template:
        template_filename = '{0:s}.c'.format(function_template)
        template_filename = os.path.join(template_directory, template_filename)

      if not template_filename or not os.path.exists(template_filename):
        logging.warning((
            'Unable to generate tests source code for type: "{0:s}" function: '
            '"{1:s}" with error: missing template').format(
                type_name, type_function))

        if self._GenerateExistingFunction(
            test_function_name, test_source_file, output_writer,
            output_filename, access_mode='a'):
          return function_name, test_function_name, last_have_extern
        else:
          return function_name, None, last_have_extern

      self._GenerateTypeTestDefineInternalEnd(
          template_mappings, last_have_extern, have_extern, output_writer,
          output_filename)

      self._GenerateTypeTestDefineInternalStart(
          template_mappings, last_have_extern, have_extern, output_writer,
          output_filename)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    else:
      self._SetValueNameInTemplateMappings(template_mappings, value_name)
      self._SetValueTypeInTemplateMappings(template_mappings, value_type)

      function_variables = []

      function_template, _, _ = function_template.partition('-')

      if function_template == 'get_binary_data_value':
        function_variables.extend([
            '{0:s} {1:s}[ 4096 ];'.format(value_type, value_name),
            ''])

      elif function_template == 'get_guid_value':
        function_variables.extend([
            'uint8_t guid_data[ 16 ];',
            ''])

      elif function_template == 'get_string_value':
        function_variables.extend([
            '{0:s} {1:s}[ 512 ];'.format(value_type, value_name),
            ''])

        if with_is_set and not with_index:
          function_variables.append(
              'int {0:s}_is_set = 0;'.format(value_name))

      elif function_template == 'get_type_value':
        function_variables.append(
            '{0:s}_t *{1:s} = NULL;'.format(value_type, value_name))

        if with_is_set and not with_index:
          function_variables.append(
              'int {0:s}_is_set = 0;'.format(value_name))

      elif function_template == 'get_uuid_value':
        function_variables.extend([
            'uint8_t uuid_data[ 16 ];',
            ''])

      elif function_template == 'get_value':
        function_variables.append(
            '{0:s} {1:s} = 0;'.format(value_type, value_name))

        if with_is_set and not with_index:
          function_variables.append(
              'int {0:s}_is_set = 0;'.format(value_name))

      elif function_template == 'read_file_io_handle':
          function_variables.append(
              'libbfio_handle_t *file_io_handle = NULL;')

      function_variables.extend([
          'libcerror_error_t *error = NULL;',
          'int result = 0;'])

      if function_template == 'clone':
        function_variables.append(
            '{0:s}_{1:s}_t *destination_{1:s} = NULL;'.format(
                project_configuration.library_name, type_name))
        function_variables.append(
            '{0:s}_{1:s}_t *source_{1:s} = NULL;'.format(
                project_configuration.library_name, type_name))

      elif not with_input:
        function_variables.append(
            '{0:s}_{1:s}_t *{1:s} = NULL;'.format(
                project_configuration.library_name, type_name))

      if function_template in (
          'get_binary_data_value', 'get_guid_value', 'get_uuid_value',
          'get_string_value', 'get_type_value', 'get_value'):
        function_template = 'get_{0:s}'.format(function_value_name)

      if (initialize_number_of_arguments == 3 and initialize_value_type and
          initialize_value_name):
        function_variable = '{0:s}_t *{1:s} = NULL;'.format(
            initialize_value_type, initialize_value_name)
        function_variables.append(function_variable)

      # TODO: add support for multiple test data files.
      test_data_size = None
      if function_template in ('copy_from_byte_stream', 'read_data'):
        test_data = self._ReadTestDataFile(type_name)
        test_data_size = len(test_data)
        if not test_data_size:
          logging.warning((
              'Unable to generate tests source code for type: "{0:s}" '
              'function: "{1:s}" with error: missing test data').format(
                  type_name, type_function))
          return function_name, None, last_have_extern

      function_variable_strings = []
      for variable in function_variables:
        # Do not indent empty lines of function_variables.
        if variable:
          variable = '\t{0:s}'.format(variable)

        function_variable_strings.append(variable)

      template_names = []

      if with_input:
        template_names.append('function-start-with_input.c')
      else:
        template_names.append('function-start.c')

      if not with_input:
        if initialize_number_of_arguments == 3:
          template_name = 'function-initialize-with_value.c'
        else:
          template_name = 'function-initialize.c'

        if function_template == 'clone':
          template_name = '{0:s}-clone.c'.format(template_name[:-2])

        template_names.append(template_name)

      template_names.append(body_template_name)

      # TODO: refactor to have unified function end handling

      if not with_input:
        template_names.append('function-cleanup-header.c')

      if function_template == 'clone':
        template_names.append('function-cleanup-clone.c')

        if initialize_number_of_arguments == 3:
          template_names.append('function-cleanup-with_value.c')

      elif free_function:
        template_names.append('function-cleanup-with_free_function.c')

      elif not with_input:
        template_names.append('function-cleanup-type.c')

        if initialize_number_of_arguments == 3:
          template_names.append('function-cleanup-with_value.c')

      template_names.append('function-end-on_error.c')

      if 'libbfio_handle_t *file_io_handle = NULL;' in function_variables:
        template_names.append('function-end-on_error-free_file_io_handle.c')

      if function_template == 'clone':
        template_names.append('function-end-on_error-clone.c')
      elif free_function:
        template_names.append('function-end-on_error-with_free_function.c')
      elif not with_input:
        template_names.append('function-end-on_error-free_type.c')

      if pointer_type_argument_name:
        template_names.append('function-end-on_error-free_pointer_type.c')

      if initialize_number_of_arguments == 3:
        template_names.append('function-end-on_error-with_value.c')

      template_names.append('function-end-footer.c')

      template_filenames = [
          os.path.join(template_directory, template_name)
          for template_name in template_names]

      template_mappings['function_name'] = function_template
      template_mappings['function_variables'] = '\n'.join(
          function_variable_strings)
      template_mappings['initialize_value_name'] = initialize_value_name
      template_mappings['initialize_value_type'] = initialize_value_type
      template_mappings['pointer_type_name'] = pointer_type_argument_type
      template_mappings['test_data_size'] = test_data_size

      self._GenerateTypeTestDefineInternalEnd(
          template_mappings, last_have_extern, have_extern, output_writer,
          output_filename)

      self._GenerateTypeTestDefineInternalStart(
          template_mappings, last_have_extern, have_extern, output_writer,
          output_filename)

      self._GenerateSections(
          template_filenames, template_mappings, output_writer,
          output_filename, access_mode='a')

      del template_mappings['function_name']
      del template_mappings['function_variables']
      del template_mappings['initialize_value_name']
      del template_mappings['initialize_value_type']
      del template_mappings['pointer_type_name']
      del template_mappings['test_data_size']

    return function_name, test_function_name, have_extern

  def _GenerateTypeTestFromTemplate(
      self, project_configuration, template_mappings, template_filename,
      type_name, type_function, last_have_extern, header_file, test_source_file,
      output_writer, output_filename, with_input=False):
    """Generates a test for a type function with a specific template.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      template_filename (str): name of template file.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      test_source_file (TestSourceFile): test source file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      tuple: contains:
        str: name of library type function.
        str: name of the test function corresponding to the library type function.
        bool: True if the function prototype was externally available.
    """
    function_name = self._GetFunctionName(
        project_configuration, type_name, type_function)

    test_function_name = self._GetTestFunctionName(
        project_configuration, type_name, type_function)

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return function_name, None, last_have_extern

    have_extern = function_prototype.have_extern

    self._GenerateTypeTestDefineInternalEnd(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    self._GenerateTypeTestDefineInternalStart(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    template_directory = os.path.join(self._template_directory, 'yal_test_type')
    if template_filename:
      # os.path.join will fail if template_filename is None.
      template_filename = os.path.join(template_directory, template_filename)
    if not template_filename or not os.path.exists(template_filename):
      logging.warning((
          'Unable to generate tests source code for type: "{0:s}" function: '
          '"{1:s}" with error: missing template').format(
              type_name, type_function))

      if self._GenerateExistingFunction(
          test_function_name, test_source_file, output_writer,
          output_filename, access_mode='a'):
        return function_name, test_function_name, have_extern
      else:
        return function_name, None, have_extern

    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    return function_name, test_function_name, have_extern

  def _GenerateTypeTestDefineInternalEnd(
      self, template_mappings, last_have_extern, have_extern, output_writer,
      output_filename):
    """Generates a define to mark the end of internal tests.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      have_extern (bool): True if the function prototype is externally
          available.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    if have_extern and not last_have_extern:
      template_directory = os.path.join(
          self._template_directory, 'yal_test_type')
      template_filename = os.path.join(
          template_directory, 'define_internal-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

  def _GenerateTypeTestDefineInternalStart(
      self, template_mappings, last_have_extern, have_extern, output_writer,
      output_filename):
    """Generates a define to mark the start of internal tests.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      have_extern (bool): True if the function prototype is externally
          available.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    if not have_extern and last_have_extern:
      template_directory = os.path.join(
          self._template_directory, 'yal_test_type')
      template_filename = os.path.join(
          template_directory, 'define_internal-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

  def _GenerateTypeTestDefineWideCharacterTypeEnd(
      self, template_mappings, last_have_wide_character_type,
      have_wide_character_type, output_writer, output_filename):
    """Generates a define to mark the end of a wide character type test.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      last_have_wide_character_type (bool): True if the previoud function
          prototype has wide character type.
      have_wide_character_type (bool): True if the function prototype has
          wide character type.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    if not have_wide_character_type and last_have_wide_character_type:
      template_directory = os.path.join(
          self._template_directory, 'yal_test_type')
      template_filename = os.path.join(
          template_directory, 'define_wide_character_type-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

  def _GenerateTypeTestDefineWideCharacterTypeStart(
      self, template_mappings, last_have_wide_character_type,
      have_wide_character_type, output_writer, output_filename):
    """Generates a define to mark the start of a wide character type test.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      last_have_wide_character_type (bool): True if the previoud function
          prototype has wide character type.
      have_wide_character_type (bool): True if the function prototype has
          wide character type.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    if have_wide_character_type and not last_have_wide_character_type:
      template_directory = os.path.join(
          self._template_directory, 'yal_test_type')
      template_filename = os.path.join(
          template_directory, 'define_wide_character_type-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

  def _GenerateTypeTestInitializeFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, test_source_file, output_writer,
      output_filename, function_names, tests_to_run):
    """Generates a test for a type initialize function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      test_source_file (TestSourceFile): test source file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.

    Returns:
      bool: True if the function prototype was externally available.
    """
    library_type_prefix = '{0:s}_'.format(project_configuration.library_name)

    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return last_have_extern

    number_of_arguments = len(function_prototype.arguments)
    template_filename = None

    if number_of_arguments == 2:
      template_filename = '{0:s}.c'.format(type_function)

    elif number_of_arguments == 3:
      template_filename = '{0:s}-with_value.c'.format(type_function)

      function_argument = function_prototype.arguments[1]

      value_type, value_name = self._GetValueTypeFromFunctionArgument(
          function_argument)

      if not value_type.startswith(library_type_prefix):
        function_name = self._GetFunctionName(
            project_configuration, type_name, type_function)
        function_names.remove(function_name)
        return last_have_extern

      # TODO: add support for non pointer value types.
      if not value_name.startswith('*'):
        function_name = self._GetFunctionName(
            project_configuration, type_name, type_function)
        function_names.remove(function_name)
        return last_have_extern

      self._SetValueNameInTemplateMappings(template_mappings, value_name)
      self._SetValueTypeInTemplateMappings(template_mappings, value_type)

    function_name, test_function_name, have_extern = (
        self._GenerateTypeTestFromTemplate(
            project_configuration, template_mappings, template_filename,
            type_name, 'initialize', last_have_extern, header_file,
            test_source_file, output_writer, output_filename))

    tests_to_run.append((function_name, test_function_name))
    function_names.remove(function_name)

    return have_extern

  def _GenerateTypeTestOpenFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      test_options, last_have_extern, header_file, output_writer,
      output_filename, function_names, tests_to_run):
    """Generates a test for a type open function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      test_options (list[tuple[str, str]]): test options.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.

    Returns:
      bool: True if the function prototype was externally available.
    """
    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return last_have_extern

    have_extern = function_prototype.have_extern

    self._GenerateTypeTestDefineInternalEnd(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    self._GenerateTypeTestDefineInternalStart(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    self._GenerateTypeTestOpen(
        project_configuration, template_mappings, type_name, type_function,
        test_options, output_writer, output_filename)

    function_name = self._GetFunctionName(
        project_configuration, type_name, type_function)
    test_function_name = self._GetTestFunctionName(
        project_configuration, type_name, type_function)

    tests_to_run.append((function_name, test_function_name))
    function_names.remove(function_name)

    return have_extern

  def _GenerateTypeTestOpen(
      self, project_configuration, template_mappings, type_name, test_name,
      test_options, output_writer, output_filename):
    """Generates an open test for a type.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_name (str): name of test.
      test_options (list[tuple[str, str]]): test options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    has_glob = self._HasGlob(project_configuration, type_name)

    has_string_test_options = bool(set(test_options).difference(set([
        ('o', 'offset')])))

    test_options_function_arguments = ['const system_character_t *source']
    for _, argument in test_options:
      if argument != 'offset':
        function_argument = 'const system_character_t *{0:s}'.format(argument)
        test_options_function_arguments.append(function_argument)

    test_options_function_variables = ['int result = 0;']
    if has_string_test_options:
      test_options_function_variables.append('size_t string_length = 0;')

    template_names = []

    if has_glob:
      template_names.append('{0:s}-start-with_glob.c'.format(test_name))
    else:
      template_names.append('{0:s}-start.c'.format(test_name))

    for _, argument in test_options:
      if argument != 'offset':
        template_names.append('{0:s}-set_{1:s}.c'.format(test_name, argument))

    if has_glob:
      template_names.append('{0:s}-end-with_glob.c'.format(test_name))
    else:
      template_names.append('{0:s}-end.c'.format(test_name))

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    test_options_function_arguments = [
        '     {0:s}'.format(function_argument)
        for function_argument in test_options_function_arguments]

    test_options_function_variables = [
        '\t{0:s}'.format(function_variable)
        for function_variable in test_options_function_variables]

    template_mappings['test_options_function_arguments'] = ',\n'.join(
        test_options_function_arguments)
    template_mappings['test_options_function_variables'] = '\n'.join(
        test_options_function_variables)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    del template_mappings['test_options_function_arguments']
    del template_mappings['test_options_function_variables']

  def _GenerateTypeTests(
      self, project_configuration, template_mappings, type_name, test_options,
      output_writer, is_internal=False, with_input=False):
    """Generates a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_options (list[tuple[str, str]]): test options.
      output_writer (OutputWriter): output writer.
      is_internal (Optional[bool]): True if the type is an internal type.
      with_input (Optional[bool]): True if the type is to be tested with
          input data.

    Returns:
      bool: True if successful or False if not.
    """
    output_filename = '{0:s}_test_{1:s}.c'.format(
        project_configuration.library_name_suffix, type_name)
    output_filename = os.path.join('tests', output_filename)

    if os.path.exists(output_filename) and not self._experimental:
      return False

    has_string_test_options = bool(set(test_options).difference(set([
        ('o', 'offset')])))

    header_file = self._GetTypeLibraryHeaderFile(
        project_configuration, type_name)
    if not header_file:
      return False

    # Read existing test file.
    test_source_file = None
    if os.path.exists(output_filename):
      test_source_file = source_file.TestSourceFile(output_filename)

      try:
        test_source_file.Read(project_configuration)
      except IOError:
        logging.warning('Unable to read test source file: {0:s}'.format(
            test_source_file.path))
        return False

    type_size_name = self._GetTypeSizeName(project_configuration, type_name)

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    template_names = []

    function_names = list(header_file.functions_per_name.keys())

    function_prototype = header_file.GetTypeFunction(
        type_name, 'open_file_io_pool')
    if function_prototype:
      bfio_type = 'pool'
    else:
      bfio_type = 'handle'

    template_mappings['bfio_type'] = bfio_type

    self._SetTypeNameInTemplateMappings(template_mappings, type_name)

    function_prototype = header_file.GetTypeFunction(
        type_name, 'read_buffer')

    with_read_buffer_function = bool(function_prototype)

    with_read_file_io_handle_function = False
    if is_internal:
      for function_prototype in header_file.functions_per_name.values():
        if function_prototype.name.endswith('_read_file_io_handle'):
          with_read_file_io_handle_function = True

    template_names.append('header.c')

    if with_input:
      template_names.append('includes_common-with_input.c')
    else:
      template_names.append('includes_common.c')

    template_names.append('includes.c')

    if with_read_buffer_function:
      template_names.append('includes_time.c')

    if project_configuration.library_name == 'libcthreads' and type_name in (
        'condition', 'lock', 'mutex', 'queue', 'read_write_lock'):
      template_names.append('includes_dlfcn.c')

    if with_input:
      template_names.append('includes_local-with_input.c')
    elif with_read_file_io_handle_function:
      template_names.append('includes_local-with_read_file_io_handle.c')
    else:
      template_names.append('includes_local.c')

    if header_file.have_internal_functions:
      template_names.append('includes_internal.c')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    if with_input:
      include_header_file = self._GetLibraryIncludeHeaderFile(
          project_configuration)

      signature_type = include_header_file.GetCheckSignatureType()

      test_options_function_arguments = []
      if bfio_type == 'pool':
        function_argument = 'libbfio_pool_t *file_io_pool'
      else:
        function_argument = 'libbfio_handle_t *file_io_handle'
      test_options_function_arguments.append(function_argument)

      for _, argument in test_options:
        if argument != 'offset':
          function_argument = 'const system_character_t *{0:s}'.format(argument)
          test_options_function_arguments.append(function_argument)

      test_options_function_variables = ['int result = 0;']
      if has_string_test_options:
        test_options_function_variables.insert(0, 'size_t string_length = 0;')

    template_names = []

    if project_configuration.library_name == 'libcthreads' and type_name in (
        'condition', 'lock', 'mutex', 'queue', 'read_write_lock', 'thread',
        'thread_pool'):
      template_names.append('start_cthreads_{0:s}.c'.format(type_name))

    if with_input:
      template_names.append('start_with_input.c')

    if with_read_buffer_function:
      template_names.append('start_read_buffer_size.c')

    if with_input:
      if bfio_type == 'pool':
        template_names.append('start_with_input-bfio_pool.c')
      else:
        template_names.append('start_with_input-bfio_handle.c')

      template_names.append('open_source-start.c')

      for _, argument in test_options:
        if argument != 'offset':
          template_names.append('open_source-set_{0:s}.c'.format(argument))

      template_names.append('open_source-body.c')

      function_prototype = header_file.GetTypeFunction(
          type_name, 'open_extent_data_files')
      if function_prototype:
        template_names.append('open_source-extend_data_files.c')

      template_names.extend(['open_source-end.c', 'close_source.c'])

      test_options_function_arguments = [
          '     {0:s}'.format(function_argument)
          for function_argument in test_options_function_arguments]

      test_options_function_variables = [
          '\t{0:s}'.format(function_variable)
          for function_variable in test_options_function_variables]

      template_mappings['signature_type'] = signature_type
      template_mappings['test_options_function_arguments'] = ',\n'.join(
          test_options_function_arguments)
      template_mappings['test_options_function_variables'] = '\n'.join(
          test_options_function_variables)

    if template_names:
      template_filenames = [
          os.path.join(template_directory, template_name)
          for template_name in template_names]

      self._GenerateSections(
          template_filenames, template_mappings, output_writer, output_filename,
          access_mode='a')

    if with_input:
      del template_mappings['signature_type']
      del template_mappings['test_options_function_arguments']
      del template_mappings['test_options_function_variables']

    # Generate test data.
    test_data_directory = os.path.join('tests', 'data')
    if os.path.exists(test_data_directory):
      for directory_entry in sorted(os.listdir(test_data_directory)):
        test_type_name, _, test_data_suffix = directory_entry.partition('.')
        if test_type_name != type_name:
          continue

        test_data_suffix, _, test_data_index = test_data_suffix.rpartition('.')
        if test_data_suffix:
          test_data_suffix = '_{0:s}'.format(test_data_suffix)

        test_data_file = os.path.join(test_data_directory, directory_entry)
        with open(test_data_file, 'rb') as file_object:
          test_data = file_object.read()

        template_mappings['test_data'] = self._FormatTestData(test_data)
        template_mappings['test_data_size'] = len(test_data)
        template_mappings['test_data_index'] = test_data_index
        template_mappings['test_data_suffix'] = test_data_suffix

        template_filename = os.path.join(template_directory, 'test_data.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='a')

    # Generate a clone, compare and/or free test function if necessary.
    clone_function = None
    compare_function = None
    free_function = None

    for function_prototype in header_file.functions_per_name.values():
      for argument in function_prototype.arguments:
        argument_string = argument.CopyToString()

        if '_clone_function' in argument_string:
          _, _, clone_function = argument_string.partition('*')
          clone_function, _, _ = clone_function.partition(')')

        elif '_compare_function' in argument_string:
          _, _, compare_function = argument_string.partition('*')
          compare_function, _, _ = compare_function.partition(')')

        elif '_free_function' in argument_string:
          _, _, free_function = argument_string.partition('*')
          free_function, _, _ = free_function.partition(')')

    if free_function:
      value_name, _, _ = free_function.rpartition('_free_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'free_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if clone_function:
      value_name, _, _ = clone_function.rpartition('_clone_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'clone_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if compare_function:
      value_name, _, _ = compare_function.rpartition('_compare_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = os.path.join(template_directory, 'compare_function.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    have_extern = True
    tests_to_run = []
    tests_to_run_with_args = []
    tests_to_run_with_source = []

    have_extern = self._GenerateTypeTestInitializeFunction(
        project_configuration, template_mappings, type_name, 'initialize',
        have_extern, header_file, test_source_file, output_writer,
        output_filename, function_names, tests_to_run)

    have_extern = self._GenerateTypeTestWithFreeFunction(
        project_configuration, template_mappings, type_name, 'free',
        have_extern, header_file, output_writer, output_filename,
        function_names, tests_to_run, free_function=free_function)

    for type_function in ('empty', 'clear', 'clone', 'resize'):
      function_name, test_function_name, have_extern = (
          self._GenerateTypeTestFunction(
              project_configuration, template_mappings, type_name,
              type_function, have_extern, header_file, test_source_file,
              output_writer, output_filename))

      if test_function_name:
        tests_to_run.append((function_name, test_function_name))
        function_names.remove(function_name)

    if with_input:
      # TODO: fix libbfio having no open wide.
      # TODO: make handling open close more generic for libpff attachment handle.
      for type_function in (
          'open', 'open_wide', 'open_file_io_handle', 'open_file_io_pool'):
        have_extern = self._GenerateTypeTestOpenFunction(
            project_configuration, template_mappings, type_name, type_function,
            test_options, have_extern, header_file, output_writer,
            output_filename, function_names, tests_to_run_with_source)

      function_name, test_function_name, have_extern = self._GenerateTypeTest(
          project_configuration, template_mappings, type_name, 'close',
          have_extern, header_file, test_source_file, output_writer,
          output_filename, with_input=with_input)

      if test_function_name:
        tests_to_run_with_source.append((function_name, test_function_name))
        function_names.remove(function_name)

      self._GenerateTypeTestOpen(
          project_configuration, template_mappings, type_name, 'open_close',
          test_options, output_writer, output_filename)

      function_name = self._GetFunctionName(
          project_configuration, type_name, 'open_close')
      test_function_name = self._GetTestFunctionName(
          project_configuration, type_name, 'open_close')

      tests_to_run_with_source.append((function_name, test_function_name))

    template_mappings['type_size_name'] = type_size_name

    function_name_prefix = '{0:s}_{1:s}_'.format(
        project_configuration.library_name, type_name)
    function_name_prefix_length = len(function_name_prefix)

    internal_function_name_prefix = '{0:s}_internal_{1:s}_'.format(
        project_configuration.library_name, type_name)
    internal_function_name_prefix_length = len(internal_function_name_prefix)

    test_data = self._ReadTestDataFile(type_name)

    for function_name in function_names:
      if function_name.startswith(function_name_prefix):
        type_function = function_name[function_name_prefix_length:]
      elif function_name.startswith(internal_function_name_prefix):
        type_function = 'internal_{0:s}'.format(
            function_name[internal_function_name_prefix_length:])
      else:
        continue

      type_function_with_input = (with_input or (test_data and (
          type_function.startswith('copy_to_') or
          type_function.startswith('get_'))))

      _, test_function_name, have_extern = self._GenerateTypeTestFunction(
          project_configuration, template_mappings, type_name, type_function,
          have_extern, header_file, test_source_file, output_writer,
          output_filename, with_input=type_function_with_input)

      if type_function_with_input:
        tests_to_run_with_args.append((function_name, test_function_name))
      else:
        tests_to_run.append((function_name, test_function_name))

    del template_mappings['type_size_name']

    self._GenerateTypeTestDefineInternalEnd(
        template_mappings, have_extern, True, output_writer, output_filename)

    # TODO: create generic test for get_number_of_X API functions.
    # TODO: make tests condition for type with read_data on availability of data.

    self._GenerateTypeTestsMainFunction(
        project_configuration, template_mappings, type_name, test_options,
        tests_to_run, tests_to_run_with_args, tests_to_run_with_source,
        header_file, output_writer, output_filename)

    del template_mappings['bfio_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

    return True

  def _GenerateTypeTestsMainFunction(
      self, project_configuration, template_mappings, type_name, test_options,
      tests_to_run, tests_to_run_with_args, tests_to_run_with_source,
      header_file, output_writer, output_filename):
    """Generates the main function of a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_options (list[tuple[str, str]]): test options.
      tests_to_run (list[tuple[str, str]]): names of the library type function
          and its corresponding test function.
      tests_to_run_with_args (list[tuple[str, str]]): names of the library type
          function and its corresponding test function with arguments.
      tests_to_run_with_source (list[tuple[str, str]]): names of the library type
          function and its corresponding test function with a source argument.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    has_glob = self._HasGlob(project_configuration, type_name)
    with_offset = 'offset' in [argument for _, argument in test_options]

    if tests_to_run_with_source:
      test_getopt_string = []
      test_options_variable_declarations = []
      for option, argument in test_options:
        getopt_string = option
        if argument:
          getopt_string = '{0:s}:'.format(getopt_string)

        test_getopt_string.append(getopt_string)

        if argument == 'offset': 
          test_options_variable_declarations.extend([
              '\tsystem_character_t *option_{0:s} = NULL;'.format(argument),
              '\toff64_t {0:s}_offset = 0;'.format(type_name)])

        else:
          variable_declaration = (
              '\tsystem_character_t *option_{0:s} = NULL;').format(argument)
          test_options_variable_declarations.append(variable_declaration)

      if has_glob:
        test_options_variable_declarations.extend([
            '\tlibbfio_handle_t *file_io_handle = NULL;',
            '\tsystem_character_t **filenames = NULL;',
            '\tint filename_index = 0;',
            '\tint number_of_filenames = 0;'])

      variable_declaration = '\tsystem_character_t *source = NULL;'
      test_options_variable_declarations.append(variable_declaration)

      template_mappings['test_getopt_string'] = ''.join(test_getopt_string)
      template_mappings['test_options_variable_declarations'] = '\n'.join(
          sorted(test_options_variable_declarations))

      template_filename = os.path.join(
          template_directory, 'main-start-with_source-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['test_getopt_string']
      del template_mappings['test_options_variable_declarations']

      for option, argument in test_options:
        template_mappings['test_option'] = option
        template_mappings['test_option_argument'] = argument

        template_filename = os.path.join(
            template_directory, 'main-start-with_source-switch_case.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

        del template_mappings['test_option']
        del template_mappings['test_option_argument']

      template_filename = os.path.join(
          template_directory, 'main-start-with_source-end.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      if with_offset:
        template_filename = os.path.join(
            template_directory, 'main-option_offset.c')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

      template_filename = os.path.join(template_directory, 'main-notify_set.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    elif tests_to_run_with_args:
      template_filename = os.path.join(
          template_directory, 'main-start-with_test_data.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    else:
      template_filename = os.path.join(template_directory, 'main-start.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name, test_options,
        tests_to_run, header_file, output_writer, output_filename)

    if tests_to_run_with_source and has_glob:
      template_filename = 'main-with_glob-start.c'
    elif tests_to_run_with_source and with_offset:
      template_filename = 'main-with_offset-start.c'
    elif tests_to_run_with_source:
      template_filename = 'main-with_source-start.c'
    elif tests_to_run_with_args:
      template_filename = 'main-with_test_data-start.c'
    else:
      template_filename = None

    if template_filename:
      include_header_file = self._GetLibraryIncludeHeaderFile(
          project_configuration)

      signature_type = include_header_file.GetCheckSignatureType()

      test_data = self._ReadTestDataFile(type_name)

      template_mappings['signature_type'] = signature_type
      template_mappings['test_data_size'] = len(test_data)

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['signature_type']
      del template_mappings['test_data_size']

    if tests_to_run_with_source:
      self._GenerateTypeTestsMainTestsToRun(
          project_configuration, template_mappings, type_name, test_options,
          tests_to_run_with_source, header_file, output_writer, output_filename,
          indentation_level=2, with_input=True)

      if has_glob:
        open_source_arguments = ['\t\t          file_io_pool']
      else:
        open_source_arguments = ['\t\t          file_io_handle']
      for _, argument in test_options:
        if argument != 'offset':
          open_source_arguments.append(
              '\t\t          option_{0:s}'.format(argument))

      template_mappings['test_options_open_source_arguments'] = ',\n'.join(
          open_source_arguments)

      if with_offset:
        template_filename = 'main-with_source-tests_with_offset.c'
      else:
        template_filename = 'main-with_source-tests.c'

      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['test_options_open_source_arguments']

    if tests_to_run_with_source:
      indentation_level = 2
    else:
      indentation_level = 1

    self._GenerateTypeTestsMainTestsToRun(
        project_configuration, template_mappings, type_name, test_options,
        tests_to_run_with_args, header_file, output_writer, output_filename,
        indentation_level=indentation_level, with_args=True)

    if tests_to_run_with_source and has_glob:
      template_filename = 'main-with_glob-end.c'
    elif tests_to_run_with_source:
      template_filename = 'main-with_source-end.c'
    elif tests_to_run_with_args:
      template_filename = 'main-with_test_data-end.c'
    else:
      template_filename = None

    if template_filename:
      template_filename = os.path.join(template_directory, template_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if tests_to_run_with_source and has_glob:
      template_filename = 'main-end-with_glob.c'
    elif tests_to_run_with_source:
      template_filename = 'main-end-with_source.c'
    elif tests_to_run_with_args:
      template_filename = 'main-end-with_test_data.c'
    else:
      template_filename = 'main-end.c'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GenerateTypeTestsMainTestsToRun(
      self, project_configuration, template_mappings, type_name, test_options,
      tests_to_run, header_file, output_writer, output_filename,
      indentation_level=1, with_args=False, with_input=False):
    """Generates a type tests source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      test_options (list[tuple[str, str]]): test options.
      tests_to_run (list[tuple[str, str]]): names of the library type function
          and its corresponding test function.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      indentation_level (Optional[int]): Number of tabs to indent the run
          test macros.
      with_args (Optional[bool]): True if the tests to run have arguments.
      with_input (Optional[bool]): True if the tests to run have input.
    """
    if not tests_to_run:
      return

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    library_name_suffix = project_configuration.library_name_suffix.upper()

    last_have_extern = None
    last_have_wide_character_type = False

    tests_to_run_mappings = []
    for function_name, test_function_name in tests_to_run:
      function_prototype = header_file.functions_per_name.get(
          function_name, None)

      if not function_prototype:
        have_wide_character_type = False
        have_extern = last_have_extern
      else:
        have_wide_character_type = function_prototype.have_wide_character_type
        have_extern = function_prototype.have_extern

      if (have_wide_character_type != last_have_wide_character_type or
          have_extern != last_have_extern):

        if last_have_extern is None:
          self._GenerateTypeTestDefineInternalStart(
              template_mappings, True, have_extern, output_writer,
              output_filename)

        if tests_to_run_mappings:
          template_mappings['tests_to_run'] = '\n'.join(tests_to_run_mappings)
          tests_to_run_mappings = []

          template_filename = os.path.join(
              template_directory, 'main-tests_to_run.c')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='a')

        self._GenerateTypeTestDefineWideCharacterTypeEnd(
            template_mappings, last_have_wide_character_type,
            have_wide_character_type, output_writer, output_filename)

        if last_have_extern is not None:
          self._GenerateTypeTestDefineInternalEnd(
              template_mappings, last_have_extern, have_extern,
              output_writer, output_filename)
  
          self._GenerateTypeTestDefineInternalStart(
              template_mappings, last_have_extern, have_extern,
              output_writer, output_filename)

        self._GenerateTypeTestDefineWideCharacterTypeStart(
            template_mappings, last_have_wide_character_type,
            have_wide_character_type, output_writer, output_filename)

        last_have_wide_character_type = have_wide_character_type
        last_have_extern = have_extern

      if tests_to_run_mappings:
        tests_to_run_mappings.append('')

      indentation = '\t' * indentation_level

      if not test_function_name:
        tests_to_run_mappings.append(
            '{0:s}/* TODO: add tests for {1:s} */'.format(
                indentation, function_name))

      else:
        if with_args:
          test_to_run_mappings = [
              '{0:s}{1:s}_TEST_RUN_WITH_ARGS('.format(
                  indentation, library_name_suffix),
              '{0:s} "{1:s}",'.format(indentation, function_name),
              '{0:s} {1:s},'.format(indentation, test_function_name),
              '{0:s} {1:s} );'.format(indentation, type_name)]

        elif with_input:
          if (function_name.endswith('_close') and
              not function_name.endswith('_open_close')):
            test_to_run_mappings = [
                '{0:s}{1:s}_TEST_RUN('.format(indentation, library_name_suffix),
                '{0:s} "{1:s}",'.format(indentation, function_name),
                '{0:s} {1:s} );'.format(indentation, test_function_name)]

          else:
            test_to_run_mappings = [
                '{0:s}{1:s}_TEST_RUN_WITH_ARGS('.format(
                    indentation, library_name_suffix),
                '{0:s} "{1:s}",'.format(indentation, function_name),
                '{0:s} {1:s},'.format(indentation, test_function_name),
                '{0:s} source'.format(indentation) ]

            for _, argument in test_options:
              if argument != 'offset':
                test_to_run_mappings[-1] = '{0:s},'.format(test_to_run_mappings[-1])
                test_to_run_mappings.append('{0:s} option_{1:s}'.format(
                    indentation, argument))

            test_to_run_mappings[-1] = '{0:s} );'.format(test_to_run_mappings[-1])

        else:
          test_to_run_mappings = [
              '{0:s}{1:s}_TEST_RUN('.format(indentation, library_name_suffix),
              '{0:s} "{1:s}",'.format(indentation, function_name),
              '{0:s} {1:s} );'.format(indentation, test_function_name)]

        tests_to_run_mappings.extend(test_to_run_mappings)

    if tests_to_run_mappings:
      template_mappings['tests_to_run'] = '\n'.join(tests_to_run_mappings)
      tests_to_run_mappings = []

      template_filename = os.path.join(
          template_directory, 'main-tests_to_run.c')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      self._GenerateTypeTestDefineWideCharacterTypeEnd(
          template_mappings, last_have_wide_character_type,
          have_wide_character_type, output_writer, output_filename)

    self._GenerateTypeTestDefineInternalEnd(
        template_mappings, have_extern, True, output_writer, output_filename)

  def _GenerateTypeTestWithFreeFunction(
      self, project_configuration, template_mappings, type_name, type_function,
      last_have_extern, header_file, output_writer, output_filename,
      function_names, tests_to_run, free_function=None):
    """Generates a test for a type function with free function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      type_name (str): name of type.
      type_function (str): type function.
      last_have_extern (bool): True if the previous function prototype was
          externally available.
      header_file (LibraryHeaderFile): library header file.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
      function_names (list[str]): function names.
      tests_to_run (list[tuple[str, str]]): pairs of the function name and
          corresponding test function name that need to be run.
      free_function (Optional[str]): name of the free function.

    Returns:
      bool: True if the function prototype was externally available.
    """
    function_prototype = header_file.GetTypeFunction(type_name, type_function)
    if not function_prototype:
      return last_have_extern

    have_extern = function_prototype.have_extern

    self._GenerateTypeTestDefineInternalEnd(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    self._GenerateTypeTestDefineInternalStart(
        template_mappings, last_have_extern, have_extern, output_writer,
        output_filename)

    template_directory = os.path.join(self._template_directory, 'yal_test_type')

    if free_function:
      value_name, _, _ = free_function.rpartition('_free_function')
      self._SetValueNameInTemplateMappings(template_mappings, value_name)

      template_filename = '{0:s}_with_free_function.c'.format(type_function)
    else:
      template_filename = '{0:s}.c'.format(type_function)

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    function_name = self._GetFunctionName(
        project_configuration, type_name, type_function)
    test_function_name = self._GetTestFunctionName(
        project_configuration, type_name, type_function)

    tests_to_run.append((function_name, test_function_name))
    function_names.remove(function_name)

    return have_extern

  def _GetFunctionName(
      self, project_configuration, type_name, type_function):
    """Retrieves the function name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      type_function (str): type function.

    Returns:
      str: function name.
    """
    return '{0:s}_{1:s}_{2:s}'.format(
        project_configuration.library_name, type_name, type_function)

  def _GetLibraryTypes(self, project_configuration, makefile_am_file):
    """Determines the types defined in the library sources.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      makefile_am_file (MainMakefileAMFile): project main Makefile.am file.

    Returns:
      tuple: contains:
        list[str]: type names.
        list[str]: function names.
    """
    library_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.library_name)

    type_name_prefix = '{0:s}_'.format(project_configuration.library_name)
    type_name_prefix_length = len(type_name_prefix)

    include_file_prefix = '{0:s}_lib'.format(project_configuration.library_name)

    types = []
    functions = []
    for source_file_path in makefile_am_file.sources:
      if not source_file_path.endswith('.h'):
        continue

      # Skip library include header files.
      # TODO: check if library name matches local libraries.
      if (source_file_path.startswith(include_file_prefix) or
          source_file_path.endswith('_debug.h')):
        continue

      header_file_path = os.path.join(library_path, source_file_path)
      header_file = source_file.LibraryHeaderFile(header_file_path)
      header_file.Read(project_configuration)

      if not header_file.types:
        _, _, source_file_path = source_file_path[:-2].partition('_')
        if source_file_path not in (
            'definitions', 'extern', 'support', 'unused'):
          functions.append(source_file_path)
        continue

      for type_name in header_file.types:
        if not type_name.startswith(type_name_prefix):
          continue

        type_name = type_name[type_name_prefix_length:]
        types.append(type_name)

    # TODO: determine if the source file for functions actually contain functions
    if 'codepage' in functions:
      functions.remove('codepage')

    return types, functions

  def _GetTemplateMappings(
      self, project_configuration, api_functions, api_functions_with_input,
      api_types, api_types_with_input, api_pseudo_types, internal_functions,
      internal_types, python_functions, python_functions_with_input):
    """Retrieves the template mappings.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      api_functions (list[str]): names of API functions to test.
      api_functions_with_input (list[str]): names of API functions to test
          with input data.
      api_types (list[str]): names of API types to test.
      api_types_with_input (list[str]): names of API types to test with
          input data.
      api_pseudo_types (list[str]): names of API pseudo types to test.
      internal_functions (list[str]): names of internal functions to test.
      internal_types (list[str]): names of internal types to test.
      python_functions (list[str]): names of Python functions to test.
      python_functions_with_input (list[str]): names of Python functions to
          test with input data.

    Returns:
      dict[str, str]: string template mappings, where the key maps to the name
          of a template variable.
    """
    template_mappings = super(
        TestSourceFileGenerator, self)._GetTemplateMappings(
            project_configuration)

    library_tests = set(api_functions)
    library_tests = library_tests.union(set(api_types))
    library_tests = library_tests.union(set(internal_functions))
    library_tests = library_tests.union(set(internal_types))
    library_tests = sorted(library_tests)

    library_tests_with_input = set(api_types_with_input)
    library_tests_with_input = library_tests_with_input.union(
        set(api_functions_with_input))
    library_tests_with_input = sorted(library_tests_with_input)

    template_mappings['library_tests'] = ' '.join(library_tests)
    template_mappings['library_tests_with_input'] = ' '.join(
        library_tests_with_input)

    template_mappings['test_python_functions'] = ' '.join(
        sorted(python_functions))
    template_mappings['test_python_functions_with_input'] = ' '.join(
        sorted(python_functions_with_input))

    template_mappings['tests_option_sets'] = ' '.join(
        project_configuration.tests_option_sets)

    template_mappings['tests_input_glob'] = (
        project_configuration.tests_input_glob)

    template_mappings['tests_export_tool_option_sets'] = ' '.join(
        project_configuration.tests_export_tool_option_sets)
    template_mappings['tests_export_tool_options'] = (
        project_configuration.tests_export_tool_options)

    template_mappings['tests_info_tool_input_glob'] = (
        project_configuration.tests_info_tool_input_glob)
    template_mappings['tests_info_tool_option_sets'] = ' '.join(
        project_configuration.tests_info_tool_option_sets)
    template_mappings['tests_info_tool_options'] = (
        project_configuration.tests_info_tool_options)

    template_mappings['tests_verify_tool_option_sets'] = ' '.join(
        project_configuration.tests_verify_tool_option_sets)
    template_mappings['tests_verify_tool_options'] = (
        project_configuration.tests_verify_tool_options)

    template_mappings['alignment_padding'] = (
        ' ' * len(project_configuration.library_name_suffix))

    return template_mappings

  def _GetTestFunctionName(
      self, project_configuration, type_name, type_function):
    """Retrieves the test function name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.
      type_function (str): type function.

    Returns:
      str: test function name.
    """
    if type_function.startswith('internal_'):
      return '{0:s}_test_internal_{1:s}_{2:s}'.format(
          project_configuration.library_name_suffix, type_name,
          type_function[9:])

    return '{0:s}_test_{1:s}_{2:s}'.format(
        project_configuration.library_name_suffix, type_name, type_function)

  def _GetTestOptions(self, project_configuration, type_name):
    """Retrieves the test options.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      list[tuple[str, str]]: test options.
    """
    # TODO: determine test_options based on function prototypes
    test_options = []

    if (project_configuration.library_name == 'libbde' and
        type_name == 'volume'):
      # TODO: add support for startup key option
      # TODO: add support for keys option
      test_options.append(('o', 'offset'))
      test_options.append(('p', 'password'))
      test_options.append(('r', 'recovery_password'))

    elif (project_configuration.library_name == 'libfvde' and
          type_name == 'volume'):
      # TODO: add support for keys option
      test_options.append(('o', 'offset'))
      test_options.append(('p', 'password'))

    elif (project_configuration.library_name == 'libfsapfs' and
          type_name == 'container'):
      test_options.append(('o', 'offset'))
      test_options.append(('p', 'password'))

    elif (project_configuration.library_name == 'libfsext' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    elif (project_configuration.library_name == 'libfsfat' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    elif (project_configuration.library_name == 'libfshfs' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    elif (project_configuration.library_name == 'libfsntfs' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    elif (project_configuration.library_name == 'libfsrefs' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    elif (project_configuration.library_name == 'libluksde' and
          type_name == 'volume'):
      # TODO: add support for keys option
      test_options.append(('p', 'password'))

    elif (project_configuration.library_name == 'libqcow' and
          type_name == 'file'):
      # TODO: add support for keys option
      test_options.append(('p', 'password'))

    elif (project_configuration.library_name == 'libvshadow' and
          type_name == 'volume'):
      test_options.append(('o', 'offset'))

    return test_options

  def _GetTypeSizeName(self, project_configuration, type_name):
    """Retrieves the test size name.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      type_name (str): name of type.

    Returns:
      str: type size name.
    """
    # TODO: determine type_size_name based on function prototypes
    # TODO: add support libfvde and libvslvm
    if (type_name == 'file' and project_configuration.library_name in (
        'libqcow', 'libvhdi')):
      return 'media_size'

    if (type_name == 'handle' and project_configuration.library_name in (
        'libewf', 'libmodi', 'libodraw', 'libphdi', 'libsmraw', 'libvmdk')):
      return 'media_size'

    return 'size'

  def _GetValueTypeFromFunctionArgument(self, function_argument):
    """Deterines a value type based on the function argument.

    Args:
      function_argument (FunctionArgument): function argument.

    Returns:
      tuple[str, str]: value type and value name.
    """
    function_argument_string = function_argument.CopyToString()

    value_type, _, value_name = function_argument_string.partition(' ')

    value_name = value_name.lstrip('*')

    return value_type, value_name

  def _SortSources(self, output_filename):
    """Sorts the sources.

    Args:
      output_filename (str): path of the output file.
    """
    with io.open(output_filename, 'r', encoding='utf8') as file_object:
      lines = file_object.readlines()

    sources = None
    in_sources = False

    with io.open(output_filename, 'w', encoding='utf8') as file_object:
      for line in lines:
        stripped_line = line.strip()
        if stripped_line.endswith('_SOURCES = \\'):
          file_object.write(line)
          sources = []
          in_sources = True

        elif in_sources:
          if stripped_line:
            if stripped_line.endswith(' \\'):
              stripped_line = stripped_line[:-2]
            sources.append(stripped_line)

          else:
            sorted_lines = ' \\\n'.join(
                ['\t{0:s}'.format(filename) for filename in sorted(sources)])

            file_object.writelines(sorted_lines)
            file_object.write('\n')
            file_object.write(line)
            in_sources = False

        else:
          file_object.write(line)

  def _ReadTestDataFile(self, type_name, sequence_number=1):
    """Reads a test data file.

    Args:
      type_name (str): name of type.
      sequence_number (int): sequence number.

    Returns:
      bytes: contents of test data file.
    """
    test_data_filename = '{0:s}.{1:d}'.format(type_name, sequence_number)
    test_data_file = os.path.join('tests', 'data', test_data_filename)

    if not os.path.exists(test_data_file):
      return bytes()

    with open(test_data_file, 'rb') as file_object:
      return file_object.read()

  def Generate(self, project_configuration, output_writer):
    """Generates tests source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: fix fcache support of maximum_cache_entries
    # TODO: compare handle fdata and cdata differences, and includes
    # TODO: weave existing test files?
    # TODO: use data files to generate test data tests/input/.data/<name>
    # TODO: add support for options in configuration file to set option sets.
    # TODO: fix creation of fwsi_test_file_entry_(item) when include header
    # file contains (item).
    # TODO: fix libwrc message-table
    # TODO: handle libfsntfs $attribute_name
    # TODO: detect internal free functions
    # TODO: handle glob, options and options sets in test scripts.

    if not self._HasTests(project_configuration):
      return

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          'Missing: {0:s} skipping generation of include source files.'.format(
              self._library_makefile_am_path))
      return

    api_functions, api_functions_with_input = (
        include_header_file.GetAPIFunctionTestGroups())

    api_types, api_types_with_input = (
        include_header_file.GetAPITypeTestGroups())

    api_pseudo_types = include_header_file.GetAPIPseudoTypeTestGroups()

    types, internal_functions = self._GetLibraryTypes(
        project_configuration, makefile_am_file)

    public_functions = set(api_functions).union(set(api_functions_with_input))
    public_types = set(api_types).union(set(api_types_with_input))

    # TODO: handle types in non-matching header files.
    internal_types = []
    for type_name in types:
      if type_name in sorted(public_types):
        continue

      # Ignore internal type that are proxies by API types.
      if type_name.startswith('internal_'):
        continue

      internal_types.append(type_name)

    logging.info('Found public functions: {0:s}'.format(
        ', '.join(public_functions)))
    logging.info('Found public types: {0:s}'.format(', '.join(public_types)))
    logging.info('Found public pseudo types: {0:s}'.format(
        ', '.join(api_pseudo_types)))
    logging.info('Found internal functions: {0:s}'.format(
        ', '.join(internal_functions)))
    logging.info('Found internal types: {0:s}'.format(
        ', '.join(internal_types)))

    # TODO: handle non-template files differently.
    # TODO: yal_test_open_close.c handle file, handle, volume

    library_header = 'yal_test_{0:s}.h'.format(
        project_configuration.library_name)

    test_python_functions = []
    for function_name in self._PYTHON_FUNCTION_NAMES:
      output_filename = '{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join('tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions.append(function_name)

    test_python_functions_with_input = []
    for function_name in self._PYTHON_FUNCTION_WITH_INPUT_NAMES:
      output_filename = '{0:s}_test_{1:s}.py'.format(
          project_configuration.python_module_name, function_name)
      output_filename = os.path.join('tests', output_filename)
      if os.path.exists(output_filename):
        test_python_functions_with_input.append(function_name)

    template_mappings = self._GetTemplateMappings(
        project_configuration, api_functions, api_functions_with_input,
        api_types, api_types_with_input, api_pseudo_types, internal_functions,
        internal_types, test_python_functions, test_python_functions_with_input)

    for directory_entry in os.listdir(self._template_directory):
      # Ignore yal_test_library.h in favor of yal_test_libyal.h
      if directory_entry == library_header:
        continue

      # For libcerror skip generating yal_test_error.c.
      if (directory_entry == 'yal_test_error.c' and
          project_configuration.library_name == 'libcerror'):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      is_script = (
          directory_entry.endswith('.ps1') or directory_entry.endswith('.sh'))

      if directory_entry == 'yal_test_libyal.h':
        output_filename = '{0:s}_test_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      elif directory_entry.startswith('yal_test_'):
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[4:])

      elif directory_entry.startswith('pyyal_test_'):
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.python_module_name, directory_entry[6:])

      elif directory_entry.startswith('test_yal') and is_script:
        output_filename = 'test_{0:s}{1:s}'.format(
            project_configuration.library_name_suffix, directory_entry[8:])

      elif directory_entry.startswith('test_pyyal') and is_script:
        output_filename = 'test_{0:s}{1:s}'.format(
            project_configuration.python_module_name, directory_entry[10:])

      else:
        output_filename = directory_entry

      if directory_entry in (
            'test_library.ps1', 'test_library.sh', 'test_manpage.sh'):
        force_create = bool(public_functions) or bool(public_types)

      elif directory_entry in ('test_yalinfo.ps1', 'test_yalinfo.sh'):
        tool_name = '{0:s}info'.format(
            project_configuration.library_name_suffix)
        force_create = tool_name in project_configuration.tools_names

      elif directory_entry == 'yal_test_error.c':
        force_create = 'error' in api_functions

      elif directory_entry == 'yal_test_notify.c':
        force_create = 'notify' in api_functions

      else:
        force_create = False

      output_filename = os.path.join('tests', output_filename)
      if not force_create and not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if output_filename.endswith('.c'):
        self._SortIncludeHeaders(project_configuration, output_filename)

      elif output_filename.endswith('.sh'):
        # Set x-bit for a shell script (.sh).
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

    with_offset = False

    signature_type = include_header_file.GetCheckSignatureType()

    test_options = self._GetTestOptions(project_configuration, signature_type)
    if 'offset' in [argument for _, argument in test_options]:
      with_offset = True

    self._GenerateAPISupportTests(
        project_configuration, template_mappings, include_header_file,
        test_options, output_writer)

    if project_configuration.HasPythonModule():
      self._GeneratePythonModuleSupportTests(
          project_configuration, template_mappings, include_header_file,
          output_writer)

    python_module_types = []

    # Making a copy since the list is changed in the loop.
    for type_name in list(api_types):
      if (type_name == 'error' and
          project_configuration.library_name == 'libcerror'):
        continue

      test_options = self._GetTestOptions(project_configuration, type_name)
      if 'offset' in [argument for _, argument in test_options]:
        with_offset = True

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, test_options,
          output_writer)
      if not result:
        api_types.remove(type_name)
        logging.warning('Unable to generate tests for API type: {0:s}'.format(
            type_name))

      if project_configuration.HasPythonModule():
        python_module_types.append(type_name)
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer,
            with_offset=with_offset)

    # Making a copy since the list is changed in the loop.
    for type_name in list(api_types_with_input):
      test_options = self._GetTestOptions(project_configuration, type_name)
      if 'offset' in [argument for _, argument in test_options]:
        with_offset = True

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, test_options,
          output_writer, with_input=True)
      if not result:
        api_types_with_input.remove(type_name)
        logging.warning('Unable to generate tests for API type: {0:s}'.format(
            type_name))

      if project_configuration.HasPythonModule():
        python_module_types.append(type_name)
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer,
            with_input=True, with_offset=with_offset)

    # Making a copy since the list is changed in the loop.
    for type_name in list(api_pseudo_types):
      if (type_name == 'error' and
          project_configuration.library_name == 'libcerror'):
        continue

      test_options = self._GetTestOptions(project_configuration, type_name)
      if 'offset' in [argument for _, argument in test_options]:
        with_offset = True

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, test_options,
          output_writer)
      if not result:
        api_pseudo_types.remove(type_name)
        logging.warning(
            'Unable to generate tests for API pseudo type: {0:s}'.format(
                type_name))

      if project_configuration.HasPythonModule():
        self._GeneratePythonModuleTypeTests(
            project_configuration, template_mappings, type_name, output_writer,
            with_offset=with_offset)

    # Making a copy since the list is changed in the loop.
    for type_name in list(internal_types):
      test_options = self._GetTestOptions(project_configuration, type_name)
      if 'offset' in [argument for _, argument in test_options]:
        with_offset = True

      result = self._GenerateTypeTests(
          project_configuration, template_mappings, type_name, test_options,
          output_writer, is_internal=True)
      if not result:
        internal_types.remove(type_name)
        logging.warning(
            'Unable to generate tests for internal type: {0:s}'.format(
                type_name))

    # TODO: generate tests for internal functions

    with_input = bool(api_types_with_input)

    self._GenerateTestFunctions(
        project_configuration, template_mappings, output_writer, output_filename,
        with_input=with_input, with_offset=with_offset)

    self._GenerateMakefileAM(
        project_configuration, template_mappings, include_header_file,
        makefile_am_file, api_functions, api_functions_with_input, api_types,
        api_types_with_input, api_pseudo_types, internal_functions,
        internal_types, python_module_types, output_writer)
