#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of source of the libyal libraries."""

from __future__ import print_function
import abc
import argparse
import json
import os
import string
import sys
import time

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class ProjectConfiguration(object):
  """Class that defines a project configuration."""

  def __init__(self):
    """Initializes a project configuation object."""
    super(ProjectConfiguration, self).__init__()
    self.project_authors = None
    self.project_copyright = None

    self.library_name = None
    self.library_description = None
    self.library_supports_codepage = None
    self.library_supports_notify = None

  def _GetConfigValue(self, config_parser, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      config_parser: the configuration parser (instance of ConfigParser).
      section_name: the name of the section that contains the value.
      value_name: the name of the value.

    Returns:
      An object containing the value.
    """
    return json.loads(config_parser.get(section_name, value_name))

  def ReadFromFile(self, filename):
    """Reads the configuration from file.

    Args:
      filename: a string containing the filename.
    """
    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.project_authors = self._GetConfigValue(
        config_parser, u'Project', u'authors')
    self.project_copyright = self._GetConfigValue(
        config_parser, u'Project', u'copyright')

    self.library_name = self._GetConfigValue(
        config_parser, u'Library', u'name')
    self.library_description = self._GetConfigValue(
        config_parser, u'Library', u'description')

    library_features = self._GetConfigValue(
        config_parser, u'Library', u'features')

    self.library_supports_codepage = u'codepage' in library_features
    self.library_supports_notify = u'notify' in library_features

  def GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      A dictionary containing the string template mappings.
    """
    # TODO: determine current year for copyright and rename attribute
    # to year_of_creation or equiv.
    template_mappings = {
        u'authors': u', '.join(self.project_authors),
        u'copyright': self.project_copyright,

        u'library_name': self.library_name,
        u'library_name_upper_case': self.library_name.upper(),
        u'library_description': self.library_description,
    }
    return template_mappings


class FunctionPrototype(object):
  """Class that defines a function prototype.

  Attributes:
    arguments: a list of strings containing the arguments.
    have_bfio: a boolean value to indicate the function prototype is defined
               if BFIO is defined.
    have_debug_output: a boolean value to indicate the function prototype
                       is defined if debug output is defined.
    have_wide_character_type: a boolean value to indicate the function
                              prototype is defined if the wide character
                              type is defined.
    name: a string containing the name.
    return_type: a string containing the return type.
  """

  def __init__(self, name, return_type):
    """Initializes a function prototype.

    Args:
      name: a string containing the name.
      return_type: a string containing the return type.
    """
    super(FunctionPrototype, self).__init__()
    self.arguments = []
    self.have_bfio = False
    self.have_debug_output = False
    self.have_wide_character_type = False
    self.name = name
    self.return_type = return_type

  def AddArgument(self, argument):
    """Adds an argument to the function prototype.

    Args:
      argument: a string containing the argument.
    """
    self.arguments.append(argument)


class IncludeHeaderFile(object):
  """Class that defines an include header file.

  Attributes:
    functions_per_sections: a dictionary of a list of function prototype objects
                            (instances of FunctionPrototype) per section.
    name: a string containing the name.
    section_names: a list of strings containing the section names.
  """

  def __init__(self, path):
    """Initializes an include header file.

    Args:
      path: a string containing the path.
    """
    super(IncludeHeaderFile, self).__init__()
    self._path = path

    self.name = os.path.basename(path)
    self.functions_per_section = {}
    self.section_names = []

  def ReadFunctions(self, project_configuration):
    """Reads the functions from the include header file.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      A boolean to indicate the functions were read from the file.
    """
    self.functions = []

    define_extern = b'{0:s}_EXTERN'.format(
        project_configuration.library_name.upper())

    define_have_bfio = b'#if defined( {0:s}_HAVE_BFIO )'.format(
        project_configuration.library_name.upper())

    define_have_debug_output = b'#if defined( HAVE_DEBUG_OUTPUT )'

    define_have_wide_character_type = (
        b'#if defined( {0:s}_HAVE_WIDE_CHARACTER_TYPE )').format(
            project_configuration.library_name.upper())

    function_prototype = None
    have_bfio = False
    have_debug_output = False
    have_wide_character_type = False
    in_define_extern = False
    in_section = False
    section_name = None
    with open(self._path, 'rb') as file_object:
      for line in file_object.readlines():
        line = line.strip()
        if in_define_extern:
          line = line.decode(u'ascii')

          if function_prototype:
            # Get the part of the line before the ','.
            argument, _, _ = line.partition(u',')

            if argument.endswith(u' );'):
              argument = argument[:-3]
            function_prototype.AddArgument(argument)

            if line.endswith(u' );'):
              self.functions_per_section[section_name].append(
                  function_prototype)
              function_prototype = None
              in_define_extern = False

          else:
            # Get the part of the line before the library name.
            return_type, _, _ = line.partition(
                project_configuration.library_name)

            # Get the part of the line after the return type.
            line = line[len(return_type):]
            return_type = return_type.strip()

            # Get the part of the remainder of the line before the '('.
            name, _, _ = line.partition(u'(')

            function_prototype = FunctionPrototype(name, return_type)
            function_prototype.have_bfio = have_bfio
            function_prototype.have_debug_output = have_debug_output
            function_prototype.have_wide_character_type = have_wide_character_type

        elif in_section:
          if line.startswith(b'* '):
            section_name = line[2:]
            self.section_names.append(section_name)
            self.functions_per_section[section_name] = []
            in_section = False

        elif line.startswith(define_extern):
          in_define_extern = True

        elif line == (
            b'/* -------------------------------------------------------------'
            b'------------'):
          in_section = True

        elif line.startswith(b'#endif'):
          have_bfio = False
          have_debug_output = False
          have_wide_character_type = False

        elif line.startswith(define_have_debug_output):
          have_debug_output = True

        elif line.startswith(define_have_bfio):
          have_bfio = True

        elif line.startswith(define_have_wide_character_type):
          have_wide_character_type = True

    return True


class SourceFileGenerator(object):
  """Class that generates source files."""

  def __init__(self, projects_directory, template_directory):
    """Initialize the source file generator.

    Args:
      projects_directory: a string containing the path of the projects
                          directory.
      template_directory: a string containing the path of the template
                          directory.
    """
    super(SourceFileGenerator, self).__init__()
    self._projects_directory = projects_directory
    self._template_directory = template_directory

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer,
      output_filename, access_mode='wb'):
    """Generates a section from template filename.

    Args:
      template_filename: a string containing the name of the template file.
      template_mpppings: a dictionary containing the template mappings, where
                         the key maps to the name of a template variable.
      output_writer: an output writer object (instance of OutputWriter).
      output_filename: string containing the name of the output file.
      access_mode: optional string containing the output file access mode.
    """
    template_string = self._ReadTemplateFile(template_filename)
    output_data = template_string.substitute(template_mappings)
    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename: string containing the name of the file containing
                the template string.

    Returns:
      A template string (instance of string.Template).
    """
    file_object = open(filename, 'rb')
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates the source file.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_writer: an output writer object (instance of OutputWriter).
    """


