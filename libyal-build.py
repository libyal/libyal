#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to automate creating builds of libyal libraries."""

import abc
import argparse
import fileinput
import glob
import io
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib2

try:
  import ConfigParser as configparser
except ImportError:
  import configparser  # pylint: disable=import-error


# Since os.path.abspath() uses the current working directory (cwd)
# os.path.abspath(__file__) will point to a different location if
# cwd has been changed. Hence we preserve the absolute location of __file__.
__file__ = os.path.abspath(__file__)


LIBYAL_LIBRARIES_CORE = frozenset([
    'libbfio',
    'libcdata',
    'libcdatetime',
    'libcdirectory',
    'libcerror',
    'libclocale',
    'libcnotify',
    'libcfile',
    'libcpath',
    'libcsplit',
    'libcstring',
    'libcsystem',
    'libcthreads',
])

LIBYAL_LIBRARIES_DATA_TYPES = frozenset([
    'libcaes',
    'libfcache',
    'libfdata',
    'libfdatetime',
    'libfguid',
    'libfmapi',
    'libfole',
    'libfusn',
    'libfvalue',
    'libfwevt',
    'libfwnt',
    'libfwsi',
    'libfwps',
    'libhmac',
    'libuna',
])


class ConfigError(Exception):
  """Class that defines a configuration error."""


