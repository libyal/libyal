# -*- coding: utf-8 -*-
#
# Script to convert Visual Studio (express) solution and project files
# from one version to another.
#
# Currently supports converting:
# * 2008 (10.0) to 2010 (11.0)
#
# Copyright (c) 2013, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO: allow to generate from source tree, e.g. Makefile.am?
# TODO: add automated tests.
# TODO: complete vs2010 reader.
# TODO: complete vs2008 writer.

import abc
import argparse
import re
import os
import sys


class VSConfiguration(object):
  """Class to represent a Visual Studio configurations."""

  def __init__(self):
    """Initializes a Visual Studio configuration."""
    self.name = ''
    self.platform = ''

  @abc.abstractmethod
  def CopyToX64(self):
    """Copies the Visual Studio solution configuration to an x64 equivalent."""


class VSConfigurations(object):
  """Class to represent a Visual Studio solution and project configurations."""

  def __init__(self):
    """Initializes a Visual Studio configurations."""
    self._configurations = {}
    self.names = []
    self.platforms = []

  @property
  def number_of_configurations(self):
    return len(self._configurations.values())

  def Append(self, configuration):
    """Appends a configuration.

    Args:
      configuration: the configuration (instance of VSConfiguration).
    """
    if configuration.name not in self.names:
      self.names.append(configuration.name)

    if configuration.platform not in self.platforms:
      self.platforms.append(configuration.platform)

    identifier = '{0:s}|{1:s}'.format(
        configuration.name, configuration.platform)

    self._configurations[identifier] = configuration

  def ExtendWithX64(self):
    """Extends the configurations with the x64 platform."""
    if 'x64' not in self.platforms:
      for configuration in self._configurations.values():
        if configuration.platform != 'x64':
          self.Append(configuration.CopyToX64())

  def GetByIdentifier(self, name, platform):
    """Retrieves a specific configuration by identtifier.

    The identifier is formatted as: name|platform.

    Args:
      name: the configuration name.
      platform: the configuration platform.

    Returns:
      The configuration (instance of VSProjectConfiguration or
      VSProjectConfiguration).
    """
    identifier = '{0:s}|{1:s}'.format(name, platform)
    return self._configurations[identifier]

  def GetSorted(self, reverse=False):
    """Retrieves configurations in sorted order.

    The sorting order is first alphabetacally by name,
    secondly alphabetacally by platform.

    Args:
      reverse: optional boolean to indicate the name sort order should be
               reversed, which is False by default. The platform sort
               order does not change.

    Yields:
      The configuration (instance of VSConfiguration).
    """
    for name in sorted(self.names, reverse=reverse):
      for platform in sorted(self.platforms):
        yield self.GetByIdentifier(name, platform)


class VSProjectConfiguration(VSConfiguration):
  """Class to represent a Visual Studio project configuration."""

  def __init__(self):
    """Initializes a Visual Studio project configuration."""
    super(VSProjectConfiguration, self).__init__()

    # Note that name and platform are inherited from VSConfiguration.
    self.basic_runtime_checks = ''
    self.character_set = ''
    self.compile_as = ''
    self.data_execution_prevention = ''
    self.debug_information_format = ''
    self.dependencies = ''
    self.dependencies_set = False
    self.enable_comdat_folding = ''
    self.enable_function_level_linking = ''
    self.enable_intrinsic_functions = ''
    self.fixed_base_address = ''
    self.generate_debug_information = ''
    self.import_library = ''
    self.include_directories = ''
    self.librarian_ignore_defaults = ''
    self.librarian_output_file = ''
    self.library_directories = ''
    self.link_incremental = ''
    self.linker_output_directory = ''
    self.linker_output_file = ''
    self.linker_values_set = False
    self.managed_extensions = ''
    self.module_definition_file = ''
    self.name = ''
    self.optimize_references = ''
    self.optimization = ''
    self.output_type = ''
    self.platform = ''
    self.platform_toolset = ''
    self.precompiled_header = ''
    self.preprocessor_definitions = ''
    self.randomized_base_address = ''
    self.runtime_library = ''
    self.smaller_type_check = ''
    self.sub_system = ''
    self.target_machine = ''
    self.warning_as_error = ''
    self.warning_level = ''
    self.whole_program_optimization = ''

  @property
  def basic_runtime_checks_string(self):
    basic_runtime_checks = int(self.basic_runtime_checks, 10)
    if basic_runtime_checks == 0:
      return 'Default'
    elif basic_runtime_checks == 3:
      return 'EnableFastChecks'
    return ''

  @property
  def character_set_string(self):
    character_set = int(self.character_set, 10)
    if character_set == 1:
      return 'Unicode'
    return ''

  @property
  def compile_as_string(self):
    compile_as = int(self.compile_as, 10)
    if compile_as == 1:
      return 'CompileAsC'
    return ''

  @property
  def data_execution_prevention_string(self):
    data_execution_prevention = int(self.data_execution_prevention, 10)
    if data_execution_prevention == 2:
      return 'true'
    return ''

  @property
  def debug_information_format_string(self):
    debug_information_format = int(self.debug_information_format, 10)
    if debug_information_format == 3:
      return 'ProgramDatabase'
    return ''

  @property
  def enable_comdat_folding_string(self):
    enable_comdat_folding = int(self.enable_comdat_folding, 10)
    if enable_comdat_folding == 2:
      return 'true'
    return ''

  @property
  def link_incremental_string(self):
    link_incremental = int(self.link_incremental, 10)
    if link_incremental == 1:
      return 'false'
    return ''

  @property
  def optimize_references_string(self):
    optimize_references = int(self.optimize_references, 10)
    if optimize_references == 2:
      return 'true'
    return ''

  @property
  def optimization_string(self):
    optimization = int(self.optimization, 10)
    if optimization == 0:
      return 'Disabled'
    elif optimization == 2:
      return 'MaxSpeed'
    return ''

  @property
  def output_type_string(self):
    output_type = int(self.output_type, 10)
    if output_type == 1:
      return 'Application'
    elif output_type == 2:
      return 'DynamicLibrary'
    elif output_type == 4:
      return 'StaticLibrary'
    return ''

  @property
  def precompiled_header_string(self):
    precompiled_header = int(self.precompiled_header, 10)
    # TODO: do something with precompiled_header.
    return ''

  @property
  def randomized_base_address_string(self):
    randomized_base_address = int(self.randomized_base_address, 10)
    if randomized_base_address == 1:
      return 'false'
    elif randomized_base_address == 2:
      return 'true'
    return ''

  @property
  def runtime_librarian_string(self):
    runtime_library = int(self.runtime_library, 10)
    if runtime_library == 2:
      return 'MultiThreadedDLL'
    if runtime_library == 3:
      return 'MultiThreadedDebugDLL'
    return ''

  @property
  def sub_system_string(self):
    sub_system = int(self.sub_system, 10)
    if sub_system == 0:
      return 'NotSet'
    elif sub_system == 1:
      return 'Console'
    return ''

  @property
  def target_machine_string(self):
    target_machine = int(self.target_machine, 10)
    if target_machine == 1:
      return 'MachineX86'
    # TODO: assuming here that 2 is x64.
    elif target_machine == 2:
      return 'MachineX64'
    return ''

  @property
  def warning_level_string(self):
    warning_level = int(self.warning_level, 10)
    if warning_level == 3:
      return 'Level3'
    elif warning_level == 4:
      return 'Level4'
    return ''

  @property
  def whole_program_optimization_string(self):
    whole_program_optimization = int(self.whole_program_optimization, 10)
    if whole_program_optimization == 0:
      return 'false'
    elif whole_program_optimization == 1:
      return 'true'
    return ''

  def CopyToX64(self):
    """Copies the Visual Studio project configuration to an x64 equivalent."""
    copy = VSProjectConfiguration()

    copy.basic_runtime_checks = self.basic_runtime_checks
    copy.character_set = self.character_set
    copy.compile_as = self.compile_as
    copy.data_execution_prevention = self.data_execution_prevention
    copy.debug_information_format = self.debug_information_format
    copy.dependencies = self.dependencies
    copy.dependencies_set = self.dependencies_set
    copy.enable_comdat_folding = self.enable_comdat_folding
    copy.enable_function_level_linking = self.enable_function_level_linking
    copy.enable_intrinsic_functions = self.enable_intrinsic_functions
    copy.generate_debug_information = self.generate_debug_information
    copy.fixed_base_address = self.fixed_base_address
    copy.import_library = self.import_library
    copy.include_directories = self.include_directories
    copy.librarian_ignore_defaults = self.librarian_ignore_defaults
    copy.librarian_output_file = self.librarian_output_file
    copy.library_directories = self.library_directories
    copy.link_incremental = self.link_incremental
    copy.linker_output_directory = self.linker_output_directory
    copy.linker_output_file = self.linker_output_file
    copy.linker_values_set = self.linker_values_set
    copy.managed_extensions = self.managed_extensions
    copy.module_definition_file = self.module_definition_file
    copy.name = self.name
    copy.optimize_references = self.optimize_references
    copy.optimization = self.optimization
    copy.output_type = self.output_type
    copy.platform = 'x64'
    copy.platform_toolset = 'Windows7.1SDK'
    copy.precompiled_header = self.precompiled_header
    copy.preprocessor_definitions = self.preprocessor_definitions
    copy.randomized_base_address = self.randomized_base_address
    copy.runtime_library = self.runtime_library
    copy.smaller_type_check = self.smaller_type_check
    copy.sub_system = self.sub_system
    copy.target_machine = '2'
    copy.warning_as_error = self.warning_as_error
    copy.warning_level = self.warning_level
    copy.whole_program_optimization = self.whole_program_optimization

    return copy


