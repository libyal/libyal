#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate different versions of Visual Studio (express) files.

Currently supported input formats:
* libyal source directory (configure.ac and Makefile.am)
* 2008 (10.0)

Currently supported output formats:
* 2008 (10.0)
* 2010 (11.0)
* 2012 (12.0)
* 2013 (13.0)
"""

# TODO: add automated tests.
# TODO: add vs2010 reader.
# TODO: add vs2012 reader.
# TODO: add vs2013 reader.
# TODO: add vs2013 writer.

from __future__ import print_function
import abc
import argparse
import logging
import re
import os
import sys
import uuid


class VSConfiguration(object):
  """Class to represent a Visual Studio configurations."""

  def __init__(self, name=u'', platform=u''):
    """Initializes a Visual Studio configuration.

    Args:
      name: optional string containing the name. The default is an empty
            string.
      platform: optional string containing the name. The default is an empty
               string.
    """
    self.name = name
    self.platform = platform

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

    identifier = u'{0:s}|{1:s}'.format(
        configuration.name, configuration.platform)

    self._configurations[identifier] = configuration

  def ExtendWithX64(self, unused_output_version):
    """Extends the configurations with the x64 platform.

    Args:
      output_version: the output Visual Studio version.
    """
    if u'x64' not in self.platforms:
      for configuration in self._configurations.values():
        if configuration.platform != u'x64':
          x64_configuration = configuration.CopyToX64()

          self.Append(x64_configuration)

  def GetByIdentifier(self, name, platform):
    """Retrieves a specific configuration by identtifier.

    The identifier is formatted as: name|platform.

    Args:
      name: the configuration name.
      platform: the configuration platform.

    Returns:
      The configuration (instance of VSConfiguration).
    """
    identifier = u'{0:s}|{1:s}'.format(name, platform)
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
    self.additional_dependencies = []
    self.basic_runtime_checks = u''
    self.character_set = u''
    self.compile_as = u''
    self.data_execution_prevention = u''
    self.debug_information_format = u''
    self.detect_64bit_portability_problems = u''
    self.enable_comdat_folding = u''
    self.enable_function_level_linking = u''
    self.enable_intrinsic_functions = u''
    self.fixed_base_address = u''
    self.generate_debug_information = u''
    self.import_library = u''
    self.include_directories = u''
    self.librarian_ignore_defaults = u''
    self.librarian_output_file = u''
    self.library_directories = u''
    self.link_incremental = u''
    self.linker_output_directory = u''
    self.linker_output_file = u''
    self.linker_values_set = False
    self.managed_extensions = u''
    self.module_definition_file = u''
    self.name = u''
    self.optimize_references = u''
    self.optimization = u''
    self.output_type = u''
    self.platform = u''
    self.platform_toolset = u''
    self.precompiled_header = u''
    self.preprocessor_definitions = u''
    self.randomized_base_address = u''
    self.runtime_library = u''
    self.smaller_type_check = u''
    self.sub_system = u''
    self.target_machine = u''
    self.warning_as_error = u''
    self.warning_level = u''
    self.whole_program_optimization = u''

  @property
  def basic_runtime_checks_string(self):
    basic_runtime_checks = int(self.basic_runtime_checks, 10)
    if basic_runtime_checks == 0:
      return u'Default'
    elif basic_runtime_checks == 3:
      return u'EnableFastChecks'
    return u''

  @property
  def character_set_string(self):
    character_set = int(self.character_set, 10)
    if character_set == 1:
      return u'Unicode'
    return u''

  @property
  def compile_as_string(self):
    compile_as = int(self.compile_as, 10)
    if compile_as == 1:
      return u'CompileAsC'
    elif compile_as == 2:
      return u'CompileAsCpp'
    return u''

  @property
  def data_execution_prevention_string(self):
    data_execution_prevention = int(self.data_execution_prevention, 10)
    if data_execution_prevention == 2:
      return u'true'
    return u''

  @property
  def debug_information_format_string(self):
    debug_information_format = int(self.debug_information_format, 10)
    if debug_information_format == 3:
      return u'ProgramDatabase'
    return u''

  @property
  def enable_comdat_folding_string(self):
    enable_comdat_folding = int(self.enable_comdat_folding, 10)
    if enable_comdat_folding == 2:
      return u'true'
    return u''

  @property
  def link_incremental_string(self):
    link_incremental = int(self.link_incremental, 10)
    if link_incremental == 1:
      return u'false'
    return u''

  @property
  def optimize_references_string(self):
    optimize_references = int(self.optimize_references, 10)
    if optimize_references == 2:
      return u'true'
    return u''

  @property
  def optimization_string(self):
    optimization = int(self.optimization, 10)
    if optimization == 0:
      return u'Disabled'
    elif optimization == 2:
      return u'MaxSpeed'
    return u''

  @property
  def output_type_string(self):
    output_type = int(self.output_type, 10)
    if output_type == 1:
      return u'Application'
    elif output_type == 2:
      return u'DynamicLibrary'
    elif output_type == 4:
      return u'StaticLibrary'
    return u''

  @property
  def precompiled_header_string(self):
    _ = int(self.precompiled_header, 10)
    # TODO: do something with precompiled_header.
    return u''

  @property
  def randomized_base_address_string(self):
    randomized_base_address = int(self.randomized_base_address, 10)
    if randomized_base_address == 1:
      return u'false'
    elif randomized_base_address == 2:
      return u'true'
    return u''

  @property
  def runtime_librarian_string(self):
    runtime_library = int(self.runtime_library, 10)
    if runtime_library == 2:
      return u'MultiThreadedDLL'
    if runtime_library == 3:
      return u'MultiThreadedDebugDLL'
    return u''

  @property
  def sub_system_string(self):
    sub_system = int(self.sub_system, 10)
    if sub_system == 0:
      return u'NotSet'
    elif sub_system == 1:
      return u'Console'
    return u''

  @property
  def target_machine_string(self):
    target_machine = int(self.target_machine, 10)
    if target_machine == 1:
      return u'MachineX86'
    # TODO: assuming here that 2 is x64.
    elif target_machine == 2:
      return u'MachineX64'
    return u''

  @property
  def warning_level_string(self):
    warning_level = int(self.warning_level, 10)
    if warning_level == 3:
      return u'Level3'
    elif warning_level == 4:
      return u'Level4'
    return u''

  @property
  def whole_program_optimization_string(self):
    whole_program_optimization = int(self.whole_program_optimization, 10)
    if whole_program_optimization == 0:
      return u'false'
    elif whole_program_optimization == 1:
      return u'true'
    return u''

  def CopyToX64(self):
    """Copies the Visual Studio project configuration to an x64 equivalent."""
    copy = VSProjectConfiguration()

    copy.additional_dependencies = self.additional_dependencies
    copy.basic_runtime_checks = self.basic_runtime_checks
    copy.character_set = self.character_set
    copy.compile_as = self.compile_as
    copy.data_execution_prevention = self.data_execution_prevention
    copy.debug_information_format = self.debug_information_format
    copy.detect_64bit_portability_problems = (
        self.detect_64bit_portability_problems)
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
    copy.platform = u'x64'
    copy.platform_toolset = u''
    copy.precompiled_header = self.precompiled_header
    copy.preprocessor_definitions = self.preprocessor_definitions
    copy.randomized_base_address = self.randomized_base_address
    copy.runtime_library = self.runtime_library
    copy.smaller_type_check = self.smaller_type_check
    copy.sub_system = self.sub_system
    copy.target_machine = u'2'
    copy.warning_as_error = self.warning_as_error
    copy.warning_level = self.warning_level
    copy.whole_program_optimization = self.whole_program_optimization

    return copy

  def GetPlatformToolset(self, output_version):
    """Retrieves the platform toolset.

    Args:
      output_version: the output Visual Studio version.
    """
    platform_toolset = self.platform_toolset
    if not platform_toolset:
      if output_version == 2010 and self.platform == u'x64':
        platform_toolset = u'Windows7.1SDK'
      elif output_version == 2012:
        platform_toolset = u'v110'
    return platform_toolset


class VSProjectInformation(object):
  """Class to represent a Visual Studio project information."""

  def __init__(self):
    """Initializes Visual Studio project information."""
    self.configurations = VSConfigurations()
    self.dependencies = []
    self.guid = u''
    self.header_files = []
    self.keyword = u''
    self.name = u''
    self.resource_files = []
    self.root_name_space = u''
    self.source_files = []
    self.third_party_dependencies = []


class VSSolutionConfiguration(VSConfiguration):
  """Class to represent a Visual Studio solution configuration."""

  def CopyToX64(self):
    """Copies the Visual Studio solution configuration to an x64 equivalent."""
    copy = VSSolutionConfiguration()

    copy.name = self.name
    copy.platform = u'x64'

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
    """Initializes a file reader."""
    self._file = None
    self._line = None

  def Open(self, filename):
    """Opens the file.

    Args:
      filename: the filename of the file.
    """
    # For reading these files we don't care about the actual end of lines.
    self._file = open(filename, 'r')

  def Close(self):
    """Closes the file."""
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

  def _ReadConfiguration(self, line):
    """Reads a configuration.

    Args:
      line: the line that contains the start of the configuration section.

    Returns:
      A configuration (instance of VSProjectConfiguration) or None if
      no configuration was found.
    """
    if not line.startswith(u'<Configuration'):
      return None

    project_configuration = VSProjectConfiguration()

    found_tool = False
    found_tool_compiler = False
    found_tool_librarian = False
    found_tool_linker = False

    while line:
      line = self._ReadLine()

      if line.startswith(u'</Configuration>'):
        break

      elif found_tool:
        if line.startswith(u'/>'):
          found_tool = False
          found_tool_compiler = False
          found_tool_librarian = False
          found_tool_linker = False

        elif found_tool_compiler:
          # Parse the compiler specific configuration.
          if line.startswith(u'Optimization='):
            values = re.findall(u'Optimization="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.optimization = values[0]

          elif line.startswith(u'EnableIntrinsicFunctions='):
            values = re.findall(
                u'EnableIntrinsicFunctions="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.enable_intrinsic_functions = values[0]

          elif line.startswith(u'AdditionalIncludeDirectories='):
            values = re.findall(
                u'AdditionalIncludeDirectories="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.include_directories = values[0]

          elif line.startswith(u'PreprocessorDefinitions='):
            values = re.findall(
                u'PreprocessorDefinitions="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.preprocessor_definitions = values[0]

          elif line.startswith(u'BasicRuntimeChecks='):
            values = re.findall(u'BasicRuntimeChecks="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.basic_runtime_checks = values[0]

          elif line.startswith(u'SmallerTypeCheck='):
            values = re.findall(u'SmallerTypeCheck="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.smaller_type_check = values[0]

          elif line.startswith(u'RuntimeLibrary='):
            values = re.findall(u'RuntimeLibrary="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.runtime_library = values[0]

          elif line.startswith(u'EnableFunctionLevelLinking='):
            values = re.findall(u'EnableFunctionLevelLinking="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.enable_function_level_linking = values[0]

          elif line.startswith(u'UsePrecompiledHeader='):
            values = re.findall(u'UsePrecompiledHeader="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.precompiled_header = values[0]

          elif line.startswith(u'WarningLevel='):
            values = re.findall(u'WarningLevel="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.warning_level = values[0]

          elif line.startswith(u'Detect64BitPortabilityProblems='):
            values = re.findall(
                u'Detect64BitPortabilityProblems="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.detect_64bit_portability_problems = (
                  values[0])

          elif line.startswith(u'WarnAsError='):
            values = re.findall(u'WarnAsError="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.warning_as_error = values[0]

          elif line.startswith(u'DebugInformationFormat='):
            values = re.findall(
                u'DebugInformationFormat="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.debug_information_format = values[0]

          elif line.startswith(u'CompileAs='):
            values = re.findall(u'CompileAs="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.compile_as = values[0]

        elif found_tool_librarian:
          # Parse the libararian specific configuration.
          if line.startswith(u'OutputFile='):
            values = re.findall(u'OutputFile="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.librarian_output_file = values[0]

          elif line.startswith(u'IgnoreAllDefaultLibraries='):
            values = re.findall(
                u'IgnoreAllDefaultLibraries="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.librarian_ignore_defaults = values[0]

        elif found_tool_linker:
          # Parse the linker specific configuration.
          if line.startswith(u'OutputDirectory='):
            project_configuration.linker_values_set = True
            values = re.findall(u'OutputDirectory="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.linker_output_directory = values[0]

          elif line.startswith(u'OutputFile='):
            project_configuration.linker_values_set = True
            values = re.findall(u'OutputFile="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.linker_output_file = values[0]

          elif line.startswith(u'AdditionalDependencies='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'AdditionalDependencies="([^"]*)"', line)
            if len(values) == 1:
              values = values[0].split(u' ')
              project_configuration.additional_dependencies = values

          elif line.startswith(u'LinkIncremental='):
            project_configuration.linker_values_set = True
            values = re.findall(u'LinkIncremental="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.link_incremental = values[0]

          elif line.startswith(u'ModuleDefinitionFile='):
            project_configuration.linker_values_set = True
            values = re.findall(u'ModuleDefinitionFile="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.module_definition_file = values[0]

          elif line.startswith(u'AdditionalLibraryDirectories='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'AdditionalLibraryDirectories="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.library_directories = values[0]

          elif line.startswith(u'GenerateDebugInformation='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'GenerateDebugInformation="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.generate_debug_information = values[0]

          elif line.startswith(u'SubSystem='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'SubSystem="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.sub_system = values[0]

          elif line.startswith(u'OptimizeReferences='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'OptimizeReferences="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.optimize_references = values[0]

          elif line.startswith(u'RandomizedBaseAddress='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'RandomizedBaseAddress="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.randomized_base_address = values[0]

          elif line.startswith(u'FixedBaseAddress='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'FixedBaseAddress="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.fixed_base_address = values[0]

          elif line.startswith(u'EnableCOMDATFolding='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'EnableCOMDATFolding="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.enable_comdat_folding = values[0]

          elif line.startswith(u'DataExecutionPrevention='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'DataExecutionPrevention="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.data_execution_prevention = values[0]

          elif line.startswith(u'ImportLibrary='):
            project_configuration.linker_values_set = True
            values = re.findall(
                u'ImportLibrary="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.import_library = values[0]

          elif line.startswith(u'TargetMachine='):
            project_configuration.linker_values_set = True
            values = re.findall(u'TargetMachine="([^"]*)"', line)
            if len(values) == 1:
              project_configuration.target_machine = values[0]

        elif line.startswith(u'Name="VCCLCompilerTool"'):
          found_tool_compiler = True

        elif line.startswith(u'Name="VCLibrarianTool"'):
          found_tool_librarian = True

        elif line.startswith(u'Name="VCLinkerTool"'):
          found_tool_linker = True

      elif line.startswith(u'<Tool'):
        found_tool = True

      elif line.startswith(u'Name='):
        # For more than 1 match findall will return a list with a tuple.
        values = re.findall(u'Name="([^|]*)[|]([^"]*)"', line)[0]
        if len(values) == 2:
          project_configuration.name = values[0]
          project_configuration.platform = values[1]

      elif line.startswith(u'ConfigurationType='):
        values = re.findall(u'ConfigurationType="([^"]*)"', line)
        if len(values) == 1:
          project_configuration.output_type = values[0]

      elif line.startswith(u'CharacterSet='):
        values = re.findall(u'CharacterSet="([^"]*)"', line)
        if len(values) == 1:
          project_configuration.character_set = values[0]

      elif line.startswith(u'ManagedExtensions='):
        values = re.findall(u'ManagedExtensions="([^"]*)"', line)
        if len(values) == 1:
          project_configuration.managed_extensions = values[0]

      elif line.startswith(u'WholeProgramOptimization='):
        values = re.findall(u'WholeProgramOptimization="([^"]*)"', line)
        if len(values) == 1:
          project_configuration.whole_program_optimization = values[0]

      # TODO: PlatformToolset.
      # TargetFrameworkVersion ?

    # Add the target machine when not defined.
    if not project_configuration.target_machine:
      if project_configuration.platform == u'Win32':
        project_configuration.target_machine = u'1'
      # TODO: assuming here that 2 is x64.
      elif project_configuration.platform == u'x64':
        project_configuration.target_machine = u'2'

    return project_configuration

  def _ReadConfigurations(self, project_information):
    """Reads the configurations.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    # Find the start of the configurations section.
    result = False
    line = self._ReadLine()

    while line:
      result = line.startswith(u'<Configurations>')
      if result:
        break
      line = self._ReadLine()

    if result:
      while line:
        line = self._ReadLine()

        if line.startswith(u'</Configurations>'):
          break

        elif line.startswith(u'<Configuration'):
          project_configuration = self._ReadConfiguration(line)

          if project_configuration:
            project_information.configurations.Append(project_configuration)

  def _ReadFiles(self, project_information):
    """Reads the files.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    # Find the start of the files section.
    result = False
    line = self._ReadLine()

    while line:
      result = line.startswith(u'<Files>')
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

        if line.startswith(u'</Files>'):
          break

        elif found_filter:
          if line.startswith(u'</Filter>'):
            found_filter = False
            found_filter_source_files = False
            found_filter_header_files = False
            found_filter_resource_files = False

          elif found_filter_source_files:
            if line.startswith(u'RelativePath='):
              values = re.findall(u'RelativePath="([^"]*)"', line)

              if len(values) == 1:
                project_information.source_files.append(values[0])

          elif found_filter_header_files:
            if line.startswith(u'RelativePath='):
              values = re.findall(u'RelativePath="([^"]*)"', line)

              if len(values) == 1:
                project_information.header_files.append(values[0])

          elif found_filter_resource_files:
            if line.startswith(u'RelativePath='):
              values = re.findall(u'RelativePath="([^"]*)"', line)

              if len(values) == 1:
                project_information.resource_files.append(values[0])

          elif line.startswith(u'Name="Source Files"'):
            found_filter_source_files = True

          elif line.startswith(u'Name="Header Files"'):
            found_filter_header_files = True

          elif line.startswith(u'Name="Resource Files"'):

            found_filter_resource_files = True

        elif line.startswith(u'<Filter'):
          found_filter = True

  def _ReadProjectInformation(self, project_information):
    """Reads project information.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    line = self._ReadLine()
    while line:
      if line.startswith(u'>'):
        break

      elif line.startswith(u'Name='):
        values = re.findall(u'Name="([^"]*)"', line)
        if len(values) == 1:
          project_information.name = values[0]

      elif line.startswith(u'ProjectGUID='):
        values = re.findall(u'ProjectGUID="{([^}]*)}"', line)
        if len(values) == 1:
          project_information.guid = values[0]

      elif line.startswith(u'RootNamespace='):
        values = re.findall(u'RootNamespace="([^"]*)"', line)
        if len(values) == 1:
          project_information.root_name_space = values[0]

      elif line.startswith(u'Keyword='):
        values = re.findall(u'Keyword="([^"]*)"', line)
        if len(values) == 1:
          project_information.keyword = values[0]

      line = self._ReadLine()

  def ReadHeader(self):
    """Reads a file header.

    Returns:
      True if successful or false otherwise.
    """
    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith(u'<?xml version="1.0"'):
      return False

    # TODO check encoding?

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith(u'<VisualStudioProject'):
      return False

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith(u'ProjectType="Visual C++"'):
      return False

    line = self._ReadLine()

    if not line:
      return False

    if not line.startswith(u'Version="9,00"'):
      return False

    return True

  def ReadProject(self):
    """Reads the project.

    Returns:
      Project information (instance of VSProjectInformation) if successful
      or None otherwise.
    """
    project_information = VSProjectInformation()

    self._ReadProjectInformation(project_information)
    self._ReadConfigurations(project_information)
    self._ReadFiles(project_information)

    return project_information