class BuildConfiguration(object):
  """Class that contains the build configuration."""

  def __init__(self):
    """Initializes the project configuation."""
    super(BuildConfiguration, self).__init__()
    self.library_names = []

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
      filename: the configuration filename.
    """
    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()
    config_parser.read([filename])

    self.library_names = self._GetConfigValue(
        config_parser, 'libraries', 'names')


class DownloadHelper(object):
  """Class that helps in downloading."""

  def __init__(self):
    """Initializes the download helper."""
    super(DownloadHelper, self).__init__()
    self._cached_url = ''
    self._cached_page_content = ''

  def Download(self, project_name, project_version):
    """Downloads the project for a given project name and version.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      The filename if successful also if the file was already downloaded
      or None on error.
    """
    download_url = self.GetDownloadUrl(project_name, project_version)
    if not download_url:
      logging.warning(u'Unable to determine download URL for: {0:s}'.format(
          project_name))
      return

    return self.DownloadFile(download_url)

  def DownloadFile(self, download_url):
    """Downloads a file from the URL.

       The filename is extracted from the last part of the URL.

    Args:
      download_url: the URL where to download the file.

    Returns:
      The filename if successful also if the file was already downloaded
      or None on error.
    """
    _, _, filename = download_url.rpartition(u'/')

    if not os.path.exists(filename):
      logging.info(u'Downloading: {0:s}'.format(download_url))

      url_object = urllib2.urlopen(download_url)
      if url_object.code != 200:
        return

      file_object = open(filename, 'wb')
      file_object.write(url_object.read())
      file_object.close()

    return filename

  def DownloadPageContent(self, download_url):
    """Downloads the page content from the URL and caches it.

    Args:
      download_url: the URL where to download the page content.

    Returns:
      The page content if successful, None otherwise.
    """
    if not download_url:
      return

    if self._cached_url != download_url:
      url_object = urllib2.urlopen(download_url)

      if url_object.code != 200:
        return

      self._cached_page_content = url_object.read()
      self._cached_url = download_url

    return self._cached_page_content

  @abc.abstractmethod
  def GetDownloadUrl(self, project_name, project_version):
    """Retrieves the download URL for a given project name and version.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      The download URL of the project or None on error.
    """


class GithubReleasesDownloadHelper(DownloadHelper):
  """Class that helps in downloading a project with GitHub releases."""

  def __init__(self, organization):
    """Initializes the download helper.

    Args:
      organization: the github organization or user name.
    """
    super(GithubReleasesDownloadHelper, self).__init__()
    self.organization = organization

  def GetLatestVersion(self, project_name):
    """Retrieves the latest version number for a given project name.

    Args:
      project_name: the name of the project.

    Returns:
      The latest version number or 0 on error.
    """
    download_url = u'https://github.com/{0:s}/{1:s}/releases'.format(
        self.organization, project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return 0

    # The format of the project download URL is:
    # /{organization}/{project name}/releases/download/{git tag}/
    # {project name}{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = (
        u'/{0:s}/{1:s}/releases/download/[^/]*/{1:s}-[a-z-]*([0-9]+)'
        u'[.]tar[.]gz').format(self.organization, project_name)
    matches = re.findall(expression_string, page_content)

    if not matches:
      return 0

    return int(max(matches))

  def GetDownloadUrl(self, project_name, project_version):
    """Retrieves the download URL for a given project name and version.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      The download URL of the project or None on error.
    """
    download_url = u'https://github.com/{0:s}/{1:s}/releases'.format(
        self.organization, project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return

    # The format of the project download URL is:
    # /{organization}/{project name}/releases/download/{git tag}/
    # {project name}{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = (
        u'/{0:s}/{1:s}/releases/download/[^/]*/{1:s}-[a-z-]*{2!s}'
        u'[.]tar[.]gz').format(self.organization, project_name, project_version)
    matches = re.findall(expression_string, page_content)

    if len(matches) != 1:
      # Try finding a match without the status in case the project provides
      # multiple versions with a different status.
      expression_string = (
          u'/{0:s}/{1:s}/releases/download/[^/]*/{1:s}-*{2!s}'
          u'[.]tar[.]gz').format(
              self.organization, project_name, project_version)
      matches = re.findall(expression_string, page_content)

    if not matches or len(matches) != 1:
      return

    return u'https://github.com{0:s}'.format(matches[0])


class GoogleDriveDownloadHelper(DownloadHelper):
  """Class that helps in downloading a Google Drive hosted project."""

  @abc.abstractmethod
  def GetGoogleDriveDownloadsUrl(self, project_name):
    """Retrieves the Google Drive Download URL.

    Args:
      project_name: the name of the project.

    Returns:
      The downloads URL or None on error.
    """

  def GetLatestVersion(self, project_name):
    """Retrieves the latest version number for a given project name.

    Args:
      project_name: the name of the project.

    Returns:
      The latest version number or 0 on error.
    """
    download_url = self.GetGoogleDriveDownloadsUrl(project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return 0

    # The format of the project download URL is:
    # /host/{random string}/{project name}-{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = u'/host/[^/]*/{0:s}-[a-z-]*([0-9]+)[.]tar[.]gz'.format(
        project_name)
    matches = re.findall(expression_string, page_content)

    if not matches:
      return 0

    return int(max(matches))

  def GetDownloadUrl(self, project_name, project_version):
    """Retrieves the download URL for a given project name and version.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      The download URL of the project or None on error.
    """
    download_url = self.GetGoogleDriveDownloadsUrl(project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return

    # The format of the project download URL is:
    # /host/{random string}/{project name}-{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = u'/host/[^/]*/{0:s}-[a-z-]*{1!s}[.]tar[.]gz'.format(
        project_name, project_version)
    matches = re.findall(expression_string, page_content)

    if len(matches) != 1:
      # Try finding a match without the status in case the project provides
      # multiple versions with a different status.
      expression_string = u'/host/[^/]*/{0:s}-{1!s}[.]tar[.]gz'.format(
          project_name, project_version)
      matches = re.findall(expression_string, page_content)

    if not matches or len(matches) != 1:
      return

    return u'https://googledrive.com{0:s}'.format(matches[0])


# TODO: Merge with LibyalGithubReleasesDownloadHelper when Google Drive
# support is no longer needed.
class LibyalGitHubDownloadHelper(DownloadHelper):
  """Class that helps in downloading a libyal GitHub project."""

  def __init__(self):
    """Initializes the download helper."""
    super(LibyalGitHubDownloadHelper, self).__init__()
    self._download_helper = None

  def GetWikiConfigurationSourcePackageUrl(self, project_name):
    """Retrieves the source package URL from the libyal wiki configuration.

    Args:
      project_name: the name of the project.

    Returns:
      The source package URL or None on error.
    """
    download_url = (
        u'https://raw.githubusercontent.com/libyal/{0:s}/master/'
        u'{0:s}-wiki.ini').format(project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return

    # TODO: replace by:
    # config_parser = configparser. ConfigParser(interpolation=None)
    config_parser = configparser.RawConfigParser()
    config_parser.readfp(io.BytesIO(page_content))

    return json.loads(config_parser.get('source_package', 'url'))

  def GetLatestVersion(self, project_name):
    """Retrieves the latest version number for a given project name.

    Args:
      project_name: the name of the project.

    Returns:
      The latest version number or 0 on error.
    """
    if not self._download_helper:
      download_url = self.GetWikiConfigurationSourcePackageUrl(project_name)

      if download_url.startswith('https://github.com'):
        self._download_helper = LibyalGithubReleasesDownloadHelper()

      elif download_url.startswith('https://googledrive.com'):
        self._download_helper = LibyalGoogleDriveDownloadHelper(download_url)

    return self._download_helper.GetLatestVersion(project_name)

  def GetDownloadUrl(self, project_name, project_version):
    """Retrieves the download URL for a given project name and version.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      The download URL of the project or None on error.
    """
    if not self._download_helper:
      download_url = self.GetWikiConfigurationSourcePackageUrl(project_name)

      if download_url.startswith('https://github.com'):
        self._download_helper = LibyalGithubReleasesDownloadHelper()

      elif download_url.startswith('https://googledrive.com'):
        self._download_helper = LibyalGoogleDriveDownloadHelper(download_url)

    return self._download_helper.GetDownloadUrl(project_name, project_version)


class LibyalGoogleDriveDownloadHelper(GoogleDriveDownloadHelper):
  """Class that helps in downloading a libyal project with Google Drive."""

  def __init__(self, google_drive_url):
    """Initializes the download helper.

    Args:
      google_drive_url: the project Google Drive URL.
    """
    super(LibyalGoogleDriveDownloadHelper, self).__init__()
    self._google_drive_url = google_drive_url

  def GetGoogleDriveDownloadsUrl(self, project_name):
    """Retrieves the Download URL from the GitHub project page.

    Args:
      project_name: the name of the project.

    Returns:
      The downloads URL or None on error.
    """
    return self._google_drive_url


class LibyalGithubReleasesDownloadHelper(GithubReleasesDownloadHelper):
  """Class that helps in downloading a libyal project with GitHub releases."""

  def __init__(self):
    """Initializes the download helper."""
    super(LibyalGithubReleasesDownloadHelper, self).__init__('libyal')


class SourceHelper(object):
  """Base class that helps in managing the source code."""

  def __init__(self, project_name):
    """Initializes the source helper.

    Args:
      project_name: the name of the project.
    """
    super(SourceHelper, self).__init__()
    self.project_name = project_name

  @abc.abstractmethod
  def Create(self):
    """Creates the source directory.

    Returns:
      The name of the source directory if successful or None on error.
    """


class LibyalGitRepositoryHelper(SourceHelper):
  """Class that manages the source code from a git repository."""

  def Clean(self):
    """Removes a previous version of the source directory."""
    if os.path.exists(self.project_name):
      logging.info(u'Removing: {0:s}'.format(self.project_name))
      shutil.rmtree(self.project_name)

  def Create(self):
    """Creates the source directory from the git repository.

    Returns:
      The name of the source directory if successful or None on error.
    """
    if not self.project_name:
      return

    source_directory = self.project_name

    command = u'git clone https://github.com/libyal/{0:s}.git'.format(
        self.project_name)
    exit_code = subprocess.call(
        u'{0:s}'.format(command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return

    command = u'./synclibs.sh'
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return

    command = u'./autogen.sh'
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return

    command = u'./configure'
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return

    return source_directory


class SourcePackageHelper(SourceHelper):
  """Class that manages the source code from a source package."""

  ENCODING = 'utf-8'

  def __init__(self, project_name):
    """Initializes the source package helper.

    Args:
      project_name: the name of the project.
    """
    super(SourcePackageHelper, self).__init__(project_name)
    self._download_helper = LibyalGitHubDownloadHelper()
    self._project_version = None
    self._source_filename = None

  @property
  def project_version(self):
    """The project version."""
    if not self._project_version:
      self._project_version = self._download_helper.GetLatestVersion(
          self.project_name)
    return self._project_version

  def Clean(self):
    """Removes previous versions of source packages and directories."""
    if not self.project_version:
      return

    filenames_to_ignore = re.compile(
        u'^{0:s}-.*{1!s}'.format(self.project_name, self.project_version))

    # Remove previous versions of source packages in the format:
    # project-*.tar.gz
    filenames = glob.glob(u'{0:s}-*.tar.gz'.format(self.project_name))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove previous versions of source directories in the format:
    # project-{version}
    filenames = glob.glob(u'{0:s}-*'.format(self.project_name))
    for filename in filenames:
      if os.path.isdir(filename) and not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        shutil.rmtree(filename)

  def Create(self):
    """Creates the source directory from the source package.

    Returns:
      The name of the source directory if successful or None on error.
    """
    if not self._source_filename:
      _ = self.Download()

    if not self._source_filename or not os.path.exists(self._source_filename):
      return

    archive = tarfile.open(self._source_filename, 'r:gz', encoding='utf-8')
    directory_name = ''

    for tar_info in archive.getmembers():
      filename = getattr(tar_info, 'name', None)
      try:
        filename = filename.decode(self.ENCODING)
      except UnicodeDecodeError:
        logging.warning(
            u'Unable to decode filename in tar file: {0:s}'.format(
                self._source_filename))
        continue

      if filename is None:
        logging.warning(u'Missing filename in tar file: {0:s}'.format(
            self._source_filename))
        continue

      if not directory_name:
        # Note that this will set directory name to an empty string
        # if filename start with a /.
        directory_name, _, _ = filename.partition(u'/')
        if not directory_name or directory_name.startswith(u'..'):
          logging.error(
              u'Unsuppored directory name in tar file: {0:s}'.format(
                  self._source_filename))
          return
        if os.path.exists(directory_name):
          break
        logging.info(u'Extracting: {0:s}'.format(self._source_filename))

      elif not filename.startswith(directory_name):
        logging.warning(
            u'Skipping: {0:s} in tar file: {1:s}'.format(
                filename, self._source_filename))
        continue

      archive.extract(tar_info)
    archive.close()

    return directory_name

  def Download(self):
    """Downloads the source package.

    Returns:
      The filename of the source package if successful also if the file was
      already downloaded or None on error.
    """
    if not self._source_filename:
      if not self.project_version:
        return

      self._source_filename = self._download_helper.Download(
          self.project_name, self.project_version)

    return self._source_filename


class BuildHelper(object):
  """Base class that helps in building."""

  LOG_FILENAME = u'build.log'

  @abc.abstractmethod
  def Build(self, source_helper):
    """Builds the source.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """


class DpkgBuildHelper(BuildHelper):
  """Class that helps in building dpkg packages (.deb)."""

  # TODO: determine BUILD_DEPENDENCIES from the build files?
  # TODO: what about flex, byacc?
  _BUILD_DEPENDENCIES = frozenset([
      u'git',
      u'build-essential',
      u'autotools-dev',
      u'autoconf',
      u'automake',
      u'autopoint',
      u'libtool',
      u'gettext',
      u'flex',
      u'byacc',
      u'debhelper',
      u'devscripts',
      u'dpkg-dev',
      u'fakeroot',
      u'quilt',
      u'zlib1g-dev',
      u'libbz2-dev',
      u'libssl-dev',
      u'libfuse-dev',
      u'python-dev',
      u'python-setuptools',
  ])

  def _BuildPrepare(
      self, source_directory, project_name, project_version, version_suffix,
      distribution, architecture):
    """Make the necassary preperations before building the dpkg packages.

    Args:
      source_directory: the name of the source directory.
      project_name: the name of the project.
      project_version: the version of the project.
      version_suffix: the version suffix.
      distribution: the distribution.
      architecture: the architecture.

    Returns:
      True if the preparations were successful, False otherwise.
    """
    # Script to run before building, e.g. to change the dpkg packaging files.
    if os.path.exists(u'prep-dpkg.sh'):
      command = u'sh ../prep-dpkg.sh {0:s} {1!s} {2:s} {3:s} {4:s}'.format(
          project_name, project_version, version_suffix, distribution,
          architecture)
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

    return True

  def _BuildFinalize(
      self, source_directory, project_name, project_version, version_suffix,
      distribution, architecture):
    """Make the necassary finalizations after building the dpkg packages.

    Args:
      source_directory: the name of the source directory.
      project_name: the name of the project.
      project_version: the version of the project.
      version_suffix: the version suffix.
      distribution: the distribution.
      architecture: the architecture.

    Returns:
      True if the finalizations were successful, False otherwise.
    """
    # Script to run after building, e.g. to automatically upload the dpkg
    # package files to an apt repository.
    if os.path.exists(u'post-dpkg.sh'):
      command = u'sh ../post-dpkg.sh {0:s} {1!s} {2:s} {3:s} {4:s}'.format(
          project_name, project_version, version_suffix, distribution,
          architecture)
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

    return True

  @classmethod
  def CheckBuildDependencies(cls):
    """Checks if the build dependencies are met.

    Returns:
      A list of package names that need to be installed or an empty list.
    """
    missing_packages = []
    for package_name in cls._BUILD_DEPENDENCIES:
      if not cls.CheckIsInstalled(package_name):
        missing_packages.append(package_name)

    return missing_packages

  @classmethod
  def CheckIsInstalled(cls, package_name):
    """Checks if a package is installed.

    Args:
      package_name: the name of the package.

    Returns:
      A boolean value containing true if the package is installed
      false otherwise.
    """
    command = u'dpkg-query -l {0:s} >/dev/null 2>&1'.format(package_name)
    exit_code = subprocess.call(command, shell=True)
    return exit_code == 0


class LibyalDpkgBuildHelper(DpkgBuildHelper):
  """Class that helps in building libyal dpkg packages (.deb)."""

  def __init__(self):
    """Initializes the build helper."""
    super(LibyalDpkgBuildHelper, self).__init__()
    self.architecture = platform.machine()
    self.distribution = ''
    self.version_suffix = ''

    if self.architecture == 'i686':
      self.architecture = 'i386'
    elif self.architecture == 'x86_64':
      self.architecture = 'amd64'

  def Build(self, source_helper):
    """Builds the dpkg packages.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_filename = source_helper.Download()
    logging.info(u'Building deb of: {0:s}'.format(source_filename))

    # dpkg-buildpackage wants an source package filename without
    # the status indication and orig indication.
    deb_orig_source_filename = u'{0:s}_{1!s}.orig.tar.gz'.format(
        source_helper.project_name, source_helper.project_version)
    shutil.copy(source_filename, deb_orig_source_filename)

    source_directory = source_helper.Create()
    if not source_directory:
      logging.error(
          u'Extraction of source package: {0:s} failed'.format(source_filename))
      return False

    dpkg_directory = os.path.join(source_directory, u'dpkg')
    if not os.path.exists(dpkg_directory):
      dpkg_directory = os.path.join(source_directory, u'config', u'dpkg')

    if not os.path.exists(dpkg_directory):
      logging.error(u'Missing dpkg sub directory in: {0:s}'.format(
          source_directory))
      return False

    debian_directory = os.path.join(source_directory, u'debian')

    # If there is a debian directory remove it and recreate it from
    # the dpkg directory.
    if os.path.exists(debian_directory):
      logging.info(u'Removing: {0:s}'.format(debian_directory))
      shutil.rmtree(debian_directory)
    shutil.copytree(dpkg_directory, debian_directory)

    if not self._BuildPrepare(
        source_directory, source_helper.project_name,
        source_helper.project_version, self.version_suffix, self.distribution,
        self.architecture):
      return False

    command = u'dpkg-buildpackage -uc -us -rfakeroot > {0:s} 2>&1'.format(
        os.path.join(u'..', self.LOG_FILENAME))
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    if not self._BuildFinalize(
        source_directory, source_helper.project_name,
        source_helper.project_version, self.version_suffix, self.distribution,
        self.architecture):
      return False

    return True

  def Clean(self, source_helper):
    """Cleans the dpkg packages in the current directory.

    Args:
      source_helper: the source helper (instance of SourceHelper).
    """
    filenames_to_ignore = re.compile(u'^{0:s}_{1!s}.orig.tar.gz'.format(
        source_helper.project_name, source_helper.project_version))

    # Remove files of previous versions in the format:
    # project_version.orig.tar.gz
    filenames = glob.glob(
        u'{0:s}_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].orig.tar.gz'.format(
            source_helper.project_name, self.architecture))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    filenames_to_ignore = re.compile(u'^{0:s}[-_].*{1!s}'.format(
        source_helper.project_name, source_helper.project_version))

    # Remove files of previous versions in the format:
    # project[-_]version-1_architecture.*
    filenames = glob.glob(
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1_'
        u'{1:s}.*'.format(source_helper.project_name, self.architecture))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove files of previous versions in the format:
    # project[-_]*version-1.*
    filenames = glob.glob(
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1.*'.format(
            source_helper.project_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, source_helper):
    """Retrieves the filename of one of the resulting files.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      A filename of one of the resulting dpkg packages.
    """
    return u'{0:s}_{1!s}-1_{2:s}.deb'.format(
        source_helper.project_name, source_helper.project_version,
        self.architecture)


