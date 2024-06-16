# -*- coding: utf-8 -*-
"""The source file generator for tool source files."""

import os
import textwrap

from yaldevtools.source_generators import interface


class ToolSourceFileGenerator(interface.SourceFileGenerator):
  """Tool source file generator."""

  def _GenerateGetoptString(self, tool_options):
    """Generates a getopt string.

    Args:
      tool_options (list[tuple[str, str, st]])): tool options.

    Returns:
      str: getopt string.
    """
    getopt_string_segments = []

    for option, argument, _ in tool_options:
      getopt_string = option
      if argument:
        getopt_string = '{0:s}:'.format(getopt_string)

      getopt_string_segments.append(getopt_string)

    return ''.join(getopt_string_segments)

  def _GenerateGetoptSwitch(self, project_configuration, tool_options):
    """Generates a getopt switch.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      tool_options (list[tuple[str, str, st]])): tool options.

    Returns:
      str: getopt switch.
    """
    largest_argument_length = 0
    for _, argument, _ in tool_options:
      largest_argument_length = max(largest_argument_length, len(argument))

    # TODO: move getopt_switch into templates.
    getopt_switch = []
    for option, argument, _ in tool_options:
      if getopt_switch:
        getopt_switch.append('')

      if argument:
        getopt_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\toption_{0:s} = optarg;'.format(argument),
            '',
            '\t\t\t\tbreak;'])

      elif option == 'h':
        getopt_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\tusage_fprint(',
            '\t\t\t\t stdout );',
            '',
            '\t\t\t\treturn( EXIT_SUCCESS );'])

      elif option == 'v':
        getopt_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\tverbose = 1;',
            '',
            '\t\t\t\tbreak;'])

      elif option == 'V':
        getopt_switch.extend([
            '\t\t\tcase (system_integer_t) \'{0:s}\':'.format(option),
            '\t\t\t\t{0:s}_output_copyright_fprint('.format(
                project_configuration.tools_directory),
            '\t\t\t\t stdout );',
            '',
            '\t\t\t\treturn( EXIT_SUCCESS );'])

    return '\n'.join(getopt_switch)

  def _GenerateInfoHandleHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates an info handle header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'info_handle')

    template_filename = os.path.join(templates_path, 'header.h')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    template_filename = os.path.join(templates_path, 'includes.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_mappings['info_tool_source_type'] = (
        project_configuration.info_tool_source_type)

    for template_name in (
        'struct.h', 'initialize.h', 'free.h', 'signal_abort.h'):
      template_filename = os.path.join(templates_path, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    # TODO: add condition
    template_filename = os.path.join(templates_path, 'set_ascii_codepage.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    for template_name in ('open.h', 'close.h'):
      template_filename = os.path.join(templates_path, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['info_tool_source_type']

    template_filename = os.path.join(templates_path, 'footer.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

  def _GenerateInfoHandleSourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates an info handle source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'info_handle')

    template_filename = os.path.join(templates_path, 'header.c')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    template_filename = os.path.join(templates_path, 'includes.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_mappings['info_tool_source_type'] = (
        project_configuration.info_tool_source_type)

    for template_name in ('initialize.c', 'free.c', 'signal_abort.c'):
      template_filename = os.path.join(templates_path, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_filename, access_mode='a')

    # TODO: add condition
    template_filename = os.path.join(templates_path, 'set_ascii_codepage.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    for template_name in ('open.c', 'close.c'):
      template_filename = os.path.join(templates_path, template_name)
      self._GenerateSection(
          template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['info_tool_source_type']

  def _GenerateInfoTool(
      self, project_configuration, template_mappings, output_writer):
    """Generates an info tool.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    info_tool_name = '{0:s}info'.format(
        project_configuration.library_name_suffix)

    info_tool_filename = '{0:s}.c'.format(info_tool_name)
    info_tool_filename = os.path.join(
        project_configuration.tools_directory, info_tool_filename)

    if os.path.exists(info_tool_filename):
      output_filename = os.path.join(
          project_configuration.tools_directory, 'info_handle.h')
      self._GenerateInfoHandleHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'info_handle.c')
      self._GenerateInfoHandleSourceFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      self._GenerateInfoToolSourceFile(
          project_configuration, template_mappings, info_tool_name,
          output_writer, info_tool_filename)

  def _GenerateInfoToolSourceFile(
      self, project_configuration, template_mappings, info_tool_name,
      output_writer, output_filename):
    """Generates an info tool source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      info_tool_name (str): name of the info tool.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalinfo')

    info_tool_options = self._GetInfoToolOptions(
        project_configuration, info_tool_name)

    template_mappings['info_tool_name'] = info_tool_name
    template_mappings['info_tool_source_description'] = (
        project_configuration.info_tool_source_description)
    template_mappings['info_tool_source_type'] = (
        project_configuration.info_tool_source_type)

    template_filename = os.path.join(templates_path, 'header.c')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    template_filename = os.path.join(templates_path, 'includes.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._GenerateInfoToolSourceUsageFunction(
        project_configuration, template_mappings, info_tool_name,
        info_tool_options, output_writer, output_filename)

    template_filename = os.path.join(templates_path, 'signal_handler.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._GenerateInfoToolSourceMainFunction(
        project_configuration, template_mappings, info_tool_name,
        info_tool_options, output_writer, output_filename)

    del template_mappings['info_tool_name']
    del template_mappings['info_tool_source_description']
    del template_mappings['info_tool_source_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateInfoToolSourceMainFunction(
      self, project_configuration, template_mappings, info_tool_name,
      info_tool_options, output_writer, output_filename):
    """Generates an info tool source main function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      info_tool_name (str): name of the info tool.
      info_tool_options (list[tuple[str, str, st]])): info tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalinfo')

    variable_declarations = self._GenerateMainFunctionVariableDeclarations(
        info_tool_options)
    getopt_string = self._GenerateGetoptString(info_tool_options)
    getopt_switch = self._GenerateGetoptSwitch(
        project_configuration, info_tool_options)

    template_mappings['info_tool_getopt_string'] = getopt_string
    template_mappings['info_tool_options_switch'] = getopt_switch
    template_mappings['info_tool_options_variable_declarations'] = (
        variable_declarations)

    template_filename = os.path.join(templates_path, 'main-start.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['info_tool_getopt_string']
    del template_mappings['info_tool_options_switch']
    del template_mappings['info_tool_options_variable_declarations']

    # TODO: add condition
    template_filename = os.path.join(templates_path, 'main-option_codepage.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    template_filename = os.path.join(templates_path, 'main-end.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

  def _GenerateInfoToolSourceUsageFunction(
      self, project_configuration, template_mappings, info_tool_name,
      info_tool_options, output_writer, output_filename):
    """Generates an info tool source usage function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      info_tool_name (str): name of the info tool.
      info_tool_options (list[tuple[str, str, st]])): info tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalinfo')

    alignment_padding = '          '
    width = 80 - len(alignment_padding)
    text_wrapper = textwrap.TextWrapper(width=width)

    options_details = []
    options_usage = []
    options_without_arguments = []
    for option, argument, description in info_tool_options:
      description_lines = text_wrapper.wrap(description)

      description_line = description_lines.pop(0)
      details = '\tfprintf( stream, "\\t-{0:s}:{1:s}{2:s}\\n"'.format(
          option, alignment_padding, description_line)

      # TODO: determine indentation size
      for description_line in description_lines:
        options_details.append(details)
        details = '\t                 "\\t   {0:s}{1:s}\\n"'.format(
            alignment_padding, description_line)

      details = '{0:s} );'.format(details)
      options_details.append(details)

      if not argument:
        options_without_arguments.append(option)
      else:
        usage = '[ -{0:s} {1:s} ]'.format(option, argument)
        options_usage.append(usage)

    usage = '[ -{0:s} ]'.format(''.join(options_without_arguments))
    options_usage.append(usage)

    if project_configuration.info_tool_source_type:
      options_usage.append(project_configuration.info_tool_source_type)

    usage = 'Usage: {0:s} '.format(info_tool_name)
    usage_length = len(usage)
    alignment_padding = ' ' * usage_length
    options_usage = ' '.join(options_usage)

    width = 80 - usage_length
    text_wrapper = textwrap.TextWrapper(width=width)

    usage_lines = text_wrapper.wrap(options_usage)

    info_tool_usage = []
    usage_line = usage_lines.pop(0)
    usage = '\tfprintf( stream, "{0:s}{1:s}\\n"'.format(usage, usage_line)

    for usage_line in usage_lines:
      info_tool_usage.append(usage)
      usage = '\t                 "{0:s}{1:s}\\n"'.format(
          alignment_padding, usage_line)

    usage = '{0:s}\\n" );'.format(usage[:-1])
    info_tool_usage.append(usage)

    template_mappings['info_tool_options'] = '\n'.join(options_details)
    template_mappings['info_tool_usage'] = '\n'.join(info_tool_usage)

    template_filename = os.path.join(templates_path, 'usage.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['info_tool_options']
    del template_mappings['info_tool_usage']

  def _GenerateMainFunctionVariableDeclarations(self, tool_options):
    """Generates the variable declarations of the main function.

    Args:
      tool_options (list[tuple[str, str, st]])): tool options.

    Returns:
      str: variable declarations.
    """
    largest_argument_length = 0
    for _, argument, _ in tool_options:
      largest_argument_length = max(largest_argument_length, len(argument))

    variable_declarations = []
    for _, argument, _ in tool_options:
      if argument:
        alignment_padding = ' ' * (largest_argument_length - len(argument))
        variable_declaration = (
            '\tsystem_character_t *option_{0:s}{1:s} = NULL;').format(
                argument, alignment_padding)
        variable_declarations.append(variable_declaration)

    return '\n'.join(sorted(variable_declarations))

  def _GenerateMountDokanHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount dokan header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_dokan')

    template_names = [
        'header.h', 'CreateFile.h', 'OpenDirectory.h', 'CloseFile.h',
        'ReadFile.h', 'FindFiles.h', 'GetFileInformation.h',
        'GetVolumeInformation.h', 'Umount.h', 'footer.h']

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountDokanSourceFile(
      self, project_configuration, template_mappings, mount_tool_name,
      output_writer, output_filename):
    """Generates a mount dokan source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_dokan')

    template_names = [
        'header.c', 'CreateFile.c', 'OpenDirectory.c', 'CloseFile.c',
        'ReadFile.c']

    # TODO: set option via configuration
    if project_configuration.library_name in (
        'libfsext', 'libfsfat', 'libfsxfs'):
      template_names.append('FindFiles-without_parent.c')
    else:
      template_names.append('FindFiles-with_parent.c')

    template_names.extend([
        'GetFileInformation.c', 'GetVolumeInformation.c', 'Umount.c',
        'footer.c'])

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    template_mappings['mount_tool_name'] = mount_tool_name

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_name']

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountFileEntryHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount file entry header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_file_entry')

    template_names = ['header.h', 'initialize.h', 'free.h']

    # TODO: set option via configuration
    if project_configuration.library_name not in (
        'libfsext', 'libfsfat'):
      template_names.append('get_parent_file_entry.h')

    template_names.extend([
        'get_creation_time.h', 'get_access_time.h', 'get_modification_time.h',
        'get_inode_change_time.h', 'get_file_mode.h', 'get_name_size.h',
        'get_name.h'])

    # TODO: set option via configuration
    if project_configuration.library_name in (
        'libfsapfs', 'libfsext'):
      template_names.append('get_symbolic_link_target.h')

    template_names.extend([
        'get_sub_file_entries.h', 'read_buffer_at_offset.h', 'get_size.h',
        'footer.h'])

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_description'] = (
        mount_tool_file_entry_type.replace('_', ' '))
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_description']
    del template_mappings['mount_tool_file_entry_type_name']

    self._CorrectDescriptionSpelling(
        project_configuration.mount_tool_file_entry_type, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountFileEntrySourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount file entry source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_file_entry')

    template_names = ['header.c', 'includes.c', 'initialize.c']

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend(['free.c', 'get_parent_file_entry.c'])
    else:
      template_names.append('free-file_system_type.c')

      # TODO: set option via configuration
      if project_configuration.library_name not in (
          'libfsext', 'libfsfat'):
        template_names.append('get_parent_file_entry-file_system_type.c')

    file_entry_creation_time_type = (
        project_configuration.mount_tool_file_entry_creation_time_type)
    if not file_entry_creation_time_type:
      template_name = 'get_creation_time-mounted_timestamp.c'

    elif not project_configuration.mount_tool_file_system_type:
      template_name = 'get_creation_time-{0:s}_and_mounted_timestamp.c'.format(
          file_entry_creation_time_type)

    else:
      template_name = 'get_creation_time-{0:s}.c'.format(
          file_entry_creation_time_type)

    template_names.append(template_name)

    file_entry_access_time_type = (
        project_configuration.mount_tool_file_entry_access_time_type)
    if not file_entry_access_time_type:
      template_name = 'get_access_time-mounted_timestamp.c'

    elif not project_configuration.mount_tool_file_system_type:
      template_name = 'get_access_time-{0:s}_and_mounted_timestamp.c'.format(
          file_entry_access_time_type)

    else:
      template_name = 'get_access_time-{0:s}.c'.format(
          file_entry_access_time_type)

    template_names.append(template_name)

    file_entry_modification_time_type = (
        project_configuration.mount_tool_file_entry_modification_time_type)
    if not file_entry_modification_time_type:
      template_name = 'get_modification_time-mounted_timestamp.c'

    elif not project_configuration.mount_tool_file_system_type:
      template_name = (
          'get_modification_time-{0:s}_and_mounted_timestamp.c'.format(
              file_entry_modification_time_type))

    else:
      template_name = 'get_modification_time-{0:s}.c'.format(
          file_entry_modification_time_type)

    template_names.append(template_name)

    file_entry_inode_change_time_type = (
        project_configuration.mount_tool_file_entry_inode_change_time_type)
    if not file_entry_inode_change_time_type:
      template_name = 'get_inode_change_time-mounted_timestamp.c'

    elif not project_configuration.mount_tool_file_system_type:
      template_name = (
          'get_inode_change_time-{0:s}_and_mounted_timestamp.c'.format(
              file_entry_inode_change_time_type))

    else:
      template_name = 'get_inode_change_time-{0:s}.c'.format(
          file_entry_inode_change_time_type)

    template_names.append(template_name)

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('get_file_mode.c')
    else:
      template_names.append('get_file_mode-file_system_type.c')

    template_names.append('get_name.c')

    # TODO: set option via configuration
    if project_configuration.library_name in (
        'libfsapfs', 'libfsext'):
      template_names.append('get_symbolic_link_target.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('get_sub_file_entries.c')
    else:
      template_names.append('get_sub_file_entries-file_system_type.c')

    template_names.append('read_buffer_at_offset.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('get_size.c')
    else:
      template_names.append('get_size-file_system_type.c')

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    file_entry_access_time_value = (
        project_configuration.mount_tool_file_entry_access_time_value)
    template_mappings['mount_tool_file_entry_access_time_value'] = (
        file_entry_access_time_value)
    template_mappings['mount_tool_file_entry_access_time_value_description'] = (
        file_entry_access_time_value.replace('_', ' '))

    file_entry_creation_time_value = (
        project_configuration.mount_tool_file_entry_creation_time_value)
    template_mappings['mount_tool_file_entry_creation_time_value'] = (
        file_entry_creation_time_value)
    template_mappings[
        'mount_tool_file_entry_creation_time_value_description'] = (
            file_entry_creation_time_value.replace('_', ' '))

    file_entry_inode_change_time_value = (
        project_configuration.mount_tool_file_entry_inode_change_time_value)
    template_mappings['mount_tool_file_entry_inode_change_time_value'] = (
        file_entry_inode_change_time_value)
    template_mappings[
        'mount_tool_file_entry_inode_change_time_value_description'] = (
            file_entry_inode_change_time_value.replace('_', ' '))

    file_entry_modification_time_value = (
        project_configuration.mount_tool_file_entry_modification_time_value)
    template_mappings['mount_tool_file_entry_modification_time_value'] = (
        file_entry_modification_time_value)
    template_mappings[
        'mount_tool_file_entry_modification_time_value_description'] = (
            file_entry_modification_time_value.replace('_', ' '))

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_description'] = (
        mount_tool_file_entry_type.replace('_', ' '))
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)

    mount_tool_file_entry_type_size_value = (
        project_configuration.mount_tool_file_entry_type_size_value or '')

    template_mappings['mount_tool_file_entry_type_size_value'] = (
        mount_tool_file_entry_type_size_value)
    template_mappings['mount_tool_file_entry_type_size_value_description'] = (
        mount_tool_file_entry_type_size_value.replace('_', ' '))

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_access_time_value']
    del template_mappings['mount_tool_file_entry_access_time_value_description']
    del template_mappings['mount_tool_file_entry_creation_time_value']
    del template_mappings[
        'mount_tool_file_entry_creation_time_value_description']
    del template_mappings['mount_tool_file_entry_inode_change_time_value']
    del template_mappings[
        'mount_tool_file_entry_inode_change_time_value_description']
    del template_mappings['mount_tool_file_entry_modification_time_value']
    del template_mappings[
        'mount_tool_file_entry_modification_time_value_description']
    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_description']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_file_entry_type_size_value']
    del template_mappings['mount_tool_file_entry_type_size_value_description']

    self._CorrectDescriptionSpelling(
        project_configuration.mount_tool_file_entry_type, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateMountFileSystemHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount file system header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_file_system')

    template_names = ['header.h', 'includes-start.h']

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('includes-file_entry_type_array.h')
    else:
      template_names.append('includes-file_system_type.h')

    template_names.extend([
        'includes-end.h', 'struct-start.h', 'struct-mounted_timestamp.h'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend([
          'struct-path_prefix.h', 'struct-file_entry_type_array.h'])
    else:
      template_names.append('struct-file_system_type.h')

    template_names.extend([
        'struct-end.h', 'initialize.h', 'free.h', 'signal_abort.h'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('set_path_prefix.h')
    else:
      template_names.extend([
          'set_file_system_type.h', 'get_file_system_type.h'])

    template_names.append('get_mounted_timestamp.h')

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend([
          'get_number_of_file_entry_types.h', 'get_file_entry_type_by_index.h'])

    template_names.append('get_file_entry_type_by_path.h')

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend([
          'append_file_entry_type.h', 'get_path_from_file_entry_index.h'])
    else:
      template_names.append('get_filename_from_file_entry_type.h')

    template_names.append('footer.h')

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_description'] = (
        mount_tool_file_entry_type.replace('_', ' '))
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)

    file_system_type = project_configuration.mount_tool_file_system_type
    if not file_system_type:
      file_system_type = mount_tool_file_entry_type

    template_mappings['mount_tool_file_system_type'] = file_system_type
    template_mappings['mount_tool_file_system_type_description'] = (
        file_system_type.replace('_', ' '))
    template_mappings['mount_tool_file_system_type_name'] = (
        '{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, file_system_type))

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_description']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_file_system_type']
    del template_mappings['mount_tool_file_system_type_description']
    del template_mappings['mount_tool_file_system_type_name']

    self._CorrectDescriptionSpelling(
        project_configuration.mount_tool_file_entry_type, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountFileSystemSourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount file system source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_file_system')

    template_names = ['header.c', 'includes-start.c']

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('includes-file_entry_type_array.c')
    else:
      template_names.append('includes-file_system_type.c')

    template_names.extend(['includes-end.c', 'initialize-start.c'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('initialize-file_entry_type_array.c')

    template_names.extend(['initialize-end.c', 'free-start.c'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('free-path_prefix.c')
      template_names.append('free-file_entry_type_array.c')

    template_names.append('free-end.c')

    # TODO: add support for signal abort base type for libvslvm.

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend(['signal_abort.c', 'set_path_prefix.c'])
    else:
      template_names.extend([
          'signal_abort-file_system_type.c', 'set_file_system_type.c',
          'get_file_system_type.c'])

    template_names.append('get_mounted_timestamp.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.extend([
          'get_number_of_file_entry_types.c', 'get_file_entry_type_by_index.c',
          'get_file_entry_type_by_path.c', 'append_file_entry_type.c',
          'get_path_from_file_entry_index.c'])
    else:
      template_names.extend([
          'get_file_entry_type_by_path-file_system_type.c',
          'get_filename_from_file_entry_type.c'])

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_description'] = (
        mount_tool_file_entry_type.replace('_', ' '))
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)

    file_system_type = project_configuration.mount_tool_file_system_type
    if not file_system_type:
      file_system_type = mount_tool_file_entry_type

    template_mappings['mount_tool_file_system_type'] = file_system_type
    template_mappings['mount_tool_file_system_type_description'] = (
        file_system_type.replace('_', ' '))
    template_mappings['mount_tool_file_system_type_name'] = (
        '{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, file_system_type))

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_description']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_file_system_type']
    del template_mappings['mount_tool_file_system_type_description']
    del template_mappings['mount_tool_file_system_type_name']

    self._CorrectDescriptionSpelling(
        project_configuration.mount_tool_file_entry_type, output_filename)
    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)

  def _GenerateMountFuseSourceFile(
      self, project_configuration, template_mappings, mount_tool_name,
      output_writer, output_filename):
    """Generates a mount fuse source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_fuse')

    template_names = ['header.c', 'includes.c', 'body-start.c']

    if project_configuration.HasMountToolsFeatureExtendedAttributes():
      template_names.append('defines-getxattr.c')

    template_names.extend([
        'set_stat_info.c', 'filldir.c', 'open.c', 'read.c', 'release.c'])

    if project_configuration.HasMountToolsFeatureExtendedAttributes():
      template_names.extend(['getxattr.c', 'listxattr.c'])

    template_names.extend([
        'opendir.c', 'readdir.c', 'releasedir.c', 'getattr.c'])

    if project_configuration.HasMountToolsFeatureSymbolicLink():
      template_names.append('readlink.c')

    template_names.extend(['destroy.c', 'body-end.c'])

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)
    template_mappings['mount_tool_name'] = mount_tool_name

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_name']

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountHandleHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount handle header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_handle')

    template_names = ['header.h', 'includes-start.h']

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('includes-file_io_handle.h')

    template_names.append('includes-end.h')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('definitions-format.h')

    template_names.append('struct-start.h')

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('struct-basename.h')

    template_names.append('struct-file_system.h')

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('struct-codepage.h')

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      template_names.append('struct-encrypted_root_plist.h')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libfsapfs':
      template_names.append('struct-file_system_index.h')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('struct-format.h')

    if project_configuration.HasMountToolsFeatureKeys():
      if project_configuration.library_name == 'libbde':
        template_names.append('struct-keys-libbde.h')
      else:
        template_names.append('struct-keys.h')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('struct-offset.h')

    if project_configuration.HasMountToolsFeaturePassword():
      template_names.append('struct-password.h')

    if project_configuration.HasMountToolsFeatureRecoveryPassword():
      template_names.append('struct-recovery_password.h')

    if project_configuration.HasMountToolsFeatureStartupKey():
      template_names.append('struct-startup_key.h')

    if project_configuration.HasMountToolsFeatureUnlock():
      template_names.append('struct-is_locked.h')

    template_names.append('struct-end.h')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('system_string_copy_from_64_bit_in_decimal.h')

    template_names.extend(['initialize.h', 'free.h', 'signal_abort.h'])

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('set_basename.h')

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('set_codepage.h')

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      template_names.append('set_encrypted_root_plist.h')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libfsapfs':
      template_names.append('set_file_system_index.h')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('set_format.h')

    if project_configuration.HasMountToolsFeatureKeys():
      template_names.append('set_keys.h')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('set_offset.h')

    if project_configuration.HasMountToolsFeaturePassword():
      template_names.append('set_password.h')

    if project_configuration.HasMountToolsFeatureRecoveryPassword():
      template_names.append('set_recovery_password.h')

    if project_configuration.HasMountToolsFeatureStartupKey():
      template_names.append('set_startup_key.h')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('set_path_prefix.h')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('open-multi_source.h')
    else:
      template_names.append('open.h')

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('open_parent.h')

    template_names.append('close.h')

    if project_configuration.HasMountToolsFeatureUnlock():
      template_names.append('is_locked.h')

    template_names.extend(['get_file_entry_by_path.h', 'footer.h'])

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)
    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_source_type']

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountHandleSourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount handle source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_handle')

    template_names = ['header.c', 'includes-start.c']

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('includes-codepage.c')

    if project_configuration.HasMountToolsFeatureKeys():
      if project_configuration.library_name == 'libbde':
        template_names.append('includes-keys-libbde.c')
      else:
        template_names.append('includes-keys.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('includes-file_io_handle.c')

    template_names.append('includes-end.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('file_io_handle.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('system_string_copy_from_64_bit_in_decimal.c')

    template_names.append('initialize-start.c')

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('initialize-codepage.c')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('initialize-format.c')

    template_names.extend(['initialize-end.c', 'free-start.c'])

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('free-basename.c')

    template_names.append('free-file_system.c')

    if project_configuration.HasMountToolsFeatureKeys():
      template_names.append('free-keys.c')

    template_names.extend(['free-end.c', 'signal_abort.c'])

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('set_basename.c')

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('set_codepage.c')

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      template_names.append('set_encrypted_root_plist.c')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libfsapfs':
      template_names.append('set_file_system_index.c')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('set_format.c')

    if project_configuration.HasMountToolsFeatureKeys():
      if project_configuration.library_name == 'libbde':
        template_names.append('set_keys-libbde.c')
      else:
        template_names.append('set_keys.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('set_offset.c')

    if not project_configuration.mount_tool_base_type:
      if project_configuration.HasMountToolsFeaturePassword():
        template_names.append('set_password.c')

      if project_configuration.HasMountToolsFeatureRecoveryPassword():
        template_names.append('set_recovery_password.c')

      if project_configuration.HasMountToolsFeatureStartupKey():
        template_names.append('set_startup_key.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('set_path_prefix.c')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('open-start-multi_source.c')
    else:
      template_names.append('open-start.c')

    template_names.append('open-variables-start.c')

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('open-variables-basename.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('open-variables-glob.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('open-variables-file_io_handle.c')

    if project_configuration.mount_tool_base_type:
      if project_configuration.library_name == 'libfsapfs':
        template_names.append('open-variables-file_system_index.c')

    template_names.append('open-variables-end.c')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('open-check_arguments-multi_source.c')
    else:
      template_names.append('open-check_arguments.c')

    if project_configuration.HasMountToolsFeatureParent():
      if project_configuration.HasMountToolsFeatureMultiSource():
        template_names.append('open-basename-multi_source.c')
      else:
        template_names.append('open-basename.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('open-glob.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('open-offset.c')

    template_names.append('open-initialize.c')

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      template_names.append('open-encrypted_root_plist.c')

    if project_configuration.HasMountToolsFeatureKeys():
      if project_configuration.library_name == 'libbde':
        template_names.append('open-keys-libbde.c')
      else:
        template_names.append('open-keys.c')

    if project_configuration.HasMountToolsFeaturePassword():
      template_names.append('open-password.c')

    if project_configuration.HasMountToolsFeatureRecoveryPassword():
      template_names.append('open-recovery_password.c')

    if project_configuration.HasMountToolsFeatureStartupKey():
      template_names.append('open-startup_key.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('open-open-file_io_handle.c')
    elif project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('open-open-multi_source.c')
    else:
      template_names.append('open-open.c')

    if project_configuration.library_name == 'libfsapfs':
      template_names.append('open-file_system_index.c')

    if project_configuration.HasMountToolsFeatureUnlock():
      template_names.append('open-is_locked.c')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('open-format.c')

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('open-open_parent.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('open-append_file_system_type.c')
    else:
      template_names.append('open-set_file_system_type.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('open-free-glob.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('open-set-file_io_handle.c')

    template_names.append('open-on_error.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('open-on_error-glob.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('open-on_error-file_io_handle.c')

    template_names.append('open-end.c')

    if project_configuration.HasMountToolsFeatureParent():
      template_names.append('open_parent.c')

    template_names.extend(['close-start.c', 'close-variables-start.c'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('close-variables-no_file_system_type.c')

    template_names.extend(['close-variables-end.c', 'close-check_arguments.c'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('close-close.c')
    else:
      template_names.append('close-close-file_system_type.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('close-file_io_handle.c')

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('close-end.c')
    else:
      template_names.append('close-end-file_system_type.c')

    if project_configuration.HasMountToolsFeatureUnlock():
      template_names.append('is_locked.c')

    template_names.extend([
        'get_file_entry_by_path-start.c',
        'get_file_entry_by_path-variables.c',
        'get_file_entry_by_path-body.c',
        'get_file_entry_by_path-file_entry_initialize.c'])

    if not project_configuration.mount_tool_file_system_type:
      template_names.append('get_file_entry_by_path-end.c')
    else:
      template_names.append('get_file_entry_by_path-end-file_system_type.c')

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_file_entry_type = (
        project_configuration.mount_tool_file_entry_type or '')

    base_type = project_configuration.mount_tool_base_type
    if not base_type:
      base_type = project_configuration.mount_tool_file_system_type
    if not base_type:
      base_type = mount_tool_file_entry_type

    template_mappings['mount_tool_base_type'] = base_type
    template_mappings['mount_tool_base_type_description'] = (
        base_type.replace('_', ' '))
    template_mappings['mount_tool_base_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, base_type)

    template_mappings['mount_tool_file_entry_type'] = mount_tool_file_entry_type
    template_mappings['mount_tool_file_entry_type_description'] = (
        mount_tool_file_entry_type.replace('_', ' '))
    template_mappings['mount_tool_file_entry_type_name'] = '{0:s}_{1:s}'.format(
        project_configuration.library_name_suffix, mount_tool_file_entry_type)

    file_system_type = project_configuration.mount_tool_file_system_type
    if not file_system_type:
      file_system_type = mount_tool_file_entry_type

    template_mappings['mount_tool_file_system_type'] = file_system_type
    template_mappings['mount_tool_file_system_type_description'] = (
        file_system_type.replace('_', ' '))
    template_mappings['mount_tool_file_system_type_name'] = (
        '{0:s}_{1:s}'.format(
            project_configuration.library_name_suffix, file_system_type))

    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)
    template_mappings['mount_tool_source_type_description'] = (
        project_configuration.mount_tool_source_type.replace('_', ' '))

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['mount_tool_base_type']
    del template_mappings['mount_tool_base_type_description']
    del template_mappings['mount_tool_base_type_name']
    del template_mappings['mount_tool_file_entry_type']
    del template_mappings['mount_tool_file_entry_type_description']
    del template_mappings['mount_tool_file_entry_type_name']
    del template_mappings['mount_tool_file_system_type']
    del template_mappings['mount_tool_file_system_type_description']
    del template_mappings['mount_tool_file_system_type_name']
    del template_mappings['mount_tool_source_type']
    del template_mappings['mount_tool_source_type_description']

    if base_type:
      self._CorrectDescriptionSpelling(base_type, output_filename)

    self._CorrectDescriptionSpelling(
        project_configuration.mount_tool_file_entry_type, output_filename)

    if file_system_type:
      self._CorrectDescriptionSpelling(file_system_type, output_filename)

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)

  def _GenerateMountPathStringHeaderFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount path string header file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_path_string')

    template_filename = os.path.join(templates_path, 'mount_path_string.h')
    self._GenerateSection(
        template_filename, template_mappings, output_filename)

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountPathStringSourceFile(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates a mount path string source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'mount_path_string')

    template_filename = os.path.join(templates_path, 'mount_path_string.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename)

    self._SortIncludeHeaders(project_configuration, output_filename)

  def _GenerateMountTool(
      self, project_configuration, template_mappings, output_writer):
    """Generates a mount tool.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    mount_tool_name = '{0:s}mount'.format(
        project_configuration.library_name_suffix)

    mount_tool_filename = '{0:s}.c'.format(mount_tool_name)
    mount_tool_filename = os.path.join(
        project_configuration.tools_directory, mount_tool_filename)

    if os.path.exists(mount_tool_filename):
      if project_configuration.mount_tool_file_system_type:
        output_filename = os.path.join(
            project_configuration.tools_directory, 'mount_path_string.h')
        self._GenerateMountPathStringHeaderFile(
            project_configuration, template_mappings, output_writer,
            output_filename)

        output_filename = os.path.join(
            project_configuration.tools_directory, 'mount_path_string.c')
        self._GenerateMountPathStringSourceFile(
            project_configuration, template_mappings, output_writer,
            output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_file_entry.h')
      self._GenerateMountFileEntryHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_file_entry.c')
      self._GenerateMountFileEntrySourceFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_file_system.h')
      self._GenerateMountFileSystemHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_file_system.c')
      self._GenerateMountFileSystemSourceFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_handle.h')
      self._GenerateMountHandleHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_handle.c')
      self._GenerateMountHandleSourceFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_dokan.h')
      self._GenerateMountDokanHeaderFile(
          project_configuration, template_mappings, output_writer,
          output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_dokan.c')
      self._GenerateMountDokanSourceFile(
          project_configuration, template_mappings, mount_tool_name,
          output_writer, output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_fuse.h')
      self._GenerateSectionsFromOperationsFile(
          'mount_fuse.h.yaml', 'main', project_configuration,
          template_mappings, output_filename)

      output_filename = os.path.join(
          project_configuration.tools_directory, 'mount_fuse.c')
      self._GenerateMountFuseSourceFile(
          project_configuration, template_mappings, mount_tool_name,
          output_writer, output_filename)
      # self._GenerateSectionsFromOperationsFile(
      #     'mount_fuse.c.yaml', 'main', project_configuration,
      #     template_mappings, output_filename)

      self._GenerateMountToolSourceFile(
          project_configuration, template_mappings, mount_tool_name,
          output_writer, mount_tool_filename)

  def _GenerateMountToolSourceFile(
      self, project_configuration, template_mappings, mount_tool_name,
      output_writer, output_filename):
    """Generates a mount tool source file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalmount')

    template_names = ['header.c', 'includes-start.c']

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('includes-rlimit.c')

    template_names.append('includes-yaltools.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('includes-glob.c')

    template_names.append('includes-end.c')

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    mount_tool_options = self._GetMountToolOptions(
        project_configuration, mount_tool_name)

    template_mappings['mount_tool_name'] = mount_tool_name
    template_mappings['mount_tool_path_prefix'] = (
        project_configuration.mount_tool_path_prefix)
    template_mappings['mount_tool_source_description'] = (
        project_configuration.mount_tool_source_description)
    template_mappings['mount_tool_source_description_long'] = (
        project_configuration.mount_tool_source_description_long)
    template_mappings['mount_tool_source_type'] = (
        project_configuration.mount_tool_source_type)

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    self._GenerateMountToolSourceUsageFunction(
        project_configuration, template_mappings, mount_tool_name,
        mount_tool_options, output_writer, output_filename)

    template_filename = os.path.join(templates_path, 'signal_handler.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    self._GenerateMountToolSourceMainFunction(
        project_configuration, template_mappings, mount_tool_name,
        mount_tool_options, output_writer, output_filename)

    del template_mappings['mount_tool_name']
    del template_mappings['mount_tool_path_prefix']
    del template_mappings['mount_tool_source_description']
    del template_mappings['mount_tool_source_description_long']
    del template_mappings['mount_tool_source_type']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)

  def _GenerateMountToolSourceMainFunction(
      self, project_configuration, template_mappings, mount_tool_name,
      mount_tool_options, output_writer, output_filename):
    """Generates a mount tool source main function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      mount_tool_options (list[tuple[str, str, st]])): mount tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalmount')

    file_system_type = project_configuration.mount_tool_file_system_type

    variable_declarations = self._GenerateMainFunctionVariableDeclarations(
        mount_tool_options)
    getopt_string = self._GenerateGetoptString(mount_tool_options)
    getopt_switch = self._GenerateGetoptSwitch(
        project_configuration, mount_tool_options)

    template_names = ['main-start.c']

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('main-variables-rlimit.c')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('main-variables-multi_source.c')
    else:
      template_names.append('main-variables.c')

    if not file_system_type:
      template_names.append('main-variables-path_prefix.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('main-variables-glob.c')

    template_names.append('main-locale.c')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('main-getopt-multi_source.c')
    else:
      template_names.append('main-getopt.c')

    template_names.append('main-verbose.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('main-initialize-glob.c')

    template_names.append('main-initialize.c')

    if project_configuration.HasMountToolsFeatureCodepage():
      template_names.append('main-option_codepage.c')

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      template_names.append('main-option_encrypted_root_plist.c')

    if project_configuration.library_name == 'libfsapfs':
      template_names.append('main-option_file_system_index.c')

    if project_configuration.HasMountToolsFeatureKeys():
      template_names.append('main-option_keys.c')

    if project_configuration.HasMountToolsFeatureOffset():
      template_names.append('main-option_offset.c')

    if project_configuration.HasMountToolsFeaturePassword():
      template_names.append('main-option_password.c')

    if project_configuration.HasMountToolsFeatureRecoveryPassword():
      template_names.append('main-option_recovery_password.c')

    if project_configuration.HasMountToolsFeatureStartupKey():
      template_names.append('main-option_startup_key.c')

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      template_names.append('main-set_maximum_number_of_open_handles.c')

    if not file_system_type:
      template_names.append('main-set_path_prefix.c')

    if project_configuration.HasMountToolsFeatureMultiSource():
      template_names.append('main-open-multi_source.c')
    else:
      template_names.append('main-open.c')

    if project_configuration.HasMountToolsFeatureUnlock():
      template_names.append('main-is_locked.c')

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('main-glob_free.c')

    template_names.append('main-fuse-start.c')

    if project_configuration.HasMountToolsFeatureExtendedAttributes():
      template_names.append('main-fuse-operations-xattr.c')

    # TODO: add fuse_operations write support
    template_names.append('main-fuse-operations.c')

    if project_configuration.HasMountToolsFeatureSymbolicLink():
      template_names.append('main-fuse-operations-readlink.c')

    template_names.extend([
        'main-fuse-end.c', 'main-dokan.c', 'main-on_error.c'])

    if project_configuration.HasMountToolsFeatureGlob():
      template_names.append('main-on_error-glob.c')

    template_names.append('main-end.c')

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    template_mappings['data_format'] = project_configuration.project_data_format
    template_mappings['mount_tool_getopt_string'] = getopt_string
    template_mappings['mount_tool_options_switch'] = getopt_switch
    template_mappings['mount_tool_options_variable_declarations'] = (
        variable_declarations)

    self._GenerateSections(
        template_filenames, template_mappings, output_filename, access_mode='a')

    del template_mappings['data_format']
    del template_mappings['mount_tool_getopt_string']
    del template_mappings['mount_tool_options_switch']
    del template_mappings['mount_tool_options_variable_declarations']

    self._SortIncludeHeaders(project_configuration, output_filename)
    self._SortVariableDeclarations(output_filename)
    self._VerticalAlignFunctionArguments(output_filename)

  def _GenerateMountToolSourceUsageFunction(
      self, project_configuration, template_mappings, mount_tool_name,
      mount_tool_options, output_writer, output_filename):
    """Generates a mount tool source usage function.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      mount_tool_name (str): name of the mount tool.
      mount_tool_options (list[tuple[str, str, st]])): mount tool options.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    templates_path = os.path.join(self._templates_path, 'yalmount')

    alignment_padding = '          '
    width = 80 - len(alignment_padding)
    text_wrapper = textwrap.TextWrapper(width=width)

    options_details = []
    options_usage = []
    options_without_arguments = []
    for option, argument, description in mount_tool_options:
      description_lines = text_wrapper.wrap(description)

      description_line = description_lines.pop(0)
      details = '\tfprintf( stream, "\\t-{0:s}:{1:s}{2:s}\\n"'.format(
          option, alignment_padding, description_line)

      for description_line in description_lines:
        options_details.append(details)
        details = '\t                 "\\t   {0:s}{1:s}\\n"'.format(
            alignment_padding, description_line)

      details = '{0:s} );'.format(details)
      options_details.append(details)

      if not argument:
        options_without_arguments.append(option)
      else:
        usage = '[ -{0:s} {1:s} ]'.format(option, argument)
        options_usage.append(usage)

    usage = '[ -{0:s} ]'.format(''.join(options_without_arguments))
    options_usage.append(usage)

    options_usage.extend([
        project_configuration.mount_tool_source_type, 'mount_point'])

    mount_tool_source_alignment = ' ' *(
        len('mount_point') - len(project_configuration.mount_tool_source_type))

    usage = 'Usage: {0:s} '.format(mount_tool_name)
    usage_length = len(usage)
    alignment_padding = ' ' * usage_length
    options_usage = ' '.join(options_usage)

    width = 80 - usage_length
    text_wrapper = textwrap.TextWrapper(width=width)

    usage_lines = text_wrapper.wrap(options_usage)

    mount_tool_usage = []
    usage_line = usage_lines.pop(0)
    usage = '\tfprintf( stream, "{0:s}{1:s}\\n"'.format(usage, usage_line)

    for usage_line in usage_lines:
      mount_tool_usage.append(usage)
      usage = '\t                 "{0:s}{1:s}\\n"'.format(
          alignment_padding, usage_line)

    usage = '{0:s}\\n" );'.format(usage[:-1])
    mount_tool_usage.append(usage)

    template_mappings['mount_tool_options'] = '\n'.join(options_details)
    template_mappings['mount_tool_source_alignment'] = (
        mount_tool_source_alignment)
    template_mappings['mount_tool_usage'] = '\n'.join(mount_tool_usage)

    template_filename = os.path.join(templates_path, 'usage.c')
    self._GenerateSection(
        template_filename, template_mappings, output_filename, access_mode='a')

    del template_mappings['mount_tool_options']
    del template_mappings['mount_tool_source_alignment']
    del template_mappings['mount_tool_usage']

  def _GetInfoToolOptions(self, project_configuration, info_tool_name):
    """Retrieves the info tool options.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      info_tool_name (str): name of the info tool.

    Returns:
      list[tuple[str, str, str]]: info tool options.
    """
    # TODO: sort options with lower case before upper case.
    info_tool_options = []

    # TODO: add condition
    info_tool_options.append(
        ('c', 'codepage', (
            'codepage of ASCII strings, options: ascii, windows-874, '
            'windows-932, windows-936, windows-949, windows-950, '
            'windows-1250, windows-1251, windows-1252 (default), '
            'windows-1253, windows-1254, windows-1255, windows-1256, '
            'windows-1257 or windows-1258 ')))

    info_tool_options.extend([
        ('h', '', 'shows this help'),
        ('v', '', 'verbose output to stderr'),
        ('V', '', 'print version')])

    return info_tool_options

  def _GetMountToolOptions(self, project_configuration, mount_tool_name):
    """Retrieves the mount tool options.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      mount_tool_name (str): name of the mount tool.

    Returns:
      list[tuple[str, str, str]]: mount tool options.
    """
    # TODO: sort options with lower case before upper case.
    mount_tool_options = []

    if project_configuration.HasMountToolsFeatureCodepage():
      option = ('c', 'codepage', (
          'codepage of ASCII strings, options: ascii, windows-874, '
          'windows-932, windows-936, windows-949, windows-950, windows-1250, '
          'windows-1251, windows-1252 (default), windows-1253, windows-1254, '
          'windows-1255, windows-1256, windows-1257 or windows-1258'))

      mount_tool_options.append(option)

    if project_configuration.HasMountToolsFeatureEncryptedRootPlist():
      option = ('e', 'plist_path', (
          'specify the path of the EncryptedRoot.plist.wipekey file'))

      mount_tool_options.append(option)

    # TODO: set option via configuration
    if project_configuration.library_name == 'libfsapfs':
      option = ('f', 'file_system_index', (
          'specify a specific file system or \\"all\\"'))

      mount_tool_options.append(option)

    # TODO: set option via configuration
    if project_configuration.library_name == 'libewf':
      option = ('f', 'format', (
          'specify the input format, options: raw (default), files (restricted '
          'to logical volume files)'))

      mount_tool_options.append(option)

    mount_tool_options.append(('h', '', 'shows this help'))

    if project_configuration.HasMountToolsFeatureKeys():
      # TODO: set keys option description via configuration
      if project_configuration.library_name == 'libbde':
        option = ('k', 'keys', (
            'specify the full volume encryption key and tweak key formatted in '
            'base16 and separated by a : character e.g. FVEK:TWEAK'))

      elif project_configuration.library_name == 'libfvde':
        option = ('k', 'keys', (
            'specify the volume master key formatted in base16'))

      elif project_configuration.library_name in ('libluksde', 'libqcow'):
        option = ('k', 'keys', 'specify the key formatted in base16')

      mount_tool_options.append(option)

    if project_configuration.HasMountToolsFeatureOffset():
      option = ('o', 'offset', 'specify the {0:s} offset in bytes'.format(
          project_configuration.mount_tool_source_type))

      mount_tool_options.append(option)

    if project_configuration.HasMountToolsFeaturePassword():
      option = ('p', 'password', 'specify the password/passphrase')

      mount_tool_options.append(option)

    if project_configuration.HasMountToolsFeatureRecoveryPassword():
      option = (
          'r', 'recovery_password', 'specify the recovery password/passphrase')

      mount_tool_options.append(option)

    if project_configuration.HasMountToolsFeatureStartupKey():
      option = ('s', 'startup_key_path', (
          'specify the path of the file containing the startup key. Typically '
          'this file has the extension .BEK'))

      mount_tool_options.append(option)

    mount_tool_options.extend([
        ('v', '', ('verbose output to stderr, while {0:s} will remain '
                    'running in the foreground').format(mount_tool_name)),
        ('V', '', 'print version'),
        ('X', 'extended_options', 'extended options to pass to sub system')])

    return mount_tool_options

  def Generate(self, project_configuration, output_writer):
    """Generates tools source files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    tools_path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        project_configuration.tools_directory)

    library_header = 'yaltools_{0:s}.h'.format(
        project_configuration.library_name)

    if not os.path.exists(tools_path):
      return

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    # TODO: add support for ouput.[ch]

    for directory_entry in os.listdir(self._templates_path):
      # Ignore yaltools_library.h in favor of yaltools_libyal.h
      if directory_entry == library_header:
        continue

      template_filename = os.path.join(self._templates_path, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if directory_entry == 'yaltools_libyal.h':
        output_filename = '{0:s}tools_{1:s}.h'.format(
            project_configuration.library_name_suffix,
            project_configuration.library_name)

      else:
        output_filename = '{0:s}_{1:s}'.format(
            project_configuration.tools_directory, directory_entry[9:])

      output_filename = os.path.join(
          project_configuration.tools_directory, output_filename)

      if not os.path.exists(output_filename):
        continue

      self._GenerateSection(
          template_filename, template_mappings, output_filename)

    self._GenerateInfoTool(
        project_configuration, template_mappings, output_writer)

    self._GenerateMountTool(
        project_configuration, template_mappings, output_writer)