class CommonSourceFileGenerator(SourceFileGenerator):
  """Class that generates the common source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates common source files.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_writer: an output writer object (instance of OutputWriter).
    """
    template_mappings = project_configuration.GetTemplateMappings()
    for directory_entry in os.listdir(self._template_directory):
      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      output_filename = os.path.join(u'common', directory_entry)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class LibrarySourceFileGenerator(SourceFileGenerator):
  """Class that generates the library source files."""

  def Generate(self, project_configuration, output_writer):
    """Generates library source files.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_writer: an output writer object (instance of OutputWriter).
    """
    template_mappings = project_configuration.GetTemplateMappings()
    for directory_entry in os.listdir(self._template_directory):
      if not directory_entry.startswith(u'libyal_'):
        continue

      if not project_configuration.library_supports_codepage and (
        directory_entry.endswith(u'_codepage.h')):
        continue

      if not project_configuration.library_supports_notify and (
        directory_entry.endswith(u'_libcnotify.h') or
        directory_entry.endswith(u'_notify.c') or
        directory_entry.endswith(u'_notify.h')):
        continue

      template_filename = os.path.join(
          self._template_directory, directory_entry)
      if not os.path.isfile(template_filename):
        continue

      # TODO: generate types in _types.h from config.
      # TODO: generate _libX.h include headers from config.

      output_filename = u'{0:s}_{1:s}'.format(
          project_configuration.library_name, directory_entry[7:])
      output_filename = os.path.join(
          project_configuration.library_name, output_filename)

      self._GenerateSection(
          template_filename, template_mappings, output_writer, output_filename)