class LibyalSourceDpkgBuildHelper(DpkgBuildHelper):
  """Class that helps in building libyal source dpkg packages (.deb)."""

  def __init__(self):
    """Initializes the build helper."""
    super(LibyalSourceDpkgBuildHelper, self).__init__()
    self.architecture = 'source'
    self.distribution = 'trusty'
    self.version_suffix = 'ppa1'

  def Build(self, source_helper):
    """Builds the dpkg packages.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_filename = source_helper.Download()
    logging.info(u'Building source deb of: {0:s}'.format(source_filename))

    # dpkg-buildpackage wants an source package filename without
    # the status indication and orig indication.
    deb_orig_source_filename = u'{0:s}_{1!s}.orig.tar.gz'.format(
        source_helper.project_name, source_helper.project_version)
    shutil.copy(source_filename, deb_orig_source_filename)

    source_directory = source_helper.Create()
    if not source_directory:
      logging.error(
          u'Extraction of source package: {0:s} failed'.format(source_filename))
      return False

    dpkg_directory = os.path.join(source_directory, u'dpkg')
    if not os.path.exists(dpkg_directory):
      dpkg_directory = os.path.join(source_directory, u'config', u'dpkg')

    if not os.path.exists(dpkg_directory):
      logging.error(u'Missing dpkg sub directory in: {0:s}'.format(
          source_directory))
      return False

    debian_directory = os.path.join(source_directory, u'debian')

    # If there is a debian directory remove it and recreate it from
    # the dpkg directory.
    if os.path.exists(debian_directory):
      logging.info(u'Removing: {0:s}'.format(debian_directory))
      shutil.rmtree(debian_directory)
    shutil.copytree(dpkg_directory, debian_directory)

    if not self._BuildPrepare(
        source_directory, source_helper.project_name,
        source_helper.project_version, self.version_suffix, self.distribution,
        self.architecture):
      return False

    command = u'debuild -S -sa > {0:s} 2>&1'.format(
        os.path.join(u'..', self.LOG_FILENAME))
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    if not self._BuildFinalize(
        source_directory, source_helper.project_name,
        source_helper.project_version, self.version_suffix, self.distribution,
        self.architecture):
      return False

    return True

  def Clean(self, source_helper):
    """Cleans the dpkg packages in the current directory.

    Args:
      source_helper: the source helper (instance of SourceHelper).
    """
    filenames_to_ignore = re.compile(u'^{0:s}_{1!s}.orig.tar.gz'.format(
        source_helper.project_name, source_helper.project_version))

    # Remove files of previous versions in the format:
    # project_version.orig.tar.gz
    filenames = glob.glob(
        u'{0:s}_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].orig.tar.gz'.format(
            source_helper.project_name, self.architecture))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    filenames_to_ignore = re.compile(u'^{0:s}[-_].*{1!s}'.format(
        source_helper.project_name, source_helper.project_version))

    # Remove files of previous versions in the format:
    # project[-_]version-1suffix~distribution_architecture.*
    filenames = glob.glob((
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
        u'-1{1:s}~{2:s}_{3:s}.*').format(
            source_helper.project_name, self.version_suffix, self.distribution,
            self.architecture))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove files of previous versions in the format:
    # project[-_]*version-1suffix~distribution.*
    filenames = glob.glob((
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'
        u'-1{1:s}~{2:s}.*').format(
            source_helper.project_name, self.version_suffix, self.distribution))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, source_helper):
    """Retrieves the filename of one of the resulting files.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      A filename of one of the resulting dpkg packages.
    """
    return u'{0:s}_{1!s}-1{2:s}~{3:s}_{4:s}.changes'.format(
        source_helper.project_name, source_helper.project_version,
        self.version_suffix, self.distribution, self.architecture)


class MakeBuildHelper(BuildHelper):
  """Class that helps in building using make."""

  def Build(self, source_helper):
    """Builds the source using make.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_directory = source_helper.project_name

    command = u'./configure'
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    command = u'make'
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True