class VS2010ProjectFileReader(VSProjectFileReader):
  """Class to represent a Visual Studio 2010 project file reader."""
  # TODO: implement.


class VS2012ProjectFileReader(VSProjectFileReader):
  """Class to represent a Visual Studio 2012 project file reader."""
  # TODO: implement.


class VS2013ProjectFileReader(VSProjectFileReader):
  """Class to represent a Visual Studio 2013 project file reader."""
  # TODO: implement.


class VSProjectFileWriter(object):
  """Class to represent a Visual Studio project file writer."""

  def __init__(self):
    """Initializes a Visual Studio project configuration."""
    super(VSProjectFileWriter, self).__init__()
    self._file = None

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
    # TODO: handle encoding properly.
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

  def __init__(self):
    """Initializes a Visual Studio project file writer."""
    super(VS2008ProjectFileWriter, self).__init__()
    self._version = 2008

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLine('<?xml version="1.0" encoding="Windows-1252"?>')

  def WriteProjectConfigurations(self, unused_project_configurations):
    """Writes the project configurations.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    return

  def WriteProjectInformation(self, project_information):
    """Writes the project information.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    self.WriteLines([
        '<VisualStudioProject',
        '\tProjectType="Visual C++"',
        '\tVersion="9,00"'])

    self.WriteLine('\tName="{0:s}"'.format(project_information.name))

    self.WriteLine('\tProjectGUID="{{{0:s}}}"'.format(
        project_information.guid.upper()))

    self.WriteLine(
        '\tRootNamespace="{0:s}"'.format(project_information.root_name_space))

    if project_information.keyword:
      self.WriteLine(
          '\tKeyword="{0:s}"'.format(project_information.keyword))

    # Also seen 196613.
    self.WriteLines([
        '\tTargetFrameworkVersion="131072"',
        '\t>'])

    # TODO: handle platforms.
    self.WriteLines([
        '\t<Platforms>',
        '\t\t<Platform',
        '\t\t\tName="Win32"',
        '\t\t/>',
        '\t</Platforms>'])

    self.WriteLines([
        '\t<ToolFiles>',
        '\t</ToolFiles>'])

  def _WriteConfiguration(self, project_configuration):
    """Writes the project configuration.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine('\t\t<Configuration')

    self.WriteLine('\t\t\tName="{0:s}|{1:s}"'.format(
        project_configuration.name, project_configuration.platform))

    self.WriteLines([
        '\t\t\tOutputDirectory="$(SolutionDir)$(ConfigurationName)"',
        '\t\t\tIntermediateDirectory="$(ConfigurationName)"'])

    self.WriteLine('\t\t\tConfigurationType="{0:s}"'.format(
        project_configuration.output_type))

    self.WriteLine('\t\t\tCharacterSet="{0:s}"'.format(
        project_configuration.character_set))

    if project_configuration.managed_extensions:
      self.WriteLine('\t\t\tManagedExtensions="{0:s}"'.format(
          project_configuration.managed_extensions))

    if project_configuration.whole_program_optimization:
      self.WriteLine('\t\t\tWholeProgramOptimization="{0:s}"'.format(
          project_configuration.whole_program_optimization))

    self.WriteLine('\t\t\t>')

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCPreBuildEventTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCCustomBuildTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCXMLDataGeneratorTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCWebServiceProxyGeneratorTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCMIDLTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCCLCompilerTool"'])

    if project_configuration.optimization:
      self.WriteLine('\t\t\t\tOptimization="{0:s}"'.format(
          project_configuration.optimization))

    self.WriteLine('\t\t\t\tAdditionalIncludeDirectories="{0:s}"'.format(
        project_configuration.include_directories))

    self.WriteLine('\t\t\t\tPreprocessorDefinitions="{0:s}"'.format(
        project_configuration.preprocessor_definitions))

    if project_configuration.basic_runtime_checks:
      self.WriteLine('\t\t\t\tBasicRuntimeChecks="{0:s}"'.format(
          project_configuration.basic_runtime_checks))

    if project_configuration.smaller_type_check:
      self.WriteLine('\t\t\t\tSmallerTypeCheck="{0:s}"'.format(
          project_configuration.smaller_type_check))

    self.WriteLine('\t\t\t\tRuntimeLibrary="{0:s}"'.format(
        project_configuration.runtime_library))

    if project_configuration.precompiled_header:
      self.WriteLine('\t\t\t\tUsePrecompiledHeader="{0:s}"'.format(
          project_configuration.precompiled_header))

    self.WriteLine('\t\t\t\tWarningLevel="{0:s}"'.format(
        project_configuration.warning_level))

    if project_configuration.warning_as_error:
      self.WriteLine('\t\t\t\tWarnAsError="{0:s}"'.format(
          project_configuration.warning_as_error))

    if project_configuration.detect_64bit_portability_problems:
      self.WriteLine('\t\t\t\tDetect64BitPortabilityProblems="{0:s}"'.format(
          project_configuration.detect_64bit_portability_problems))

    if project_configuration.debug_information_format:
      self.WriteLine('\t\t\t\tDebugInformationFormat="{0:s}"'.format(
          project_configuration.debug_information_format))

    self.WriteLine('\t\t\t\tCompileAs="{0:s}"'.format(
        project_configuration.compile_as))

    self.WriteLine('\t\t\t/>')

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCManagedResourceCompilerTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCResourceCompilerTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCPreLinkEventTool"',
        '\t\t\t/>'])

    # TODO: add librarian values set?
    if project_configuration.librarian_output_file:
      self.WriteLines([
          '\t\t\t<Tool',
          '\t\t\t\tName="VCLibrarianTool"'])

      self.WriteLine('\t\t\t\tOutputFile="{0:s}"'.format(
          project_configuration.librarian_output_file))

      self.WriteLine('\t\t\t\tModuleDefinitionFile=""')

      self.WriteLine('\t\t\t\tIgnoreAllDefaultLibraries="{0:s}"'.format(
          project_configuration.librarian_ignore_defaults))

      self.WriteLine('\t\t\t/>')

    if project_configuration.linker_values_set:
      self.WriteLines([
          '\t\t\t<Tool',
          '\t\t\t\tName="VCLinkerTool"'])

      if project_configuration.additional_dependencies:
        self.WriteLine('\t\t\t\tAdditionalDependencies="{0:s}"'.format(
            ' '.join(sorted(project_configuration.additional_dependencies))))

      if project_configuration.linker_output_file:
        self.WriteLine('\t\t\t\tOutputFile="{0:s}"'.format(
            project_configuration.linker_output_file))

      if project_configuration.link_incremental:
        self.WriteLine('\t\t\t\tLinkIncremental="{0:s}"'.format(
            project_configuration.link_incremental))

      library_directories = '&quot;$(OutDir)&quot;'
      if project_configuration.library_directories:
        library_directories = '{0:s};{1:s}'.format(
            library_directories, project_configuration.library_directories)

      self.WriteLine('\t\t\t\tAdditionalLibraryDirectories="{0:s}"'.format(
          library_directories))

      if project_configuration.generate_debug_information:
        self.WriteLine('\t\t\t\tGenerateDebugInformation="{0:s}"'.format(
            project_configuration.generate_debug_information))

      if project_configuration.sub_system:
        self.WriteLine('\t\t\t\tSubSystem="{0:s}"'.format(
            project_configuration.sub_system))

      if project_configuration.optimize_references:
        self.WriteLine('\t\t\t\tOptimizeReferences="{0:s}"'.format(
            project_configuration.optimize_references))

      if project_configuration.enable_comdat_folding:
        self.WriteLine('\t\t\t\tEnableCOMDATFolding="{0:s}"'.format(
            project_configuration.enable_comdat_folding))

      if project_configuration.randomized_base_address:
        self.WriteLine('\t\t\t\tRandomizedBaseAddress="{0:s}"'.format(
            project_configuration.randomized_base_address))

      if project_configuration.data_execution_prevention:
        self.WriteLine('\t\t\t\tDataExecutionPrevention="{0:s}"'.format(
            project_configuration.data_execution_prevention))

      if project_configuration.target_machine:
        self.WriteLine('\t\t\t\tTargetMachine="{0:s}"'.format(
            project_configuration.target_machine))

      if project_configuration.import_library:
        self.WriteLine('\t\t\t\tImportLibrary="{0:s}"'.format(
            project_configuration.import_library))

      self.WriteLine('\t\t\t/>')

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCALinkTool"',
        '\t\t\t/>'])

    if project_configuration.linker_values_set:
      self.WriteLines([
          '\t\t\t<Tool',
          '\t\t\t\tName="VCManifestTool"',
          '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCXDCMakeTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCBscMakeTool"',
        '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCFxCopTool"',
        '\t\t\t/>'])

    if project_configuration.linker_values_set:
      self.WriteLines([
          '\t\t\t<Tool',
          '\t\t\t\tName="VCAppVerifierTool"',
          '\t\t\t/>'])

    self.WriteLines([
        '\t\t\t<Tool',
        '\t\t\t\tName="VCPostBuildEventTool"',
        '\t\t\t/>'])

    self.WriteLine('\t\t</Configuration>')

  def WriteConfigurations(self, project_configurations):
    """Writes the configurations.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLine('\t<Configurations>')

    for project_configuration in project_configurations.GetSorted():
      self._WriteConfiguration(project_configuration)

    self.WriteLine('\t</Configurations>')

    self.WriteLines([
        '\t<References>',
        '\t</References>'])

  def _WriteSourceFiles(self, source_files):
    """Writes the source files.

    Args:
      source_files: a list of strings of the source filenames.
    """
    self.WriteLines([
        '\t\t<Filter',
        '\t\t\tName="Source Files"',
        '\t\t\tFilter="cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx"',
        '\t\t\tUniqueIdentifier="{4FC737F1-C7A5-4376-A066-2A32D752A2FF}"',
        '\t\t\t>'])

    for filename in source_files:
      self.WriteLine('\t\t\t<File')

      self.WriteLine('\t\t\t\tRelativePath="{0:s}"'.format(filename))

      self.WriteLines([
          '\t\t\t\t>',
          '\t\t\t</File>'])

    self.WriteLine('\t\t</Filter>')

  def _WriteHeaderFiles(self, header_files):
    """Writes the header files.

    Args:
      header_files: a list of strings of the header filenames.
    """
    self.WriteLines([
        '\t\t<Filter',
        '\t\t\tName="Header Files"',
        '\t\t\tFilter="h;hpp;hxx;hm;inl;inc;xsd"',
        '\t\t\tUniqueIdentifier="{93995380-89BD-4b04-88EB-625FBE52EBFB}"',
        '\t\t\t>'])

    for filename in header_files:
      self.WriteLine('\t\t\t<File')

      self.WriteLine('\t\t\t\tRelativePath="{0:s}"'.format(filename))

      self.WriteLines([
          '\t\t\t\t>',
          '\t\t\t</File>'])

    self.WriteLine('\t\t</Filter>')

  def _WriteResourceFiles(self, resource_files):
    """Writes the resource files.

    Args:
      resource_files: a list of strings of the resource filenames.
    """
    self.WriteLines([
        '\t\t<Filter',
        '\t\t\tName="Resource Files"',
        ('\t\t\tFilter="rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;'
         'resx;tiff;tif;png;wav"'),
        '\t\t\tUniqueIdentifier="{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}"',
        '\t\t\t>'])

    for filename in resource_files:
      self.WriteLine('\t\t\t<File')

      self.WriteLine('\t\t\t\tRelativePath="{0:s}"'.format(filename))

      self.WriteLines([
          '\t\t\t\t>',
          '\t\t\t</File>'])

    self.WriteLine('\t\t</Filter>')

  def WriteFiles(self, source_files, header_files, resource_files):
    """Writes the files.

    Args:
      source_files: a list of strings of the source filenames.
      header_files: a list of strings of the header filenames.
      resource_files: a list of strings of the resource filenames.
    """
    self.WriteLine('\t<Files>')

    self._WriteSourceFiles(source_files)
    self._WriteHeaderFiles(header_files)
    self._WriteResourceFiles(resource_files)

    self.WriteLine('\t</Files>')

    self.WriteLines([
        '\t<Globals>',
        '\t</Globals>'])

  def WriteDependencies(
      self, unused_dependencies, unused_solution_projects_by_guid):
    """Writes the dependencies.

    Args:
      dependencies: a list of the GUID of the dependencies.
      solution_projects_by_guid: a dictionary of the projects (instances of
                                 VSSolutionProject) with their GUID in lower
                                 case as the key.
    """
    return

  def WriteFooter(self):
    """Writes a file footer."""
    self.WriteLine('</VisualStudioProject>')


