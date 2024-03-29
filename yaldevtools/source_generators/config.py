# -*- coding: utf-8 -*-
"""The source file generator for configuration files."""

import glob
import logging
import os

from yaldevtools.source_generators import interface


class ConfigurationFileGenerator(interface.SourceFileGenerator):
  """Configuration file generator."""

  def _GenerateACIncludeM4(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the acinclude.m4 configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'acinclude.m4')

    library_name = project_configuration.library_name
    tools_name = '{0:s}tools'.format(project_configuration.library_name_suffix)

    m4_file = '{0:s}.m4'.format(library_name)
    m4_file = os.path.join(self._data_directory, 'm4', m4_file)

    if os.path.exists(m4_file):
      with open(m4_file, 'r', encoding='utf8') as file_object:
        input_lines = file_object.readlines()

      with open(output_filename, 'w', encoding='utf8') as file_object:
        # Generate the first line
        input_lines.pop(0)
        file_object.write('dnl Checks for required headers and functions\n')

        # Copy the rest of the header
        while input_lines:
          line = input_lines.pop(0)
          file_object.write(line)
          if not line.strip():
            break

        # Find the line with the start of the definition of the
        # AX_${library_name}_CHECK_LOCAL macro.
        m4_macro_definition = 'AC_DEFUN([AX_{0:s}_CHECK_LOCAL],'.format(
            library_name.upper())

        macro_start_line_number = None
        for line_number, line in enumerate(input_lines):
          if line.startswith(m4_macro_definition):
            macro_start_line_number = line_number
            break

        macro_start_line_number -= 1

        macro_end_line_number = None
        for line_number, line in enumerate(
            input_lines[macro_start_line_number + 2:]):
          if line.startswith('dnl ') or line.startswith('AC_DEFUN(['):
            macro_end_line_number = line_number
            break

        macro_end_line_number += macro_start_line_number + 2

        for _ in range(5):
          input_lines.pop(macro_end_line_number - 3)
          macro_end_line_number -= 1

        # Copy the AX_${library_name}_CHECK_LOCAL macro.
        for line in input_lines[macro_start_line_number:macro_end_line_number]:
          file_object.write(line)

    else:
      template_names = ['header.m4', 'check_library.m4']

      if project_configuration.HasTools():
        template_names.append('check_tools.m4-start')

        log_handle_path = os.path.join(tools_name, 'log_handle.c')
        if os.path.exists(log_handle_path):
          template_names.append('check_tools.m4-log_handle')

        mount_tool_name = '{0:s}mount'.format(
            project_configuration.library_name_suffix)
        mount_tool_path = os.path.join(
            tools_name, '{0:s}.c'.format(mount_tool_name))
        if os.path.exists(mount_tool_path):
          template_names.append('check_tools.m4-mount_tool')

        template_names.append('check_tools.m4-end')

      template_mappings['library_name'] = library_name
      template_mappings['library_name_upper_case'] = library_name.upper()
      template_mappings['mount_tool_name'] = mount_tool_name
      template_mappings['tools_name'] = tools_name
      template_mappings['tools_name_upper_case'] = tools_name.upper()

      template_filenames = [
          os.path.join(template_directory, template_name)
          for template_name in template_names]

      self._GenerateSections(
          template_filenames, template_mappings, output_writer, output_filename)

      del template_mappings['library_name']
      del template_mappings['library_name_upper_case']
      del template_mappings['mount_tool_name']
      del template_mappings['tools_name']
      del template_mappings['tools_name_upper_case']

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    if project_configuration.HasTools():
      template_filename = 'check_dll_support.m4-tools'
    else:
      template_filename = 'check_dll_support.m4'

    template_filename = os.path.join(template_directory, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, output_writer,
        output_filename, access_mode='a')

    del template_mappings['library_name']
    del template_mappings['library_name_upper_case']

  def _GenerateAppVeyorYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the appveyor.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'appveyor.yml')

    template_names = ['environment.yml']

    if project_configuration.deploy_to_nuget:
      template_names.append('environment-nuget.yml')

    if project_configuration.HasPythonModule():
      template_names.append('environment-pypi.yml')

    template_names.append('environment-matrix.yml')

    if project_configuration.HasPythonModule():
      template_names.append('environment-matrix-vs_with_python.yml')

    if project_configuration.deploy_to_nuget:
      template_names.append('environment-matrix-nuget.yml')

    template_names.append('environment-matrix-macos.yml')

    if project_configuration.HasPythonModule():
      template_names.append('environment-matrix-macos-python.yml')
    else:
      template_names.append('environment-matrix-macos-pkgbuild.yml')

    if project_configuration.HasPythonModule():
      template_names.append('environment-matrix-wheel.yml')

    template_names.append('environment-matrix-cygwin64.yml')

    # if project_configuration.HasDependencyCrypto():
    # TODO: add environment-cygwin64-openssl.yml

    if project_configuration.HasPythonModule():
      template_names.append('environment-matrix-cygwin64-python.yml')

    if project_configuration.HasTools():
      template_names.append(
          'environment-matrix-cygwin64-static-executables.yml')

    template_names.append('environment-matrix-mingw-w64.yml')

    if project_configuration.HasTools():
      template_names.append(
          'environment-matrix-mingw-w64-static-executables.yml')

    template_names.append('install-header.yml')

    # TODO: check test more generic.
    if project_configuration.library_name == 'libfsntfs':
      template_names.append('install-testdata.yml')

    if (project_configuration.HasDependencyLex() or
        project_configuration.HasDependencyYacc()):
      template_names.append('install-winflexbison.yml')

    if project_configuration.HasDependencyZlib():
      template_names.append('install-zlib.yml')

    if project_configuration.HasDependencyBzip2():
      template_names.append('install-bzip2.yml')

    if project_configuration.HasDependencyDokan():
      template_names.append('install-dokan.yml')

    template_names.append('install-macos.yml')

    if project_configuration.HasPythonModule():
      template_names.append('install-python.yml')

    brew_build_dependencies = self._GetBrewBuildDependencies(
        project_configuration)

    template_mappings['brew_build_dependencies'] = ' '.join(
        sorted(brew_build_dependencies))
    template_mappings['pypi_token'] = getattr(
        project_configuration, 'pypi_token_appveyor', '')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['pypi_token']
    del template_mappings['brew_build_dependencies']

    cygwin_build_dependencies = self._GetCygwinBuildDependencies(
        project_configuration)

    if cygwin_build_dependencies:
      cygwin_build_dependencies = ' '.join([
          '-P {0:s}'.format(name) for name in cygwin_build_dependencies])
      template_mappings['cygwin_build_dependencies'] = cygwin_build_dependencies

      template_filename = os.path.join(template_directory, 'install-cygwin.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['cygwin_build_dependencies']

    mingw_msys2_build_dependencies = self._GetMinGWMSYS2BuildDependencies(
        project_configuration)

    if mingw_msys2_build_dependencies:
      mingw_msys2_build_dependencies = ' '.join(mingw_msys2_build_dependencies)
      template_mappings['mingw_msys2_build_dependencies'] = (
          mingw_msys2_build_dependencies)

      template_filename = os.path.join(
          template_directory, 'install-mingw-msys2.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['mingw_msys2_build_dependencies']

    # TODO: refactor code above to use template_names

    template_names = []

    template_names.append('install-codecov.yml')

    template_names.append('build_script-header.yml')

    if project_configuration.HasPythonModule():
      template_names.append('build_script-vs_with_python.yml')

    if project_configuration.deploy_to_nuget:
      template_names.append('build_script-nuget.yml')

    template_names.append('build_script-macos.yml')

    if project_configuration.HasPythonModule():
      template_names.append('build_script-python.yml')

    template_names.extend([
        'build_script-footer.yml', 'test_script.yml', 'after_test.yml'])

    if (project_configuration.deploy_to_nuget or
        project_configuration.HasPythonModule()):
      template_names.append('artifacts.yml')

      if project_configuration.deploy_to_nuget:
        template_names.append('artifacts-nuget.yml')

      if project_configuration.HasPythonModule():
        template_names.append('artifacts-pypi.yml')

      template_names.append('deploy_script-header.yml')

      if project_configuration.deploy_to_nuget:
        template_names.append('deploy_script-nuget.yml')

      if project_configuration.HasPythonModule():
        template_names.append('deploy_script-pypi.yml')

      template_names.append('deploy_script-footer.yml')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

  def _GenerateCodecovYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .codecov.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, '.codecov.yml')

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    ignore_paths = list(makefile_am_file.libraries)
    ignore_paths.append('tests')

    template_mappings['codecov_ignore'] = '\n'.join([
        '    - "{0:s}/*"'.format(path) for path in sorted(ignore_paths)])

    template_filename = os.path.join(
        template_directory, 'body.yml')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['codecov_ignore']

  def _GenerateConfigureAC(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the configure.ac configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    # TODO: change indentation of templates.

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    libraries = list(makefile_am_file.libraries)
    library_dependencies = list(makefile_am_file.library_dependencies)

    libcrypto_index = len(library_dependencies)
    if 'libcaes' in library_dependencies:
      libcrypto_index = min(
          libcrypto_index, library_dependencies.index('libcaes'))

    if 'libhmac' in library_dependencies:
      libcrypto_index = min(
          libcrypto_index, library_dependencies.index('libhmac'))

    if project_configuration.HasDependencyCrypto():
      if libcrypto_index == len(library_dependencies):
        libraries.append('libcrypto')
        library_dependencies.append('libcrypto')

    if 'sgutils' in project_configuration.library_build_dependencies:
      libraries.append('sgutils2')
      library_dependencies.append('sgutils2')

    if 'bzip2' in project_configuration.library_build_dependencies:
      if libcrypto_index < len(library_dependencies):
        libraries.insert(libcrypto_index, 'bzip2')
        library_dependencies.insert(libcrypto_index, 'bzip2')
      else:
        libraries.append('bzip2')
        library_dependencies.append('bzip2')

    # Have zlib checked before libcrypto.
    if project_configuration.HasDependencyZlib():
      if libcrypto_index < len(library_dependencies):
        libraries.insert(libcrypto_index, 'zlib')
        library_dependencies.insert(libcrypto_index, 'zlib')
      else:
        libraries.append('zlib')
        library_dependencies.append('zlib')

    template_directory = os.path.join(self._template_directory, 'configure.ac')

    template_names = ['header.ac', 'programs.ac-start']

    if os.path.isdir('ossfuzz'):
      template_names.append('programs.ac-ossfuzz')

    template_names.extend([
        'programs.ac-end', 'compiler_language.ac', 'build_features.ac'])

    if project_configuration.HasTools():
      template_names.append('check_static_executables.ac')

    template_names.append('check_winapi.ac')

    if (include_header_file and include_header_file.have_wide_character_type or
        project_configuration.HasTools()):
      template_names.append('check_wide_character_support.ac')

    if project_configuration.HasDebugOutput():
      template_names.append('check_debug_output.ac')

    template_names.extend(['check_types_support.ac', 'check_common_support.ac'])

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    # TODO: refactor code below to use template_names

    if library_dependencies:
      for name in library_dependencies:
        if (name == 'libcrypto' and
            project_configuration.library_name == 'libcaes'):
          continue

        if name == 'zlib':
          # TODO: make check more generic based on the source itself.
          if project_configuration.library_name == 'libewf':
            template_filename = 'check_zlib_compress.ac'

          # TODO: determine deflate function via configuration setting?
          elif project_configuration.library_name in (
              'libfsapfs', 'libfshfs', 'libfvde', 'libmodi', 'libpff',
              'libvmdk'):
            template_filename = 'check_zlib_uncompress.ac'

          else:
            template_filename = 'check_zlib_inflate.ac'

        else:
          template_filename = 'check_dependency_support.ac'

        template_mappings['local_library_name'] = name
        template_mappings['local_library_name_upper_case'] = name.upper()

        template_filename = os.path.join(template_directory, template_filename)
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

        del template_mappings['local_library_name']
        del template_mappings['local_library_name_upper_case']

    template_names = ['check_library_support.ac']

    if project_configuration.HasPythonModule():
      template_names.append('check_python_support.ac')

    if project_configuration.HasJavaBindings():
      template_names.append('check_java_support.ac')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: refactor code below to use template_names

    if project_configuration.HasTools():
      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'uuid' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libuuid')

      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      if tools_dependencies:
        for name in tools_dependencies:
          template_mappings['local_library_name'] = name
          template_mappings['local_library_name_upper_case'] = name.upper()

          template_filename = os.path.join(
              template_directory, 'check_dependency_support.ac')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='a')

        del template_mappings['local_library_name']
        del template_mappings['local_library_name_upper_case']

      template_filename = os.path.join(
          template_directory, 'check_tools_support.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='a')

    template_names = ['check_dll_support.ac', 'check_tests_support.ac']

    if os.path.isdir('ossfuzz'):
      template_names.append('check_ossfuzz_support.ac')

    template_names.append('compiler_flags.ac')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: refactor code below to use template_names

    if library_dependencies:
      local_library_tests = []
      for name in library_dependencies:
        if name in makefile_am_file.library_dependencies:
          local_library_test = 'test "x$ac_cv_{0:s}" = xyes'.format(name)
        else:
          local_library_test = 'test "x$ac_cv_{0:s}" != xno'.format(name)

        local_library_tests.append(local_library_test)

      if 'libcaes' in library_dependencies or 'libhmac' in library_dependencies:
        local_library_tests.append('test "x$ac_cv_libcrypto" != xno')

      template_mappings['local_library_tests'] = ' || '.join(
          local_library_tests)

      template_filename = os.path.join(
          template_directory, 'spec_requires_library.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['local_library_tests']

    if project_configuration.HasTools():
      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'crypto' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libcrypto')
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')
      if 'uuid' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libuuid')

      if tools_dependencies:
        local_library_tests = []
        for name in tools_dependencies:
          if name in ('libcrypto', 'libfuse'):
            local_library_test = 'test "x$ac_cv_{0:s}" != xno'.format(name)
          else:
            local_library_test = 'test "x$ac_cv_{0:s}" = xyes'.format(name)

          local_library_tests.append(local_library_test)

        template_mappings['local_library_tests'] = ' || '.join(
            local_library_tests)

        template_filename = os.path.join(
            template_directory, 'spec_requires_tools.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

        del template_mappings['local_library_tests']

    template_names = ['dates.ac', 'config_files_start.ac']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: refactor code below to use template_names

    if makefile_am_file.library_dependencies:
      for name in makefile_am_file.library_dependencies:
        template_mappings['local_library_name'] = name

        template_filename = os.path.join(
            template_directory, 'config_files_dependency.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

      del template_mappings['local_library_name']

    template_names = ['config_files_library.ac']

    if project_configuration.HasPythonModule():
      template_names.append('config_files_python.ac')

    if project_configuration.HasDotNetBindings():
      template_names.append('config_files_dotnet.ac')

    if project_configuration.HasJavaBindings():
      template_names.append('config_files_java.ac')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: refactor code below to use template_names

    if project_configuration.HasTools():
      if makefile_am_file.tools_dependencies:
        for name in makefile_am_file.tools_dependencies:
          template_mappings['local_library_name'] = name

          template_filename = os.path.join(
              template_directory, 'config_files_dependency.ac')
          self._GenerateSection(
              template_filename, template_mappings, output_writer,
              output_filename, access_mode='a')

        del template_mappings['local_library_name']

      template_filename = os.path.join(
          template_directory, 'config_files_tools.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer,
          output_filename, access_mode='a')

    # TODO: add support for Makefile in documents (libuna)

    template_names = ['config_files_common.ac']

    if os.path.isdir('ossfuzz'):
      template_names.append('config_files_ossfuzz.ac')

    template_names.append('config_files_headers.ac')

    if project_configuration.HasDotNetBindings():
      template_names.append('config_files_dotnet_rc.ac')

    template_names.append('config_files_rpm_spec.ac')

    if project_configuration.HasPythonModule():
      template_names.append('config_files_setup_cfg.ac')

    template_names.append('config_files_end.ac')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: add support for build options configuration

    build_options = []
    for name in libraries:
      if name not in ('bzip2', 'libcrypto', 'zlib'):
        build_options.append((
            '{0:s} support'.format(name), '$ac_cv_{0:s}'.format(name)))

      if name == 'bzip2':
        build_options.append(('BZIP2 compression support', '$ac_cv_bzip2'))

      if name == 'libcaes':
        if project_configuration.library_name in ('libbde', 'libluksde'):
          build_options.extend([
              ('AES-CBC support', '$ac_cv_libcaes_aes_cbc'),
              ('AES-ECB support', '$ac_cv_libcaes_aes_ecb'),
              ('AES-XTS support', '$ac_cv_libcaes_aes_xts')])

        elif project_configuration.library_name == 'libewf':
          pass

        elif project_configuration.library_name in ('libfsapfs', 'libfvde'):
          build_options.extend([
              ('AES-ECB support', '$ac_cv_libcaes_aes_ecb'),
              ('AES-XTS support', '$ac_cv_libcaes_aes_xts')])

        elif project_configuration.library_name in ('libmodi', 'libqcow'):
          build_options.append(
              ('AES-CBC support', '$ac_cv_libcaes_aes_cbc'))

      elif name == 'libhmac':
        # TODO: make check more generic based on the source itself.
        if project_configuration.library_name in (
            'libewf', 'libfsapfs', 'libfsext', 'libfsfat', 'libfshfs',
            'libfsntfs', 'libfsxfs', 'libodraw', 'libsmraw'):
          build_options.append(('MD5 support', '$ac_cv_libhmac_md5'))

        if project_configuration.library_name in (
            'libewf', 'libluksde', 'libodraw', 'libsmraw'):
          build_options.append(('SHA1 support', '$ac_cv_libhmac_sha1'))

        if project_configuration.library_name in (
            'libbde', 'libewf', 'libfsapfs', 'libfvde', 'libmodi', 'libodraw',
            'libsmraw'):
          build_options.append(('SHA256 support', '$ac_cv_libhmac_sha256'))

        elif project_configuration.library_name == 'libluksde':
          build_options.extend([
              ('SHA224 support', '$ac_cv_libhmac_sha224'),
              ('SHA256 support', '$ac_cv_libhmac_sha256'),
              ('SHA512 support', '$ac_cv_libhmac_sha512')])

      elif name == 'libfcrypto':
        if project_configuration.library_name == 'libluksde':
          build_options.extend([
              ('ARC4-ECB support', '$ac_cv_libfcrypto'),
              ('Serpent-CBC support', '$ac_cv_libfcrypto'),
              ('Serpent-ECB support', '$ac_cv_libfcrypto')])

      elif name == 'zlib':
        if project_configuration.library_name == 'libewf':
          build_options.append(('ADLER32 checksum support', '$ac_cv_adler32'))

        # TODO: determine deflate function via configuration setting?
        if project_configuration.library_name in (
            'libfsapfs', 'libewf', 'libfvde', 'libmodi', 'libpff', 'libvmdk'):
          value = '$ac_cv_uncompress'
        else:
          value = '$ac_cv_inflate'

        build_options.append(('DEFLATE compression support', value))

    if project_configuration.library_name == 'libcaes':
      build_options.extend([
          ('AES-CBC support', '$ac_cv_libcaes_aes_cbc'),
          ('AES-ECB support', '$ac_cv_libcaes_aes_ecb'),
          ('AES-XTS support', '$ac_cv_libcaes_aes_xts')])

    elif project_configuration.library_name == 'libhmac':
      build_options.extend([
          ('MD5 support', '$ac_cv_libhmac_md5'),
          ('SHA1 support', '$ac_cv_libhmac_sha1'),
          ('SHA224 support', '$ac_cv_libhmac_sha224'),
          ('SHA256 support', '$ac_cv_libhmac_sha256'),
          ('SHA512 support', '$ac_cv_libhmac_sha512')])

    if 'uuid' in project_configuration.tools_build_dependencies:
      build_options.append(('GUID/UUID support', '$ac_cv_libuuid'))

    if 'fuse' in project_configuration.tools_build_dependencies:
      build_options.append(('FUSE support', '$ac_cv_libfuse'))

    build_information = []
    maximum_description_length = 0

    for description, value in build_options:
      build_information_tuple = (description, value)
      build_information.append(build_information_tuple)

      maximum_description_length = max(
          maximum_description_length, len(description))

    features_information = []
    if (project_configuration.library_name == 'libcthreads' or
        'libcthreads' in makefile_am_file.libraries):
      description = 'Multi-threading support'
      value = '$ac_cv_libcthreads_multi_threading'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if (include_header_file and include_header_file.have_wide_character_type or
        project_configuration.HasTools()):
      description = 'Wide character type support'
      value = '$ac_cv_enable_wide_character_type'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasTools():
      description = '{0:s} are build as static executables'.format(
          project_configuration.tools_directory)
      value = '$ac_cv_enable_static_executables'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasPythonModule():
      description = 'Python ({0:s}) support'.format(
          project_configuration.python_module_name)
      value = '$ac_cv_enable_python'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasDebugOutput():
      description = 'Verbose output'
      value = '$ac_cv_enable_verbose_output'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

      description = 'Debug output'
      value = '$ac_cv_enable_debug_output'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    notice_message = []

    if build_information:
      notice_message.append('Building:')

      for description, value in build_information:
        padding_length = maximum_description_length - len(description)
        padding = ' ' * padding_length

        notice_line = '   {0:s}: {1:s}{2:s}'.format(description, padding, value)
        notice_message.append(notice_line)

      notice_message.append('')

    if features_information:
      notice_message.append('Features:')

      for description, value in features_information:
        padding_length = maximum_description_length - len(description)
        padding = ' ' * padding_length

        notice_line = '   {0:s}: {1:s}{2:s}'.format(description, padding, value)
        notice_message.append(notice_line)

    template_filename = os.path.join(template_directory, 'output.ac')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: improve this condition
    if project_configuration.library_name != 'libcerror':
      template_mappings['notice_message'] = '\n'.join(notice_message)

      template_filename = os.path.join(template_directory, 'notice.ac')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['notice_message']

  def _GenerateDpkg(
      self, project_configuration, template_mappings, output_writer,
      output_directory):
    """Generates the dpkg packaging files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_directory (str): path of the output directory.
    """
    # TODO: add support for projects without Python bindings.
    # TODO: fix lintian issues.

    library_name = project_configuration.library_name

    template_directory = os.path.join(self._template_directory, 'dpkg')

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if (directory_entry.startswith('control') or
          directory_entry.startswith('rules')):
        continue

      if directory_entry.endswith('.install'):
        if (not project_configuration.HasPythonModule() and
            '-python' in directory_entry):
          continue

        if (not project_configuration.HasTools() and
            '-tools' in directory_entry):
          continue

      output_filename = directory_entry
      if output_filename.startswith('libyal'):
        output_filename = '{0:s}{1:s}'.format(
            project_configuration.library_name, output_filename[6:])

      output_filename = os.path.join(output_directory, output_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    dpkg_build_dependencies = self._GetDpkgBuildDependenciesDpkgControl(
        project_configuration)

    template_mappings['dpkg_build_dependencies'] = ', '.join(
        dpkg_build_dependencies)

    template_filename = os.path.join(template_directory, 'control')
    output_filename = os.path.join(output_directory, 'control')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

    if project_configuration.HasTools():
      template_filename = os.path.join(template_directory, 'control-tools')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'control-python')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if (project_configuration.HasPythonModule() and
        project_configuration.HasTools()):
      template_filename = 'rules-with-python-and-tools'
    elif project_configuration.HasPythonModule():
      template_filename = 'rules-with-python'
    elif project_configuration.HasTools():
      template_filename = 'rules-with-tools'
    else:
      template_filename = 'rules'

    template_filename = os.path.join(template_directory, template_filename)
    output_filename = os.path.join(output_directory, 'rules')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_directory = os.path.join(
        self._template_directory, 'dpkg', 'source')
    output_directory = os.path.join(output_directory, 'source')

    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['library_name']
    del template_mappings['library_name_upper_case']

  def _GenerateGitignore(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .gitignore configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    template_directory = os.path.join(self._template_directory, '.gitignore')

    template_filename = os.path.join(template_directory, 'header')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    template_filename = os.path.join(template_directory, 'library')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    # TODO: add support for lex yacc BUILT_SOURCES

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'python_module')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasDotNetBindings():
      template_filename = os.path.join(template_directory, 'dotnet_bindings')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasJavaBindings():
      template_filename = os.path.join(template_directory, 'java_bindings')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasTools():
      tools_executables = []
      for name in sorted(project_configuration.tools_names):
        tools_executable = '/{0:s}/{1:s}'.format(
            project_configuration.tools_directory, name)
        tools_executables.append(tools_executable)

      template_mappings['tools_executables'] = '\n'.join(tools_executables)

      template_filename = os.path.join(template_directory, 'tools')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['tools_executables']

    source_glob = '{0:s}_test_*.c'.format(
        project_configuration.library_name_suffix)
    source_glob = os.path.join('tests', source_glob)

    tests_files = ['/tests/tmp*']
    if os.path.exists(os.path.join('tests', 'input')):
      tests_files.append('/tests/input')

    for source_file_path in sorted(glob.glob(source_glob)):
      if (source_file_path.endswith('_functions.c') or
          source_file_path.endswith('_getopt.c') or
          source_file_path.endswith('_i18n.c') or
          source_file_path.endswith('_memory.c') or
          source_file_path.endswith('_rwlock.c')):
        continue

      source_file_path = '/{0:s}'.format(source_file_path[:-2])
      tests_files.append(source_file_path)

    template_mappings['tests_files'] = '\n'.join(sorted(tests_files))

    template_filename = os.path.join(template_directory, 'tests')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    del template_mappings['tests_files']

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    libraries = [
        '/{0:s}'.format(name) for name in sorted(makefile_am_file.libraries)]

    if libraries:
      template_mappings['local_libraries'] = '\n'.join(libraries)

      template_filename = os.path.join(template_directory, 'local_libraries')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['local_libraries']

  def _GenerateRpmSpec(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the RPM spec file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    library_name = project_configuration.library_name

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_directory = os.path.join(
        self._template_directory, 'libyal.spec.in')

    library_dependencies = list(makefile_am_file.library_dependencies)

    if project_configuration.HasDependencyCrypto():
      library_dependencies.append('libcrypto')
    if project_configuration.HasDependencyZlib():
      library_dependencies.append('zlib')

    template_names = ['header.in']

    template_mappings['library_name'] = library_name
    template_mappings['library_name_upper_case'] = library_name.upper()

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    if not library_dependencies:
      template_filename = os.path.join(template_directory, 'build_requires.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    else:
      spec_requires = []
      spec_build_requires = []
      for name in sorted(library_dependencies):
        requires = '@ax_{0:s}_spec_requires@'.format(name)
        spec_requires.append(requires)

        build_requires = '@ax_{0:s}_spec_build_requires@'.format(name)
        spec_build_requires.append(build_requires)

      template_mappings['spec_requires'] = ' '.join(spec_requires)
      template_mappings['spec_build_requires'] = ' '.join(spec_build_requires)

      template_filename = os.path.join(template_directory, 'requires.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['spec_requires']
      del template_mappings['spec_build_requires']

    template_filename = os.path.join(template_directory, 'package.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'package-python.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasTools():
      requires_library = '{0:s} = %{{version}}-%{{release}}'.format(
          project_configuration.library_name)

      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'crypto' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libcrypto')
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      spec_requires = [requires_library]
      spec_build_requires = []
      for name in sorted(tools_dependencies):
        requires = '@ax_{0:s}_spec_requires@'.format(name)
        spec_requires.append(requires)

        build_requires = '@ax_{0:s}_spec_build_requires@'.format(name)
        spec_build_requires.append(build_requires)

      template_mappings['spec_requires'] = ' '.join(spec_requires)

      template_filename = os.path.join(
          template_directory, 'package-tools-header.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['spec_requires']

      if tools_dependencies:
        template_mappings['spec_build_requires'] = ' '.join(spec_build_requires)

        template_filename = os.path.join(
            template_directory, 'package-tools-requires.in')
        self._GenerateSection(
            template_filename, template_mappings, output_writer,
            output_filename, access_mode='a')

        del template_mappings['spec_build_requires']

      template_filename = os.path.join(
          template_directory, 'package-tools-footer.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'prep.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'build-python.in')
    else:
      template_filename = os.path.join(template_directory, 'build.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    template_filename = os.path.join(template_directory, 'install.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    template_filename = os.path.join(template_directory, 'files.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(template_directory, 'files-python.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    if project_configuration.HasTools():
      template_filename = os.path.join(template_directory, 'files-tools.in')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

    template_filename = os.path.join(template_directory, 'changelog.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='a')

    del template_mappings['library_name']
    del template_mappings['library_name_upper_case']

  def _GenerateGitHubActions(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates the .github/workflows/*.yml configuration files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, 'github_workflows')

    output_directory = os.path.join('.github', 'workflows')

    for directory_entry in os.listdir(template_directory):
      template_filename = os.path.join(template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

  def _GenerateGitHubActionsBuildYML(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates the .github/workflows/build.yml configuration file.

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
        self._template_directory, 'github_workflows', 'build.yml')

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_names = ['header.yml']

    template_names.append('build_ubuntu-header.yml')

    # TODO: improve check.
    if project_configuration.library_name in ('libbfio', 'libcdata'):
      template_names.append('build_ubuntu-no_pthread.yml')

    if include_header_file.have_wide_character_type:
      template_names.append('build_ubuntu-wide_character_type.yml')

    if project_configuration.HasDependencyZlib():
      template_names.append('build_ubuntu-zlib.yml')

    if project_configuration.HasDependencyCrypto():
      template_names.append('build_ubuntu-openssl.yml')

    if project_configuration.HasTools():
      template_names.append('build_ubuntu-static_executables.yml')

    template_names.append('build_ubuntu-end.yml')

    if project_configuration.HasPythonModule():
      template_names.append('build_python_ubuntu.yml')

    template_names.append('coverage_ubuntu-start.yml')

    if include_header_file.have_wide_character_type:
      template_names.append('coverage_ubuntu-wide_character_type.yml')
    else:
      template_names.append('coverage_ubuntu.yml')

    template_names.append('footer.yml')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

  def _GenerateGitHubActionsBuildFreeBSDYML(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates the .github/workflows/build_freebsd.yml configuration file.

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
        self._template_directory, 'github_workflows', 'build_freebsd.yml')

    freebsd_build_dependencies = self._GetFreeBSDBuildDependencies(
        project_configuration)

    template_names = ['main.yml']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['freebsd_build_dependencies'] = ' '.join(
        freebsd_build_dependencies)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['freebsd_build_dependencies']

  def _GenerateGitHubActionsBuildSharedYML(
      self, project_configuration, template_mappings, include_header_file,
      output_writer, output_filename):
    """Generates the .github/workflows/build_shared.yml configuration file.

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
        self._template_directory, 'github_workflows', 'build_shared.yml')

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_names = ['header.yml']

    if include_header_file.have_wide_character_type:
      template_names.append('build_shared_ubuntu-wide_character_type.yml')

    template_names.append('footer.yml')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

  def _GenerateGitHubActionsBuildWheelYML(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the .github/workflows/build_wheel.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(
        self._template_directory, 'github_workflows', 'build_wheel.yml')

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_names = ['body.yml']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

  def _GeneratePyprojectToml(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the pyproject.toml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory)

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_names = ['pyproject.toml']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

  def _GenerateSetupCfgIn(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the setup.cfg.in configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'setup.cfg.in')

    if project_configuration.project_status == 'experimental':
      python_module_development_status = '2 - Pre-Alpha'
    elif project_configuration.project_status == 'alpha':
      python_module_development_status = '3 - Alpha'
    elif project_configuration.project_status == 'beta':
      python_module_development_status = '4 - Beta'
    else:
      python_module_development_status = '5 - Production/Stable'

    template_names = ['body']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['library_name'] = project_configuration.library_name
    template_mappings['python_module_development_status'] = (
        python_module_development_status)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['library_name']
    del template_mappings['python_module_development_status']

  def _GenerateToxIni(
      self, project_configuration, template_mappings, output_writer,
      output_filename):
    """Generates the tox.ini configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): path of the output file.
    """
    template_directory = os.path.join(self._template_directory, 'tox.ini')

    template_names = ['body.ini']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['library_name'] = project_configuration.library_name

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['library_name']

  def _GetBrewBuildDependencies(self, project_configuration):
    """Retrieves the brew build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies.
    """
    brew_build_dependencies = [
        'autoconf', 'automake', 'gettext', 'gnu-sed', 'libtool', 'pkg-config']

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      brew_build_dependencies.append('openssl')

    if 'fuse' in project_configuration.tools_build_dependencies:
      brew_build_dependencies.append('macfuse')

    return sorted(brew_build_dependencies)

  def _GetCygwinBuildDependencies(self, project_configuration):
    """Retrieves the Cygwin build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: Cygwin build dependencies.
    """
    cygwin_build_dependencies = list(
        project_configuration.cygwin_build_dependencies)

    cygwin_build_dependencies.extend(['gettext-devel', 'wget'])

    if project_configuration.HasDependencyYacc():
      cygwin_build_dependencies.append('bison')
    if project_configuration.HasDependencyLex():
      cygwin_build_dependencies.append('flex')

    if project_configuration.HasDependencyZlib():
      cygwin_build_dependencies.append('zlib-devel')
    if project_configuration.HasDependencyBzip2():
      cygwin_build_dependencies.append('libbz2-devel')

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      # On Cygwin also link zlib since libcrypto relies on it.
      if 'zlib' not in project_configuration.library_build_dependencies:
        cygwin_build_dependencies.append('zlib-devel')

      cygwin_build_dependencies.append('libssl-devel')

    if project_configuration.HasPythonModule():
      cygwin_build_dependencies.append('python3-devel')

    if ('uuid' in project_configuration.library_build_dependencies or
        'uuid' in project_configuration.tools_build_dependencies):
      cygwin_build_dependencies.append('libuuid-devel')

    return cygwin_build_dependencies

  def _GetDpkgBuildDependencies(self, project_configuration):
    """Retrieves the dpkg build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies in alphabetical order.
    """
    dpkg_build_dependencies = [
        'autoconf',
        'automake',
        'autopoint',
        'build-essential',
        'git',
        'libtool',
        'pkg-config']

    if project_configuration.HasDependencyYacc():
      dpkg_build_dependencies.append('byacc')
    if project_configuration.HasDependencyLex():
      dpkg_build_dependencies.append('flex')

    if project_configuration.HasDependencyZlib():
      dpkg_build_dependencies.append('zlib1g-dev')

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if 'fuse' in project_configuration.tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse-dev')

    if 'sgutils' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('libsgutils2-dev')

    dpkg_build_dependencies.extend(
        project_configuration.dpkg_build_dependencies)

    return sorted(dpkg_build_dependencies)

  def _GetDpkgBuildDependenciesDpkgControl(self, project_configuration):
    """Retrieves the dpkg build dependencies for the dpkg/control file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies.
    """
    dpkg_build_dependencies = ['debhelper (>= 9)', 'dh-autoreconf']

    if project_configuration.HasPythonModule():
      dpkg_build_dependencies.append('dh-python')

    dpkg_build_dependencies.append('pkg-config')

    if project_configuration.HasDependencyZlib():
      dpkg_build_dependencies.append('zlib1g-dev')
    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if project_configuration.HasPythonModule():
      dpkg_build_dependencies.extend(['python3-dev', 'python3-setuptools'])

    if 'fuse' in project_configuration.tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse-dev')

    if 'sgutils' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('libsgutils2-dev')

    if project_configuration.dpkg_build_dependencies:
      dpkg_build_dependencies.extend(
          project_configuration.dpkg_build_dependencies)

    return dpkg_build_dependencies

  def _GetFreeBSDBuildDependencies(self, project_configuration):
    """Retrieves the FreeBSD build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: FreeBSD build dependencies in alphabetical order.
    """
    freebsd_build_dependencies = [
        'autoconf',
        'automake',
        'bash',
        'gettext',
        'git',
        'libtool',
        'pkgconf']

    if project_configuration.HasDependencyYacc():
      freebsd_build_dependencies.append('byacc')
    if project_configuration.HasDependencyLex():
      freebsd_build_dependencies.append('flex')

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      freebsd_build_dependencies.append('openssl')

    if 'fuse' in project_configuration.tools_build_dependencies:
      freebsd_build_dependencies.append('fusefs-libs')

    freebsd_build_dependencies.extend(
        project_configuration.freebsd_build_dependencies)

    return sorted(freebsd_build_dependencies)

  def _GetMinGWMSYS2BuildDependencies(self, project_configuration):
    """Retrieves the MinGW-MSYS2 build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: MinGW-MSYS2 build dependencies.
    """
    mingw_msys2_build_dependencies = list(
        project_configuration.mingw_msys2_build_dependencies)

    mingw_msys2_build_dependencies.extend([
        'autoconf', 'automake', 'gettext-devel', 'libtool', 'make',
        'mingw-w64-x86_64-gcc'])

    if project_configuration.HasDependencyYacc():
      mingw_msys2_build_dependencies.append('msys/bison')
    if project_configuration.HasDependencyLex():
      mingw_msys2_build_dependencies.append('msys/flex')

    # TODO: add support for other dependencies.
    if project_configuration.HasDependencyZlib():
      mingw_msys2_build_dependencies.append('msys/zlib-devel')

    return mingw_msys2_build_dependencies

  def Generate(self, project_configuration, output_writer):
    """Generates configuration files.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      output_writer (OutputWriter): output writer.
    """
    # TODO: generate spec file, what about Python versus non-Python?

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    if not include_header_file:
      logging.warning(
          'Missing: {0:s} skipping generation of configuration files.'.format(
              self._library_include_header_path))
      return

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning(
          'Missing: {0:s} skipping generation of configuration files.'.format(
              self._library_makefile_am_path))
      return

    pc_libs_private = []
    for library in sorted(makefile_am_file.libraries):
      if library == 'libdl':
        continue

      pc_lib_private = '@ax_{0:s}_pc_libs_private@'.format(library)
      pc_libs_private.append(pc_lib_private)

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    template_mappings['authors'] = 'Joachim Metz <joachim.metz@gmail.com>'

    template_mappings['pc_libs_private'] = ' '.join(pc_libs_private)

    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      if (directory_entry in ('pyproject.toml', 'setup.py') and
          not project_configuration.HasPythonModule()):
        continue

      if directory_entry == 'libyal.nuspec':
        output_filename = '{0:s}.nuspec'.format(
            project_configuration.library_name)

        if not project_configuration.deploy_to_nuget:
          logging.warning('Skipping: {0:s}'.format(output_filename))
          continue

      elif directory_entry == 'libyal.pc.in':
        output_filename = '{0:s}.pc.in'.format(
            project_configuration.library_name)

      else:
        output_filename = directory_entry

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)

    del template_mappings['pc_libs_private']

    self._GenerateCodecovYML(
        project_configuration, template_mappings, output_writer, '.codecov.yml')

    self._GenerateGitignore(
        project_configuration, template_mappings, output_writer, '.gitignore')

    self._GenerateGitHubActions(
        project_configuration, template_mappings, include_header_file,
        output_writer)

    output_filename = os.path.join('.github', 'workflows', 'build.yml')
    self._GenerateGitHubActionsBuildYML(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)

    output_filename = os.path.join('.github', 'workflows', 'build_freebsd.yml')
    self._GenerateGitHubActionsBuildFreeBSDYML(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)

    output_filename = os.path.join('.github', 'workflows', 'build_shared.yml')
    self._GenerateGitHubActionsBuildSharedYML(
        project_configuration, template_mappings, include_header_file,
        output_writer, output_filename)

    if project_configuration.HasPythonModule():
      output_filename = os.path.join('.github', 'workflows', 'build_wheel.yml')
      self._GenerateGitHubActionsBuildWheelYML(
          project_configuration, template_mappings, output_writer,
          output_filename)

    self._GenerateAppVeyorYML(
        project_configuration, template_mappings, output_writer, 'appveyor.yml')

    self._GenerateConfigureAC(
        project_configuration, template_mappings, output_writer, 'configure.ac')

    self._GenerateACIncludeM4(
        project_configuration, template_mappings, output_writer, 'acinclude.m4')

    self._GenerateDpkg(
        project_configuration, template_mappings, output_writer, 'dpkg')

    output_filename = '{0:s}.spec.in'.format(project_configuration.library_name)
    self._GenerateRpmSpec(
        project_configuration, template_mappings, output_writer,
        output_filename)

    if project_configuration.HasPythonModule():
      self._GenerateSetupCfgIn(
          project_configuration, template_mappings, output_writer,
          "setup.cfg.in")

      self._GenerateToxIni(
          project_configuration, template_mappings, output_writer, "tox.ini")