class VSProjectInformation(object):
  """Class to represent a Visual Studio project information."""

  def __init__(self):
    """Initializes Visual Studio project information."""
    self.project_guid = ''
    self.root_name_space = ''
    self.keyword = ''


class VSSolutionConfiguration(VSConfiguration):
  """Class to represent a Visual Studio solution configuration."""

  def CopyToX64(self):
    """Copies the Visual Studio solution configuration to an x64 equivalent."""
    copy = VSSolutionConfiguration()

    copy.name = self.name
    copy.platform = 'x64'

    return copy


class VSSolutionProject(object):
  """Class to represent a Visual Studio solution project."""

  def __init__(self, name, filename, guid):
    """Initializes a Visual Studio project.

    Args:
      name: the project name.
      filename: the project filename without extension.
      guid: the project identifier (GUID).
    """
    self.name = name
    self.filename = filename
    self.guid = guid.lower()
    self.dependencies = []

  def AddDependency(self, dependency_guid):
    """Adds a dependency GUID to the project.

    Args:
      dependency_guid: the project GUID of the dependency.
    """
    self.dependencies.append(dependency_guid.lower())


class FileReader(object):
  """Class to represent a file reader."""

  def __init__(self):
    """Initializes a Visual Studio solution file reader."""
    self._line = None

  def Open(self, filename):
    """Opens the solution file.

    Args:
      filename: the filename of the solution file.
    """
    # For reading these files we don't care about the actual end of lines.
    self._file = open(filename, 'r')

  def Close(self):
    """Closes the solution file."""
    self._file.close()

  def _ReadLine(self, look_ahead=False):
    """Reads a line.

    Args:
      look_ahead: optional boolean value to indicate the line
                  should be considered read (False) or not (True).
                  The default is to consider the line read.

    Returns:
      The line stripped of leading and trailing white space
      or None if no input is available.
    """
    if self._line != None:
      line = self._line
      if not look_ahead:
        self._line = None

    else:
      line = self._file.readline()
      if line:
        line = line.strip()
      if look_ahead:
        self._line = line

    return line


class VSProjectFileReader(FileReader):
  """Class to represent a Visual Studio project file reader."""