class VS2010ProjectFileWriter(VSProjectFileWriter):
  """Class to represent a Visual Studio 2010 project file writer."""

  def __init__(self):
    """Initializes a Visual Studio project file writer."""
    super(VS2010ProjectFileWriter, self).__init__()
    self._project_file_version = '10.0.40219.1'
    self._tools_version = '4.0'
    self._version = 2010

  def WriteHeader(self):
    """Writes a file header."""
    self._file.write('\xef\xbb\xbf')
    self.WriteLines([
        '<?xml version="1.0" encoding="utf-8"?>',
        ('<Project DefaultTargets="Build" ToolsVersion="{0:s}" '
         'xmlns="http://schemas.microsoft.com/developer/msbuild/2003">').format(
             self._tools_version)])

  def WriteProjectConfigurations(self, project_configurations):
    """Writes the project configurations.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLine('  <ItemGroup Label="ProjectConfigurations">')

    for project_configuration in project_configurations.GetSorted():
      self.WriteLine('    <ProjectConfiguration Include="{0:s}|{1:s}">'.format(
          project_configuration.name, project_configuration.platform))

      self.WriteLine('      <Configuration>{0:s}</Configuration>'.format(
          project_configuration.name))

      self.WriteLine('      <Platform>{0:s}</Platform>'.format(
          project_configuration.platform))

      self.WriteLine('    </ProjectConfiguration>')

    self.WriteLine('  </ItemGroup>')

  def WriteProjectInformation(self, project_information):
    """Writes the project information.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
    """
    self.WriteLine('  <PropertyGroup Label="Globals">')

    self.WriteLine('    <ProjectGuid>{{{0:s}}}</ProjectGuid>'.format(
        project_information.guid))

    self.WriteLine('    <RootNamespace>{0:s}</RootNamespace>'.format(
        project_information.root_name_space))

    if project_information.keyword:
      self.WriteLine('    <Keyword>{0:s}</Keyword>'.format(
          project_information.keyword))

    self.WriteLine('  </PropertyGroup>')

  def _WriteConfigurationPropertyGroup(self, project_configuration):
    """Writes the configuration property group.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine((
        '  <PropertyGroup Condition="\'$(Configuration)|$(Platform)\'=='
        '\'{0:s}|{1:s}\'" Label="Configuration">').format(
            project_configuration.name, project_configuration.platform))

    self.WriteLine('    <ConfigurationType>{0:s}</ConfigurationType>'.format(
        project_configuration.output_type_string))

    if project_configuration.character_set:
      self.WriteLine('    <CharacterSet>{0:s}</CharacterSet>'.format(
          project_configuration.character_set_string))

    if project_configuration.managed_extensions == '1':
      self.WriteLine('    <CLRSupport>true</CLRSupport>')

    if project_configuration.whole_program_optimization:
      self.WriteLine((
          '    <WholeProgramOptimization>{0:s}'
          '</WholeProgramOptimization>').format(
              project_configuration.whole_program_optimization_string))

    platform_toolset = project_configuration.GetPlatformToolset(self._version)
    if platform_toolset:
      self.WriteLine('    <PlatformToolset>{0:s}</PlatformToolset>'.format(
          platform_toolset))

    self.WriteLine('  </PropertyGroup>')

  def _WriteOutIntDirConditions(
      self, configuration_name, project_configurations):
    """Writes the OutDir and IntDir conditions.

    Args:
      configuration_name: the name of the configuration.
      project_configurations: the configurations (instance of VSConfigurations).
    """
    for configuration_platform in sorted(project_configurations.platforms):
      project_configuration = project_configurations.GetByIdentifier(
          configuration_name, configuration_platform)

      self.WriteLine((
          '    <OutDir Condition="\'$(Configuration)|$(Platform)\'=='
          '\'{0:s}|{1:s}\'">$(SolutionDir)$(Configuration)\\'
          '</OutDir>').format(
              project_configuration.name, project_configuration.platform))

    for configuration_platform in sorted(project_configurations.platforms):
      project_configuration = project_configurations.GetByIdentifier(
          configuration_name, configuration_platform)

      self.WriteLine((
          '    <IntDir Condition="\'$(Configuration)|$(Platform)\'=='
          '\'{0:s}|{1:s}\'">$(Configuration)\\</IntDir>').format(
              project_configuration.name, project_configuration.platform))

  def _WriteOutIntDirPropertyGroups(self, project_configurations):
    """Writes the OutDir and IntDir property groups.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLines([
        '  <PropertyGroup>',
        '    <_ProjectFileVersion>{0:s}</_ProjectFileVersion>'.format(
            self._project_file_version)])

    # Mimic Visual Studio behavior and output the configurations
    # in platforms by name.
    for configuration_name in sorted(project_configurations.names):
      self._WriteOutIntDirConditions(configuration_name, project_configurations)

      for configuration_platform in sorted(project_configurations.platforms):
        project_configuration = project_configurations.GetByIdentifier(
            configuration_name, configuration_platform)

        if project_configuration.link_incremental != '':
          self.WriteLine((
              '    <LinkIncremental Condition="\'$(Configuration)|'
              '$(Platform)\'==\'{0:s}|{1:s}\'">{2:s}</LinkIncremental>').format(
                  project_configuration.name, project_configuration.platform,
                  project_configuration.link_incremental_string))

    self.WriteLine('  </PropertyGroup>')

  def _WriteClCompileSection(self, project_configuration):
    """Writes the CLCompile section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    include_directories = re.sub(
        r'&quot;', r'', project_configuration.include_directories)

    if include_directories and include_directories[-1] != ';':
      include_directories = '{0:s};'.format(
          include_directories)

    include_directories = '{0:s}%(AdditionalIncludeDirectories)'.format(
        include_directories)

    preprocessor_definitions = project_configuration.preprocessor_definitions

    if preprocessor_definitions and preprocessor_definitions[-1] != ';':
      preprocessor_definitions = '{0:s};'.format(preprocessor_definitions)

    preprocessor_definitions = '{0:s}%(PreprocessorDefinitions)'.format(
        preprocessor_definitions)

    self.WriteLine('    <ClCompile>')

    if project_configuration.optimization != '':
      self.WriteLine('      <Optimization>{0:s}</Optimization>'.format(
          project_configuration.optimization_string))

    if project_configuration.enable_intrinsic_functions != '':
      self.WriteLine((
          '      <IntrinsicFunctions>{0:s}</IntrinsicFunctions>').format(
              project_configuration.enable_intrinsic_functions))

    if project_configuration.whole_program_optimization:
      self.WriteLine((
          '      <WholeProgramOptimization>{0:s}'
          '</WholeProgramOptimization>').format(
              project_configuration.whole_program_optimization_string))

    self.WriteLine((
        '      <AdditionalIncludeDirectories>{0:s}'
        '</AdditionalIncludeDirectories>').format(include_directories))

    self.WriteLine((
        '      <PreprocessorDefinitions>{0:s}'
        '</PreprocessorDefinitions>').format(preprocessor_definitions))

    if project_configuration.basic_runtime_checks != '':
      self.WriteLine((
          '      <BasicRuntimeChecks>{0:s}'
          '</BasicRuntimeChecks>').format(
              project_configuration.basic_runtime_checks_string))

    if project_configuration.smaller_type_check != '':
      self.WriteLine((
          '      <SmallerTypeCheck>{0:s}</SmallerTypeCheck>').format(
              project_configuration.smaller_type_check))

    self.WriteLine((
        '      <RuntimeLibrary>{0:s}</RuntimeLibrary>').format(
            project_configuration.runtime_librarian_string))

    if project_configuration.enable_function_level_linking != '':
      self.WriteLine((
          '      <FunctionLevelLinking>{0:s}</FunctionLevelLinking>').format(
              project_configuration.enable_function_level_linking))

    if project_configuration.precompiled_header != '':
      # A value of 0 is represented by a new line.
      if project_configuration.precompiled_header == '0':
        self.WriteLines([
            '      <PrecompiledHeader>',
            '      </PrecompiledHeader>'])
      else:
        self.WriteLine((
            '      <PrecompiledHeader>{0:s}</PrecompiledHeader>').format(
                project_configuration.precompiled_header_string))

    self.WriteLine('      <WarningLevel>{0:s}</WarningLevel>'.format(
        project_configuration.warning_level_string))

    if project_configuration.warning_as_error:
      self.WriteLine((
          '      <TreatWarningAsError>{0:s}'
          '</TreatWarningAsError>').format(
              project_configuration.warning_as_error))

    if project_configuration.debug_information_format != '':
      # A value of 0 is represented by a new line.
      if project_configuration.debug_information_format == '0':
        self.WriteLines([
            '      <DebugInformationFormat>',
            '      </DebugInformationFormat>'])
      else:
        self.WriteLine((
            '      <DebugInformationFormat>{0:s}'
            '</DebugInformationFormat>').format(
                project_configuration.debug_information_format_string))

    if project_configuration.compile_as:
      self.WriteLine('      <CompileAs>{0:s}</CompileAs>'.format(
          project_configuration.compile_as_string))

    self.WriteLine('    </ClCompile>')

  def _WriteLibrarianSection(self, project_configuration):
    """Writes the librarian section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    librarian_output_file = re.sub(
        r'[$][(]OutDir[)]\\', r'$(OutDir)',
        project_configuration.librarian_output_file)

    self.WriteLines([
        '    <Lib>',
        '      <OutputFile>{0:s}</OutputFile>'.format(librarian_output_file)])

    if project_configuration.module_definition_file != '':
      self.WriteLine((
          '      <ModuleDefinitionFile>{0:s}'
          '</ModuleDefinitionFile>').format(
              project_configuration.module_definition_file))
    else:
      self.WriteLines([
          '      <ModuleDefinitionFile>',
          '      </ModuleDefinitionFile>'])

    if project_configuration.librarian_ignore_defaults != '':
      self.WriteLine((
          '      <IgnoreAllDefaultLibraries>{0:s}'
          '</IgnoreAllDefaultLibraries>').format(
              project_configuration.librarian_ignore_defaults))

    self.WriteLine('    </Lib>')

  def _WriteLinkerSection(self, project_configuration):
    """Writes the linker section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine('    <Link>')

    # Visual Studio will convert an empty additional dependencies value.
    if project_configuration.additional_dependencies:
      additional_dependencies = ';'.join(
          sorted(project_configuration.additional_dependencies))

      additional_dependencies = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)', additional_dependencies)

      if additional_dependencies and additional_dependencies[-1] != ';':
        additional_dependencies = '{0:s};'.format(additional_dependencies)

      additional_dependencies = '{0:s}%(AdditionalDependencies)'.format(
          additional_dependencies)

      self.WriteLine((
          '      <AdditionalDependencies>{0:s}'
          '</AdditionalDependencies>').format(
              additional_dependencies))

    if project_configuration.linker_output_file:
      linker_output_file = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.linker_output_file)

      self.WriteLine('      <OutputFile>{0:s}</OutputFile>'.format(
          linker_output_file))

      if project_configuration.module_definition_file != '':
        self.WriteLine((
            '      <ModuleDefinitionFile>{0:s}'
            '</ModuleDefinitionFile>').format(
                project_configuration.module_definition_file))

    if project_configuration.library_directories:
      library_directories = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.library_directories)
      library_directories = re.sub(
          r'&quot;', r'', library_directories)

      if library_directories and library_directories[-1] != ';':
        library_directories = '{0:s};'.format(library_directories)

      library_directories = '{0:s}%(AdditionalLibraryDirectories)'.format(
          library_directories)

      self.WriteLine((
          '      <AdditionalLibraryDirectories>{0:s}'
          '</AdditionalLibraryDirectories>').format(
              library_directories))

    if project_configuration.generate_debug_information != '':
      self.WriteLine((
          '      <GenerateDebugInformation>{0:s}'
          '</GenerateDebugInformation>').format(
              project_configuration.generate_debug_information))

    if project_configuration.sub_system != '':
      self.WriteLine('      <SubSystem>{0:s}</SubSystem>'.format(
          project_configuration.sub_system_string))

    if project_configuration.optimize_references == '0':
      self.WriteLines([
          '      <OptimizeReferences>',
          '      </OptimizeReferences>'])

    elif project_configuration.optimize_references != '':
      self.WriteLine((
          '      <OptimizeReferences>{0:s}</OptimizeReferences>').format(
              project_configuration.optimize_references_string))

    if project_configuration.enable_comdat_folding == '0':
      self.WriteLines([
          '      <EnableCOMDATFolding>',
          '      </EnableCOMDATFolding>'])

    elif project_configuration.enable_comdat_folding != '':
      self.WriteLine((
          '      <EnableCOMDATFolding>{0:s}</EnableCOMDATFolding>').format(
              project_configuration.enable_comdat_folding_string))

    if project_configuration.randomized_base_address != '':
      self.WriteLine((
          '      <RandomizedBaseAddress>{0:s}'
          '</RandomizedBaseAddress>').format(
              project_configuration.randomized_base_address_string))

    if project_configuration.fixed_base_address == '0':
      self.WriteLines([
          '      <FixedBaseAddress>',
          '      </FixedBaseAddress>'])

    if project_configuration.data_execution_prevention != '':
      # A value of 0 is represented by a new line.
      if project_configuration.data_execution_prevention == '0':
        self.WriteLines([
            '      <DataExecutionPrevention>',
            '      </DataExecutionPrevention>'])
      else:
        self.WriteLine((
            '      <DataExecutionPrevention>{0:s}'
            '</DataExecutionPrevention>').format(
                project_configuration.data_execution_prevention_string))

    if project_configuration.import_library:
      import_library = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.import_library)

      self.WriteLine('      <ImportLibrary>{0:s}</ImportLibrary>'.format(
          import_library))

    if project_configuration.target_machine != '':
      self.WriteLine('      <TargetMachine>{0:s}</TargetMachine>'.format(
          project_configuration.target_machine_string))

    self.WriteLine('    </Link>')

  def _WriteItemDefinitionGroup(self, project_configuration):
    """Writes the item definition group.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine((
        '  <ItemDefinitionGroup Condition="\'$(Configuration)|'
        '$(Platform)\'==\'{0:s}|{1:s}\'">').format(
            project_configuration.name, project_configuration.platform))

    # Write the compiler specific section.
    self._WriteClCompileSection(project_configuration)

    # Write the librarian specific section.
    if project_configuration.librarian_output_file:
      self._WriteLibrarianSection(project_configuration)

    # Write the linker specific section.
    if project_configuration.linker_values_set:
      self._WriteLinkerSection(project_configuration)

    self.WriteLine('  </ItemDefinitionGroup>')

  def WriteConfigurations(self, project_configurations):
    """Writes the configurations.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLine(
        '  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.Default.props" />')

    # Mimic Visual Studio behavior and output the configurations
    # in reverse order of name.
    for project_configuration in project_configurations.GetSorted(reverse=True):
      self._WriteConfigurationPropertyGroup(project_configuration)

    self.WriteLines([
        '  <Import Project="$(VCTargetsPath)\\Microsoft.Cpp.props" />',
        '  <ImportGroup Label="ExtensionSettings">',
        '  </ImportGroup>'])

    # Mimic Visual Studio behavior and output the configurations
    # in reverse of name.
    for project_configuration in project_configurations.GetSorted(reverse=True):
      self.WriteLines([
          ('  <ImportGroup Condition="\'$(Configuration)|$(Platform)\'=='
           '\'{0:s}|{1:s}\'" Label="PropertySheets">'.format(
               project_configuration.name, project_configuration.platform)),
          ('    <Import Project="$(UserRootDir)\\Microsoft.Cpp.$(Platform)'
           '.user.props" Condition="exists(\'$(UserRootDir)\\Microsoft.Cpp'
           '.$(Platform).user.props\')" Label="LocalAppDataPlatform" />'),
          '  </ImportGroup>'])

    self.WriteLine('  <PropertyGroup Label="UserMacros" />')

    self._WriteOutIntDirPropertyGroups(project_configurations)

    for project_configuration in project_configurations.GetSorted():
      self._WriteItemDefinitionGroup(project_configuration)

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

  def WriteDependencies(self, dependencies, solution_projects_by_guid):
    """Writes the dependencies.

    Args:
      dependencies: a list of the GUID of the dependencies.
      solution_projects_by_guid: a dictionary of the projects (instances of
                                 VSSolutionProject) with their GUID in lower
                                 case as the key.
    """
    if len(dependencies) > 0:
      self.WriteLine('  <ItemGroup>')

      dependencies_by_name = {}

      # Mimic Visual Studio behavior and ouput the depencies in order
      # of name (perhaps filename?).
      for dependency_guid in dependencies:
        dependency_project = solution_projects_by_guid[dependency_guid]

        dependencies_by_name[dependency_project.name] = dependency_project

      for dependency_name in sorted(dependencies_by_name.keys()):
        dependency_project = dependencies_by_name[dependency_name]

        dependency_filename = '..\\{0:s}.vcxproj'.format(
            dependency_project.filename)

        dependency_guid = dependency_project.guid.lower()

        self.WriteLines([
            ('    <ProjectReference Include="{0:s}">').format(
                dependency_filename),
            '      <Project>{{{0:s}}}</Project>'.format(dependency_guid),
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


class VS2012ProjectFileWriter(VS2010ProjectFileWriter):
  """Class to represent a Visual Studio 2012 project file writer."""

  def __init__(self):
    """Initializes a Visual Studio project file writer."""
    super(VS2012ProjectFileWriter, self).__init__()
    self._project_file_version = '11.0.61030.0'
    self._tools_version = '4.0'
    self._version = 2012

  def _WriteConfigurationPropertyGroup(self, project_configuration):
    """Writes the configuration property group.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine((
        '  <PropertyGroup Condition="\'$(Configuration)|$(Platform)\'=='
        '\'{0:s}|{1:s}\'" Label="Configuration">').format(
            project_configuration.name, project_configuration.platform))

    self.WriteLine('    <ConfigurationType>{0:s}</ConfigurationType>'.format(
        project_configuration.output_type_string))

    platform_toolset = project_configuration.GetPlatformToolset(self._version)
    if platform_toolset:
      self.WriteLine('    <PlatformToolset>{0:s}</PlatformToolset>'.format(
          platform_toolset))

    if project_configuration.character_set:
      self.WriteLine('    <CharacterSet>{0:s}</CharacterSet>'.format(
          project_configuration.character_set_string))

    if project_configuration.managed_extensions == '1':
      self.WriteLine('    <CLRSupport>true</CLRSupport>')

    if project_configuration.whole_program_optimization:
      self.WriteLine((
          '    <WholeProgramOptimization>{0:s}'
          '</WholeProgramOptimization>').format(
              project_configuration.whole_program_optimization_string))

    self.WriteLine('  </PropertyGroup>')

  def _WriteOutIntDirConditions(
      self, configuration_name, project_configurations):
    """Writes the OutDir and IntDir conditions.

    Args:
      configuration_name: the name of the configuration.
      project_configurations: the configurations (instance of VSConfigurations).
    """
    for configuration_platform in sorted(project_configurations.platforms):
      project_configuration = project_configurations.GetByIdentifier(
          configuration_name, configuration_platform)

      self.WriteLines([
          ('  <PropertyGroup Condition="\'$(Configuration)|$(Platform)\'=='
           '\'{0:s}|{1:s}\'">').format(
               project_configuration.name, project_configuration.platform),
          '    <OutDir>$(SolutionDir)$(Configuration)\\</OutDir>',
          '    <IntDir>$(Configuration)\\</IntDir>'])

      if project_configuration.linker_values_set:
        self.WriteLine('    <LinkIncremental>false</LinkIncremental>')

      self.WriteLine('  </PropertyGroup>')

  def _WriteOutIntDirPropertyGroups(self, project_configurations):
    """Writes the OutDir and IntDir property groups.

    Args:
      project_configurations: the configurations (instance of VSConfigurations).
    """
    self.WriteLines([
        '  <PropertyGroup>',
        '    <_ProjectFileVersion>{0:s}</_ProjectFileVersion>'.format(
            self._project_file_version),
        '  </PropertyGroup>'])

    # Mimic Visual Studio behavior and output the configurations
    # in platforms by name.
    for configuration_name in sorted(project_configurations.names):
      self._WriteOutIntDirConditions(configuration_name, project_configurations)

      # for configuration_platform in sorted(project_configurations.platforms):
      #   project_configuration = project_configurations.GetByIdentifier(
      #       configuration_name, configuration_platform)

      #   if project_configuration.link_incremental != '':
      #     self.WriteLine((
      #         '    <LinkIncremental Condition="\'$(Configuration)|'
      #         '$(Platform)\'==\'{0:s}|{1:s}\'">{2:s}'
      #         '</LinkIncremental>').format(
      #             project_configuration.name, project_configuration.platform,
      #             project_configuration.link_incremental_string))

  def _WriteClCompileSection(self, project_configuration):
    """Writes the CLCompile section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    include_directories = re.sub(
        r'&quot;', r'', project_configuration.include_directories)

    if include_directories and include_directories[-1] != ';':
      include_directories = '{0:s};'.format(
          include_directories)

    include_directories = '{0:s}%(AdditionalIncludeDirectories)'.format(
        include_directories)

    preprocessor_definitions = project_configuration.preprocessor_definitions

    if preprocessor_definitions and preprocessor_definitions[-1] != ';':
      preprocessor_definitions = '{0:s};'.format(preprocessor_definitions)

    preprocessor_definitions = '{0:s}%(PreprocessorDefinitions)'.format(
        preprocessor_definitions)

    self.WriteLine('    <ClCompile>')

    if project_configuration.optimization != '':
      self.WriteLine('      <Optimization>{0:s}</Optimization>'.format(
          project_configuration.optimization_string))

    if project_configuration.enable_intrinsic_functions != '':
      self.WriteLine((
          '      <IntrinsicFunctions>{0:s}</IntrinsicFunctions>').format(
              project_configuration.enable_intrinsic_functions))

    self.WriteLine((
        '      <AdditionalIncludeDirectories>{0:s}'
        '</AdditionalIncludeDirectories>').format(include_directories))

    self.WriteLine((
        '      <PreprocessorDefinitions>{0:s}'
        '</PreprocessorDefinitions>').format(preprocessor_definitions))

    if project_configuration.basic_runtime_checks != '':
      self.WriteLine((
          '      <BasicRuntimeChecks>{0:s}'
          '</BasicRuntimeChecks>').format(
              project_configuration.basic_runtime_checks_string))

    if project_configuration.smaller_type_check != '':
      self.WriteLine((
          '      <SmallerTypeCheck>{0:s}</SmallerTypeCheck>').format(
              project_configuration.smaller_type_check))

    self.WriteLine((
        '      <RuntimeLibrary>{0:s}</RuntimeLibrary>').format(
            project_configuration.runtime_librarian_string))

    if project_configuration.enable_function_level_linking != '':
      self.WriteLine((
          '      <FunctionLevelLinking>{0:s}</FunctionLevelLinking>').format(
              project_configuration.enable_function_level_linking))

    if project_configuration.precompiled_header != '':
      # A value of 0 is represented by an empty XML tag.
      if project_configuration.precompiled_header == '0':
        self.WriteLine('      <PrecompiledHeader />')
      else:
        self.WriteLine((
            '      <PrecompiledHeader>{0:s}</PrecompiledHeader>').format(
                project_configuration.precompiled_header_string))

    self.WriteLine('      <WarningLevel>{0:s}</WarningLevel>'.format(
        project_configuration.warning_level_string))

    if project_configuration.warning_as_error:
      self.WriteLine((
          '      <TreatWarningAsError>{0:s}'
          '</TreatWarningAsError>').format(
              project_configuration.warning_as_error))

    if project_configuration.debug_information_format != '':
      # A value of 0 is represented by an empty XML tag.
      if project_configuration.debug_information_format == '0':
        self.WriteLine('      <DebugInformationFormat />')
      else:
        self.WriteLine((
            '      <DebugInformationFormat>{0:s}'
            '</DebugInformationFormat>').format(
                project_configuration.debug_information_format_string))

    if project_configuration.compile_as:
      self.WriteLine('      <CompileAs>{0:s}</CompileAs>'.format(
          project_configuration.compile_as_string))

    self.WriteLine('    </ClCompile>')

  def _WriteLibrarianSection(self, project_configuration):
    """Writes the librarian section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    librarian_output_file = re.sub(
        r'[$][(]OutDir[)]\\', r'$(OutDir)',
        project_configuration.librarian_output_file)

    self.WriteLines([
        '    <Lib>',
        '      <OutputFile>{0:s}</OutputFile>'.format(librarian_output_file)])

    if project_configuration.module_definition_file != '':
      self.WriteLine((
          '      <ModuleDefinitionFile>{0:s}'
          '</ModuleDefinitionFile>').format(
              project_configuration.module_definition_file))
    else:
      self.WriteLine('      <ModuleDefinitionFile />')

    if project_configuration.librarian_ignore_defaults != '':
      self.WriteLine((
          '      <IgnoreAllDefaultLibraries>{0:s}'
          '</IgnoreAllDefaultLibraries>').format(
              project_configuration.librarian_ignore_defaults))

    self.WriteLine('    </Lib>')

  def _WriteLinkerSection(self, project_configuration):
    """Writes the linker section.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine('    <Link>')

    # Visual Studio will convert an empty additional dependencies value.
    if project_configuration.additional_dependencies_set:
      additional_dependencies = ';'.join(
          sorted(project_configuration.additional_dependencies))

      additional_dependencies = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)', additional_dependencies)

      if additional_dependencies and additional_dependencies[-1] != ';':
        additional_dependencies = '{0:s};'.format(additional_dependencies)

      additional_dependencies = (
          '{0:s}%(AdditionalDependencies)').format(
              additional_dependencies)

      self.WriteLine((
          '      <AdditionalDependencies>{0:s}'
          '</AdditionalDependencies>').format(
              additional_dependencies))

    if project_configuration.linker_output_file:
      linker_output_file = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.linker_output_file)

      self.WriteLine('      <OutputFile>{0:s}</OutputFile>'.format(
          linker_output_file))

      if project_configuration.module_definition_file != '':
        self.WriteLine((
            '      <ModuleDefinitionFile>{0:s}'
            '</ModuleDefinitionFile>').format(
                project_configuration.module_definition_file))

    if project_configuration.library_directories:
      library_directories = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.library_directories)
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

    if project_configuration.generate_debug_information != '':
      self.WriteLine((
          '      <GenerateDebugInformation>{0:s}'
          '</GenerateDebugInformation>').format(
              project_configuration.generate_debug_information))

    if project_configuration.sub_system != '':
      self.WriteLine('      <SubSystem>{0:s}</SubSystem>'.format(
          project_configuration.sub_system_string))

    if project_configuration.optimize_references == '0':
      self.WriteLine('      <OptimizeReferences />')

    elif project_configuration.optimize_references != '':
      self.WriteLine((
          '      <OptimizeReferences>{0:s}</OptimizeReferences>').format(
              project_configuration.optimize_references_string))

    if project_configuration.enable_comdat_folding == '0':
      self.WriteLine('      <EnableCOMDATFolding />')

    elif project_configuration.enable_comdat_folding != '':
      self.WriteLine((
          '      <EnableCOMDATFolding>{0:s}</EnableCOMDATFolding>').format(
              project_configuration.enable_comdat_folding_string))

    if project_configuration.randomized_base_address != '':
      self.WriteLine((
          '      <RandomizedBaseAddress>{0:s}'
          '</RandomizedBaseAddress>').format(
              project_configuration.randomized_base_address_string))

    if project_configuration.fixed_base_address == '0':
      # A value of 0 is represented by an empty XML tag.
      self.WriteLine('      <FixedBaseAddress />')

    if project_configuration.data_execution_prevention != '':
      # A value of 0 is represented by an empty XML tag.
      if project_configuration.data_execution_prevention == '0':
        self.WriteLine('      <DataExecutionPrevention />')
      else:
        self.WriteLine((
            '      <DataExecutionPrevention>{0:s}'
            '</DataExecutionPrevention>').format(
                project_configuration.data_execution_prevention_string))

    if (project_configuration.target_machine != '' and
        project_configuration.linker_values_set):
      self.WriteLine('      <TargetMachine>{0:s}</TargetMachine>'.format(
          project_configuration.target_machine_string))

    if project_configuration.import_library:
      import_library = re.sub(
          r'[$][(]OutDir[)]\\', r'$(OutDir)',
          project_configuration.import_library)

      self.WriteLine('      <ImportLibrary>{0:s}</ImportLibrary>'.format(
          import_library))

    self.WriteLine('    </Link>')

  def _WriteItemDefinitionGroup(self, project_configuration):
    """Writes the item definition group.

    Args:
      project_configuration: the configuration (instance of
                             VSProjectConfiguration).
    """
    self.WriteLine((
        '  <ItemDefinitionGroup Condition="\'$(Configuration)|'
        '$(Platform)\'==\'{0:s}|{1:s}\'">').format(
            project_configuration.name, project_configuration.platform))

    # Write the compiler specific section.
    self._WriteClCompileSection(project_configuration)

    # Write the librarian specific section.
    if project_configuration.librarian_output_file:
      self._WriteLibrarianSection(project_configuration)

    # Write the linker specific section.
    if project_configuration.linker_values_set:
      self._WriteLinkerSection(project_configuration)

    self.WriteLine('  </ItemDefinitionGroup>')


