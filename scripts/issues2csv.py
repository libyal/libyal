#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to convert github.com issues into CSV."""

from __future__ import print_function
import argparse
import json
import logging
import os
import re
import sys

# pylint: disable=no-name-in-module
if sys.version_info[0] < 3:
  # Keep urllib2 here since we this code should be able to be used
  # by a default Python set up.
  import urllib2 as urllib_error
  from urllib2 import urlopen
else:
  import urllib.error as urllib_error
  from urllib.request import urlopen

# pylint: disable=wrong-import-order
try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


class Project(object):
  """Class that defines a project.

  Attributes:
    appveyor_identifier: a string containing the AppVeyor identifier.
    category: a string containing the category.
    description: a string containing the description.
    display_name: a string containing the display name.
    documentation_only: a boolean indicating if the project only contains
                        documentation.
    name: a string containing the name.
  """

  def __init__(self, name):
    """Initializes a project object.

    Args:
      name: a string containing the name.
    """
    super(Project, self).__init__()
    self.appveyor_identifier = None
    self.category = None
    self.description = None
    self.display_name = name
    self.documentation_only = False
    self.name = name


class ProjectsReader(object):
  """Class that defines a project reader."""

  def __init__(self):
    """Initializes a projects reader object."""
    super(ProjectsReader, self).__init__()
    # TODO: replace by:
    # self._config_parser = configparser. ConfigParser(interpolation=None)
    self._config_parser = configparser.RawConfigParser()

  def _GetConfigValue(self, section_name, value_name):
    """Retrieves a value from the config parser.

    Args:
      section_name: the name of the section that contains the value.
      value_name: the name of the value.

    Returns:
      An object containing the value.
    """
    return json.loads(self._config_parser.get(section_name, value_name))

  def ReadFromFile(self, filename):
    """Reads the projects from file.

    Args:
      filename: a string containing the filename.

    Returns:
      A list of project objects (instances of Project).
    """
    self._config_parser.read([filename])

    projects = []
    for project_name in self._config_parser.sections():
      project = Project(project_name)

      try:
        project.appveyor_identifier = self._GetConfigValue(
            project_name, u'appveyor_identifier')
      except configparser.NoOptionError:
        pass

      project.category = self._GetConfigValue(project_name, u'category')
      project.description = self._GetConfigValue(project_name, u'description')

      try:
        project.display_name = self._GetConfigValue(
            project_name, u'display_name')
      except configparser.NoOptionError:
        pass

      try:
        project.documentation_only = self._GetConfigValue(
            project_name, u'documentation_only')
      except configparser.NoOptionError:
        pass

      projects.append(project)

    return projects


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
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates an overview of open github issues of the libyal libraries.'))

  argument_parser.add_argument(
      u'configuration_file', action=u'store', metavar=u'CONFIGURATION_FILE',
      default=u'projects.ini', help=(
          u'The overview generation configuration file.'))

  argument_parser.add_argument(
      u'-o', u'--output', dest=u'output_file', action=u'store',
      metavar=u'OUTPUT_FILE', default=None, help=(
          u'path of the output file to write to.'))

  argument_parser.add_argument(
      u'-p', u'--projects', dest=u'projects', action=u'store',
      metavar=u'PROJECT_NAME(S)', default=None,
      help=u'comma separated list of specific project names to query.')

  options = argument_parser.parse_args()

  if not options.configuration_file:
    print(u'Configuration file missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  if not os.path.exists(options.configuration_file):
    print(u'No such configuration file: {0:s}.'.format(
        options.configuration_file))
    print(u'')
    return False

  projects_reader = ProjectsReader()

  if options.projects:
    project_names = options.projects
  else:
    projects = projects_reader.ReadFromFile(options.configuration_file)
    if not projects:
      print(u'Unable to read projects from configuration file: {0:s}.'.format(
          options.configuration_file))
      print(u'')
      return False

    project_names = [project.name for project in projects]

  if options.output_file:
    output_writer = FileWriter(options.output_file)
  else:
    output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  # https://developer.github.com/v3/issues/
  # Keys: {
  #   assignee: {
  #     login:
  #   }
  #   body:
  #   closed_at:
  #   comments:
  #   comments_url:
  #   created_at:
  #   events_url:
  #   html_url:
  #   id:
  #   labels: [{
  #     name:
  #   }]
  #   labels_url:
  #   locked:
  #   milestone: {
  #     title:
  #   }
  #   number:
  #   state:
  #   title:
  #   updated_at:
  #   url:
  #   user: {}
  # }

  keys = [
      u'number', u'state', u'created_at', u'assignee', u'milestone', u'labels',
      u'title', u'html_url']
  line = u'project:\t{0:s}\n'.format(
      u'\t'.join([u'{0:s}:'.format(key) for key in keys]))
  output_writer.Write(line.decode(u'utf-8'))

  organization = u'libyal'
  project_names = [u'libewf']

  organization = u'log2timeline'
  project_names = [u'plaso']

  last_page_re = re.compile(
      r'<(https://api.github.com/repositories/[0-9]+/issues\?'
      r'state=open&page=)([0-9]+)>; rel="last"')

  for project_name in project_names:
    # TODO: add rate limit support
    # https://api.github.com/rate_limit
    # "remaining": 58,
    # "reset": 1451996174
    #
    # Check if remaining hits 0 and wait until reset.

    url_object = urlopen((
        u'https://api.github.com/repos/{0:s}/{1:s}/issues?'
        u'state=open').format(organization, project_name))
    if not url_object or url_object.code != 200:
      logging.error(u'Unable to determine issues of project: {0:s}'.format(
          project_name))
      continue

    issues_data = url_object.read()
    if not issues_data:
      continue

    for issue_json in json.loads(issues_data):
      values = [u'{0!s}'.format(issue_json[key]) for key in keys]
      line = u'{0:s}\t{1:s}\n'.format(project_name, u'\t'.join(values))
      output_writer.Write(line.decode(u'utf-8'))

    # Handle the multi-page response.
    response = url_object.info()
    link_header = response.getheader(u'Link')
    if link_header:
      matches = last_page_re.findall(link_header)
      if len(matches) != 1 and len(matches[0]) != 2:
        # TODO print error.
        continue
      base_url = matches[0][0]
      last_page = int(matches[0][1], 10)

      page_number = 2
      while page_number < last_page:
        url = u'{0:s}{1:d}'.format(base_url, page_number)

        url_object = urlopen(url)
        if not url_object or url_object.code != 200:
          logging.error(u'Unable to determine issues of project: {0:s}'.format(
              project_name))
          continue

        issues_data = url_object.read()
        if not issues_data:
          continue

        for issue_json in json.loads(issues_data):
          # TODO: handle assignee, milestone, labels
          values = [u'{0!s}'.format(issue_json[key]) for key in keys]
          line = u'{0:s}\t{1:s}\n'.format(project_name, u'\t'.join(values))
          output_writer.Write(line.decode(u'utf-8'))

        page_number += 1

  output_writer.Write(u'\n'.decode(u'utf-8'))

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