class VS2008ProjectFileReader(VSProjectFileReader):
  """Class to represent a Visual Studio 2008 project file reader."""

  def ReadHeader(self):
    """Reads a file header.

    Returns:
      True if successful or false otherwise.
    """
    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith('<?xml version="1.0"'):
      return False

    # TODO check encoding?

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith('<VisualStudioProject'):
      return False

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith('ProjectType="Visual C++"'):
      return False

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith('Version="9,00"'):
      return False

    return True

  def ReadProjectInformation(self):
    """Reads project information.

    Returns:
      Project information (instance of VSProjectInformation) if successful
      or None otherwise.
    """
    project_information = VSProjectInformation()

    line = self._ReadLine()
    while line:
      if line.startswith('>'):
        break

      elif line.startswith('ProjectGUID='):
        values = re.findall('ProjectGUID="([^"]*)"', line)
        if len(values) == 1:
          project_information.project_guid = values[0]

      elif line.startswith('RootNamespace='):
        values = re.findall('RootNamespace="([^"]*)"', line)
        if len(values) == 1:
          project_information.root_name_space = values[0]

      elif line.startswith('Keyword='):
        values = re.findall('Keyword="([^"]*)"', line)
        if len(values) == 1:
          project_information.keyword = values[0]

      line = self._ReadLine()

    return project_information

  def ReadConfigurations(self):
    """Reads the configurations.

    Returns:
      The configurations (instance of VSConfigurations).
    """
    configurations = VSConfigurations()

    # Find the start of the configurations section.
    result = False
    line = self._ReadLine()

    while line:
      result = line.startswith('<Configurations>')
      if result:
        break
      line = self._ReadLine()

    if result:
      while line:
        line = self._ReadLine()

        if line.startswith('</Configurations>'):
          break

        elif line.startswith('<Configuration'):
          configuration = self._ReadConfiguration(line)

          if configuration:
            configurations.Append(configuration)

    return configurations

  def _ReadConfiguration(self, line):
    """Reads a configuration.

    Args:
      line: the line that contains the start of the configuration section.

    Returns:
      A configuration (instance of VSProjectConfiguration) or None if
      no configuration was found.
    """
    if not line.startswith('<Configuration'):
      return None

    configuration = VSProjectConfiguration()

    found_tool = False
    found_tool_compiler = False
    found_tool_librarian = False
    found_tool_linker = False

    while line:
      line = self._ReadLine()

      if line.startswith('</Configuration>'):
        break

      elif found_tool:
        if line.startswith('/>'):
          found_tool = False
          found_tool_compiler = False
          found_tool_librarian = False
          found_tool_linker = False

        elif found_tool_compiler:
          # Parse the compiler specific configuration.
          if line.startswith('Optimization='):
            values = re.findall('Optimization="([^"]*)"', line)
            if len(values) == 1:
              configuration.optimization = values[0]

          elif line.startswith('EnableIntrinsicFunctions='):
            values = re.findall(
                'EnableIntrinsicFunctions="([^"]*)"', line)
            if len(values) == 1:
              configuration.enable_intrinsic_functions = values[0]

          elif line.startswith('AdditionalIncludeDirectories='):
            values = re.findall(
                'AdditionalIncludeDirectories="([^"]*)"', line)
            if len(values) == 1:
              configuration.include_directories = values[0]

          elif line.startswith('PreprocessorDefinitions='):
            values = re.findall(
                'PreprocessorDefinitions="([^"]*)"', line)
            if len(values) == 1:
              configuration.preprocessor_definitions = values[0]

          elif line.startswith('BasicRuntimeChecks='):
            values = re.findall('BasicRuntimeChecks="([^"]*)"', line)
            if len(values) == 1:
              configuration.basic_runtime_checks = values[0]

          elif line.startswith('SmallerTypeCheck='):
            values = re.findall('SmallerTypeCheck="([^"]*)"', line)
            if len(values) == 1:
              configuration.smaller_type_check = values[0]

          elif line.startswith('RuntimeLibrary='):
            values = re.findall('RuntimeLibrary="([^"]*)"', line)
            if len(values) == 1:
              configuration.runtime_library = values[0]

          elif line.startswith('EnableFunctionLevelLinking='):
            values = re.findall('EnableFunctionLevelLinking="([^"]*)"', line)
            if len(values) == 1:
              configuration.enable_function_level_linking = values[0]

          elif line.startswith('UsePrecompiledHeader='):
            values = re.findall('UsePrecompiledHeader="([^"]*)"', line)
            if len(values) == 1:
              configuration.precompiled_header = values[0]

          elif line.startswith('WarningLevel='):
            values = re.findall('WarningLevel="([^"]*)"', line)
            if len(values) == 1:
              configuration.warning_level = values[0]

          elif line.startswith('WarnAsError='):
            values = re.findall('WarnAsError="([^"]*)"', line)
            if len(values) == 1:
              configuration.warning_as_error = values[0]

          elif line.startswith('DebugInformationFormat='):
            values = re.findall(
                'DebugInformationFormat="([^"]*)"', line)
            if len(values) == 1:
              configuration.debug_information_format = values[0]

          elif line.startswith('CompileAs='):
            values = re.findall('CompileAs="([^"]*)"', line)
            if len(values) == 1:
              configuration.compile_as = values[0]

        elif found_tool_librarian:
          # Parse the libararian specific configuration.
          if line.startswith('OutputFile='):
            values = re.findall('OutputFile="([^"]*)"', line)
            if len(values) == 1:
              configuration.librarian_output_file = values[0]

          elif line.startswith('IgnoreAllDefaultLibraries='):
            values = re.findall(
                'IgnoreAllDefaultLibraries="([^"]*)"', line)
            if len(values) == 1:
              configuration.librarian_ignore_defaults = values[0]

        elif found_tool_linker:
          # Parse the linker specific configuration.
          if line.startswith('OutputDirectory='):
            configuration.linker_values_set = True
            values = re.findall('OutputDirectory="([^"]*)"', line)
            if len(values) == 1:
              configuration.linker_output_directory = values[0]

          elif line.startswith('OutputFile='):
            configuration.linker_values_set = True
            values = re.findall('OutputFile="([^"]*)"', line)
            if len(values) == 1:
              configuration.linker_output_file = values[0]

          elif line.startswith('AdditionalDependencies='):
            configuration.linker_values_set = True
            values = re.findall(
                'AdditionalDependencies="([^"]*)"', line)
            if len(values) == 1:
              configuration.dependencies = values[0]
              configuration.dependencies_set = True

          elif line.startswith('LinkIncremental='):
            configuration.linker_values_set = True
            values = re.findall('LinkIncremental="([^"]*)"', line)
            if len(values) == 1:
              configuration.link_incremental = values[0]

          elif line.startswith('ModuleDefinitionFile='):
            configuration.linker_values_set = True
            values = re.findall('ModuleDefinitionFile="([^"]*)"', line)
            if len(values) == 1:
              configuration.module_definition_file = values[0]

          elif line.startswith('AdditionalLibraryDirectories='):
            configuration.linker_values_set = True
            values = re.findall(
                'AdditionalLibraryDirectories="([^"]*)"', line)
            if len(values) == 1:
              configuration.library_directories = values[0]

          elif line.startswith('GenerateDebugInformation='):
            configuration.linker_values_set = True
            values = re.findall(
                'GenerateDebugInformation="([^"]*)"', line)
            if len(values) == 1:
              configuration.generate_debug_information = values[0]

          elif line.startswith('SubSystem='):
            configuration.linker_values_set = True
            values = re.findall(
                'SubSystem="([^"]*)"', line)
            if len(values) == 1:
              configuration.sub_system = values[0]

          elif line.startswith('OptimizeReferences='):
            configuration.linker_values_set = True
            values = re.findall(
                'OptimizeReferences="([^"]*)"', line)
            if len(values) == 1:
              configuration.optimize_references = values[0]

          elif line.startswith('RandomizedBaseAddress='):
            configuration.linker_values_set = True
            values = re.findall(
                'RandomizedBaseAddress="([^"]*)"', line)
            if len(values) == 1:
              configuration.randomized_base_address = values[0]

          elif line.startswith('FixedBaseAddress='):
            configuration.linker_values_set = True
            values = re.findall(
                'FixedBaseAddress="([^"]*)"', line)
            if len(values) == 1:
              configuration.fixed_base_address = values[0]

          elif line.startswith('EnableCOMDATFolding='):
            configuration.linker_values_set = True
            values = re.findall(
                'EnableCOMDATFolding="([^"]*)"', line)
            if len(values) == 1:
              configuration.enable_comdat_folding = values[0]

          elif line.startswith('DataExecutionPrevention='):
            configuration.linker_values_set = True
            values = re.findall(
                'DataExecutionPrevention="([^"]*)"', line)
            if len(values) == 1:
              configuration.data_execution_prevention = values[0]

          elif line.startswith('ImportLibrary='):
            configuration.linker_values_set = True
            values = re.findall(
                'ImportLibrary="([^"]*)"', line)
            if len(values) == 1:
              configuration.import_library = values[0]

          elif line.startswith('TargetMachine='):
            configuration.linker_values_set = True
            values = re.findall('TargetMachine="([^"]*)"', line)
            if len(values) == 1:
              configuration.target_machine = values[0]

        elif line.startswith('Name="VCCLCompilerTool"'):
          found_tool_compiler = True

        elif line.startswith('Name="VCLibrarianTool"'):
          found_tool_librarian = True

        elif line.startswith('Name="VCLinkerTool"'):
          found_tool_linker = True

      elif line.startswith('<Tool'):
        found_tool = True

      elif line.startswith('Name='):
        # For more than 1 match findall will return a list with a tuple.
        values = re.findall('Name="([^|]*)[|]([^"]*)"', line)[0]
        if len(values) == 2:
          configuration.name = values[0]
          configuration.platform = values[1]

      elif line.startswith('ConfigurationType='):
        values = re.findall('ConfigurationType="([^"]*)"', line)
        if len(values) == 1:
          configuration.output_type = values[0]

      elif line.startswith('CharacterSet='):
        values = re.findall('CharacterSet="([^"]*)"', line)
        if len(values) == 1:
          configuration.character_set = values[0]

      elif line.startswith('ManagedExtensions='):
        values = re.findall('ManagedExtensions="([^"]*)"', line)
        if len(values) == 1:
          configuration.managed_extensions = values[0]

      elif line.startswith('WholeProgramOptimization='):
        values = re.findall('WholeProgramOptimization="([^"]*)"', line)
        if len(values) == 1:
          configuration.whole_program_optimization = values[0]

      # TODO: PlatformToolset.

    # Add the target machine when not defined.
    if not configuration.target_machine:
      if configuration.platform == 'Win32':
        configuration.target_machine = '1'
      # TODO: assuming here that 2 is x64.
      elif configuration.platform == 'x64':
        configuration.target_machine = '2'

    return configuration

  def ReadFiles(self):
    """Reads the files.

    Returns:
      A tuple of three list of strings. The first containing the source files,
      the second the header files and the third the resource files. The list is
      used to preserve the order of files.
    """
    source_files = []
    header_files = []
    resource_files = []

    # Find the start of the files section.
    result = False
    line = self._ReadLine()

    while line:
      result = line.startswith('<Files>')
      if result:
        break
      line = self._ReadLine()

    if result:
      found_filter = False
      found_filter_source_files = False
      found_filter_header_files = False
      found_filter_resource_files = False

      while line:
        line = self._ReadLine()

        if line.startswith('</Files>'):
          break

        elif found_filter:
          if line.startswith('</Filter>'):
            found_filter = False
            found_filter_source_files = False
            found_filter_header_files = False
            found_filter_resource_files = False

          elif found_filter_source_files:
            if line.startswith('RelativePath='):
              values = re.findall('RelativePath="([^"]*)"', line)

              if len(values) == 1:
                source_files.append(values[0])

          elif found_filter_header_files:
            if line.startswith('RelativePath='):
              values = re.findall('RelativePath="([^"]*)"', line)

              if len(values) == 1:
                header_files.append(values[0])

          elif found_filter_resource_files:
            if line.startswith('RelativePath='):
              values = re.findall('RelativePath="([^"]*)"', line)

              if len(values) == 1:
                resource_files.append(values[0])

          elif line.startswith('Name="Source Files"'):
            found_filter_source_files = True

          elif line.startswith('Name="Header Files"'):
            found_filter_header_files = True

          elif line.startswith('Name="Resource Files"'):

            found_filter_resource_files = True

        elif line.startswith('<Filter'):
          found_filter = True

    return source_files, header_files, resource_files


