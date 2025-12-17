# -*- coding: utf-8 -*-
"""The source file generator for script files."""

import os
import stat

from yaldevtools.source_generators import interface


class ScriptFileGenerator(interface.SourceFileGenerator):
  """Script files generator."""

  def _GenerateRunTestsSh(
      self, project_configuration, template_mappings, output_writer):
    """Generates the runtests.sh script.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    templates_path = os.path.join(self._templates_path, 'runtests.sh')
    output_filename = os.path.join('runtests.sh')

    template_names = ['header.sh', 'functions.sh']

    if project_configuration.HasPythonModule():
      template_names.append('functions-python.sh')

    template_names.append('configure-start.sh')

    template_names.append('configure-debug_output.sh')

    if project_configuration.library_name not in ('libcerror', 'libcthreads'):
      template_names.append('configure-pthread.sh')

    template_names.append('tests-start.sh')

    template_names.append('tests-debug_output.sh')

    if project_configuration.library_name not in ('libcerror', 'libcthreads'):
      template_names.append('tests-pthread.sh')

    if project_configuration.HasDependencyZlib():
      template_names.append('tests-zlib.sh')

    if project_configuration.HasDependencyCrypto():
      template_names.append('tests-openssl.sh')

    if project_configuration.HasTools():
      template_names.append('tests-static_executables.sh')

    if project_configuration.HasPythonModule():
      template_names.append('tests-python.sh')

    asan_configure_options = []
    coverage_configure_options = ['--enable-shared=no']

    if project_configuration.HasDependencyCrypto():
      asan_configure_options.append('--with-openssl=no')
      coverage_configure_options.append('--with-openssl=no')

    if project_configuration.HasDependencyZlib():
      asan_configure_options.append('--with-zlib=no')
      coverage_configure_options.append('--with-zlib=no')

    # TODO: test python bindings with asan?

    template_names.append('tests-end.sh')

    template_mappings['asan_configure_options'] = ' '.join(
        asan_configure_options)

    template_mappings['coverage_configure_options'] = ' '.join(
        coverage_configure_options)

    template_filenames = [
        os.path.join(templates_path, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_filename)

    del template_mappings['asan_configure_options']
    del template_mappings['coverage_configure_options']

    # Set the x-bit for the shell script (.sh).
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

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

    shared_libs = list(makefile_am_file.libraries)
    if 'bzip2' in shared_libs:
      shared_libs.remove('bzip2')
    if 'libcrypto' in shared_libs:
      shared_libs.remove('libcrypto')
    if 'libdl' in shared_libs:
      shared_libs.remove('libdl')
    if 'lzma' in shared_libs:
      shared_libs.remove('lzma')
    if 'pthread' in shared_libs:
      shared_libs.remove('pthread')
    if 'zlib' in shared_libs:
      shared_libs.remove('zlib')

    template_mappings = self._GetTemplateMappings(project_configuration)
    template_mappings['local_libs'] = ' '.join(
        sorted(makefile_am_file.libraries))
    template_mappings['shared_libs'] = ' '.join(shared_libs)

    template_mappings['test_data_files'] = ' '.join(
        project_configuration.test_data_files)
    template_mappings['test_data_path'] = project_configuration.test_data_path
    template_mappings['test_data_repository'] = (
        project_configuration.test_data_repository)

    if self._experimental:
      self._GenerateRunTestsSh(
          project_configuration, template_mappings, output_writer)

    for directory_entry in os.listdir(self._templates_path):
      template_filename = os.path.join(self._templates_path, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = directory_entry

      if directory_entry in (
          'syncbzip2.ps1', 'synctestdata.ps1', 'synctestdata.sh',
          'syncwinflexbison.ps1', 'synczlib.ps1'):
        if not os.path.exists(output_filename):
          continue

      if directory_entry in ('builddokan.ps1', 'syncdokan.ps1'):
        if not os.path.exists(mount_tool_filename):
          continue

      self._GenerateSection(
          template_filename, template_mappings, output_filename)

      if output_filename.endswith('.sh'):
        # Set the x-bit for a shell script (.sh).
        stat_info = os.stat(output_filename)
        os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)