class VS2013ProjectFileWriter(VS2010ProjectFileWriter):
  """Class to represent a Visual Studio 2013 project file writer."""

  def __init__(self):
    """Initializes a Visual Studio project file writer."""
    super(VS2013ProjectFileWriter, self).__init__()
    self._project_file_version = '12.0.21005.1'
    self._tools_version = '12.0'
    self._version = 2013


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
         '"{([0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*)}"'),
        line)

    if len(values) != 1:
      return None

    values = values[0]
    if len(values) != 3:
      return None

    solution_project = VSSolutionProject(values[0], values[1], values[2])

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
              ('{([0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*)} = '
               '{([0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*-[0-9A-F]*)}'),
              line)

          if len(guids) == 1:
            guids = guids[0]

            if len(guids) == 2 and guids[0] == guids[1]:
              solution_project.AddDependency(guids[0])

      elif line == 'ProjectSection(ProjectDependencies) = postProject':
        found_dependencies = True

    return solution_project

  def ReadProjects(self):
    """Reads the projects.

    Returns:
      A list containing the projects (instances of VSSolutionProject).
      The list is used to preserve the order of projects.
    """
    solution_projects = []
    solution_project = self.ReadProject()

    while solution_project:
      solution_projects.append(solution_project)
      solution_project = self.ReadProject()

    return solution_projects

  def ReadConfigurations(self):
    """Reads the configurations.

    Returns:
      The configurations (instance of VSConfigurations).
    """
    solution_configurations = VSConfigurations()

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
          values = re.findall('([^|]*)[|]([^ ]*) = ([^|]*)[|]([^ ]*)', line)

          if len(values) == 1:
            values = values[0]
            if (len(values) == 4 and values[0] == values[2] and
                values[1] == values[3]):
              configuration = VSSolutionConfiguration()
              configuration.name = values[0]
              configuration.platform = values[1]

              solution_configurations.Append(configuration)

      elif line == ('GlobalSection(SolutionConfigurationPlatforms) = '
                    'preSolution'):
        found_section = True

    return solution_configurations


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


