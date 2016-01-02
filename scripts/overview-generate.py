#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate generation of an overview of the libyal libraries."""

from __future__ import print_function
import argparse
import string
import os
import sys


class WikiPageGenerator(object):
  """Class that generates wiki pages."""

  def __init__(self, template_directory):
    """Initialize a wiki page generator.

    Args:
      template_directory: the path of the template directory.
    """
    super(WikiPageGenerator, self).__init__()
    self._template_directory = template_directory

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename: the name of the file containing the template string.

    Returns:
      A template string (instance of string.Template).
    """
    file_object = open(os.path.join(self._template_directory, filename))
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)

  def _GenerateSection(
      self, project_configuration, template_filename, output_writer):
    """Generates a section from template filename.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      template_filename: the name of the file containing the template string.
      output_write: the output writer.
    """
    template_string = self._ReadTemplateFile(template_filename)

    output_writer.Write(
        template_string.substitute(
            project_configuration.GetTemplateMappings()))

  @abc.abstractmethod
  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """

  @abc.abstractmethod
  def HasContent(self, project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """


class OverviewPageGenerator(WikiPageGenerator):
  """Class that generates the "Overview" wiki page."""

  # TODO: move to config file and determine categories based on per-project label
  CROSS_PLATFORM_LIBRARIES = [
      u'libcdata',
      u'libcdatetime',
      u'libcdirectory',
      u'libcerror',
      u'libcfile',
      u'libclocale',
      u'libcnotify',
      u'libcpath',
      u'libcsplit',
      u'libcstring',
      u'libcsystem',
      u'libcthreads']

  DATA_FORMAT_LIBRARIES = [
      u'libcaes',
      u'libfcache',
      u'libfdata',
      u'libfdatetime',
      u'libfguid',
      u'libfmapi',
      u'libfole',
      u'libftxf',
      u'libftxr',
      u'libfusn',
      u'libfvalue',
      u'libfwevt',
      u'libfwnt',
      u'libfwps',
      u'libfwsi',
      u'libhmac',
      u'libuna']

  FILE_FORMAT_LIBRARIES = [
      u'libagdb',
      u'libcreg',
      u'libesedb',
      u'libevt',
      u'libevtx',
      u'libexe',
      u'liblnk',
      u'libmdmp',
      u'libmsiecf',
      u'libnk2',
      u'libnsfdb',
      u'libolecf',
      u'libpff',
      u'libregf',
      u'libscca',
      u'libswf',
      u'libwtcdb']

  IN_FILE_FORMAT_LIBRARIES = [
      u'libmapidb',
      u'libwrc']

  FILE_SYSTEM_LIBRARIES = [
      u'libfsclfs',
      u'libfsext',
      u'libfshfs',
      u'libfsntfs',
      u'libfsrefs']

  VOLUME_SYSTEM_LIBRARIES = [
      u'libbde',
      u'libfvde',
      u'libluksde',
      u'libvshadow',
      u'libvslvm',
      u'libvsmbr']

  STORAGE_MEDIA_LIBRARIES = [
      u'libewf',
      u'libhibr',
      u'libodraw',
      u'libphdi',
      u'libqcow',
      u'libsmdev',
      u'libsmraw',
      u'libvdi',
      u'libvhdi',
      u'libvmdk']

  UTILITY_LIBRARIES = [
      u'libbfio',
      u'libsigscan']

  CATEGORIES = [
      (u'Cross-platform functionality',
       u'Several libraries for cross-platform C functions',
       CROSS_PLATFORM_LIBRARIES),
      (u'Data formats',
       u'Several libraries for different types of file format data',
       DATA_FORMAT_LIBRARIES),
      (u'File formats',
       u'Several libraries for different types of file formats',
       FILE_FORMAT_LIBRARIES),
      (u'In-file formats',
       u'Several libraries for different types of in-file formats',
       IN_FILE_FORMAT_LIBRARIES),
      (u'File system formats',
       u'Several libraries for different types of file systems',
       FILE_SYSTEM_LIBRARIES),
      (u'Volume (system) formats',
       u'Several libraries for different types of volume (system) formats',
       VOLUME_SYSTEM_LIBRARIES),
      (u'Storage media image formats',
       u'Several libraries for different types of storage media image formats',
       STORAGE_MEDIA_LIBRARIES),
      (u'Utility libraries',
       u'Several libraries for different "utility" functionality',
       UTILITY_LIBRARIES)]

  def Generate(self, project_configuration, output_writer):
    """Generates a wiki page.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).
      output_write: the output writer.
    """
    # TODO: replace project_configuration by template values?
    self._GenerateSection(
        project_configuration, u'introduction.txt', output_writer)

    for category in self.CATEGORIES:
      self._GenerateSection(
          project_configuration, u'category.txt', output_writer)

      for library in category[2]:
        project_name = u''
        project_description = u''
        appveyor_identifier = u''

        self._GenerateSection(
            project_configuration, u'library.txt', output_writer)

    self._GenerateSection(
        project_configuration, u'other.txt', output_writer)

  def HasContent(self, unused_project_configuration):
    """Determines if the generator will generate content.

    Args:
      project_configuration: the project configuration (instance of
                             ProjectConfiguration).

    Returns:
      Boolean value to indicate the generator will generate content.
    """
    return True


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initialize the output writer.

    Args:
      name: the name of the output.
    """
    super(FileWriter, self).__init__()
    self._file_object = None
    self._name = name

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    self._file_object = open(self._name, 'wb')
    return True

  def Close(self):
    """Closes the output writer object."""
    self._file_object.close()

  def Write(self, data):
    """Writes the data to file.

    Args:
      data: the data to write.
    """
    self._file_object.write(data)


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self):
    """Initialize the output writer."""
    super(StdoutWriter, self).__init__()

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    return

  def Write(self, data):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      data: the data to write.
    """
    print(data, end=u'')


def Main():
  args_parser = argparse.ArgumentParser(description=(
      u'Generates an overview of the libyal libraries.'))

  args_parser.add_argument(
      u'-o', u'--output', dest=u'output_directory', action=u'store',
      metavar=u'OUTPUT_DIRECTORY', default=None,
      help=u'path of the output files to write to.')

  options = args_parser.parse_args()

  if options.output_directory and not os.path.exists(options.output_directory):
    print(u'No such output directory: {0:s}.'.format(options.output_directory))
    print(u'')
    return False

  page_name = u'Overview'
  template_directory = os.path.join(
      script_directory, u'data', u'wiki', page_name)
  wiki_page = OverviewPageGenerator(template_directory)

  if not wiki_page.HasContent(project_configuration):
    continue

  filename = u'{0:s}.md'.format(page_name)

  if options.output_directory:
    output_file = os.path.join(options.output_directory, filename)
    output_writer = FileWriter(output_file)
  else:
    output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  wiki_page.Generate(project_configuration, output_writer)

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
