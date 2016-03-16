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
import time

# pylint: disable=import-error

# pylint: disable=wrong-import-order
try:
  import ConfigParser as configparser
except ImportError:
  import configparser

# pylint: disable=no-name-in-module
if sys.version_info[0] < 3:
  # Keep urllib2 here since we this code should be able to be used
  # by a default Python set up.
  import urllib2 as urllib_error
  from urllib2 import urlopen
else:
  import urllib.error as urllib_error
  from urllib.request import urlopen


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


class GithubIssueHelper(object):
  """Class that defines a github issue helper."""

  _KEYS = [
      u'number', u'state', u'created_at', u'assignee', u'milestone', u'labels',
      u'title', u'html_url']

  _LAST_PAGE_RE = re.compile(
      r'<(https://api.github.com/repositories/[0-9]+/issues\?'
      r'state=open&page=)([0-9]+)>; rel="last"')

  def __init__(self, organization):
    """Initialize the issue helper object.

    Args:
      organization: a string containing the name of the organization.
    """
    super(GithubIssueHelper, self).__init__()
    self._organization = organization

  def _DownloadPageContent(self, download_url):
    """Downloads the page content from the URL.

    Args:
      download_url: the URL where to download the page content.

    Returns:
      A tuple of a binary string containing the page content and
      a HTTP response message object containing the response headers
      (instance of HTTPMessage) if successful, None otherwise.
    """
    if not download_url:
      return None, None

    try:
      url_object = urlopen(download_url)
    except urllib_error.URLError as exception:
      logging.warning(
          u'Unable to download URL: {0:s} with error: {1:s}'.format(
              download_url, exception))
      return None, None

    if url_object.code != 200:
      logging.warning(
          u'Unable to download URL: {0:s} with status code: {1:d}'.format(
              download_url, url_object.code))
      return None, None

    return url_object.read(), url_object.info()

  def _ListIssuesForProject(self, project_name, output_writer):
    """Lists the issues of a specific project.

    Args:
      project_name: a string containing the name of the project.
      output_writer: an output writer object (instance of OutputWriter).
    """
    self._WaitForRateLimit()

    download_url = (
        u'https://api.github.com/repos/{0:s}/{1:s}/issues?state=open').format(
            self._organization, project_name)

    issues_data, response = self._DownloadPageContent(download_url)
    if not issues_data:
      return

    for issue_json in json.loads(issues_data):
      self._WriteIssue(project_name, issue_json, output_writer)

    if not response:
      logging.error(u'Missing HTTP response message.')
      return

    # Handle the multi-page response.
    link_header = response.getheader(u'Link')
    if not link_header:
      return

    matches = self._LAST_PAGE_RE.findall(link_header)
    if len(matches) != 1 and len(matches[0]) != 2:
      logging.error(u'Unsupported Link HTTP header: {0:s}'.format(
          link_header))
      return

    base_url = matches[0][0]

    try:
      last_page = int(matches[0][1], 10) + 1
    except ValueError:
      logging.error(u'Unsupported Link HTTP header: {0:s}'.format(
          link_header))
      return

    for page_number in range(2, last_page):
      self._WaitForRateLimit()

      download_url = u'{0:s}{1:d}'.format(base_url, page_number)
      issues_data, _ = self._DownloadPageContent(download_url)
      if not issues_data:
        logging.error(u'Missing issues page content: {0:s}'.format(
            download_url))
        continue

      for issue_json in json.loads(issues_data):
        self._WriteIssue(project_name, issue_json, output_writer)

  def _WaitForRateLimit(self):
    """Checks and waits for the rate limit."""
    download_url = u'https://api.github.com/rate_limit'

    remaining_count = 0
    while remaining_count == 0:
      rate_limit_data, _ = self._DownloadPageContent(download_url)
      if not rate_limit_data:
        logging.error(u'Missing rate limit page content.')
        return

      rate_limit_json = json.loads(rate_limit_data)

      rate_json = rate_limit_json.get(u'rate', None)
      if not rate_json:
        logging.error(u'Invalid rate limit information - missing rate.')
        return

      remaining_count = rate_json.get(u'remaining', None)
      if remaining_count is None:
        logging.error(u'Invalid rate limit information - missing remaining.')
        return

      reset_timestamp = rate_json.get(u'reset', None)
      if reset_timestamp is None:
        logging.error(u'Invalid rate limit information - missing reset.')
        return

      if remaining_count > 0:
        break

      current_timestamp = int(time.time())
      if current_timestamp > reset_timestamp:
        break

      reset_timestamp -= current_timestamp
      logging.info((
          u'Rate limiting calls to github API - sleeping for {0:d} '
          u'seconds.').format(reset_timestamp))
      time.sleep(reset_timestamp)

  def _WriteHeader(self, output_writer):
    """Writes a header to CSV.

    Args:
      output_writer: an output writer object (instance of OutputWriter).
    """
    csv_line = u'project:\t{0:s}\n'.format(
        u'\t'.join([u'{0:s}:'.format(key) for key in self._KEYS]))

    output_writer.Write(csv_line.decode(u'utf-8'))

  def _WriteIssue(self, project_name, issue_json, output_writer):
    """Writes an issue to CSV.

    Args:
      project_name: a string containing the name of the project.
      issue_json: a dictionary containing the JSON issue.
      output_writer: an output writer object (instance of OutputWriter).
    """
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

    csv_values = []
    for key in self._KEYS:
      csv_value = u''
      if key == u'assignee':
        assignee_json = issue_json[key]
        if assignee_json:
          csv_value = assignee_json[u'login']

      elif key == u'milestone':
        milestone_json = issue_json[key]
        if milestone_json:
          csv_value = milestone_json[u'title']

      elif key == u'labels':
        labels_json = issue_json[key]
        if labels_json:
          csv_value = u', '.join([
              label_json[u'name'] for label_json in labels_json])

      else:
        csv_value = u'{0!s}'.format(issue_json[key])

      csv_values.append(csv_value)

    csv_line = u'{0:s}\t{1:s}\n'.format(project_name, u'\t'.join(csv_values))

    output_writer.Write(csv_line.decode(u'utf-8'))

  def ListIssues(self, project_names, output_writer):
    """Lists the issues of projects.

    Args:
      project_names: a list of strings containing the names of the projects.
      output_writer: an output writer object (instance of OutputWriter).
    """
    self._WriteHeader(output_writer)

    for project_name in project_names:
      self._ListIssuesForProject(project_name, output_writer)

    output_writer.Write(u'\n'.decode(u'utf-8'))


class FileWriter(object):
  """Class that defines a file output writer."""

  def __init__(self, name):
    """Initializes an output writer object.

    Args:
      name: a string containing the name of the output.
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
    """Initializes an output writer object."""
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
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
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
    project_names = options.projects.split(u',')
  else:
    projects = projects_reader.ReadFromFile(options.configuration_file)
    if not projects:
      print(u'Unable to read projects from configuration file: {0:s}.'.format(
          options.configuration_file))
      print(u'')
      return False

    project_names = [project.name for project in projects]

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if options.output_file:
    output_writer = FileWriter(options.output_file)
  else:
    output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  issue_helper = GithubIssueHelper(u'libyal')
  issue_helper.ListIssues(project_names, output_writer)

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