class MsiBuildHelper(BuildHelper):
  """Class that helps in building Microsoft Installer packages (.msi)."""

  LOG_FILENAME = u'msbuild.log'

  def __init__(self):
    """Initializes the build helper."""
    super(MsiBuildHelper, self).__init__()

    if self.architecture == 'x86':
      self.architecture = 'win32'
    elif self.architecture == 'AMD64':
      self.architecture = 'win-amd64'


class LibyalMsiBuildHelper(MsiBuildHelper):
  """Class that helps in building Microsoft Installer packages (.msi)."""

  def __init__(self):
    """Initializes the build helper.

    Raises:
      RuntimeError: if the Visual Studio version could be determined or
                    msvscpp-convert.py could not be found.
    """
    super(LibyalMsiBuildHelper, self).__init__()

    if 'VS90COMNTOOLS' in os.environ:
      self.version = '2008'

    elif 'VS100COMNTOOLS' in os.environ:
      self.version = '2010'

    elif 'VS110COMNTOOLS' in os.environ:
      self.version = '2012'

    elif 'VS120COMNTOOLS' in os.environ:
      self.version = '2013'

    else:
      raise RuntimeError(u'Unable to determine Visual Studio version.')

    if self.version != '2008':
      self._msvscpp_convert = os.path.join(
          os.path.dirname(__file__), u'msvscpp-convert.py')

      if not os.path.exists(self._msvscpp_convert):
        raise RuntimeError(u'Unable to find msvscpp-convert.py')

  def _BuildPrepare(self, source_directory):
    """Prepares the source for building with Visual Studio.

    Args:
      source_directory: the name of the source directory.
    """
    # For the vs2008 build make sure the binary is XP compatible,
    # by setting WINVER to 0x0501. For the vs2010 build WINVER is
    # set to 0x0600 (Windows Vista).

    # WINVER is set in common\config_winapi.h or common\config_msc.h.
    config_filename = os.path.join(
        source_directory, u'common', u'config_winapi.h')

    # If the WINAPI configuration file is not available use
    # the MSC compiler configuration file instead.
    if not os.path.exists(config_filename):
      config_filename = os.path.join(
          source_directory, u'common', u'config_msc.h')

    # Add a line to the config file that sets WINVER.
    parsing_mode = 0

    for line in fileinput.input(config_filename, inplace=1):
      # Remove trailing whitespace and end-of-line characters.
      line = line.rstrip()

      if parsing_mode != 2 or line:
        if parsing_mode == 1:
          if self.version == '2008':
            if not line.startswith('#define WINVER 0x0501'):
              print '#define WINVER 0x0501'
              print ''

          else:
            if not line.startswith('#define WINVER 0x0600'):
              print '#define WINVER 0x0600'
              print ''

          parsing_mode = 2

        elif line.startswith('#define _CONFIG_'):
          parsing_mode = 1

      print line

  def _ConvertSolutionFiles(self, source_directory):
    """Converts the Visual Studio solution and project files.

    Args:
      source_directory: the name of the source directory.
    """
    os.chdir(source_directory)

    solution_filenames = glob.glob(os.path.join(u'msvscpp', u'*.sln'))
    if len(solution_filenames) != 1:
      logging.error(u'Unable to find Visual Studio solution file')
      return False

    solution_filename = solution_filenames[0]

    if not os.path.exists(u'vs2008'):
      command = u'{0:s} {1:s} --to {2:s} {3:s}'.format(
          sys.executable, self._msvscpp_convert, self.version,
          solution_filename)
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      # Note that setup.py needs the Visual Studio solution directory
      # to be named: msvscpp. So replace the Visual Studio 2008 msvscpp
      # solution directory with the converted one.
      os.rename(u'msvscpp', u'vs2008')
      os.rename(u'vs{0:s}'.format(self.version), u'msvscpp')

    os.chdir(u'..')

  def Build(self, source_helper):
    """Builds using Visual Studio.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_filename = source_helper.Download()
    logging.info(u'Building: {0:s} with Visual Studio {1:s}'.format(
        source_filename, self.version))

    source_directory = source_helper.Create()
    if not source_directory:
      logging.error(
          u'Extraction of source package: {0:s} failed'.format(source_filename))
      return False

    # Search common locations for MSBuild.exe
    if self.version == '2008':
      msbuild = u'{0:s}:{1:s}{2:s}'.format(
          u'C', os.sep, os.path.join(
              u'Windows', u'Microsoft.NET', u'Framework', u'v3.5',
              u'MSBuild.exe'))

    # Note that MSBuild in .NET 3.5 does not support vs2010 solution files
    # and MSBuild in .NET 4.0 is needed instead.
    elif self.version in ['2010', '2012', '2013']:
      msbuild = u'{0:s}:{1:s}{2:s}'.format(
          u'C', os.sep, os.path.join(
              u'Windows', u'Microsoft.NET', u'Framework', u'v4.0.30319',
              u'MSBuild.exe'))

    if not os.path.exists(msbuild):
      logging.error(u'Unable to find MSBuild.exe')
      return False

    if self.version == '2008':
      if not os.environ['VS90COMNTOOLS']:
        logging.error(u'Missing VS90COMNTOOLS environment variable.')
        return False

    elif self.version == '2010':
      if not os.environ['VS100COMNTOOLS']:
        logging.error(u'Missing VS100COMNTOOLS environment variable.')
        return False

    elif self.version == '2012':
      if not os.environ['VS110COMNTOOLS']:
        logging.error(u'Missing VS110COMNTOOLS environment variable.')
        return False

    elif self.version == '2013':
      if not os.environ['VS120COMNTOOLS']:
        logging.error(u'Missing VS120COMNTOOLS environment variable.')
        return False

    # For the Visual Studio builds later than 2008 the convert the 2008
    # solution and project files need to be converted to the newer version.
    if self.version in ['2010', '2012', '2013']:
      self._ConvertSolutionFiles(source_directory)

    self._BuildPrepare(source_directory)

    # Detect architecture based on Visual Studion Platform environment
    # variable. If not set the platform with default to Win32.
    msvscpp_platform = os.environ.get('Platform', None)
    if not msvscpp_platform:
      msvscpp_platform = os.environ.get('TARGET_CPU', None)

    if not msvscpp_platform or msvscpp_platform == 'x86':
      msvscpp_platform = 'Win32'

    if msvscpp_platform not in ['Win32', 'x64']:
      logging.error(u'Unsupported build platform: {0:s}'.format(
          msvscpp_platform))
      return False

    if self.version == '2008' and msvscpp_platform == 'x64':
      logging.error(u'Unsupported 64-build platform for vs2008.')
      return False

    solution_filenames = glob.glob(os.path.join(
        source_directory, u'msvscpp', u'*.sln'))
    if len(solution_filenames) != 1:
      logging.error(u'Unable to find Visual Studio solution file')
      return False

    solution_filename = solution_filenames[0]

    command = (
        u'{0:s} /p:Configuration=Release /p:Platform={1:s} /noconsolelogger '
        u'/fileLogger /maxcpucount {2:s}').format(
            msbuild, msvscpp_platform, solution_filename)
    exit_code = subprocess.call(command, shell=False)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    python_module_name, _, _ = source_directory.partition(u'-')
    python_module_name = u'py{0:s}'.format(python_module_name[3:])
    python_module_directory = os.path.join(
        source_directory, python_module_name)
    python_module_dist_directory = os.path.join(
        python_module_directory, u'dist')

    if not os.path.exists(python_module_dist_directory):
      build_directory = os.path.join(u'..', u'..')

      os.chdir(python_module_directory)

      # Setup.py uses VS90COMNTOOLS which is vs2008 specific
      # so we need to set it for the other Visual Studio versions.
      if self.version == '2010':
        os.environ['VS90COMNTOOLS'] = os.environ['VS100COMNTOOLS']

      elif self.version == '2012':
        os.environ['VS90COMNTOOLS'] = os.environ['VS110COMNTOOLS']

      elif self.version == '2013':
        os.environ['VS90COMNTOOLS'] = os.environ['VS120COMNTOOLS']

      # TODO: append to log file?
      command = u'{0:s} setup.py bdist_msi'.format(sys.executable)
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      # Move the msi to the build directory.
      msi_filename = glob.glob(os.path.join(
          u'dist', u'{0:s}-*.msi'.format(python_module_name)))

      logging.info(u'Moving: {0:s}'.format(msi_filename[0]))
      shutil.move(msi_filename[0], build_directory)

      os.chdir(build_directory)

    return True

  def Clean(self, unused_source_helper):
    """Cleans the Visual Studio build directory.

    Args:
      source_helper: the source helper (instance of SourceHelper).
    """

  def GetOutputFilename(self, source_helper):
    """Retrieves the filename of one of the resulting files.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      A filename of one of the resulting build directory.
    """
    source_directory = u'{0:s}-{1!s}'.format(
        source_helper.project_name, source_helper.project_version)
    return os.path.join(source_directory, u'msvscpp', u'Release')


class PkgBuildHelper(BuildHelper):
  """Class that helps in building MacOS-X packages (.pkg)."""

  def __init__(self):
    """Initializes the build helper."""
    super(PkgBuildHelper, self).__init__()
    self._pkgbuild = os.path.join(u'/', u'usr', u'bin', u'pkgbuild')

  def _BuildDmg(self, pkg_filename, dmg_filename):
    """Builds the distributable disk image (.dmg) from the pkg.

    Args:
      pkg_filename: the name of the pkg file (which is technically
                    a directory).
      dmg_filename: the name of the dmg file.

    Returns:
      True if the build was successful, False otherwise.
    """
    command = (
        u'hdiutil create {0:s} -srcfolder {1:s} -fs HFS+').format(
            dmg_filename, pkg_filename)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True

  def _BuildPkg(
      self, source_directory, project_identifier, project_version,
      pkg_filename):
    """Builds the distributable disk image (.dmg) from the pkg.

    Args:
      source_directory: the name of the source directory.
      project_identifier: the project identifier.
      project_version: the version of the project.
      pkg_filename: the name of the pkg file (which is technically
                    a directory).

    Returns:
      True if the build was successful, False otherwise.
    """
    command = (
        u'{0:s} --root {1:s}/tmp/ --identifier {2:s} '
        u'--version {3!s} --ownership recommended {4:s}').format(
            self._pkgbuild, source_directory, project_identifier,
            project_version, pkg_filename)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True

  def Clean(self, source_helper):
    """Cleans the MacOS-X packages in the current directory.

    Args:
      source_helper: the source helper (instance of SourceHelper).
    """
    filenames_to_ignore = re.compile(u'^{0:s}-.*{1!s}'.format(
        source_helper.project_name, source_helper.project_version))

    # Remove files of previous versions in the format:
    # project-*version.dmg
    filenames = glob.glob(u'{0:s}-*.dmg'.format(source_helper.project_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove files of previous versions in the format:
    # project-*version.pkg
    filenames = glob.glob(u'{0:s}-*.pkg'.format(source_helper.project_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, source_helper):
    """Retrieves the filename of one of the resulting files.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      A filename of one of the resulting rpms.
    """
    return u'{0:s}-{1!s}.dmg'.format(
        source_helper.project_name, source_helper.project_version)


class LibyalPkgBuildHelper(PkgBuildHelper):
  """Class that helps in building MacOS-X packages (.pkg)."""

  def Build(self, source_helper):
    """Builds the pkg package and distributable disk image (.dmg).

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_filename = source_helper.Download()
    logging.info(u'Building pkg of: {0:s}'.format(source_filename))

    source_directory = source_helper.Create()
    if not source_directory:
      logging.error(
          u'Extraction of source package: {0:s} failed'.format(source_filename))
      return False

    dmg_filename = u'{0:s}-{1!s}.dmg'.format(
        source_helper.project_name, source_helper.project_version)
    pkg_filename = u'{0:s}-{1!s}.pkg'.format(
        source_helper.project_name, source_helper.project_version)
    log_filename = os.path.join(u'..', self.LOG_FILENAME)

    sdks_path = os.path.join(
        u'/', u'Applications', u'Xcode.app', u'Contents', u'Developer',
        u'Platforms', u'MacOSX.platform', u'Developer', u'SDKs')

    for sub_path in [u'MacOSX10.7.sdk', u'MacOSX10.8.sdk', u'MacOSX10.9.sdk']:
      sdk_path = os.path.join(sdks_path, sub_path)
      if os.path.isdir(sub_path):
        break

    if sdk_path:
      cflags = u'CFLAGS="-isysroot {0:s}"'.format(sdk_path)
      ldflags = u'LDFLAGS="-Wl,-syslibroot,{0:s}"'.format(sdk_path)
    else:
      cflags = u''
      ldflags = u''

    if not os.path.exists(pkg_filename):
      if cflags and ldflags:
        command = (
            u'{0:s} {1:s} ./configure --prefix=/usr --enable-python '
            u'--with-pyprefix --disable-dependency-tracking > {2:s} '
            u'2>&1').format(cflags, ldflags, log_filename)
      else:
        command = (
            u'./configure --prefix=/usr --enable-python --with-pyprefix '
            u'> {0:s} 2>&1').format(log_filename)

      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      command = u'make >> {0:s} 2>&1'.format(log_filename)
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      command = u'make install DESTDIR={0:s}/tmp >> {1:s} 2>&1'.format(
          os.path.abspath(source_directory), log_filename)
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      share_doc_path = os.path.join(
          source_directory, u'tmp', u'usr', u'share', u'doc',
          source_helper.project_name)
      if not os.path.exists(share_doc_path):
        os.makedirs(share_doc_path)

      shutil.copy(os.path.join(source_directory, u'AUTHORS'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'COPYING'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'NEWS'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'README'), share_doc_path)

      project_identifier = u'com.github.libyal.{0:s}'.format(
          source_helper.project_name)
      if not self._BuildPkg(
          source_directory, project_identifier, source_helper.project_version,
          pkg_filename):
        return False

    if not self._BuildDmg(pkg_filename, dmg_filename):
      return False

    return True