class VS2010ProjectFileReader(VSProjectFileReader):
  """Class to represent a Visual Studio 2010 project file reader."""


class VSProjectFileWriter(object):
  """Class to represent a Visual Studio project file writer."""

  def Open(self, filename):
    """Opens the project file.

    Args:
      filename: the filename of the project file.
    """
    # Using binary mode to make sure to write Windows/DOS end of lines.
    self._file = open(filename, 'wb')

  def Close(self):
    """Closes the project file."""
    self._file.close()

  def WriteLine(self, line):
    """Writes a line."""
    self._file.write('{0:s}\r\n'.format(line))

  def WriteLines(self, lines):
    """Writes lines."""
    for line in lines:
      self.WriteLine(line)

  @abc.abstractmethod
  def WriteHeader(self):
    """Writes a file header."""

  @abc.abstractmethod
  def WriteFooter(self):
    """Writes a file footer."""


class VS2008ProjectFileWriter(VSProjectFileWriter):
  """Class to represent a Visual Studio 2008 project file writer."""


class VS2010ProjectFileWriter(VSProjectFileWriter):
  """Class to represent a Visual Studio 2010 project file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self._file.write('\xef\xbb\xbf')
    self.WriteLines([
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Project DefaultTargets="Build" ToolsVersion="4.0" '
        'xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'])

  def WriteProjectConfigurations(self, configurations):
    """Writes the project configurations.

    Args:
      configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLine('  <ItemGroup Label="ProjectConfigurations">')

    for configuration in configurations.GetSorted():
      self.WriteLines([
          ('    <ProjectConfiguration Include="{0:s}|{1:s}">').format(
              configuration.name, configuration.platform),
          ('      <Configuration>{0:s}</Configuration>').format(
              configuration.name),
          '      <Platform>{0:s}</Platform>'.format(configuration.platform),
          '    </ProjectConfiguration>'])

    self.WriteLine('  </ItemGroup>')

  def WriteProjectInformation(self, project_information):
    """Writes the project information.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    self.WriteLine('  <PropertyGroup Label="Globals">')

    self.WriteLine('    <ProjectGuid>{0:s}</ProjectGuid>'.format(
        project_information.project_guid))

    self.WriteLine('    <RootNamespace>{0:s}</RootNamespace>'.format(
        project_information.root_name_space))

    if project_information.keyword:
      self.WriteLine('    <Keyword>{0:s}</Keyword>'.format(
          project_information.keyword))

    self.WriteLine('  </PropertyGroup>')


  def WriteConfigurations(self, configurations):
    """Writes the configurations.

    Args:
      configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLine(
        '  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />')

    # Mimic Visual Studio behavior and output the configurations
    # in reverse order of name.
    for configuration in configurations.GetSorted(reverse=True):
      self.WriteLine((
          '  <PropertyGroup Condition="\'$(Configuration)|$(Platform)\'=='
          '\'{0:s}|{1:s}\'" Label="Configuration">').format(
              configuration.name, configuration.platform))

      self.WriteLine('    <ConfigurationType>{0:s}</ConfigurationType>'.format(
          configuration.output_type_string))

      if configuration.character_set:
        self.WriteLine('    <CharacterSet>{0:s}</CharacterSet>'.format(
            configuration.character_set_string))

      if configuration.managed_extensions == '1':
        self.WriteLine('    <CLRSupport>true</CLRSupport>')

      if configuration.whole_program_optimization:
        self.WriteLine((
            '    <WholeProgramOptimization>{0:s}'
            '</WholeProgramOptimization>').format(
                configuration.whole_program_optimization_string))

      if configuration.platform_toolset:
        self.WriteLine('    <PlatformToolset>{0:s}</PlatformToolset>'.format(
            configuration.platform_toolset))

      self.WriteLine('  </PropertyGroup>')

    self.WriteLines([
        '  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />',
        '  <ImportGroup Label="ExtensionSettings">',
        '  </ImportGroup>'])

    # Mimic Visual Studio behavior and output the configurations
    # in reverse of name.
    for configuration in configurations.GetSorted(reverse=True):
      self.WriteLines([
          ('  <ImportGroup Condition="\'$(Configuration)|$(Platform)\'=='
           '\'{0:s}|{1:s}\'" Label="PropertySheets">'.format(
              configuration.name, configuration.platform)),
          ('    <Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform)'
           '.user.props" Condition="exists(\'$(UserRootDir)\\Microsoft.Cpp'
           '.$(Platform).user.props\')" Label="LocalAppDataPlatform" />'),
          '  </ImportGroup>'])

    self.WriteLines([
        '  <PropertyGroup Label="UserMacros" />',
        '  <PropertyGroup>',
        '    <_ProjectFileVersion>10.0.40219.1</_ProjectFileVersion>'])

    # Mimic Visual Studio behavior and output the configurations
    # in platforms by name.
    for configuration_name in sorted(configurations.names):
      for configuration_platform in sorted(configurations.platforms):
        configuration = configurations.GetByIdentifier(
            configuration_name, configuration_platform)

        self.WriteLine((
            '    <OutDir Condition="\'$(Configuration)|$(Platform)\'=='
            '\'{0:s}|{1:s}\'">$(SolutionDir)$(Configuration)\\'
            '</OutDir>').format(
                configuration.name, configuration.platform))

      for configuration_platform in sorted(configurations.platforms):
        configuration = configurations.GetByIdentifier(
            configuration_name, configuration_platform)

        self.WriteLine((
            '    <IntDir Condition="\'$(Configuration)|$(Platform)\'=='
            '\'{0:s}|{1:s}\'">$(Configuration)\\</IntDir>').format(
                configuration.name, configuration.platform))

      for configuration_platform in sorted(configurations.platforms):
        configuration = configurations.GetByIdentifier(
            configuration_name, configuration_platform)

        if configuration.link_incremental != '':
          self.WriteLine((
              '    <LinkIncremental Condition="\'$(Configuration)|'
              '$(Platform)\'==\'{0:s}|{1:s}\'">{2:s}</LinkIncremental>').format(
                  configuration.name, configuration.platform,
                  configuration.link_incremental_string))

    self.WriteLine('  </PropertyGroup>')

    for configuration in configurations.GetSorted():
      self.WriteLine((
          '  <ItemDefinitionGroup Condition="\'$(Configuration)|'
          '$(Platform)\'==\'{0:s}|{1:s}\'">').format(
              configuration.name, configuration.platform))

      include_directories = re.sub(
          r'&quot;', r'', configuration.include_directories)

      if include_directories and include_directories[-1] != ';':
        include_directories = '{0:s};'.format(
            include_directories)
  
      include_directories = (
          '{0:s}%(AdditionalIncludeDirectories)').format(
          include_directories)
  
      preprocessor_definitions = configuration.preprocessor_definitions

      if preprocessor_definitions and preprocessor_definitions[-1] != ';':
        preprocessor_definitions = '{0:s};'.format(preprocessor_definitions)
  
      preprocessor_definitions = (
          '{0:s}%(PreprocessorDefinitions)').format(
          preprocessor_definitions)
  
      # Write the compiler specific section.
      self.WriteLine('    <ClCompile>')

      if configuration.optimization != '':
        self.WriteLine('      <Optimization>{0:s}</Optimization>'.format(
            configuration.optimization_string))

      if configuration.enable_intrinsic_functions != '':
        self.WriteLine((
            '      <IntrinsicFunctions>{0:s}</IntrinsicFunctions>').format(
                configuration.enable_intrinsic_functions))

      if configuration.whole_program_optimization:
        self.WriteLine((
            '    <WholeProgramOptimization>{0:s}'
            '</WholeProgramOptimization>').format(
                configuration.whole_program_optimization_string))

      self.WriteLine((
          '      <AdditionalIncludeDirectories>{0:s}'
          '</AdditionalIncludeDirectories>').format(include_directories))

      self.WriteLine((
          '      <PreprocessorDefinitions>{0:s}'
          '</PreprocessorDefinitions>').format(preprocessor_definitions))

      if configuration.basic_runtime_checks != '':
        self.WriteLine((
            '      <BasicRuntimeChecks>{0:s}'
            '</BasicRuntimeChecks>').format(
                configuration.basic_runtime_checks_string))

      if configuration.smaller_type_check != '':
        self.WriteLine((
            '      <SmallerTypeCheck>{0:s}</SmallerTypeCheck>').format(
                configuration.smaller_type_check))

      self.WriteLine((
          '      <RuntimeLibrary>{0:s}</RuntimeLibrary>').format(
              configuration.runtime_librarian_string))

      if configuration.enable_function_level_linking != '':
        self.WriteLine((
            '      <FunctionLevelLinking>{0:s}</FunctionLevelLinking>').format(
                configuration.enable_function_level_linking))

      if configuration.precompiled_header != '':
        # A value of 0 is represented by a new line.
        if configuration.precompiled_header == '0':
          self.WriteLines([
              '      <PrecompiledHeader>',
              '      </PrecompiledHeader>'])
        else:
          self.WriteLine((
              '      <PrecompiledHeader>{0:s}</PrecompiledHeader>').format(
                  configuration.precompiled_header_string))

      self.WriteLine('      <WarningLevel>{0:s}</WarningLevel>'.format(
          configuration.warning_level_string))

      if configuration.warning_as_error:
        self.WriteLine((
            '      <TreatWarningAsError>{0:s}'
            '</TreatWarningAsError>').format(configuration.warning_as_error))

      if configuration.debug_information_format != '':
        # A value of 0 is represented by a new line.
        if configuration.debug_information_format == '0':
          self.WriteLines([
              '      <DebugInformationFormat>',
              '      </DebugInformationFormat>'])
        else:
          self.WriteLine((
              '      <DebugInformationFormat>{0:s}'
              '</DebugInformationFormat>').format(
                  configuration.debug_information_format_string))

      if configuration.compile_as:
        self.WriteLine('      <CompileAs>{0:s}</CompileAs>'.format(
            configuration.compile_as_string))

      self.WriteLine('    </ClCompile>')

      # Write the librarian specific section.
      if configuration.librarian_output_file:
        librarian_output_file = re.sub(
            r'[$][(]OutDir[)]\\', r'$(OutDir)',
            configuration.librarian_output_file)
  
        self.WriteLine('    <Lib>')

        self.WriteLine('      <OutputFile>{0:s}</OutputFile>'.format(
            librarian_output_file))

        if configuration.module_definition_file != '':
          self.WriteLine((
               '      <ModuleDefinitionFile>{0:s}'
               '</ModuleDefinitionFile>').format(
                   configuration.module_definition_file))
        else:
          self.WriteLines([
               '      <ModuleDefinitionFile>',
               '      </ModuleDefinitionFile>'])

        if configuration.librarian_ignore_defaults != '':
          self.WriteLine((
               '      <IgnoreAllDefaultLibraries>{0:s}'
               '</IgnoreAllDefaultLibraries>').format(
                   configuration.librarian_ignore_defaults))

        self.WriteLine('    </Lib>')
  
      # Write the linker specific section.
      if configuration.linker_values_set:
        self.WriteLine('    <Link>')

        # Visual Studio will convert an empty additional dependencies value.
        if configuration.dependencies_set:
          dependencies = re.sub(
              r'[.]lib ', r'.lib;', configuration.dependencies)
          dependencies = re.sub(
              r'[$][(]OutDir[)]\\', r'$(OutDir)', dependencies)

          if dependencies and dependencies[-1] != ';':
            dependencies = '{0:s};'.format(dependencies)

          dependencies = (
              '{0:s}%(AdditionalDependencies)').format(
              dependencies)
  
          self.WriteLine((
              '      <AdditionalDependencies>{0:s}'
              '</AdditionalDependencies>').format(
                  dependencies))

        if configuration.linker_output_file:
          linker_output_file = re.sub(
              r'[$][(]OutDir[)]\\', r'$(OutDir)',
              configuration.linker_output_file)
  
          self.WriteLine('      <OutputFile>{0:s}</OutputFile>'.format(
              linker_output_file))

          if configuration.module_definition_file != '':
            self.WriteLine((
                 '      <ModuleDefinitionFile>{0:s}'
                 '</ModuleDefinitionFile>').format(
                     configuration.module_definition_file))

        if configuration.library_directories:
          library_directories = re.sub(
              r'[$][(]OutDir[)]\\', r'$(OutDir)',
              configuration.library_directories)
          library_directories = re.sub(
              r'&quot;', r'', library_directories)

          if library_directories and library_directories[-1] != ';':
            library_directories = '{0:s};'.format(library_directories)

          library_directories = (
              '{0:s}%(AdditionalLibraryDirectories)').format(
              library_directories)
  
          self.WriteLine((
              '      <AdditionalLibraryDirectories>{0:s}'
              '</AdditionalLibraryDirectories>').format(
                  library_directories))

        if configuration.generate_debug_information != '':
          self.WriteLine((
              '      <GenerateDebugInformation>{0:s}'
              '</GenerateDebugInformation>').format(
                  configuration.generate_debug_information))

        if configuration.sub_system != '':
          self.WriteLine('      <SubSystem>{0:s}</SubSystem>'.format(
              configuration.sub_system_string))

        if configuration.optimize_references == '0':
          self.WriteLines([
              '      <OptimizeReferences>',
              '      </OptimizeReferences>'])

        elif configuration.optimize_references != '':
          self.WriteLine((
              '      <OptimizeReferences>{0:s}</OptimizeReferences>').format(
                  configuration.optimize_references_string))

        if configuration.enable_comdat_folding == '0':
          self.WriteLines([
              '      <EnableCOMDATFolding>',
              '      </EnableCOMDATFolding>'])

        elif configuration.enable_comdat_folding != '':
          self.WriteLine((
              '      <EnableCOMDATFolding>{0:s}</EnableCOMDATFolding>').format(
                  configuration.enable_comdat_folding_string))

        if configuration.randomized_base_address != '':
          self.WriteLine((
              '      <RandomizedBaseAddress>{0:s}'
              '</RandomizedBaseAddress>').format(
                  configuration.randomized_base_address_string))

        if configuration.fixed_base_address == '0':
          self.WriteLines([
              '      <FixedBaseAddress>',
              '      </FixedBaseAddress>'])

        if configuration.data_execution_prevention != '':
          # A value of 0 is represented by a new line.
          if configuration.data_execution_prevention == '0':
            self.WriteLines([
                '      <DataExecutionPrevention>',
                '      </DataExecutionPrevention>'])
          else:
            self.WriteLine((
                '      <DataExecutionPrevention>{0:s}'
                '</DataExecutionPrevention>').format(
                    configuration.data_execution_prevention_string))

        if configuration.import_library:
          import_library = re.sub(
              r'[$][(]OutDir[)]\\', r'$(OutDir)',
              configuration.import_library)

          self.WriteLine('      <ImportLibrary>{0:s}</ImportLibrary>'.format(
              import_library))

        if configuration.target_machine != '':
          self.WriteLine('      <TargetMachine>{0:s}</TargetMachine>'.format(
              configuration.target_machine_string))

        self.WriteLine('    </Link>')

      self.WriteLine('  </ItemDefinitionGroup>')

  def _WriteSourceFiles(self, source_files):
    """Writes the source files.

    Args:
      source_files: a list of strings of the source filenames.
    """
    if len(source_files) > 0:
      self.WriteLine('  <ItemGroup>')

      for filename in source_files:
        self.WriteLine('    <ClCompile Include="{0:s}" />'.format(filename))

      self.WriteLine('  </ItemGroup>')

  def _WriteHeaderFiles(self, header_files):
    """Writes the header files.

    Args:
      header_files: a list of strings of the header filenames.
    """
    if len(header_files) > 0:
      self.WriteLine('  <ItemGroup>')

      for filename in header_files:
        self.WriteLine('    <ClInclude Include="{0:s}" />'.format(filename))

      self.WriteLine('  </ItemGroup>')

  def _WriteResourceFiles(self, resource_files):
    """Writes the resource files.

    Args:
      resource_files: a list of strings of the resource filenames.
    """
    if len(resource_files) > 0:
      self.WriteLine('  <ItemGroup>')

      for filename in resource_files:
        self.WriteLine('    <ResourceCompile Include="{0:s}" />'.format(
            filename))

      self.WriteLine('  </ItemGroup>')

  def WriteFiles(self, source_files, header_files, resource_files):
    """Writes the files.

    Args:
      source_files: a list of strings of the source filenames.
      header_files: a list of strings of the header filenames.
      resource_files: a list of strings of the resource filenames.
    """
    self._WriteSourceFiles(source_files)
    self._WriteHeaderFiles(header_files)
    self._WriteResourceFiles(resource_files)

  def WriteDependencies(self, dependencies, projects_by_guid):
    """Writes the dependencies.

    Args:
      dependencies: a list of the GUID of the dependencies.
      projects_by_guid: a dictionary of the projects with their GUID
                        in lower case as the key.
    """
    if len(dependencies) > 0:
      self.WriteLine('  <ItemGroup>')

      dependencies_by_name = {}

      # Mimic Visual Studio behavior and ouput the depencies in order
      # of name (perhaps filename?).
      for dependency_guid in dependencies:
        dependency_project = projects_by_guid[dependency_guid]

        dependencies_by_name[dependency_project.name] = dependency_project

      for dependency_name in sorted(dependencies_by_name.keys()):
        dependency_project = dependencies_by_name[dependency_name]

        dependency_filename = '..\\{0:s}.vcxproj'.format(
            dependency_project.filename)

        dependency_guid = dependency_project.guid.lower()

        self.WriteLines([
            ('    <ProjectReference Include="{0:s}">').format(
                dependency_filename),
            '      <Project>{0:s}</Project>'.format(dependency_guid),
            '      <ReferenceOutputAssembly>false</ReferenceOutputAssembly>',
            '    </ProjectReference>'])

      self.WriteLine('  </ItemGroup>')

  def WriteFooter(self):
    """Writes a file footer."""
    self.WriteLines([
        '  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />',
        '  <ImportGroup Label="ExtensionTargets">',
        '  </ImportGroup>'])

    # The last line has no \r\n.
    self._file.write('</Project>')