class VS2012SolutionFileReader(object):
  """Class to represent a Visual Studio 2012 solution file reader."""
  # TODO: implement.


class VS2013SolutionFileReader(object):
  """Class to represent a Visual Studio 2013 solution file reader."""
  # TODO: implement.


class VSSolutionFileWriter(object):
  """Class to represent a Visual Studio solution file writer."""

  def __init__(self):
    """Initializes a Visual Studio project configuration."""
    super(VSSolutionFileWriter, self).__init__()
    self._file = None

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
  def WriteProject(self, solution_project):
    """Writes a project section.

    Args:
      solution_project: the project (instance of VSSolutionProject).
    """

  def WriteLine(self, line):
    """Writes a line."""
    self._file.write('{0:s}\r\n'.format(line))

  def WriteLines(self, lines):
    """Writes lines."""
    for line in lines:
      self.WriteLine(line)

  def WriteProjects(self, solution_projects):
    """Writes the projects.

    Args:
      solution_projects: a list containing the projects (instances of
                         VSSolutionProject).
    """
    for solution_project in solution_projects:
      self.WriteProject(solution_project)


class VS2008SolutionFileWriter(VSSolutionFileWriter):
  """Class to represent a Visual Studio 2008 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 10.00',
        '# Visual C++ Express 2008'])

  def WriteProject(self, solution_project):
    """Writes a project section.

    Args:
      solution_project: the project (instance of VSSolutionProject).
    """
    solution_project_filename = '{0:s}.vcproj'.format(
        solution_project.filename)

    self.WriteLine((
        'Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{0:s}", '
        '"{1:s}", "{{{2:s}}}"').format(
            solution_project.name, solution_project_filename,
            solution_project.guid.upper()))

    if len(solution_project.dependencies) > 0:
      self.WriteLine(
          '\tProjectSection(ProjectDependencies) = postProject')

      for dependency_guid in solution_project.dependencies:
        self.WriteLine('\t\t{{{0:s}}} = {{{0:s}}}'.format(
            dependency_guid.upper()))

      self.WriteLine('\tEndProjectSection')

    self.WriteLine('EndProject')

  def WriteConfigurations(self, solution_configurations, solution_projects):
    """Writes the configurations.

    Args:
      solution_configurations: the configurations (instance of
                               VSConfigurations).
      solution_projects: a list containing the projects (instances of
                         VSSolutionProject).
    """
    self.WriteLine('Global')

    if solution_configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution')

      for configuration_platform in sorted(solution_configurations.platforms):
        for configuration_name in sorted(solution_configurations.names):
          configuration = solution_configurations.GetByIdentifier(
              configuration_name, configuration_platform)

          self.WriteLine('\t\t{0:s}|{1:s} = {0:s}|{1:s}'.format(
              configuration.name, configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    if solution_configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution')

      for configuration_platform in sorted(solution_configurations.platforms):
        for solution_project in solution_projects:
          for configuration_name in sorted(solution_configurations.names):
            configuration = solution_configurations.GetByIdentifier(
                configuration_name, configuration_platform)

            self.WriteLine((
                '\t\t{{{0:s}}}.{1:s}|{2:s}.ActiveCfg = '
                '{1:s}|{2:s}').format(
                    solution_project.guid.upper(), configuration.name,
                    configuration.platform))
            self.WriteLine((
                '\t\t{{{0:s}}}.{1:s}|{2:s}.Build.0 = {1:s}|{2:s}').format(
                    solution_project.guid.upper(), configuration.name,
                    configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    self.WriteLines([
        '\tGlobalSection(SolutionProperties) = preSolution',
        '\t\tHideSolutionNode = FALSE',
        '\tEndGlobalSection',
        'EndGlobal'])


class VS2010SolutionFileWriter(VSSolutionFileWriter):
  """Class to represent a Visual Studio 2010 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 11.00',
        '# Visual C++ Express 2010'])

  def WriteProject(self, solution_project):
    """Writes a project section.

    Args:
      solution_project: the project (instance of VSSolutionProject).
    """
    solution_project_filename = '{0:s}.vcxproj'.format(
        solution_project.filename)

    self.WriteLine((
        'Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{0:s}", '
        '"{1:s}", "{{{2:s}}}"').format(
            solution_project.name, solution_project_filename,
            solution_project.guid.upper()))

    self.WriteLine('EndProject')

  def WriteConfigurations(self, solution_configurations, solution_projects):
    """Writes the configurations.

    Args:
      solution_configurations: the configurations (instance of
                               VSConfigurations).
      solution_projects: a list containing the projects (instances of
                         VSSolutionProject).
    """
    self.WriteLine('Global')

    if solution_configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution')

      for configuration_platform in sorted(solution_configurations.platforms):
        for configuration_name in sorted(solution_configurations.names):
          configuration = solution_configurations.GetByIdentifier(
              configuration_name, configuration_platform)

          self.WriteLine('\t\t{0:s}|{1:s} = {0:s}|{1:s}'.format(
              configuration.name, configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    if solution_configurations.number_of_configurations > 0:
      self.WriteLine(
          '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution')

      for configuration_platform in sorted(solution_configurations.platforms):
        for solution_project in solution_projects:
          for configuration_name in sorted(solution_configurations.names):
            configuration = solution_configurations.GetByIdentifier(
                configuration_name, configuration_platform)

            self.WriteLine((
                '\t\t{{{0:s}}}.{1:s}|{2:s}.ActiveCfg = {1:s}|{2:s}').format(
                    solution_project.guid.upper(), configuration.name,
                    configuration.platform))
            self.WriteLine((
                '\t\t{{{0:s}}}.{1:s}|{2:s}.Build.0 = {1:s}|{2:s}').format(
                    solution_project.guid.upper(), configuration.name,
                    configuration.platform))

      self.WriteLine('\tEndGlobalSection')

    self.WriteLines([
        '\tGlobalSection(SolutionProperties) = preSolution',
        '\t\tHideSolutionNode = FALSE',
        '\tEndGlobalSection',
        'EndGlobal'])


class VS2012SolutionFileWriter(VS2010SolutionFileWriter):
  """Class to represent a Visual Studio 2013 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 12.00',
        '# Visual Studio Express 2012 for Windows Desktop'])

  def WriteProject(self, solution_project):
    """Writes a project section.

    Args:
      solution_project: the project (instance of VSSolutionProject).
    """
    solution_project_filename = '{0:s}.vcxproj'.format(
        solution_project.filename)

    self.WriteLine((
        'Project("{{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}}") = "{0:s}", '
        '"{1:s}", "{{{2:s}}}"').format(
            solution_project.name, solution_project_filename,
            solution_project.guid.upper()))

    # TODO: what about:
    # '\tProjectSection(ProjectDependencies) = postProject'
    # '\t\t{%GUID%} = {%GUID}'
    # '\tEndProjectSection'

    self.WriteLine('EndProject')


class VS2013SolutionFileWriter(VS2010SolutionFileWriter):
  """Class to represent a Visual Studio 2013 solution file writer."""

  def WriteHeader(self):
    """Writes a file header."""
    self.WriteLines([
        '\xef\xbb\xbf',
        'Microsoft Visual Studio Solution File, Format Version 12.00',
        '# Visual Studio Express 2013 for Windows Desktop',
        'VisualStudioVersion = 12.0.21005.1'
        'MinimumVisualStudioVersion = 10.0.40219.1'])


class VSSolution(object):
  """Class to represent a Visual Studio solution."""

  def _ConvertProject(
      self, input_version, input_directory, output_version, solution_project,
      solution_projects_by_guid):
    """Converts a Visual Studio project.

    Args:
      input_version: the input version of the Visual Studio.
      input_directory: the path of the input directory.
      output_version: the output version of the Visual Studio.
      solution_project: the project (instance of VSSolutionProject).
      solution_projects_by_guid: a dictionary of the projects (instances of
                                 VSSolutionProject) with their GUID in lower
                                 case as the key.

    Returns:
      True if the conversion successful or False if not.
    """
    if not solution_project:
      return False

    input_project_filename = input_directory
    for path_segment in solution_project.filename.split('\\'):
      input_project_filename = os.path.join(
          input_project_filename, path_segment)

    # TODO: move logic into the reader?
    if input_version == '2008':
      input_project_filename = '{0:s}.vcproj'.format(input_project_filename)
    elif output_version in ['2010', '2012', '2013']:
      input_project_filename = '{0:s}.vcxproj'.format(input_project_filename)

    if not os.path.exists(input_project_filename):
      return False

    if input_version == '2008':
      project_reader = VS2008ProjectFileReader()
    elif input_version == '2010':
      project_reader = VS2010ProjectFileReader()
    elif input_version == '2012':
      project_reader = VS2012ProjectFileReader()
    elif input_version == '2013':
      project_reader = VS2013ProjectFileReader()

    logging.info('Reading: {0:s}'.format(input_project_filename))

    project_reader.Open(input_project_filename)

    if not project_reader.ReadHeader():
      return False

    project_information = project_reader.ReadProject()
    project_reader.Close()

    # Add x64 as a platform.
    project_information.configurations.ExtendWithX64(output_version)

    self._WriteProject(
        output_version, solution_project, project_information,
        solution_projects_by_guid)

    return True

  def _WriteProject(
      self, output_version, solution_project, project_information,
      solution_projects_by_guid):
    """Writes a Visual Studio project file.

    Args:
      output_version: the output version of the Visual Studio.
      solution_project: the project (instance of VSSolutionProject).
      project_information: the project information (instance of
                           VSProjectInformation).
      solution_projects_by_guid: a dictionary of the projects (instances of
                                 VSSolutionProject) with their GUID in lower
                                 case as the key.
    """
    output_directory = 'vs{0:s}'.format(output_version)
    output_project_filename = output_directory
    for path_segment in solution_project.filename.split('\\'):
      output_project_filename = os.path.join(
          output_project_filename, path_segment)

    # TODO: move logic into the writer?
    if output_version == '2008':
      output_project_filename = '{0:s}.vcproj'.format(output_project_filename)
    elif output_version in ['2010', '2012', '2013']:
      output_project_filename = '{0:s}.vcxproj'.format(output_project_filename)

    output_directory = os.path.dirname(output_project_filename)
    os.mkdir(output_directory)

    if output_version == '2008':
      project_writer = VS2008ProjectFileWriter()
    elif output_version == '2010':
      project_writer = VS2010ProjectFileWriter()
    elif output_version == '2012':
      project_writer = VS2012ProjectFileWriter()
    elif output_version == '2013':
      project_writer = VS2013ProjectFileWriter()

    logging.info('Writing: {0:s}'.format(output_project_filename))

    project_writer.Open(output_project_filename)
    project_writer.WriteHeader()
    project_writer.WriteProjectConfigurations(
        project_information.configurations)
    project_writer.WriteProjectInformation(project_information)
    project_writer.WriteConfigurations(project_information.configurations)
    project_writer.WriteFiles(
        project_information.source_files, project_information.header_files,
        project_information.resource_files)
    project_writer.WriteDependencies(
        solution_project.dependencies, solution_projects_by_guid)
    project_writer.WriteFooter()
    project_writer.Close()

  def _WriteSolution(
      self, solution_filename, output_version, solution_projects,
      solution_configurations):
    """Writes a Visual Studio solution file.

    Args:
      solution_filename: the Visual Studio solution filename.
      output_version: the output version of the Visual Studio.
      solution_projects: a list containing the projects (instances of
                         VSSolutionProject).
      solution_configurations: the configurations (instance of
                               VSConfigurations).
    """
    output_directory = 'vs{0:s}'.format(output_version)
    os.mkdir(output_directory)

    output_sln_filename = os.path.join(output_directory, solution_filename)

    logging.info('Writing: {0:s}'.format(output_sln_filename))

    if output_version == '2008':
      solution_writer = VS2008SolutionFileWriter()
    elif output_version == '2010':
      solution_writer = VS2010SolutionFileWriter()
    elif output_version == '2012':
      solution_writer = VS2012SolutionFileWriter()
    elif output_version == '2013':
      solution_writer = VS2013SolutionFileWriter()

    solution_writer.Open(output_sln_filename)
    solution_writer.WriteHeader()
    solution_writer.WriteProjects(solution_projects)
    solution_writer.WriteConfigurations(
        solution_configurations, solution_projects)
    solution_writer.Close()

  def Convert(self, input_sln_path, output_version):
    """Converts a Visual Studio solution.

    Args:
      input_sln_path: the path of the Visual Studio solution file.
      output_version: the output version of the Visual Studio.

    Returns:
      True if the conversion successful or False if not.
    """
    if not os.path.exists(input_sln_path):
      return False

    logging.info('Reading: {0:s}'.format(input_sln_path))

    # TODO: detect input version based on solution file reader?
    input_version = '2008'

    if input_version == '2008':
      solution_reader = VS2008SolutionFileReader()
    elif input_version == '2010':
      solution_reader = VS2010SolutionFileReader()
    elif input_version == '2012':
      solution_reader = VS2012SolutionFileReader()
    elif input_version == '2013':
      solution_reader = VS2013SolutionFileReader()

    solution_reader.Open(input_sln_path)

    if not solution_reader.ReadHeader():
      return False

    solution_projects = solution_reader.ReadProjects()
    solution_configurations = solution_reader.ReadConfigurations()
    solution_reader.Close()

    # Add x64 as a platform.
    solution_configurations.ExtendWithX64(output_version)

    solution_filename = os.path.basename(input_sln_path)
    self._WriteSolution(
        solution_filename, output_version, solution_projects,
        solution_configurations)

    input_directory = os.path.dirname(input_sln_path)

    solution_projects_by_guid = {}
    for solution_project in solution_projects:
      solution_projects_by_guid[solution_project.guid] = solution_project

    result = True
    for solution_project in solution_projects:
      result = self._ConvertProject(
          input_version, input_directory, output_version, solution_project,
          solution_projects_by_guid)
      if not result:
        break

    return result


class LibyalReleaseVSProjectConfiguration(VSProjectConfiguration):
  """Class to represent a libyal release VS project configuration."""

  def __init__(self):
    """Initializes a Visual Studio project configuration."""
    super(LibyalReleaseVSProjectConfiguration, self).__init__()

    self.name = 'Release'
    self.platform = 'Win32'
    self.character_set = '1'

    self.runtime_library = '2'
    # self.smaller_type_check = 'false'
    # self.precompiled_header = '0'
    self.warning_level = '4'
    # self.warning_as_error = 'false'
    self.compile_as = '1'

    self.target_machine = '1'


class LibyalDebugVSProjectConfiguration(VSProjectConfiguration):
  """Class to represent a libyal debug VS project configuration."""

  def __init__(self):
    """Initializes a Visual Studio project configuration."""
    super(LibyalDebugVSProjectConfiguration, self).__init__()

    self.name = 'VSDebug'
    self.platform = 'Win32'
    self.character_set = '1'

    self.optimization = '0'
    self.basic_runtime_checks = '3'
    self.smaller_type_check = 'true'
    self.runtime_library = '3'
    # self.precompiled_header = '0'
    self.warning_level = '4'
    # self.warning_as_error = 'false'
    self.debug_information_format = '3'
    self.compile_as = '1'

    self.target_machine = '1'


class LibyalSourceVSSolution(VSSolution):
  """Class to represent a libyal source Visual Studio solution generator."""

  _SUPPORTED_THIRD_PARTY_DEPENDENCIES = frozenset([
      'bzip2', 'dokan', 'zlib'])

  def _ConfigureAsBzip2Dll(
      self, project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as the bzip2 DLL.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    project_information.source_files = sorted([
        '..\\..\\..\\bzip2\\blocksort.c',
        '..\\..\\..\\bzip2\\bzlib.c',
        '..\\..\\..\\bzip2\\compress.c',
        '..\\..\\..\\bzip2\\crctable.c',
        '..\\..\\..\\bzip2\\decompress.c',
        '..\\..\\..\\bzip2\\huffman.c',
        '..\\..\\..\\bzip2\\randtable.c'])

    project_information.header_files = sorted([
        '..\\..\\..\\bzip2\\bzlib.h',
        '..\\..\\..\\bzip2\\bzlib_private.h'])

    include_directories = sorted([
        '..\\..\\..\\bzip2'])

    preprocessor_definitions = [
        'WIN32',
        'NDEBUG',
        '_WINDOWS',
        '_USRDLL',
        '_CRT_SECURE_NO_WARNINGS',
        'BZ_DLL']

    release_project_configuration.include_directories = ';'.join(
        include_directories)
    release_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    debug_project_configuration.include_directories = ';'.join(
        include_directories)
    debug_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    self._ConfigureAsDll(
        project_information, release_project_configuration,
        debug_project_configuration)

  def _ConfigureAsDll(
      self, project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as a DLL.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    if project_information.name.startswith('py'):
      dll_extension = 'pyd'
      library_directories = 'C:\\Python27\\libs'
    else:
      dll_extension = 'dll'
      library_directories = ''

    dll_filename = '$(OutDir)\\$(ProjectName).{0:s}'.format(dll_extension)
    lib_filename = '$(OutDir)\\$(ProjectName).lib'

    release_project_configuration.output_type = '2'
    release_project_configuration.linker_output_file = dll_filename
    release_project_configuration.library_directories = library_directories
    release_project_configuration.randomized_base_address = '2'
    release_project_configuration.data_execution_prevention = '2'
    release_project_configuration.import_library = lib_filename
    release_project_configuration.linker_values_set = True

    if project_information.name.endswith('.net'):
      release_project_configuration.compile_as = '2'
      release_project_configuration.managed_extensions = '1'

    debug_project_configuration.output_type = '2'
    debug_project_configuration.linker_output_file = dll_filename
    debug_project_configuration.library_directories = library_directories
    debug_project_configuration.generate_debug_information = 'true'
    debug_project_configuration.randomized_base_address = '1'
    debug_project_configuration.data_execution_prevention = '1'
    debug_project_configuration.import_library = lib_filename
    debug_project_configuration.linker_values_set = True

    if project_information.name.endswith('.net'):
      debug_project_configuration.compile_as = '2'
      debug_project_configuration.managed_extensions = '1'
      debug_project_configuration.basic_runtime_checks = ''
      debug_project_configuration.smaller_type_check = ''

  def _ConfigureAsDokanDll(
      self, project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as the dokan DLL.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    project_information.source_files = sorted([
        '..\\..\\..\\dokan\\dokan\\access.c',
        '..\\..\\..\\dokan\\dokan\\cleanup.c',
        '..\\..\\..\\dokan\\dokan\\close.c',
        '..\\..\\..\\dokan\\dokan\\create.c',
        '..\\..\\..\\dokan\\dokan\\directory.c',
        '..\\..\\..\\dokan\\dokan\\dokan.c',
        '..\\..\\..\\dokan\\dokan\\fileinfo.c',
        '..\\..\\..\\dokan\\dokan\\flush.c',
        '..\\..\\..\\dokan\\dokan\\lock.c',
        '..\\..\\..\\dokan\\dokan\\mount.c',
        '..\\..\\..\\dokan\\dokan\\read.c',
        '..\\..\\..\\dokan\\dokan\\security.c',
        '..\\..\\..\\dokan\\dokan\\setfile.c',
        '..\\..\\..\\dokan\\dokan\\status.c',
        '..\\..\\..\\dokan\\dokan\\timeout.c',
        '..\\..\\..\\dokan\\dokan\\version.c',
        '..\\..\\..\\dokan\\dokan\\volume.c',
        '..\\..\\..\\dokan\\dokan\\write.c'])

    project_information.header_files = sorted([
        '..\\..\\..\\dokan\\dokan\\dokan.h',
        '..\\..\\..\\dokan\\dokan\\dokanc.h',
        '..\\..\\..\\dokan\\dokan\\dokani.h',
        '..\\..\\..\\dokan\\dokan\\fileinfo.h',
        '..\\..\\..\\dokan\\dokan\\list.h'])

    include_directories = sorted([
        '..\\..\\..\\dokan\\sys\\'])

    preprocessor_definitions = [
        'WIN32',
        'NDEBUG',
        '_WINDOWS',
        '_USRDLL',
        '_CRT_SECURE_NO_WARNINGS',
        'DOKAN_DLL']

    module_definition_file = '..\\..\\..\\dokan\\dokan\\dokan.def'

    release_project_configuration.include_directories = ';'.join(
        include_directories)
    release_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)
    release_project_configuration.module_definition_file = (
        module_definition_file)

    debug_project_configuration.include_directories = ';'.join(
        include_directories)
    debug_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)
    debug_project_configuration.module_definition_file = (
        module_definition_file)

    self._ConfigureAsDll(
        project_information, release_project_configuration,
        debug_project_configuration)

  def _ConfigureAsExe(
      self, project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as an EXE.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    project_information.keyword = 'Win32Proj'

    release_project_configuration.output_type = '1'

    release_project_configuration.whole_program_optimization = '1'

    # release_project_configuration.precompiled_header = '0'

    release_project_configuration.link_incremental = '1'
    release_project_configuration.sub_system = '1'
    release_project_configuration.optimize_references = '2'
    release_project_configuration.enable_comdat_folding = '2'
    release_project_configuration.randomized_base_address = '2'
    release_project_configuration.data_execution_prevention = '2'
    release_project_configuration.target_machine = '1'
    release_project_configuration.linker_values_set = True

    debug_project_configuration.output_type = '1'

    # debug_project_configuration.precompiled_header = '0'

    debug_project_configuration.generate_debug_information = 'true'
    debug_project_configuration.link_incremental = '1'
    debug_project_configuration.sub_system = '1'
    debug_project_configuration.optimize_references = '2'
    debug_project_configuration.enable_comdat_folding = '2'
    debug_project_configuration.randomized_base_address = '1'
    debug_project_configuration.data_execution_prevention = '1'
    debug_project_configuration.target_machine = '1'
    debug_project_configuration.linker_values_set = True

  def _ConfigureAsLibrary(
      self, unused_project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as a local library.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    lib_filename = '$(OutDir)\\$(ProjectName).lib'

    release_project_configuration.output_type = '4'
    release_project_configuration.librarian_output_file = lib_filename
    release_project_configuration.librarian_ignore_defaults = 'false'

    debug_project_configuration.output_type = '4'
    debug_project_configuration.librarian_output_file = lib_filename
    debug_project_configuration.librarian_ignore_defaults = 'false'

  def _ConfigureAsZlibDll(
      self, project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project as the zlib DLL.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    project_information.source_files = sorted([
        '..\\..\\..\\zlib\\adler32.c',
        '..\\..\\..\\zlib\\compress.c',
        '..\\..\\..\\zlib\\crc32.c',
        '..\\..\\..\\zlib\\deflate.c',
        '..\\..\\..\\zlib\\gzclose.c',
        '..\\..\\..\\zlib\\gzlib.c',
        '..\\..\\..\\zlib\\gzread.c',
        '..\\..\\..\\zlib\\gzwrite.c',
        '..\\..\\..\\zlib\\infback.c',
        '..\\..\\..\\zlib\\inffast.c',
        '..\\..\\..\\zlib\\inflate.c',
        '..\\..\\..\\zlib\\inftrees.c',
        '..\\..\\..\\zlib\\trees.c',
        '..\\..\\..\\zlib\\uncompr.c',
        '..\\..\\..\\zlib\\zutil.c'])

    project_information.header_files = sorted([
        '..\\..\\..\\zlib\\crc32.h',
        '..\\..\\..\\zlib\\deflate.h',
        '..\\..\\..\\zlib\\gzguts.h',
        '..\\..\\..\\zlib\\inffast.h',
        '..\\..\\..\\zlib\\inffixed.h',
        '..\\..\\..\\zlib\\inflate.h',
        '..\\..\\..\\zlib\\inftrees.h',
        '..\\..\\..\\zlib\\trees.h',
        '..\\..\\..\\zlib\\zconf.h',
        '..\\..\\..\\zlib\\zlib.h',
        '..\\..\\..\\zlib\\zutil.h'])

    project_information.resource_files = sorted([
        '..\\..\\..\\zlib\\win32\\zlib1.rc'])

    include_directories = sorted([
        '..\\..\\..\\zlib'])

    preprocessor_definitions = [
        'WIN32',
        'NDEBUG',
        '_WINDOWS',
        '_USRDLL',
        '_CRT_SECURE_NO_WARNINGS',
        'ZLIB_DLL']

    release_project_configuration.include_directories = ';'.join(
        include_directories)
    release_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    debug_project_configuration.include_directories = ';'.join(
        include_directories)
    debug_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    self._ConfigureAsDll(
        project_information, release_project_configuration,
        debug_project_configuration)

  def _ConfigureLibcrypto(
      self, unused_project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project for the Windows libcrypto equivalent.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    dependency = 'advapi32.lib'

    if dependency not in release_project_configuration.additional_dependencies:
      release_project_configuration.additional_dependencies.append(dependency)

    if dependency not in debug_project_configuration.additional_dependencies:
      debug_project_configuration.additional_dependencies.append(dependency)

  def _ConfigureLibuuid(
      self, unused_project_information, release_project_configuration,
      debug_project_configuration):
    """Configures the project for the Windows libuuid equivalent.

    Args:
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    dependency = 'rpcrt4.lib'

    if dependency not in release_project_configuration.additional_dependencies:
      release_project_configuration.additional_dependencies.append(dependency)

    if dependency not in debug_project_configuration.additional_dependencies:
      debug_project_configuration.additional_dependencies.append(dependency)

  def _CreateThirdPartyDepencies(
      self, solution_projects, projects_by_guid, project_guids_by_name):
    """Creates the project files for third party dependencies.

    Args:
      solution_projects: a list containing the projects (instances of
                         VSSolutionProject).
      projects_by_guid: a dictionary of the projects (instances of
                        VSProjectInformation) with their GUID in lower case
                        as the key.
      project_guids_by_name: a dictionary of the project GUIDs in lower case
                             with their name as the key. This dictionary is
                             use as a lookup table to preserve the existing
                             GUIDs.
    """
    third_party_dependencies = []
    for project_information in projects_by_guid.itervalues():
      for dependency in project_information.third_party_dependencies:
        if dependency not in third_party_dependencies:
          third_party_dependencies.append(dependency)

    for project_name in third_party_dependencies:
      if project_name not in self._SUPPORTED_THIRD_PARTY_DEPENDENCIES:
        logging.info('Unsupported third party dependency: {0:s}'.format(
            project_name))
        continue

      project_filename = '{0:s}\\{0:s}'.format(project_name)

      project_guid = project_guids_by_name.get(project_name, '')
      if not project_guid:
        project_guid = project_guids_by_name.get(
            '{0:s}.dll'.format(project_name), '')
      if not project_guid:
        project_guid = str(uuid.uuid4())

      solution_project = VSSolutionProject(
          project_name, project_filename, project_guid)

      solution_projects.append(solution_project)

      project_information = VSProjectInformation()

      project_information.name = project_name
      project_information.guid = project_guid
      project_information.root_name_space = project_name

      release_project_configuration = LibyalReleaseVSProjectConfiguration()
      debug_project_configuration = LibyalDebugVSProjectConfiguration()

      if project_name == 'bzip2':
        self._ConfigureAsBzip2Dll(
            project_information, release_project_configuration,
            debug_project_configuration)

      elif project_name == 'dokan':
        self._ConfigureAsDokanDll(
            project_information, release_project_configuration,
            debug_project_configuration)

      elif project_name == 'zlib':
        self._ConfigureAsZlibDll(
            project_information, release_project_configuration,
            debug_project_configuration)

      project_information.configurations.Append(release_project_configuration)
      project_information.configurations.Append(debug_project_configuration)

      projects_by_guid[project_guid] = project_information

  def _ReadMakefile(
      self, makefile_am_path, solution_name, project_information,
      release_project_configuration, debug_project_configuration):
    """Reads the Makefile.am.

    Args:
      makefile_am_path: the path of the Makefile.am file.
      solution_name: the name of the solution.
      project_information: the project information (instance of
                           VSProjectInformation).
      release_project_configuration: the release project configuration (instance
                                     of LibyalReleaseVSProjectConfiguration).
      debug_project_configuration: the debug project configuration (instance
                                   of LibyalReleaseVSProjectConfiguration).
    """
    project_name = project_information.name

    file_object = open(makefile_am_path, 'r')

    include_directories = []
    preprocessor_definitions = []

    include_directories.append('\\'.join(['..', '..', 'include']))
    include_directories.append('\\'.join(['..', '..', 'common']))

    if (not project_name.startswith('lib') and
        not project_name.startswith('py') and
        not project_name.endswith('.net')):
      preprocessor_definitions.append('WIN32')
      preprocessor_definitions.append('NDEBUG')
      preprocessor_definitions.append('_CONSOLE')

    preprocessor_definitions.append('_CRT_SECURE_NO_DEPRECATE')

    alternate_dependencies = []
    dependencies = []
    source_files = []
    header_files = []
    resource_files = []

    in_am_cppflags_section = False
    in_extra_dist_section = False
    in_la_libadd_section = False
    in_la_sources_section = False
    in_ldadd_section = False
    in_sources_section = False

    for line in file_object.readlines():
      line = line.strip()

      if in_am_cppflags_section:
        if not line:
          in_am_cppflags_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          elif line.endswith('\\'):
            logging.warning(
                u'Detected missing space before \\ in line: ${0:s}'.format(
                    line))
            line = line[:-1]

          if line.startswith('@') and line.endswith('_CPPFLAGS@'):
            directory_name = line[1:-10].lower()
            if directory_name == 'bzip2':
              include_directories.append('..\\..\\..\\bzip2')

              preprocessor_definitions.append('BZ_DLL')

              alternate_dependencies.append('bzip2')

            elif directory_name == 'libfuse' and project_name.endswith('mount'):
              include_directories.append('..\\..\\..\\dokan\\dokan')

              preprocessor_definitions.append('HAVE_LIBDOKAN')

              alternate_dependencies.append('dokan')

            elif directory_name == 'zlib':
              include_directories.append('..\\..\\..\\zlib')

              preprocessor_definitions.append('ZLIB_DLL')

              alternate_dependencies.append('zlib')

            elif os.path.isdir(directory_name):
              include_directories.append(
                  '\\'.join(['..', '..', directory_name]))

              preprocessor_definitions.append(
                  'HAVE_LOCAL_{0:s}'.format(line[1:-10]))

              alternate_dependencies.append(directory_name)

      elif in_extra_dist_section:
        if not line:
          in_extra_dist_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          elif line.endswith('\\'):
            logging.warning(
                u'Detected missing space before \\ in line: ${0:s}'.format(
                    line))
            line = line[:-1]

          for filename in line.split(' '):
            if filename.endswith('.c') or filename.endswith('.cpp'):
              source_files.append('\\'.join([
                  '..', '..', project_name, filename]))

            elif filename.endswith('.h'):
              header_files.append('\\'.join([
                  '..', '..', project_name, filename]))

            elif filename.endswith('.rc'):
              resource_files.append('\\'.join([
                  '..', '..', project_name, filename]))

      elif in_la_libadd_section:
        if not line:
          in_la_libadd_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          if line in frozenset([
              'endif', '@LIBDL_LIBADD@', '@LIBINTL@', '@PTHREAD_LIBADD@']):
            dependency_name = ''
          elif line.startswith('@') and line.endswith('_LIBADD@'):
            dependency_name = line[1:-8].lower()
          elif line.endswith('.la'):
            _, _, dependency_name = line.rpartition('/')
            dependency_name = dependency_name[:-3]
          else:
            logging.warning(
                u'Unuspported dependency definition: {0:s}'.format(line))
            dependency_name = ''

          if dependency_name:
            if dependency_name == 'libcrypto':
              preprocessor_definitions.append('HAVE_WINCRYPT')

              self._ConfigureLibcrypto(
                  project_information, release_project_configuration,
                  debug_project_configuration)

            elif dependency_name == 'libuuid':
              self._ConfigureLibuuid(
                  project_information, release_project_configuration,
                  debug_project_configuration)

            else:
              dependencies.append(dependency_name)

      elif in_la_sources_section:
        if not line:
          in_la_sources_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          elif line.endswith('\\'):
            logging.warning(
                u'Detected missing space before \\ in line: ${0:s}'.format(
                    line))
            line = line[:-1]

          for filename in line.split(' '):
            if filename.endswith('.c') or filename.endswith('.cpp'):
              source_files.append('\\'.join([
                  '..', '..', project_name, filename]))

            elif filename.endswith('.h'):
              header_files.append('\\'.join([
                  '..', '..', project_name, filename]))

      elif in_ldadd_section:
        if not line:
          in_ldadd_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          if line in frozenset([
              'endif', '@LIBDL_LIBADD@', '@LIBINTL@', '@PTHREAD_LIBADD@']):
            dependency_name = ''
          elif line.startswith('@') and line.endswith('_LIBADD@'):
            dependency_name = line[1:-8].lower()
          elif line.endswith('.la'):
            _, _, dependency_name = line.rpartition('/')
            dependency_name = dependency_name[:-3]
          else:
            logging.warning(
                u'Unuspported dependency definition: {0:s}'.format(line))
            dependency_name = ''

          if dependency_name:
            if dependency_name == 'libcrypto':
              preprocessor_definitions.append('HAVE_WINCRYPT')

              self._ConfigureLibcrypto(
                  project_information, release_project_configuration,
                  debug_project_configuration)

            elif dependency_name == 'libfuse':
              dependencies.append('dokan')

            elif dependency_name == 'libuuid':
              self._ConfigureLibuuid(
                  project_information, release_project_configuration,
                  debug_project_configuration)

            else:
              dependencies.append(dependency_name)

      elif in_sources_section:
        if not line:
          in_sources_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          _, _, directory_name = os.path.dirname(
              makefile_am_path).rpartition(os.path.sep)

          for filename in line.split(' '):
            if filename.endswith('.c') or filename.endswith('.cpp'):
              source_files.append('\\'.join([
                  '..', '..', directory_name, filename]))

            elif filename.endswith('.h'):
              header_files.append('\\'.join([
                  '..', '..', directory_name, filename]))

      if line.startswith('AM_CFLAGS') or line.startswith('AM_CPPFLAGS'):
        in_am_cppflags_section = True

      elif line.startswith('{0:s}_la_LIBADD'.format(project_name)):
        in_la_libadd_section = True

      elif line.startswith('{0:s}_la_SOURCES'.format(project_name)):
        in_la_sources_section = True

      elif line.startswith('{0:s}_LDADD'.format(project_name)):
        in_ldadd_section = True

      elif line.startswith('{0:s}_SOURCES'.format(project_name)):
        in_sources_section = True

      elif line.startswith('EXTRA_DIST'):
        in_extra_dist_section = True

    file_object.close()

    if project_name in ('libcaes', 'libhmac'):
      preprocessor_definitions.append('HAVE_WINCRYPT')

    if project_name.endswith('.net'):
      dependencies.append(solution_name)

    if dependencies:
      project_information.dependencies = dependencies
    else:
      project_information.dependencies = alternate_dependencies

    if 'bzip2' in project_information.dependencies:
      project_information.third_party_dependencies.append('bzip2')

    if 'dokan' in project_information.dependencies:
      project_information.third_party_dependencies.append('dokan')

    if 'zlib' in project_information.dependencies:
      project_information.third_party_dependencies.append('zlib')

    if project_name == solution_name:
      preprocessor_definitions.append(
          '{0:s}_DLL_EXPORT'.format(project_name.upper()))

    elif project_name.startswith('lib'):
      preprocessor_definitions.append(
          'HAVE_LOCAL_{0:s}'.format(project_name.upper()))

    else:
      preprocessor_definitions.append(
          '{0:s}_DLL_IMPORT'.format(solution_name.upper()))

    if project_name.startswith('py'):
      include_directories.append('C:\\Python27\\include')

    release_project_configuration.include_directories = ';'.join(
        include_directories)
    release_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    debug_project_configuration.include_directories = ';'.join(
        include_directories)
    debug_project_configuration.preprocessor_definitions = ';'.join(
        preprocessor_definitions)

    if project_name.endswith('.net'):
      dependency = '{0:s}.lib'.format(solution_name)

      release_project_configuration.additional_dependencies.append(
          dependency)
      debug_project_configuration.additional_dependencies.append(
          dependency)

    project_information.source_files = sorted(source_files)
    project_information.header_files = sorted(header_files)
    project_information.resource_files = sorted(resource_files)

  def _ReadMakefilePrograms(self, makefile_am_path):
    """Reads the programs section in the Makefile.am.

    Args:
      makefile_am_path: the path of the Makefile.am file.

    Returns:
      A list containing the binary program names.
    """
    file_object = open(makefile_am_path, 'r')

    bin_programs = []

    in_bin_programs_section = False

    for line in file_object.readlines():
      line = line.strip()

      if in_bin_programs_section:
        if not line:
          in_bin_programs_section = False

        else:
          if line.endswith(' \\'):
            line = line[:-2]

          bin_programs.append(line)

      elif line.endswith('_PROGRAMS = \\'):
        in_bin_programs_section = True

    file_object.close()

    return bin_programs

  def Convert(self, input_directory, output_version):
    """Converts a Visual Studio solution.

    Args:
      input_directory: the path of the input directory.
      output_version: the output version of the Visual Studio.

    Returns:
      True if the conversion successful or False if not.
    """
    configure_ac_path = os.path.join(input_directory, 'configure.ac')
    if not os.path.exists(configure_ac_path):
      logging.warning(u'No such file: {0:s}.'.format(configure_ac_path))
      return False

    solution_name = None
    file_object = open(configure_ac_path, 'r')

    in_ac_init_section = False

    for line in file_object.readlines():
      line = line.strip()

      if in_ac_init_section:
        if line.startswith('[') and line.endswith('],'):
          solution_name = line[1:-2]
        break

      elif line.startswith('AC_INIT('):
        in_ac_init_section = True

    file_object.close()

    if not solution_name:
      logging.warning(u'Unable to determine solution name.')
      return False

    # Use the existing msvscpp solution file to determine the project
    # GUID so that they can be reused.
    project_guids_by_name = {}

    input_sln_path = os.path.join(
        input_directory, 'msvscpp', '{0:s}.sln'.format(solution_name))
    if os.path.exists(input_sln_path):
      solution_reader = VS2008SolutionFileReader()
      solution_reader.Open(input_sln_path)

      if not solution_reader.ReadHeader():
        return False

      solution_projects = solution_reader.ReadProjects()
      solution_reader.Close()

      for solution_project in solution_projects:
        project_guids_by_name[solution_project.name] = solution_project.guid

    solution_projects = []
    projects_by_guid = {}

    for directory_entry in os.listdir(input_directory):
      if not os.path.isdir(directory_entry):
        continue

      if (not directory_entry.startswith('lib') and
          not directory_entry.startswith('py') and
          not directory_entry == 'tests' and
          not directory_entry.endswith('.net') and
          not directory_entry.endswith('tools')):
        continue

      # Ignore the Python version specific build directories.
      if (directory_entry.startswith('py') and (
          directory_entry.endswith('2') or
          directory_entry.endswith('3'))):
        continue

      makefile_am_path = os.path.join(
          input_directory, directory_entry, 'Makefile.am')
      if not os.path.exists(makefile_am_path):
        logging.warning(u'No such file: {0:s}.'.format(makefile_am_path))
        continue

      if directory_entry == 'tests' or directory_entry.endswith('tools'):
        project_names = self._ReadMakefilePrograms(makefile_am_path)
      else:
        project_names = [directory_entry]

      for project_name in project_names:
        project_filename = '{0:s}\\{0:s}'.format(project_name)

        project_guid = project_guids_by_name.get(project_name, '')
        if not project_guid:
          project_guid = project_guids_by_name.get(
              '{0:s}.dll'.format(project_name), '')
        if not project_guid:
          project_guid = str(uuid.uuid4())

        solution_project = VSSolutionProject(
            project_name, project_filename, project_guid)

        solution_projects.append(solution_project)

        project_information = VSProjectInformation()
        project_information.name = project_name
        project_information.guid = project_guid
        project_information.root_name_space = project_name

        release_project_configuration = LibyalReleaseVSProjectConfiguration()
        debug_project_configuration = LibyalDebugVSProjectConfiguration()

        # TODO: determine autogenerated source.

        self._ReadMakefile(
            makefile_am_path, solution_name, project_information,
            release_project_configuration, debug_project_configuration)

        # TODO: add additional Python 3 project.

        if (project_name == solution_name or project_name.startswith('py') or
            project_name.endswith('.net')):
          self._ConfigureAsDll(
              project_information, release_project_configuration,
              debug_project_configuration)

        elif project_name.startswith('lib'):
          self._ConfigureAsLibrary(
              project_information, release_project_configuration,
              debug_project_configuration)

        else:
          self._ConfigureAsExe(
              project_information, release_project_configuration,
              debug_project_configuration)

        project_information.configurations.Append(release_project_configuration)
        project_information.configurations.Append(debug_project_configuration)

        projects_by_guid[project_guid] = project_information

    self._CreateThirdPartyDepencies(
        solution_projects, projects_by_guid, project_guids_by_name)

    # Set-up the solution configurations.
    solution_configurations = VSConfigurations()
    solution_configurations.Append(
        VSSolutionConfiguration(name='Release', platform='Win32'))
    solution_configurations.Append(
        VSSolutionConfiguration(name='VSDebug', platform='Win32'))

    if output_version not in ['2008']:
      # Add x64 as a platform.
      solution_configurations.ExtendWithX64(output_version)

    # Create some look-up dictionaries.
    solution_project_guids_by_name = {}
    solution_projects_by_guid = {}
    for solution_project in solution_projects:
      solution_project_guids_by_name[solution_project.name] = (
          solution_project.guid)
      solution_projects_by_guid[solution_project.guid] = solution_project

    # Set-up the solution dependencies.
    for guid, project_information in projects_by_guid.iteritems():
      solution_project = solution_projects_by_guid[guid]

      for dependency in project_information.dependencies:
        if dependency in ['pthread']:
          continue

        dependency_guid = solution_project_guids_by_name.get(dependency, '')
        if not dependency_guid:
          logging.info('Missing GUID for dependency: {0:s}'.format(dependency))

        solution_project.AddDependency(dependency_guid)

    solution_filename = '{0:s}.sln'.format(solution_name)
    self._WriteSolution(
        solution_filename, output_version, solution_projects,
        solution_configurations)

    for solution_project in solution_projects:
      project_information = projects_by_guid[solution_project.guid]
      self._WriteProject(
          output_version, solution_project, project_information,
          solution_projects_by_guid)

    # Create the corresponding Makefile.am
    solution_project_filenames = []
    for solution_project in solution_projects:
      if output_version in ['2008']:
        solution_project_extension = 'vcproj'
      else:
        solution_project_extension = 'vcxproj'

      path_segments = solution_project.filename.split('\\')
      solution_project_filenames.append('\t{0:s}.{1:s} \\'.format(
          os.path.join(*path_segments), solution_project_extension))

    makefile_am_lines = ['MSVSCPP_FILES = \\']
    for solution_project_filename in sorted(solution_project_filenames):
      makefile_am_lines.append(solution_project_filename)

    makefile_am_lines.append('\t{0:s}'.format(solution_filename))

    makefile_am_lines.extend([
        '',
        'SCRIPT_FILES = \\',
        '\tscripts/vs2008_x64.sh \\',
        '\tscripts/vs2008_x64_sln.sed \\',
        '\tscripts/vs2008_x64_vcproj.sed \\',
        '\tscripts/vs2010_x64.sh \\',
        '\tscripts/vs2010_x64_sln.sed \\',
        '\tscripts/vs2010_x64_vcxproj.sed',
        '',
        'EXTRA_DIST = \\',
        '\t$(MSVSCPP_FILES) \\',
        '\t$(SCRIPT_FILES)',
        '',
        'MAINTAINERCLEANFILES = \\',
        '\tMakefile.in',
        '',
        'distclean: clean',
        '\t/bin/rm -f Makefile',
        '',
        ''])

    filename = os.path.join('vs{0:s}'.format(output_version), 'Makefile.am')
    logging.info('Writing: {0:s}'.format(filename))

    makefile_am = open(filename, 'wb')
    makefile_am.write('\n'.join(makefile_am_lines))
    makefile_am.close()

    return True


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  output_formats = frozenset(['2008', '2010', '2012', '2013'])

  argument_parser = argparse.ArgumentParser(description=(
      'Converts source directory (autoconf and automake files) into '
      'Visual Studio express solution and project files. It is also '
      'possible to convert from one version of Visual Studio to another.'))

  argument_parser.add_argument(
      'solution_file', nargs='?', action='store', metavar='FILENAME',
      default=None, help=(
          'The location of the source directory or the Visual Studio solution '
          'file (.sln).'))

  argument_parser.add_argument(
      '--to', dest='output_format', nargs='?', choices=sorted(output_formats),
      action='store', metavar='FORMAT', default='2010',
      help='The format to convert to.')

  options = argument_parser.parse_args()

  if not options.solution_file:
    print('Solution file missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if options.output_format not in output_formats:
    print('Unsupported output format: {0:s}.'.format(options.format_to))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if os.path.isdir(options.solution_file):
    input_solution = LibyalSourceVSSolution()
  else:
    input_solution = VSSolution()

  if not input_solution.Convert(options.solution_file, options.output_format):
    print('Unable to convert Visual Studio solution file.')
    return False

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