class RpmBuildHelper(BuildHelper):
  """Class that helps in building rpm packages (.rpm)."""

  # TODO: determine BUILD_DEPENDENCIES from the build files?
  _BUILD_DEPENDENCIES = frozenset([
      'git',
      'binutils',
      'autoconf',
      'automake',
      'libtool',
      'gettext-devel',
      'make',
      'pkgconfig',
      'gcc',
      'flex',
      'byacc',
      'zlib-devel',
      'bzip2-devel',
      'openssl-devel',
      'fuse-devel',
      'rpm-build',
      'python-devel',
  ])

  def __init__(self):
    """Initializes the build helper."""
    super(RpmBuildHelper, self).__init__()
    self.architecture = platform.machine()

    self.rpmbuild_path = os.path.join(u'~', u'rpmbuild')
    self.rpmbuild_path = os.path.expanduser(self.rpmbuild_path)

    self._rpmbuild_rpms_path = os.path.join(
        self.rpmbuild_path, u'RPMS', self.architecture)
    self._rpmbuild_sources_path = os.path.join(self.rpmbuild_path, u'SOURCES')
    self._rpmbuild_specs_path = os.path.join(self.rpmbuild_path, u'SPECS')

  def _BuildFromSpecFile(self, spec_filename):
    """Builds the rpms directly from a spec file.

    Args:
      spec_filename: the name of the spec file as stored in the rpmbuild
                     SPECS sub directory.

    Returns:
      True if the build was successful, False otherwise.
    """
    current_path = os.getcwd()
    os.chdir(self.rpmbuild_path)

    command = u'rpmbuild -ba {0:s} > {1:s} 2>&1'.format(
        os.path.join(u'SPECS', spec_filename), self.LOG_FILENAME)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))

    os.chdir(current_path)

    return exit_code == 0

  def _BuildFromSourcePackage(self, source_filename):
    """Builds the rpms directly from the source package file.

    For this to work the source package needs to contain a valid rpm .spec file.

    Args:
      source_filename: the name of the source package file.

    Returns:
      True if the build was successful, False otherwise.
    """
    command = u'rpmbuild -ta {0:s} > {1:s} 2>&1'.format(
        source_filename, self.LOG_FILENAME)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True

  def _CreateRpmbuildDirectories(self):
    """Creates the rpmbuild and sub directories."""
    if not os.path.exists(self.rpmbuild_path):
      os.mkdir(self.rpmbuild_path)

    if not os.path.exists(self._rpmbuild_sources_path):
      os.mkdir(self._rpmbuild_sources_path)

    if not os.path.exists(self._rpmbuild_specs_path):
      os.mkdir(self._rpmbuild_specs_path)

  def _CreateSpecFile(self, project_name, spec_file_data):
    """Creates a spec file in the rpmbuild directory.

    Args:
      project_name: the name of the project.
      spec_file_data: the spec file data.
    """
    spec_filename = os.path.join(
        self._rpmbuild_specs_path, u'{0:s}.spec'.format(project_name))

    spec_file = open(spec_filename, 'w')
    spec_file.write(spec_file_data)
    spec_file.close()

  def _CopySourceFile(self, source_filename):
    """Copies the source file to the rpmbuild directory.

    Args:
      source_filename: the name of the source package file.
    """
    shutil.copy(source_filename, self._rpmbuild_sources_path)

  def _MoveRpms(self, project_name, project_version):
    """Moves the rpms from the rpmbuild directory into to current directory.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.
    """
    filenames = glob.glob(os.path.join(
        self._rpmbuild_rpms_path, u'{0:s}-*{1!s}-1.{2:s}.rpm'.format(
            project_name, project_version, self.architecture)))
    for filename in filenames:
      logging.info(u'Moving: {0:s}'.format(filename))
      shutil.move(filename, '.')

  @classmethod
  def CheckBuildDependencies(cls):
    """Checks if the build dependencies are met.

    Returns:
      A list of package names that need to be installed or an empty list.
    """
    missing_packages = []
    for package_name in cls._BUILD_DEPENDENCIES:
      if not cls.CheckIsInstalled(package_name):
        missing_packages.append(package_name)

    return missing_packages

  @classmethod
  def CheckIsInstalled(cls, package_name):
    """Checks if a package is installed.

    Args:
      package_name: the name of the package.

    Returns:
      A boolean value containing true if the package is installed
      false otherwise.
    """
    command = u'rpm -qi {0:s} >/dev/null 2>&1'.format(package_name)
    exit_code = subprocess.call(command, shell=True)
    return exit_code == 0

  def Clean(self, source_helper):
    """Cleans the rpmbuild directory.

    Args:
      source_helper: the source helper (instance of SourceHelper).
    """
    # Remove previous versions build directories.
    filenames_to_ignore = re.compile(u'{0:s}-{1!s}'.format(
        source_helper.project_name, source_helper.project_version))

    filenames = glob.glob(os.path.join(
        self.rpmbuild_path, u'BUILD', u'{0:s}-*'.format(
            source_helper.project_name)))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        shutil.rmtree(filename)

    # Remove previous versions of rpms.
    filenames_to_ignore = re.compile(
        u'{0:s}-.*{1!s}-1.{2:s}.rpm'.format(
            source_helper.project_name, source_helper.project_version,
            self.architecture))

    rpm_filenames_glob = u'{0:s}-*-1.{1:s}.rpm'.format(
        source_helper.project_name, self.architecture)

    filenames = glob.glob(rpm_filenames_glob)
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    filenames = glob.glob(os.path.join(
        self.rpmbuild_path, u'RPMS', self.architecture, rpm_filenames_glob))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove previous versions of source rpms.
    filenames_to_ignore = re.compile(u'{0:s}-.*{1!s}-1.src.rpm'.format(
        source_helper.project_name, source_helper.project_version))

    filenames = glob.glob(os.path.join(
        self.rpmbuild_path, u'SRPMS',
        u'{0:s}-*-1.src.rpm'.format(source_helper.project_name)))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, source_helper):
    """Retrieves the filename of one of the resulting files.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      A filename of one of the resulting rpms.
    """
    return u'{0:s}-{1!s}-1.{2:s}.rpm'.format(
        source_helper.project_name, source_helper.project_version,
        self.architecture)