class VSSolutionFileReader(FileReader):
  """Class to represent a Visual Studio solution file reader."""

  @abc.abstractmethod
  def _CheckFormatVersion(self, line):
    """Checks the format version.

    Args:
      line: the line containing the Visual Studio format version.

    Returns:
      True if successful or false otherwise.
    """

  def ReadHeader(self):
    """Reads a file header.

    Returns:
      True if successful or false otherwise.
    """
    line = self._ReadLine()

    if not line:
      return False

    if line != '\xef\xbb\xbf':
      return False

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith(
        'Microsoft Visual Studio Solution File, Format Version '):
      return False

    if not self._CheckFormatVersion(line):
      return False

    line = self._ReadLine(look_ahead=True)

    if line and line.startswith('# Visual C++ '):
      line = self._ReadLine()

    return True

  def ReadProject(self):
    """Reads a project.

    Returns:
      A project (instance of VSSolutionProject) if successful or None otherwise.
    """
    line = self._ReadLine(look_ahead=True)

    if not line:
      return None

    # 8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942 is a Visual C++ related GUID.
    if not line.startswith(
        'Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = '):
      return None

    # For more than 1 match findall will return a list with a tuple.
    values = re.findall(
        ('Project\\("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}"\\) = "([^"]*)", '
         '"([^"]*)\\.vcproj", '
         '"({[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*})"'),
        line)[0]

    if len(values) != 3:
      return None

    project = VSSolutionProject(values[0], values[1], values[2])

    found_dependencies = False

    line = self._ReadLine()

    while line and line != 'EndProject':
      line = self._ReadLine()

      if found_dependencies:
        if line == 'EndProjectSection':
          found_dependencies = False

        else:
          # The dependencies are defined as: {%GUID%} = {%GUID%}
          # For more than 1 match findall will return a list with a tuple.
          guids = re.findall(
              ('({[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*}) = '
               '({[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*})'),
              line)[0]

          if len(guids) == 2 and guids[0] == guids[1]:
            project.AddDependency(guids[0])

      elif line == 'ProjectSection(ProjectDependencies) = postProject':
        found_dependencies = True

    return project

  def ReadProjects(self):
    """Reads the projects.

    Returns:
      A list containing the projects (instances of VSSolutionProject).
      The list is used to preserve the order of projects.
    """
    projects = []
    project = self.ReadProject()

    while project:
      projects.append(project)
      project = self.ReadProject()

    return projects

  def ReadConfigurations(self):
    """Reads the configurations.

    Returns:
      The configurations (instance of VSConfigurations).
    """
    configurations = VSConfigurations()

    line = self._ReadLine(look_ahead=True)

    if not line:
      return None

    if line != 'Global':
      return None

    found_section = False

    line = self._ReadLine()

    while line and line != 'EndGlobal':
      line = self._ReadLine()

      if found_section:
        if line == 'EndGlobalSection':
          found_section = False

        else:
          # For more than 1 match findall will return a list with a tuple.
          values = re.findall('([^|]*)[|]([^ ]*) = ([^|]*)[|]([^ ]*)', line)[0]

          if (len(values) == 4 and values[0] == values[2] and
              values[1] == values[3]):
            configuration = VSSolutionConfiguration()
            configuration.name = values[0]
            configuration.platform = values[1]

            configurations.Append(configuration)

      elif line == ('GlobalSection(SolutionConfigurationPlatforms) = '
                    'preSolution'):
        found_section = True

    return configurations


