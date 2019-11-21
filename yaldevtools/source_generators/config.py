# -*- coding: utf-8 -*-
"""The source file generator for configuration files."""

from __future__ import unicode_literals

import glob
import logging
import os
import stat

from yaldevtools.source_generators import interface


class ConfigurationFileGenerator(interface.SourceFileGenerator):
  """Configuration file generator."""

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

    if project_configuration.HasPythonModule():
      template_names.append('environment-pypi.yml')

    template_names.append('environment-matrix.yml')

    if project_configuration.HasPythonModule():
      template_names.append('environment-python.yml')

    template_names.append('environment-cygwin.yml')

    # if 'crypto' in project_configuration.library_build_dependencies:
    # TODO: add environment-cygwin-openssl.yml

    if project_configuration.HasPythonModule():
      template_names.append('environment-cygwin-python.yml')

    if project_configuration.HasTools():
      template_names.append('environment-cygwin-static-executables.yml')

    template_names.append('environment-cygwin64.yml')

    # if 'crypto' in project_configuration.library_build_dependencies:
    # TODO: add environment-cygwin64-openssl.yml

    if project_configuration.HasPythonModule():
      template_names.append('environment-cygwin64-python.yml')

    if project_configuration.HasTools():
      template_names.append('environment-cygwin64-static-executables.yml')

    template_names.append('environment-mingw.yml')

    if project_configuration.HasTools():
      template_names.append('environment-mingw-static-executables.yml')

    template_names.append('environment-mingw-w64.yml')

    if project_configuration.HasTools():
      template_names.append('environment-mingw-w64-static-executables.yml')

    template_names.append('install-header.yml')

    if (project_configuration.HasDependencyLex() or
        project_configuration.HasDependencyYacc()):
      template_names.append('install-winflexbison.yml')

    if 'zlib' in project_configuration.library_build_dependencies:
      template_names.append('install-zlib.yml')

    if project_configuration.HasDependencyDokan():
      template_names.append('install-dokan.yml')

    if project_configuration.HasPythonModule():
      template_names.append('install-python.yml')

    template_mappings['pypi_token'] = getattr(
        project_configuration, 'pypi_token_appveyor', '')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['pypi_token']

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

    mingw_msys_build_dependencies = self._GetMinGWMSYSBuildDependencies(
        project_configuration)

    if mingw_msys_build_dependencies:
      mingw_msys_build_dependencies = ' '.join(mingw_msys_build_dependencies)
      template_mappings['mingw_msys_build_dependencies'] = (
          mingw_msys_build_dependencies)

      template_filename = os.path.join(
          template_directory, 'install-mingw-msys.yml')
      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename,
          access_mode='a')

      del template_mappings['mingw_msys_build_dependencies']

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

    template_names.append('build_script-header.yml')

    # TODO: make this configuration driven
    if project_configuration.library_name == 'libevt':
      template_names.append('build_script-vs2017-nuget.yml')
    else:
      template_names.append('build_script-vs2017.yml')

    if project_configuration.HasPythonModule():
      template_names.append('build_script-python.yml')

    template_names.extend([
        'build_script-footer.yml', 'test_script.yml', 'after_test.yml'])

    # TODO: make this configuration driven
    if (project_configuration.library_name == 'libevt' or
        project_configuration.HasPythonModule()):
      template_names.append('artifacts.yml')

      if project_configuration.library_name == 'libevt':
        template_names.append('artifacts-nuget.yml')

      elif project_configuration.HasPythonModule():
        template_names.append('artifacts-pypi.yml')

      if project_configuration.library_name == 'libevt':
        template_names.append('deploy-nuget.yml')

      if project_configuration.HasPythonModule():
        template_names.append('deploy-pypi.yml')

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

    if 'crypto' in project_configuration.library_build_dependencies:
      if libcrypto_index == len(library_dependencies):
        libraries.append('libcrypto')
        library_dependencies.append('libcrypto')

    if 'sgutils' in project_configuration.library_build_dependencies:
      libraries.append('sgutils2')
      library_dependencies.append('sgutils2')

    # Have zlib checked before libcrypto.
    if 'zlib' in project_configuration.library_build_dependencies:
      if libcrypto_index < len(library_dependencies):
        libraries.insert(libcrypto_index, 'zlib')
        library_dependencies.insert(libcrypto_index, 'zlib')
      else:
        libraries.append('zlib')
        library_dependencies.append('zlib')

    template_directory = os.path.join(self._template_directory, 'configure.ac')

    template_names = [
        'header.ac', 'programs.ac', 'compiler_language.ac', 'build_features.ac']

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
        template_mappings['local_library_name'] = name
        template_mappings['local_library_name_upper_case'] = name.upper()

        if name != 'zlib':
          template_filename = 'check_dependency_support.ac'

        # TODO: make check more generic based on the source itself.
        elif project_configuration.library_name == 'libewf':
          template_filename = 'check_zlib_compress.ac'

        # TODO: determine deflate function via configuration setting? 
        elif project_configuration.library_name in (
            'libfsapfs', 'libfvde', 'libmodi', 'libpff', 'libvmdk'):
          template_filename = 'check_zlib_uncompress.ac'

        else:
          template_filename = 'check_zlib_inflate.ac'

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

    template_names = ['check_tests_support.ac', 'dll_support.ac', 'compiler_flags.ac']

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
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

      if tools_dependencies:
        local_library_tests = []
        for name in tools_dependencies:
          if name == 'libfuse':
            local_library_test = 'test "x$ac_cv_{0:s}" != xno'.format(name)
          else:
            local_library_test = 'test "x$ac_cv_{0:s}" = xyes'.format(name)

          local_library_tests.append(local_library_test)

        template_mappings['local_library_tests'] = ' || '.join(
            local_library_tests)

        template_filename = os.path.join(
            template_directory, 'spec_requires_tools.ac')
        self._GenerateSection(
            template_filename, template_mappings, output_writer, output_filename,
            access_mode='a')

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

    if project_configuration.HasDotNetBindings():
      template_names.append('config_files_dotnet_rc.ac')

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
      if name not in ('libcrypto', 'zlib'):
        build_options.append((
            '{0:s} support'.format(name), '$ac_cv_{0:s}'.format(name)))

      if name == 'libcaes':
       if project_configuration.library_name == 'libbde':
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

       elif project_configuration.library_name == 'libluksde':
          build_options.extend([
              ('AES-CBC support', '$ac_cv_libcaes_aes_cbc'),
              ('AES-ECB support', '$ac_cv_libcaes_aes_ecb')])

       elif project_configuration.library_name in ('libmodi', 'libqcow'):
          build_options.append(
              ('AES-CBC support', '$ac_cv_libcaes_aes_cbc'))

      elif name == 'libhmac':
        # TODO: make check more generic based on the source itself.
        if project_configuration.library_name in (
            'libbde', 'libfsapfs', 'libfvde', 'libmodi'):
          build_options.append(('SHA256 support', '$ac_cv_libhmac_sha256'))

        elif project_configuration.library_name in (
            'libewf', 'libodraw', 'libsmraw'):
          build_options.extend([
              ('MD5 support', '$ac_cv_libhmac_md5'),
              ('SHA1 support', '$ac_cv_libhmac_sha1'),
              ('SHA256 support', '$ac_cv_libhmac_sha256')])

        elif project_configuration.library_name == 'libluksde':
          build_options.extend([
              ('SHA1 support', '$ac_cv_libhmac_sha1'),
              ('SHA224 support', '$ac_cv_libhmac_sha224'),
              ('SHA256 support', '$ac_cv_libhmac_sha256'),
              ('SHA512 support', '$ac_cv_libhmac_sha512')])

      elif name == 'zlib':
        # TODO: determine deflate function via configuration setting? 
        if project_configuration.library_name in (
            'libfsapfs', 'libfvde', 'libmodi', 'libpff', 'libvmdk'):
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

    template_directory = os.path.join(self._template_directory, 'dpkg')

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

    template_mappings['dpkg_build_dependencies'] = ', '.join(dpkg_build_dependencies)

    template_filename = os.path.join(template_directory, 'control')
    output_filename = os.path.join(output_directory, 'control')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

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
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    template_directory = os.path.join(
        self._template_directory, 'libyal.spec.in')

    template_filename = os.path.join(template_directory, 'header.in')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    library_dependencies = list(makefile_am_file.library_dependencies)

    if 'crypto' in project_configuration.library_build_dependencies:
      library_dependencies.append('libcrypto')
    if 'zlib' in project_configuration.library_build_dependencies:
      library_dependencies.append('zlib')

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

  def _GenerateTravisBeforeInstallSh(
      self, project_configuration, template_mappings, output_writer):
    """Generates the .travis/before_install.sh script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, '.travis', 'before_install.sh')

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    if 'fuse' in project_configuration.tools_build_dependencies:
      template_names = ['header-fuse.sh']
    else:
      template_names = ['header.sh']

    if project_configuration.coverity_scan_token:
      template_names.append('coverity.sh')

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['dpkg_build_dependencies'] = ' '.join(
        dpkg_build_dependencies)

    output_filename = os.path.join('.travis', 'before_install.sh')
    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

    # Set x-bit for .sh script.
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

  def _GenerateTravisInstallSh(self, template_mappings, output_writer):
    """Generates the .travis/install.sh script file.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, '.travis', 'install.sh')

    template_names = ['body.sh']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    output_filename = os.path.join('.travis', 'install.sh')
    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    # Set x-bit for .sh script.
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

  def _GenerateTravisRunTestsSh(self, template_mappings, output_writer):
    """Generates the .travis/runtests.sh script file.

    Args:
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, '.travis', 'runtests.sh')

    template_names = ['body.sh']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    output_filename = os.path.join('.travis', 'runtests.sh')
    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    # Set x-bit for .sh script.
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

  def _GenerateTravisScriptDockerSh(
      self, project_configuration, template_mappings, output_writer):
    """Generates the .travis/script_docker.sh script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, '.travis', 'script_docker.sh')

    template_names = ['body.sh']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    dpkg_build_dependencies = self._GetDpkgBuildDependencies(
        project_configuration)

    template_mappings['dpkg_build_dependencies'] = ' '.join(sorted(
        dpkg_build_dependencies))

    output_filename = os.path.join('.travis', 'script_docker.sh')
    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    del template_mappings['dpkg_build_dependencies']

    # Set x-bit for .sh script.
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

  def _GenerateTravisScriptSh(
      self, project_configuration, template_mappings, output_writer):
    """Generates the .travis/script.sh script file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(
        self._template_directory, '.travis', 'script.sh')

    if project_configuration.HasPythonModule():
      template_names = ['body-python.sh']
    else:
      template_names = ['body.sh']

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    output_filename = os.path.join('.travis', 'script.sh')
    self._GenerateSections(
        template_filenames, template_mappings, output_writer, output_filename)

    # Set x-bit for .sh script.
    stat_info = os.stat(output_filename)
    os.chmod(output_filename, stat_info.st_mode | stat.S_IEXEC)

  def _GenerateTravisYML(
      self, project_configuration, template_mappings, include_header_file,
      output_writer):
    """Generates the .travis.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      include_header_file (LibraryIncludeHeaderFile): library include header
          file.
      output_writer (OutputWriter): output writer.
    """
    template_directory = os.path.join(self._template_directory, '.travis.yml')

    template_names = ['header.yml']

    if project_configuration.coverity_scan_token:
      template_names.append('env.yml')

    template_names.append('matrix-header.yml')

    if project_configuration.coverity_scan_token:
      template_names.append('matrix-coverity.yml')

    template_names.append('matrix-linux.yml')

    # TODO: improve check.
    if project_configuration.library_name in ('libbfio', 'libcdata'):
      template_names.append('matrix-linux-no_pthread.yml')

    if include_header_file.have_wide_character_type:
      template_names.append('matrix-linux-wide_character_type.yml')

    # TODO: make conditional
    # template_names.append('matrix-linux-debug_output.yml')

    template_names.append('matrix-linux-no_optimization.yml')

    if 'crypto' in project_configuration.library_build_dependencies:
      template_names.append('matrix-linux-openssl.yml')

    if project_configuration.HasPythonModule():
      template_names.append('matrix-linux-python.yml')

    template_names.append('matrix-linux-shared.yml')

    if (include_header_file and include_header_file.have_wide_character_type or
        project_configuration.HasTools()):
      template_names.append('matrix-linux-shared-wide_character_type.yml')

    if project_configuration.HasTools():
      template_names.append('matrix-linux-static-executables.yml')

    template_names.append('matrix-macos.yml')

    if project_configuration.HasPythonModule():
      template_names.append('matrix-macos-python.yml')

    if project_configuration.HasPythonModule():
      template_names.append('matrix-macos-python-pkgbuild.yml')
    else:
      template_names.append('matrix-macos-pkgbuild.yml')

    template_names.extend([
        'before_install.yml', 'install.yml', 'script.yml', 'after_success.yml'])

    template_filenames = [
        os.path.join(template_directory, template_name)
        for template_name in template_names]

    template_mappings['coverity_scan_token'] = (
        project_configuration.coverity_scan_token or '')

    no_optimization_configure_options = ['--enable-shared=no']
    if include_header_file.have_wide_character_type:
      no_optimization_configure_options.append('--enable-wide-character-type')

    template_mappings['no_optimization_configure_options'] = ' '.join(
        no_optimization_configure_options)

    self._GenerateSections(
        template_filenames, template_mappings, output_writer, '.travis.yml')

    del template_mappings['coverity_scan_token']
    del template_mappings['no_optimization_configure_options']

  def _GetBrewBuildDependencies(self, project_configuration):
    """Retrieves the brew build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.

    Returns:
      list[str]: dpkg build dependencies.
    """
    brew_build_dependencies = ['gettext', 'gnu-sed']

    if 'fuse' in project_configuration.tools_build_dependencies:
      brew_build_dependencies.append('osxfuse')

    return brew_build_dependencies

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

    if 'zlib' in project_configuration.library_build_dependencies:
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
    dpkg_build_dependencies = ['debhelper (>= 9)', 'dh-autoreconf', 'pkg-config']

    if 'zlib' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('zlib1g-dev')
    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if project_configuration.HasPythonModule():
      dpkg_build_dependencies.extend([
          'python-dev', 'python-setuptools', 'python3-dev',
          'python3-setuptools'])

    if 'fuse' in project_configuration.tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse-dev')

    if 'sgutils' in project_configuration.library_build_dependencies:
      dpkg_build_dependencies.append('libsgutils2-dev')

    if project_configuration.dpkg_build_dependencies:
      dpkg_build_dependencies.extend(project_configuration.dpkg_build_dependencies)

    return dpkg_build_dependencies

  def _GetCygwinBuildDependencies(self, project_configuration):
    """Retrieves the Cygwin build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    cygwin_build_dependencies = list(
        project_configuration.cygwin_build_dependencies)

    if project_configuration.HasDependencyYacc():
      cygwin_build_dependencies.append('bison')
    if project_configuration.HasDependencyLex():
      cygwin_build_dependencies.append('flex')

    if 'zlib' in project_configuration.library_build_dependencies:
      cygwin_build_dependencies.append('zlib-devel')
    if project_configuration.HasDependencyBzip2():
      cygwin_build_dependencies.append('bzip2-devel')

    if ('crypto' in project_configuration.library_build_dependencies or
        'crypto' in project_configuration.tools_build_dependencies):
      # On Cygwin also link zlib since libcrypto relies on it.
      if 'zlib' not in project_configuration.library_build_dependencies:
        cygwin_build_dependencies.append('zlib-devel')

      cygwin_build_dependencies.append('openssl-devel')

    if project_configuration.HasPythonModule():
      cygwin_build_dependencies.append('python2-devel')
      cygwin_build_dependencies.append('python3-devel')

    if ('uuid' in project_configuration.library_build_dependencies or
        'uuid' in project_configuration.tools_build_dependencies):
      cygwin_build_dependencies.append('libuuid-devel')

    return cygwin_build_dependencies

  def _GetMinGWMSYSBuildDependencies(self, project_configuration):
    """Retrieves the MinGW-MSYS build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    mingw_msys_build_dependencies = list(
        project_configuration.mingw_msys_build_dependencies)

    # TODO: add support for other dependencies.
    if 'zlib' in project_configuration.library_build_dependencies:
      mingw_msys_build_dependencies.append('libz-dev')

    return mingw_msys_build_dependencies

  def _GetMinGWMSYS2BuildDependencies(self, project_configuration):
    """Retrieves the MinGW-MSYS2 build dependencies.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
    """
    mingw_msys2_build_dependencies = list(
        project_configuration.mingw_msys2_build_dependencies)

    if project_configuration.HasDependencyYacc():
      mingw_msys2_build_dependencies.append('msys/bison')
    if project_configuration.HasDependencyLex():
      mingw_msys2_build_dependencies.append('msys/flex')

    # TODO: add support for other dependencies.
    if 'zlib' in project_configuration.library_build_dependencies:
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

      if directory_entry == 'libyal.nuspec':
        output_filename = '{0:s}.nuspec'.format(
            project_configuration.library_name)

        # TODO: for now only generate a nuspec file when exists.
        if not os.path.isfile(output_filename):
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

    self._GenerateTravisYML(
        project_configuration, template_mappings, include_header_file,
        output_writer)

    self._GenerateTravisBeforeInstallSh(
        project_configuration, template_mappings, output_writer)

    self._GenerateTravisInstallSh(template_mappings, output_writer)

    self._GenerateTravisRunTestsSh(template_mappings, output_writer)

    self._GenerateTravisScriptSh(
        project_configuration, template_mappings, output_writer)

    self._GenerateTravisScriptDockerSh(
        project_configuration, template_mappings, output_writer)

    self._GenerateAppVeyorYML(
        project_configuration, template_mappings, output_writer, 'appveyor.yml')

    self._GenerateConfigureAC(
        project_configuration, template_mappings, output_writer, 'configure.ac')

    self._GenerateDpkg(
        project_configuration, template_mappings, output_writer, 'dpkg')

    output_filename = '{0:s}.spec.in'.format(project_configuration.library_name)
    self._GenerateRpmSpec(
        project_configuration, template_mappings, output_writer,
        output_filename)
