# -*- coding: utf-8 -*-
"""The source file generator for script files."""

import os
import stat

from source_generators import interface


class ScriptFileGenerator(interface.SourceFileGenerator):
  """Script files generator."""

  def Generate(self, project_configuration, output_writer):
    """Generates script files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    mount_tool_name = '{0:s}mount'.format(
        project_configuration.library_name_suffix)

    mount_tool_filename = '{0:s}.c'.format(mount_tool_name)
    mount_tool_filename = os.path.join(
        project_configuration.tools_directory, mount_tool_filename)

    template_mappings = self._GetTemplateMappings(project_configuration)
    template_mappings['local_libs'] = ' '.join(
        sorted(makefile_am_file.libraries))
    template_mappings['shared_libs'] = ' '.join(makefile_am_file.libraries)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = directory_entry

      if not os.path.exists(output_filename) and directory_entry in (
          'syncbzip2.ps1', 'syncwinflexbison.ps1', 'synczlib.ps1'):
        continue

      if directory_entry in ('builddokan.ps1', 'syncdokan.ps1'):
        if not os.path.exists(mount_tool_filename):
          continue

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

      if output_filename.endswith('.sh'):
        # Set x-bit for .sh scripts.
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)