class LibyalRpmBuildHelper(RpmBuildHelper):
  """Class that helps in building libyal rpm packages (.rpm)."""

  def Build(self, source_helper):
    """Builds the rpms.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build was successful, False otherwise.
    """
    source_filename = source_helper.Download()
    logging.info(u'Building rpm of: {0:s}'.format(source_filename))

    # rpmbuild wants the source package filename without the status indication.
    rpm_source_filename = u'{0:s}-{1!s}.tar.gz'.format(
        source_helper.project_name, source_helper.project_version)
    os.rename(source_filename, rpm_source_filename)

    build_successful = self._BuildFromSourcePackage(rpm_source_filename)

    if build_successful:
      # Move the rpms to the build directory.
      self._MoveRpms(source_helper.project_name, source_helper.project_version)

      # Remove BUILD directory.
      filename = os.path.join(
          self.rpmbuild_path, u'BUILD', u'{0:s}-{1!s}'.format(
              source_helper.project_name, source_helper.project_version))
      logging.info(u'Removing: {0:s}'.format(filename))
      shutil.rmtree(filename)

      # Remove SRPMS file.
      filename = os.path.join(
          self.rpmbuild_path, u'SRPMS', u'{0:s}-{1!s}-1.src.rpm'.format(
              source_helper.project_name, source_helper.project_version))
      logging.info(u'Removing: {0:s}'.format(filename))
      os.remove(filename)

    # Change the source package filename back to the original.
    os.rename(rpm_source_filename, source_filename)

    return build_successful