class VS2008SolutionFileReader(VSSolutionFileReader):
  """Class to represent a Visual Studio 2008 solution file reader."""

  def _CheckFormatVersion(self, line):
    """Checks the format version.

    Args:
      line: the line containing the Visual Studio format version.

    Returns:
      True if successful or false otherwise.
    """
    return line.endswith(' 10.00')


class VS2010SolutionFileReader(object):
  """Class to represent a Visual Studio 2010 solution file reader."""

  def _CheckFormatVersion(self, line):
    """Checks the format version.

    Args:
      line: the line containing the Visual Studio format version.

    Returns:
      True if successful or false otherwise.
    """
    return line.endswith(' 11.00')


class VSSolutionFileWriter(object):
  """Class to represent a Visual Studio solution file writer."""

  def Open(self, filename):
    """Opens the solution file.

    Args:
      filename: the filename of the solution file.
    """
    # Using binary mode to make sure to write Windows/DOS end of lines.
    self._file = open(filename, 'wb')

  def Close(self):
    """Closes the solution file."""
    self._file.close()

  @abc.abstractmethod
  def WriteHeader(self):
    """Writes a file header."""

  @abc.abstractmethod
  def WriteProject(self, project):
    """Writes a project section.

    Args:
      project: the project (instance of VSSolutionProject).
    """

  def WriteLine(self, line):
    """Writes a line."""
    self._file.write('{0:s}\r\n'.format(line))

  def WriteLines(self, lines):
    """Writes lines."""
    for line in lines:
      self.WriteLine(line)

  def WriteProjects(self, projects):
    """Writes the projects.

    Args:
      projects: a list containing the projects (instances of VSSolutionProject).
    """
    for project in projects:
      self.WriteProject(project)