class LibraryManPageGenerator(SourceFileGenerator):
  """Class that generates the library man page file (libyal.3)."""

  def Generate(self, project_configuration, output_writer):
    """Generates a library man page file (libyal.3).

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_writer: an output writer object (instance of OutputWriter).
    """
    path = os.path.join(
        self._projects_directory, project_configuration.library_name,
        u'include', u'{0:s}.h'.format(project_configuration.library_name))

    include_header_file = IncludeHeaderFile(path)
    include_header_file.ReadFunctions(project_configuration)

    output_filename = u'{0:s}.3'.format(project_configuration.library_name)
    output_filename = os.path.join(u'manuals', output_filename)

    template_filename = os.path.join(self._template_directory, u'header.txt')
    template_mappings = project_configuration.GetTemplateMappings()
    template_mappings[u'date'] = time.strftime(
        u'%B %d, %Y').replace(u' 0', u'  ')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename)

    for section_name in include_header_file.section_names:
      section_template_mappings = {
          u'section_name': section_name,
      }
      template_filename = os.path.join(self._template_directory, u'section.txt')
      self._GenerateSection(
          template_filename, section_template_mappings, output_writer,
          output_filename, access_mode='ab')

      bfio_functions = []
      debug_output_functions = []
      functions = []
      wide_character_type_functions = []
      for function_prototype in include_header_file.functions_per_section.get(
          section_name, []):
        if function_prototype.have_bfio:
          bfio_functions.append(function_prototype)
        elif function_prototype.have_debug_output:
          debug_output_functions.append(function_prototype)
        elif function_prototype.have_wide_character_type:
          wide_character_type_functions.append(function_prototype)
        else:
          functions.append(function_prototype)

      for function_prototype in functions:
        function_template_mappings = {
            u'function_arguments': u', '.join(function_prototype.arguments),
            u'function_name': function_prototype.name,
            u'function_return_type': function_prototype.return_type,
        }
        template_filename = os.path.join(
            self._template_directory, u'function.txt')
        self._GenerateSection(
            template_filename, function_template_mappings, output_writer,
            output_filename, access_mode='ab')

      if wide_character_type_functions:
        section_template_mappings = {
            u'section_name': (
                u'Available when compiled with wide character string support:')
        }
        template_filename = os.path.join(self._template_directory, u'section.txt')
        self._GenerateSection(
            template_filename, section_template_mappings, output_writer,
            output_filename, access_mode='ab')

        for function_prototype in wide_character_type_functions:
          function_template_mappings = {
              u'function_arguments': u', '.join(function_prototype.arguments),
              u'function_name': function_prototype.name,
              u'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, u'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

      if bfio_functions:
        section_template_mappings = {
            u'section_name': (
                u'Available when compiled with libbfio support:')
        }
        template_filename = os.path.join(self._template_directory, u'section.txt')
        self._GenerateSection(
            template_filename, section_template_mappings, output_writer,
            output_filename, access_mode='ab')

        for function_prototype in bfio_functions:
          function_template_mappings = {
              u'function_arguments': u', '.join(function_prototype.arguments),
              u'function_name': function_prototype.name,
              u'function_return_type': function_prototype.return_type,
          }
          template_filename = os.path.join(
              self._template_directory, u'function.txt')
          self._GenerateSection(
              template_filename, function_template_mappings, output_writer,
              output_filename, access_mode='ab')

    template_filename = os.path.join(self._template_directory, u'footer.txt')
    self._GenerateSection(
        template_filename, template_mappings, output_writer, output_filename,
        access_mode='ab')


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, output_directory):
    """Initialize the output writer.

    Args:
      output_directory: string containing the path of the output directory.
    """
    super(FileWriter, self).__init__()
    self._output_directory = output_directory

  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to file.

    Args:
      file_path: string containing the path of the file to write.
      file_data: binary string containing the data to write.
      access_mode: optional string containing the output file access mode.
    """
    self._file_object = open(file_path, access_mode)
    self._file_object.write(file_data)
    self._file_object.close()


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self):
    """Initialize the output writer."""
    super(StdoutWriter, self).__init__()

  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      file_path: string containing the path of the file to write.
      file_data: binary string containing the data to write.
      access_mode: optional string containing the output file access mode.
    """
    print(u'-' * 80)
    print(u'{0: ^80}'.format(file_path))
    print(u'-' * 80)
    print(u'')
    print(file_data, end=u'')