class LibyalBuilder(object):
  """Class that helps in building libyal libaries."""

  def __init__(self, build_target):
    """Initializes the dependency builder.

    Args:
      build_target: the build target.
    """
    super(LibyalBuilder, self).__init__()
    self._build_target = build_target

  def _BuildLibyalLibrary(self, source_helper):
    """Builds a libyal project and its Python module.

    Args:
      source_helper: the source helper (instance of SourceHelper).

    Returns:
      True if the build is successful or False on error.
    """
    build_helper = None
    if self._build_target == 'dpkg':
      build_helper = LibyalDpkgBuildHelper()

    elif self._build_target == 'dpkg-source':
      build_helper = LibyalSourceDpkgBuildHelper()

    elif self._build_target == 'pkg':
      build_helper = LibyalPkgBuildHelper()

    elif self._build_target == 'rpm':
      build_helper = LibyalRpmBuildHelper()

    elif self._build_target in ['vs2008', 'vs2010', 'vs2012', 'vs2013']:
      if self._build_target == 'vs2013':
        logging.warning(u'Untested experimental build target: vs2013.')

      build_helper = LibyalMsiBuildHelper()

    if not build_helper:
      return False

    output_filename = build_helper.GetOutputFilename(source_helper)

    build_helper.Clean(source_helper)

    if not os.path.exists(output_filename):
      if not build_helper.Build(source_helper):
        logging.warning((
            u'Build of: {0:s} failed, for more information check '
            u'{1:s}').format(
                source_helper.project_name, build_helper.LOG_FILENAME))
        return False

    if os.path.exists(build_helper.LOG_FILENAME):
      logging.info(u'Removing: {0:s}'.format(build_helper.LOG_FILENAME))
      os.remove(build_helper.LOG_FILENAME)

    return True

  def Build(self, project_name):
    """Builds a libyal project.

    Args:
      project_name: the project name.

    Returns:
      True if the build is successful or False on error.
    """
    if self._build_target == 'download':
      source_helper = SourcePackageHelper(project_name)

      source_helper.Clean()

      source_filename = source_helper.Download()

      # If available run the script post-download.sh after download.
      if os.path.exists(u'post-download.sh'):
        command = u'sh ./post-download.sh {0:s}'.format(source_filename)
        exit_code = subprocess.call(command, shell=True)
        if exit_code != 0:
          logging.error(u'Running: "{0:s}" failed.'.format(command))
          return False

    elif self._build_target == 'git':
      source_helper = LibyalGitRepositoryHelper(project_name)

      source_helper.Clean()

      # TODO: build source.
      # source_directory = source_helper.Create()
      _ = source_helper.Create()

      build_helper = MakeBuildHelper()

      if not build_helper.Build(source_helper):
        logging.warning((
            u'Build of: {0:s} failed, for more information check '
            u'{1:s}').format(
                source_helper.project_name, build_helper.LOG_FILENAME))
        return False

    else:
      source_helper = SourcePackageHelper(project_name)

      source_helper.Clean()

      if not self._BuildLibyalLibrary(source_helper):
        return False

    return True


