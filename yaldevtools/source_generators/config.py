# -*- coding: utf-8 -*-
"""The source file generator for configuration files."""

import glob
import logging
import os

from yaldevtools.source_generators import interface


class Dependency(object):
  """Dependency.

  Attributes:
    is_local (bool): True if the library is included as part of the source.
    name (str): name.
  """

  def __init__(self, is_local=False, name=None):
    """Initializes a dependency.

    Args:
      is_local (Optional[bool]): True if the library is included as part of the
          source.
      name (Optional[str]): name.
    """
    super(Dependency, self).__init__()
    self.is_local = is_local
    self.name = name


class ConfigurationFileGenerator(interface.SourceFileGenerator):
  """Configuration file generator."""

  _PLACEHOLDER_VALUE_CALLBACKS = {
      'brew_build_dependencies': '_GetBrewBuildDependencies',
      'cygwin_build_dependencies': '_GetCygwinBuildDependencies',
      'dpkg_build_dependencies': '_GetDpkgBuildDependencies',
      'freebsd_build_dependencies': '_GetFreeBSDBuildDependencies',
      'mingw_msys2_build_dependencies': '_GetMinGWMSYS2BuildDependencies',
      'python_module_development_status': '_GetPythonModuleDevelopmentStatus'}

  def _GenerateACIncludeM4(self, project_configuration, template_mappings):
    """Generates the acinclude.m4 configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    templates_path = os.path.join(self._templates_path, 'acinclude.m4')

    library_name = project_configuration.library_name

    m4_file = os.path.join(self._data_directory, 'm4', f'{library_name:s}.m4')
    if os.path.exists(m4_file):
      with open(m4_file, 'r', encoding='utf8') as file_object:
        input_lines = file_object.readlines()

      with open('acinclude.m4', 'w', encoding='utf8') as file_object:
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
        library_name_upper = library_name.upper()
        m4_macro_definition = (
            f'AC_DEFUN([AX_{library_name_upper:s}_CHECK_LOCAL],')

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
      template_mappings['library_name'] = library_name

      self._GenerateSectionsFromOperationsFile(
          'acinclude.m4.yaml', 'main', project_configuration, template_mappings,
          'acinclude.m4')

      del template_mappings['library_name']

    template_mappings['library_name'] = library_name

    if project_configuration.HasTools():
      template_filename = 'check_dll_support.m4-tools'
    else:
      template_filename = 'check_dll_support.m4'

    template_filename = os.path.join(templates_path, template_filename)
    self._GenerateSection(
        template_filename, template_mappings, 'acinclude.m4', access_mode='a')

    del template_mappings['library_name']

  def _GenerateAppVeyorYML(self, project_configuration, template_mappings):
    """Generates the appveyor.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    # if project_configuration.HasDependencyCrypto():
    # TODO: add environment-cygwin64-openssl.yml

    template_mappings['has_test_data_script'] = bool(
        os.path.isfile('synctestdata.sh'))

    template_mappings['pypi_token'] = getattr(
        project_configuration, 'pypi_token_appveyor', '')

    self._GenerateSectionsFromOperationsFile(
        'appveyor.yml.yaml', 'main', project_configuration, template_mappings,
        'appveyor.yml')

    del template_mappings['has_test_data_script']
    del template_mappings['pypi_token']

  def _GenerateCodecovYML(self, project_configuration, template_mappings):
    """Generates the .codecov.yml configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    ignore_paths = list(makefile_am_file.libraries)
    ignore_paths.append('tests')

    template_mappings['ignore_paths'] = sorted(ignore_paths)

    self._GenerateSectionsFromOperationsFile(
        'codecov.yml.yaml', 'main', project_configuration, template_mappings,
        '.codecov.yml')

    del template_mappings['ignore_paths']

  def _GenerateConfigureAC(self, project_configuration, template_mappings):
    """Generates the configure.ac configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    # TODO: change indentation of templates.

    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    library_dependencies = [
        Dependency(is_local=True, name=name)
        for name in makefile_am_file.library_dependencies]

    libcrypto_index = len(makefile_am_file.library_dependencies)
    if 'libcaes' in makefile_am_file.library_dependencies:
      libcaes_index = makefile_am_file.library_dependencies.index('libcaes')
      libcrypto_index = min(libcrypto_index, libcaes_index)

    if 'libhmac' in makefile_am_file.library_dependencies:
      libhmac_index = makefile_am_file.library_dependencies.index('libhmac')
      libcrypto_index = min(libcrypto_index, libhmac_index)

    if project_configuration.HasDependencyCrypto():
      if libcrypto_index == len(makefile_am_file.library_dependencies):
        dependency = Dependency(name='libcrypto')
        library_dependencies.append(dependency)

    if 'sgutils' in project_configuration.library_build_dependencies:
      dependency = Dependency(name='sgutils2')
      library_dependencies.append(dependency)

    if 'bzip2' in project_configuration.library_build_dependencies:
      dependency = Dependency(name='bzip2')

      if libcrypto_index < len(makefile_am_file.library_dependencies):
        library_dependencies.insert(libcrypto_index, dependency)
      else:
        library_dependencies.append(dependency)

    # Have zlib checked before libcrypto.
    if project_configuration.HasDependencyZlib():
      dependency = Dependency(name='bzip2')

      if libcrypto_index < len(makefile_am_file.library_dependencies):
        library_dependencies.insert(libcrypto_index, dependency)
      else:
        library_dependencies.append(dependency)

    tools_dependencies = []
    if project_configuration.HasTools():
      tools_dependencies = [
          Dependency(is_local=True, name=name)
          for name in makefile_am_file.tools_dependencies]

      if 'uuid' in project_configuration.tools_build_dependencies:
        dependency = Dependency(name='libuuid')
        tools_dependencies.append(dependency)

      if 'fuse' in project_configuration.tools_build_dependencies:
        dependency = Dependency(name='libfuse')
        tools_dependencies.append(dependency)

    spec_library_tests = []
    for dependency in library_dependencies:
      if dependency.name in makefile_am_file.library_dependencies:
        spec_dependency_test = f'test "x$ac_cv_{dependency.name:s}" = xyes'
      else:
        spec_dependency_test = f'test "x$ac_cv_{dependency.name:s}" != xno'

      spec_library_tests.append(spec_dependency_test)

    if 'libcaes' in library_dependencies or 'libhmac' in library_dependencies:
      spec_library_tests.append('test "x$ac_cv_libcrypto" != xno')

    spec_tools_tests = []
    if project_configuration.HasTools():
      spec_tools_dependencies = list(tools_dependencies)
      if 'crypto' in project_configuration.tools_build_dependencies:
        dependency = Dependency(name='libcrypto')
        spec_tools_dependencies.append(dependency)

      for dependency in spec_tools_dependencies:
        if dependency.name in ('libcrypto', 'libfuse'):
          spec_dependency_test = f'test "x$ac_cv_{dependency.name:s}" != xno'
        else:
          spec_dependency_test = f'test "x$ac_cv_{dependency.name:s}" = xyes'

        spec_tools_tests.append(spec_dependency_test)

    # TODO: move conditions below to configure.ac.yaml

    # for dependency in library_dependencies:
    #   if (dependency.name == 'libcrypto' and
    #       project_configuration.library_name == 'libcaes'):
    #     continue

    #   if dependency.name == 'zlib':
    #     # TODO: make check more generic based on the source itself.
    #     if project_configuration.library_name == 'libewf':
    #       template_filename = 'check_zlib_compress.ac'

    #     # TODO: determine deflate function via configuration setting?
    #     elif project_configuration.library_name in (
    #         'libfsapfs', 'libfshfs', 'libfvde', 'libmodi', 'libpff',
    #         'libvmdk'):
    #       template_filename = 'check_zlib_uncompress.ac'

    #     else:
    #       template_filename = 'check_zlib_inflate.ac'

    templates_path = os.path.join(self._templates_path, 'configure.ac')

    # TODO: add support for Makefile in documents (libuna)

    # TODO: add support for build options configuration

    build_options = []
    for dependency in library_dependencies:
      if dependency.name not in ('bzip2', 'libcrypto', 'zlib'):
        build_options.append(
            (f'{dependency.name:s} support', f'$ac_cv_{dependency.name:s}'))

      if dependency.name == 'bzip2':
        build_options.append(('BZIP2 compression support', '$ac_cv_bzip2'))

      if dependency.name == 'libcaes':
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

      elif dependency.name == 'libhmac':
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

      elif dependency.name == 'libfcrypto':
        if project_configuration.library_name == 'libluksde':
          build_options.extend([
              ('ARC4-ECB support', '$ac_cv_libfcrypto'),
              ('Serpent-CBC support', '$ac_cv_libfcrypto'),
              ('Serpent-ECB support', '$ac_cv_libfcrypto')])

      elif dependency.name == 'zlib':
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
      description = (
          f'{project_configuration.tools_directory:s} are build as static '
          f'executables')
      value = '$ac_cv_enable_static_executables'
      features_information.append((description, value))

      maximum_description_length = max(
          maximum_description_length, len(description))

    if project_configuration.HasPythonModule():
      description = (
          f'Python ({project_configuration.python_module_name:s}) support')
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
        padding = ' ' * (maximum_description_length - len(description))

        notice_message.append(f'   {description:s}: {padding:s}{value:s}')

      notice_message.append('')

    if features_information:
      notice_message.append('Features:')

      for description, value in features_information:
        padding = ' ' * (maximum_description_length - len(description))

        notice_message.append(f'   {description:s}: {padding:s}{value:s}')

    template_mappings['library_dependencies'] = library_dependencies
    template_mappings['notice_message'] = '\n'.join(notice_message)
    template_mappings['spec_library_tests'] = ' || '.join(spec_library_tests)
    template_mappings['spec_tools_tests'] = ' || '.join(spec_tools_tests)
    template_mappings['tools_dependencies'] = tools_dependencies

    self._GenerateSectionsFromOperationsFile(
        'configure.ac.yaml', 'main', project_configuration, template_mappings,
        'configure.ac')

    del template_mappings['library_dependencies']
    del template_mappings['notice_message']
    del template_mappings['spec_library_tests']
    del template_mappings['spec_tools_tests']
    del template_mappings['tools_dependencies']

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

    templates_path = os.path.join(self._templates_path, 'dpkg')

    template_mappings['library_name'] = project_configuration.library_name

    for directory_entry in os.listdir(templates_path):
      template_filename = os.path.join(templates_path, directory_entry)
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
        output_filename = ''.join([
            project_configuration.library_name, output_filename[6:]])

      output_filename = os.path.join(output_directory, output_filename)
      self._GenerateSection(
          template_filename, template_mappings, output_filename)

    dpkg_build_dependencies = self._GetDpkgBuildDependenciesDpkgControl(
        project_configuration)

    template_mappings['dpkg_build_dependencies'] = ', '.join(
        dpkg_build_dependencies)
    template_mappings['dpkg_library_description'] = ''.join([
        project_configuration.library_name, ' is a ',
        project_configuration.library_description[0].lower(),
        project_configuration.library_description[1:]])

    template_filename = os.path.join(templates_path, 'control')
    output_filename = os.path.join(output_directory, 'control')
    self._GenerateSection(
        template_filename, template_mappings, output_filename)

    del template_mappings['dpkg_build_dependencies']
    del template_mappings['dpkg_library_description']

    if project_configuration.HasTools():
      template_filename = os.path.join(templates_path, 'control-tools')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
          access_mode='a')

    if project_configuration.HasPythonModule():
      template_filename = os.path.join(templates_path, 'control-python')
      output_filename = os.path.join(output_directory, 'control')
      self._GenerateSection(
          template_filename, template_mappings, output_filename,
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

    template_filename = os.path.join(templates_path, template_filename)
    output_filename = os.path.join(output_directory, 'rules')
    self._GenerateSection(template_filename, template_mappings, output_filename)

    templates_path = os.path.join(self._templates_path, 'dpkg', 'source')
    output_directory = os.path.join(output_directory, 'source')

    for directory_entry in os.listdir(templates_path):
      template_filename = os.path.join(templates_path, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(output_directory, directory_entry)
      self._GenerateSection(
          template_filename, template_mappings, output_filename)

    del template_mappings['library_name']

  def _GenerateGitignore(self, project_configuration, template_mappings):
    """Generates the .gitignore configuration file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    include_header_file = self._GetLibraryIncludeHeaderFile(
        project_configuration)

    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    local_libraries = [
        '/'.join(['', name]) for name in sorted(makefile_am_file.libraries)]

    tests_files = ['/tests/tmp*']

    if (project_configuration.library_name != 'libcnotify' and
        'libcnotify' in makefile_am_file.library_dependencies):
      tests_files.append('/tests/notify_stream.log')

    if os.path.exists(os.path.join('tests', 'input')):
      tests_files.append('/tests/input')

    source_glob = os.path.join(
        'tests', f'{project_configuration.library_name_suffix:s}_test_*.c')
    for source_file_path in sorted(glob.glob(source_glob)):
      if (source_file_path.endswith('_functions.c') or
          source_file_path.endswith('_getopt.c') or
          source_file_path.endswith('_i18n.c') or
          source_file_path.endswith('_memory.c') or
          source_file_path.endswith('_rwlock.c')):
        continue

      tests_files.append(f'/{source_file_path[:-2]:s}')

    tools_executables = [
        '/'.join(['', project_configuration.tools_directory, name])
        for name in sorted(project_configuration.tools_names)]

    template_mappings['local_libraries'] = '\n'.join(sorted(local_libraries))
    template_mappings['tests_files'] = '\n'.join(sorted(tests_files))
    template_mappings['tools_executables'] = '\n'.join(tools_executables)

    self._GenerateSectionsFromOperationsFile(
        'gitignore.yaml', 'main', project_configuration, template_mappings,
        '.gitignore')

    del template_mappings['local_libraries']
    del template_mappings['tests_files']
    del template_mappings['tools_executables']

  def _GenerateRpmSpec(self, project_configuration, template_mappings):
    """Generates the RPM spec file.

    Args:
      project_configuration (ProjectConfiguration): project configuration.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
    """
    makefile_am_file = self._GetMainMakefileAM(project_configuration)

    library_dependencies = list(makefile_am_file.library_dependencies)
    if project_configuration.HasDependencyCrypto():
      library_dependencies.append('libcrypto')
    if project_configuration.HasDependencyZlib():
      library_dependencies.append('zlib')

    tools_dependencies = []
    if project_configuration.HasTools():
      tools_dependencies = list(makefile_am_file.tools_dependencies)
      if 'crypto' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libcrypto')
      if 'fuse' in project_configuration.tools_build_dependencies:
        tools_dependencies.append('libfuse')

    tools_spec_build_requires = []
    tools_spec_requires = [
        f'{project_configuration.library_name:s} = %{{version}}-%{{release}}']
    for name in sorted(tools_dependencies):
      tools_spec_build_requires.append(f'@ax_{name:s}_spec_build_requires@')
      tools_spec_requires.append(f'@ax_{name:s}_spec_requires@')

    spec_build_requires = ['gcc']
    spec_requires = []
    for name in sorted(library_dependencies):
      spec_build_requires.append(f'@ax_{name:s}_spec_build_requires@')
      spec_requires.append(f'@ax_{name:s}_spec_requires@')

    template_mappings['library_name'] = project_configuration.library_name
    template_mappings['spec_build_requires'] = ' '.join(spec_build_requires)
    template_mappings['spec_requires'] = ' '.join(spec_requires)
    template_mappings['tools_spec_build_requires'] = ' '.join(tools_spec_build_requires)
    template_mappings['tools_spec_requires'] = ' '.join(tools_spec_requires)

    self._GenerateSectionsFromOperationsFile(
        'libyal.spec.in.yaml', 'main', project_configuration, template_mappings,
        f'{project_configuration.library_name:s}.spec.in')

    del template_mappings['library_name']
    del template_mappings['spec_build_requires']
    del template_mappings['spec_requires']
    del template_mappings['tools_spec_build_requires']
    del template_mappings['tools_spec_requires']

  def _GetBrewBuildDependencies(self, namespace):
    """Retrieves the brew build dependencies.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      str: brew build dependencies.
    """
    library_build_dependencies = namespace.get(
        'library_build_dependencies', None) or []
    tools_build_dependencies = namespace.get(
        'tools_build_dependencies', None) or []

    brew_build_dependencies = [
        'autoconf', 'automake', 'gettext', 'gnu-sed', 'libtool', 'pkg-config']

    if ('crypto' in library_build_dependencies or
        'crypto' in tools_build_dependencies):
      brew_build_dependencies.append('openssl')

    if 'fuse' in tools_build_dependencies:
      brew_build_dependencies.append('macfuse')

    return ' '.join(sorted(brew_build_dependencies))

  def _GetCygwinBuildDependencies(self, namespace):
    """Retrieves the Cygwin build dependencies.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      str: Cygwin build dependencies.
    """
    library_build_dependencies = namespace.get(
        'library_build_dependencies', None) or []
    tools_build_dependencies = namespace.get(
        'tools_build_dependencies', None) or []
    project_features = namespace.get('project_features', None) or []

    cygwin_build_dependencies = ['gettext-devel', 'wget']

    cygwin_build_dependencies.extend(
        namespace.get('cygwin_build_dependencies', None) or [])

    if ('yacc' in library_build_dependencies or
        'yacc' in tools_build_dependencies):
      cygwin_build_dependencies.append('bison')
    if 'lex' in library_build_dependencies or 'lex' in tools_build_dependencies:
      cygwin_build_dependencies.append('flex')

    if 'zlib' in library_build_dependencies:
      cygwin_build_dependencies.append('zlib-devel')
    if 'bzip2' in library_build_dependencies:
      cygwin_build_dependencies.append('libbz2-devel')

    if ('crypto' in library_build_dependencies or
        'crypto' in tools_build_dependencies):
      # On Cygwin also link zlib since libcrypto relies on it.
      if 'zlib' not in library_build_dependencies:
        cygwin_build_dependencies.append('zlib-devel')

      cygwin_build_dependencies.append('libssl-devel')

    if 'python_bindings' in project_features:
      cygwin_build_dependencies.append('python3-devel')

    if ('uuid' in library_build_dependencies or
        'uuid' in tools_build_dependencies):
      cygwin_build_dependencies.append('libuuid-devel')

    if 'fuse' in tools_build_dependencies:
      cygwin_build_dependencies.append('cygfuse')

    return ' '.join([
        f'-P {name:s}' for name in sorted(cygwin_build_dependencies)])

  def _GetDpkgBuildDependencies(self, namespace):
    """Retrieves the dpkg build dependencies.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      list[str]: dpkg build dependencies in alphabetical order.
    """
    library_build_dependencies = namespace.get(
        'library_build_dependencies', None) or []
    tools_build_dependencies = namespace.get(
        'tools_build_dependencies', None) or []

    dpkg_build_dependencies = [
        'autoconf', 'automake', 'autopoint', 'build-essential', 'git',
        'libtool', 'pkg-config']

    dpkg_build_dependencies.extend(
        namespace.get('dpkg_build_dependencies', None) or [])

    if 'yacc' in library_build_dependencies:
      dpkg_build_dependencies.append('byacc')
    if 'lex' in library_build_dependencies:
      dpkg_build_dependencies.append('flex')

    if 'zlib' in library_build_dependencies:
      dpkg_build_dependencies.append('zlib1g-dev')

    if ('crypto' in library_build_dependencies or
        'crypto' in tools_build_dependencies):
      dpkg_build_dependencies.append('libssl-dev')

    if 'fuse' in tools_build_dependencies:
      dpkg_build_dependencies.append('libfuse3-dev')

    if 'sgutils' in library_build_dependencies:
      dpkg_build_dependencies.append('libsgutils2-dev')

    return ' '.join(sorted(dpkg_build_dependencies))

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

  def _GetFreeBSDBuildDependencies(self, namespace):
    """Retrieves the FreeBSD build dependencies.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      str: FreeBSD build dependencies.
    """
    library_build_dependencies = namespace.get(
        'library_build_dependencies', None) or []
    tools_build_dependencies = namespace.get(
        'tools_build_dependencies', None) or []

    freebsd_build_dependencies = [
        'autoconf', 'automake', 'bash', 'gettext', 'git', 'libtool', 'pkgconf']

    freebsd_build_dependencies.extend(
        namespace.get('freebsd_build_dependencies', None) or [])

    if 'yacc' in library_build_dependencies:
      freebsd_build_dependencies.append('byacc')
    if 'lex' in library_build_dependencies:
      freebsd_build_dependencies.append('flex')

    if ('crypto' in library_build_dependencies or
        'crypto' in tools_build_dependencies):
      freebsd_build_dependencies.append('openssl')

    if 'fuse' in tools_build_dependencies:
      freebsd_build_dependencies.append('fusefs-libs')

    return ' '.join(sorted(freebsd_build_dependencies))

  def _GetMinGWMSYS2BuildDependencies(self, namespace):
    """Retrieves the MinGW-MSYS2 build dependencies.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      str: MinGW-MSYS2 build dependencies.
    """
    library_build_dependencies = namespace.get(
        'library_build_dependencies', None) or []
    project_features = namespace.get('project_features', None) or []

    mingw_msys2_build_dependencies = [
        'autoconf', 'automake', 'gettext-devel', 'libtool', 'make',
        'mingw-w64-x86_64-gcc', 'pkg-config']

    mingw_msys2_build_dependencies.extend(
        namespace.get('mingw_msys2_build_dependencies', None) or [])

    if 'yacc' in library_build_dependencies:
      mingw_msys2_build_dependencies.append('msys/bison')
    if 'lex' in library_build_dependencies:
      mingw_msys2_build_dependencies.append('msys/flex')

    # TODO: add support for other dependencies.
    if 'zlib' in library_build_dependencies:
      mingw_msys2_build_dependencies.append('msys/zlib-devel')

    if 'python_bindings' in project_features:
      mingw_msys2_build_dependencies.append('mingw-w64-x86_64-python3')

    return ' '.join(sorted(mingw_msys2_build_dependencies))

  def _GetPythonModuleDevelopmentStatus(self, namespace):
    """Retrieves the Python module development status.

    Args:
      namespace (dict[str, object])): expression namespace.

    Returns:
      str: Python module development status.
    """
    project_status = namespace.get('project_status', None)

    if project_status == 'experimental':
      return '2 - Pre-Alpha'

    if project_status == 'alpha':
      return '3 - Alpha'

    if project_status == 'beta':
      return '4 - Beta'

    return '5 - Production/Stable'

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
      logging.warning((
          f'Missing: {self._library_include_header_path:s} skipping '
          f'generation of configuration files.'))
      return

    makefile_am_file = self._GetLibraryMakefileAM(project_configuration)

    if not makefile_am_file:
      logging.warning((
          f'Missing: {self._library_makefile_am_path:s} skipping generation '
          f'of configuration files.'))
      return

    pc_libs_private = []
    for library in sorted(makefile_am_file.libraries):
      if library != 'libdl':
        pc_libs_private.append(f'@ax_{library:s}_pc_libs_private@')

    template_mappings = self._GetTemplateMappings(
        project_configuration,
        authors_separator=',\n *                          ')

    template_mappings['authors'] = 'Joachim Metz <joachim.metz@gmail.com>'

    template_mappings['pc_libs_private'] = ' '.join(pc_libs_private)

    for directory_entry in os.listdir(self._templates_path):
      template_filename = os.path.join(self._templates_path, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      # TODO: skip operator definitons files based on header.
      if directory_entry in (
          'acinclude.m4.yaml', 'appveyor.yml.yaml', 'codecov.yml.yaml',
          'configure.ac.yaml', 'gitignore.yaml', 'libyal.spec.in.yaml',
          'setup.cfg.in.yaml', 'tox.ini.yaml'):
        continue

      if (directory_entry in ('pyproject.toml', 'setup.py') and
          not project_configuration.HasPythonModule()):
        continue

      if directory_entry == 'libyal.nuspec':
        output_filename = f'{project_configuration.library_name:s}.nuspec'

        if not project_configuration.deploy_to_nuget:
          logging.warning(f'Skipping: {output_filename:s}')
          continue

      elif directory_entry == 'libyal.pc.in':
        output_filename = f'{project_configuration.library_name:s}.pc.in'

      else:
        output_filename = directory_entry

      self._GenerateSection(
          template_filename, template_mappings, output_filename)

    del template_mappings['pc_libs_private']

    self._GenerateCodecovYML(project_configuration, template_mappings)

    self._GenerateGitignore(project_configuration, template_mappings)

    operations_file_name = os.path.join('github_workflows', 'build.yml.yaml')
    output_filename = os.path.join('.github', 'workflows', 'build.yml')
    self._GenerateSectionsFromOperationsFile(
        operations_file_name, 'main', project_configuration, template_mappings,
        output_filename)

    operations_file_name = os.path.join(
        'github_workflows', 'build_freebsd.yml.yaml')
    output_filename = os.path.join('.github', 'workflows', 'build_freebsd.yml')
    self._GenerateSectionsFromOperationsFile(
        operations_file_name, 'main', project_configuration, template_mappings,
        output_filename)

    operations_file_name = os.path.join(
        'github_workflows', 'build_macos.yml.yaml')
    output_filename = os.path.join('.github', 'workflows', 'build_macos.yml')
    self._GenerateSectionsFromOperationsFile(
        operations_file_name, 'main', project_configuration, template_mappings,
        output_filename)

    operations_file_name = os.path.join(
        'github_workflows', 'build_shared.yml.yaml')
    output_filename = os.path.join('.github', 'workflows', 'build_shared.yml')
    self._GenerateSectionsFromOperationsFile(
        operations_file_name, 'main', project_configuration, template_mappings,
        output_filename)

    if project_configuration.HasPythonModule():
      operations_file_name = os.path.join(
          'github_workflows', 'build_wheel.yml.yaml')
      output_filename = os.path.join('.github', 'workflows', 'build_wheel.yml')
      self._GenerateSectionsFromOperationsFile(
          operations_file_name, 'main', project_configuration,
          template_mappings, output_filename)

    if os.path.isdir('ossfuzz'):
      operations_file_name = os.path.join(
          'github_workflows', 'build_ossfuzz.yml.yaml')
      output_filename = os.path.join(
          '.github', 'workflows', 'build_ossfuzz.yml')
      self._GenerateSectionsFromOperationsFile(
          operations_file_name, 'main', project_configuration,
          template_mappings, output_filename)

    self._GenerateAppVeyorYML(project_configuration, template_mappings)

    self._GenerateConfigureAC(project_configuration, template_mappings)

    self._GenerateACIncludeM4(project_configuration, template_mappings)

    self._GenerateDpkg(
        project_configuration, template_mappings, output_writer, 'dpkg')

    self._GenerateRpmSpec(project_configuration, template_mappings)

    if project_configuration.HasPythonModule():
      self._GenerateSectionsFromOperationsFile(
          'setup.cfg.in.yaml', 'main', project_configuration,
          template_mappings, 'setup.cfg.in')

      self._GenerateSectionsFromOperationsFile(
          'tox.ini.yaml', 'main', project_configuration, template_mappings,
          'tox.ini')