class VS2008SolutionFileWriter(VSSolutionFileWriter):
  """Class to represent a Visual Studio 2008 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 10.00',
        '# Visual C++ Express 2008'])

  def WriteProject(self, project):
    """Writes a project section.

    Args:
      project: the project (instance of VSSolutionProject).
    """
    project_filename = '{0:s}.vcproj'.format(project.filename)

    self.WriteLine((
        'Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{0:s}", '
        '"{1:s}", "{2:s}"').format(
            project.name, project_filename, project.guid.upper()))

    if len(project.dependencies) > 0:
      self.WriteLine(
          '        ProjectSection(ProjectDependencies) = postProject')

      for dependency_guid in project.dependencies:
        self.WriteLine('                {0:s} = {0:s}'.format(
            dependency_guid.upper()))

      self.WriteLine('        EndProjectSection')

    self.WriteLine('EndProject')

  def WriteConfigurations(self, configurations, projects):
    """Writes the configurations.

    Args:
      configurations: the configurations (instance of VSConfigurations).
      projects: a list containing the projects (instances of VSSolutionProject).
    """
    self.WriteLine('Global')

    if configurations.number_of_configurations > 0:
      self.WriteLine(
          '        GlobalSection(SolutionConfigurationPlatforms) = preSolution')

      for configuration_platform in sorted(configurations.platforms):
        for configuration_name in sorted(configurations.names):
          configuration = configurations.GetByIdentifier(
              configuration_name, configuration_platform)

          self.WriteLine('                {0:s}|{1:s} = {0:s}|{1:s}'.format(
              configuration.name, configuration.platform))

      self.WriteLine('        EndGlobalSection')

    if configurations.number_of_configurations > 0:
      self.WriteLine(
          '        GlobalSection(ProjectConfigurationPlatforms) = postSolution')

      for configuration_platform in sorted(configurations.platforms):
        for project in projects:
          for configuration_name in sorted(configurations.names):
            configuration = configurations.GetByIdentifier(
                configuration_name, configuration_platform)

            self.WriteLine((
                '                {0:s}.{1:s}|{2:s}.ActiveCfg = '
                '{1:s}|{2:s}').format(
                    project.guid.upper(), configuration.name,
                    configuration.platform))
            self.WriteLine((
                '                {0:s}.{1:s}|{2:s}.Build = {1:s}|{2:s}').format(
                    project.guid.upper(), configuration.name,
                    configuration.platform))

      self.WriteLine('        EndGlobalSection')

    self.WriteLines([
        '        GlobalSection(SolutionProperties) = preSolution',
        '                HideSolutionNode = FALSE',
        '        EndGlobalSection',
        'EndGlobal'])


class VS2010SolutionFileWriter(VSSolutionFileWriter):
  """Class to represent a Visual Studio 2010 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 11.00',
        '# Visual C++ Express 2010'])

  def WriteProject(self, project):
    """Writes a project section.

    Args:
      project: the project (instance of VSSolutionProject).
    """
    project_filename = '{0:s}.vcxproj'.format(project.filename)

    self.WriteLine((
        'Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{0:s}", '
        '"{1:s}", "{2:s}"').format(
            project.name, project_filename, project.guid.upper()))

    self.WriteLine('EndProject')

  def WriteConfigurations(self, configurations, projects):
    """Writes the configurations.

    Args:
      configurations: a list containing the solution configurations (instances
                      of VSSolutionConfiguration).
      projects: a list containing the projects (instances of VSSolutionProject).
    """
    self.WriteLine('Global')

    if configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution')

      for configuration_platform in sorted(configurations.platforms):
        for configuration_name in sorted(configurations.names):
          configuration = configurations.GetByIdentifier(
              configuration_name, configuration_platform)

          self.WriteLine('\t\t{0:s}|{1:s} = {0:s}|{1:s}'.format(
              configuration.name, configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    if configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution')

      for configuration_platform in sorted(configurations.platforms):
        for project in projects:
          for configuration_name in sorted(configurations.names):
            configuration = configurations.GetByIdentifier(
                configuration_name, configuration_platform)

            self.WriteLine((
                '\t\t{0:s}.{1:s}|{2:s}.ActiveCfg = {1:s}|{2:s}').format(
                    project.guid.upper(), configuration.name,
                    configuration.platform))
            self.WriteLine((
                '\t\t{0:s}.{1:s}|{2:s}.Build.0 = {1:s}|{2:s}').format(
                    project.guid.upper(), configuration.name,
                    configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    self.WriteLines([
        '\tGlobalSection(SolutionProperties) = preSolution',
        '\t\tHideSolutionNode = FALSE',
        '\tEndGlobalSection',
        'EndGlobal'])


class VSSolution(object):
  """Class to represent a Visual Studio solution."""

  def _ConvertProject(self, input_version, input_directory, output_version,
                      output_directory, project, projects_by_guid):
    """Converts a Visual Studio project.

    Args:
      input_version: the input version of the Visual Studio.
      input_directory: the path of the input directory.
      output_version: the output version of the Visual Studio.
      output_directory: the path of the output directory.
      project: the project.
      projects_by_guid: a dictionary of the projects with their GUID
                        in lower case as the key.

    Returns:
      True if the conversion successful or False if not.
    """
    if not project:
      return False

    input_project_filename = input_directory
    output_project_filename = output_directory
    for path_segment in project.filename.split('\\'):
      input_project_filename = os.path.join(
          input_project_filename, path_segment)
      output_project_filename = os.path.join(
          output_project_filename, path_segment)

    # TODO: move logic into the reader?
    if input_version == '2008':
      input_project_filename = '{0:s}.vcproj'.format(input_project_filename)
    elif input_version == '2010':
      input_project_filename = '{0:s}.vcxproj'.format(input_project_filename)

    # TODO: move logic into the writer?
    if output_version == '2008':
      output_project_filename = '{0:s}.vcproj'.format(output_project_filename)
    elif output_version == '2010':
      output_project_filename = '{0:s}.vcxproj'.format(output_project_filename)

    if not os.path.exists(input_project_filename):
      return False

    print 'Reading: {0:s}'.format(input_project_filename)

    if input_version == '2008':
      project_reader = VS2008ProjectFileReader()
    elif input_version == '2010':
      project_reader = VS2010ProjectFileReader()

    project_reader.Open(input_project_filename)

    if not project_reader.ReadHeader():
      return False

    project_information = project_reader.ReadProjectInformation()
    configurations = project_reader.ReadConfigurations()
    source_files, header_files, resource_files = project_reader.ReadFiles()
    project_reader.Close()

    # Add x64 as a platform.
    configurations.ExtendWithX64()

    # Create the output directory.
    output_directory = os.path.dirname(output_project_filename)

    os.mkdir(output_directory)

    if output_version == '2008':
      project_writer = VS2008ProjectFileWriter()
    elif output_version == '2010':
      project_writer = VS2010ProjectFileWriter()

    print 'Writing: {0:s}'.format(output_project_filename)

    project_writer.Open(output_project_filename)
    project_writer.WriteHeader()
    project_writer.WriteProjectConfigurations(configurations)
    project_writer.WriteProjectInformation(project_information)
    project_writer.WriteConfigurations(configurations)
    project_writer.WriteFiles(source_files, header_files, resource_files)
    project_writer.WriteDependencies(project.dependencies, projects_by_guid)
    project_writer.WriteFooter()
    project_writer.Close()

    return True

  def Convert(self, input_sln_filename, output_version):
    """Convert a Visual Studio solution.

    Args:
      input_sln_filename: the name of the Visual Studio solution file.
      output_version: the output version of the Visual Studio.

    Returns:
      True if the conversion successful or False if not.
    """
    output_directory = 'vs{0:s}'.format(output_version)

    if not os.path.exists(input_sln_filename):
      return False

    print 'Reading: {0:s}'.format(input_sln_filename)

    # TODO: detect input version based on solution file reader?
    input_version = '2008'

    if input_version == '2008':
      solution_reader = VS2008SolutionFileReader()
    elif input_version == '2010':
      solution_reader = VS2010SolutionFileReader()

    solution_reader.Open(input_sln_filename)

    if not solution_reader.ReadHeader():
      return False

    projects = solution_reader.ReadProjects()
    configurations = solution_reader.ReadConfigurations()
    solution_reader.Close()

    # Add x64 as a platform.
    configurations.ExtendWithX64()

    # Create the output directory.
    os.mkdir(output_directory)

    output_sln_filename = os.path.join(
        output_directory, os.path.basename(input_sln_filename))

    print 'Writing: {0:s}'.format(output_sln_filename)

    if output_version == '2008':
      solution_writer = VS2008SolutionFileWriter()
    elif output_version == '2010':
      solution_writer = VS2010SolutionFileWriter()

    solution_writer.Open(output_sln_filename)
    solution_writer.WriteHeader()
    solution_writer.WriteProjects(projects)
    solution_writer.WriteConfigurations(configurations, projects)
    solution_writer.Close()

    result = True
    input_directory = os.path.dirname(input_sln_filename)

    projects_by_guid = {}
    for project in projects:
      projects_by_guid[project.guid] = project

    for project in projects:
      result = self._ConvertProject(
          input_version, input_directory, output_version, output_directory,
          project, projects_by_guid)
      if not result:
        break

    return result


def Main():
  args_parser = argparse.ArgumentParser(description=(
      'Converts Visual Studio express solution and project files '
      'from one version to another.'))

  args_parser.add_argument(
      'solution_file', nargs='?', action='store', metavar='SOLUTION_FILE',
      default=None, help='The solution file (.sln).')

  args_parser.add_argument(
      '--to', dest='output_format', nargs='?', action='store', metavar='FORMAT',
      default='2010', help='The format to convert to.')

  options = args_parser.parse_args()

  if not options.solution_file:
    print 'Solution file missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  if options.output_format != '2010':
    print 'Unsupported output format: {0:s}.'.format(options.format_to)
    print ''
    return False

  input_solution = VSSolution()

  if not input_solution.Convert(options.solution_file, options.output_format):
    print 'Unable to convert Visual Studio solution file.'
    return False

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