def Main():
  build_targets = frozenset([
      'download', 'dpkg', 'dpkg-source', 'git', 'pkg', 'rpm',
      'vs2008', 'vs2010', 'vs2012', 'vs2013'])

  args_parser = argparse.ArgumentParser(description=(
      'Downloads and builds the latest versions of the libyal libraries.'))

  args_parser.add_argument(
      'build_target', choices=sorted(build_targets), action='store',
      metavar='BUILD_TARGET', default=None, help='The build target.')

  args_parser.add_argument(
      '--build-directory', '--build_directory', action='store',
      metavar='DIRECTORY', dest='build_directory', type=unicode,
      default=u'.', help=(
          u'The location of the the build directory.'))

  args_parser.add_argument(
      '-c', '--config', dest='config_file', action='store',
      metavar='CONFIG_FILE', default=None,
      help='path of the build configuration file.')

  # TODO allow to set msbuild, python path
  # TODO allow to set dpkg version suffix and distribution.

  options = args_parser.parse_args()

  if not options.build_target:
    print 'Build target missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  if options.build_target not in build_targets:
    print 'Unsupported build target: {0:s}.'.format(options.build_target)
    print ''
    args_parser.print_help()
    print ''
    return False

  if not options.config_file:
    options.config_file = os.path.join(
        os.path.dirname(__file__), 'data', 'libraries.ini')

  if not os.path.exists(options.config_file):
    print u'No such config file: {0:s}.'.format(options.config_file)
    print u''
    return False

  build_configuration = BuildConfiguration()
  build_configuration.ReadFromFile(options.config_file)

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if options.build_target in ['dpkg', 'dpkg-source']:
    missing_packages = DpkgBuildHelper.CheckBuildDependencies()
    if missing_packages:
      print (u'Required build package(s) missing. Please install: '
             u'{0:s}.'.format(u', '.join(missing_packages)))
      print u''
      return False

  elif options.build_target == 'rpm':
    missing_packages = RpmBuildHelper.CheckBuildDependencies()
    if missing_packages:
      print (u'Required build package(s) missing. Please install: '
             u'{0:s}.'.format(u', '.join(missing_packages)))
      print u''
      return False

  libyal_builder = LibyalBuilder(options.build_target)

  if not os.path.exists(options.build_directory):
    os.mkdir(options.build_directory)

  current_working_directory = os.getcwd()
  os.chdir(options.build_directory)

  result = True
  for project_name in build_configuration.library_names:
    if not libyal_builder.Build(project_name):
      print u'Failed building: {0:s}'.format(project_name)
      result = False
      break

  os.chdir(current_working_directory)

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