def Main():
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates source files of the libyal libraries.'))

  argument_parser.add_argument(
      u'configuration_file', action=u'store', metavar=u'CONFIGURATION_FILE',
      default='source.conf', help=u'The source generation configuration file.')

  argument_parser.add_argument(
      u'-e', u'--experimental', dest=u'experimental', action=u'store_true',
      default=False, help=u'enable experimental functionality.')

  argument_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  argument_parser.add_argument(
      u'-p', u'--projects', dest=u'projects_directory', action=u'store',
      metavar=u'PROJECTS_DIRECTORY', default=None,
      help=u'path of the projects.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print(u'Config file missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  if not os.path.exists(options.configuration_file):
    print(u'No such configuration file: {0:s}.'.format(
        options.configuration_file))
    print(u'')
    return False

  if options.output_directory and not os.path.exists(options.output_directory):
    print(u'No such output directory: {0:s}.'.format(options.output_directory))
    print(u'')
    return False

  project_configuration = ProjectConfiguration()
  project_configuration.ReadFromFile(options.configuration_file)

  libyal_directory = os.path.abspath(__file__)
  libyal_directory = os.path.dirname(libyal_directory)
  libyal_directory = os.path.dirname(libyal_directory)

  projects_directory = options.projects_directory
  if not projects_directory:
    projects_directory = os.path.dirname(libyal_directory)

  # TODO: generate more source files.
  # configure.ac
  # common
  # include headers
  # pyyal files
  # yal.net files
  source_files = [
      (u'common', CommonSourceFileGenerator),
  ]
  if options.experimental:
    source_files.extend([
        (u'libyal', LibrarySourceFileGenerator),
    ])

  for page_name, page_generator_class in source_files:
    template_directory = os.path.join(
        libyal_directory, u'data', u'source', page_name)
    source_file = page_generator_class(
        projects_directory, template_directory)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  if not options.experimental:
    return True

  source_files = [
      (u'libyal.3', LibraryManPageGenerator),
  ]

  for page_name, page_generator_class in source_files:
    template_directory = os.path.join(
        libyal_directory, u'data', u'source', u'manuals', page_name)
    source_file = page_generator_class(
        projects_directory, template_directory)

    if options.output_directory:
      output_writer = FileWriter(options.output_directory)
    else:
      output_writer = StdoutWriter()

    source_file.Generate(project_configuration, output_writer)

  # TODO: add support for Unicode templates.

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
