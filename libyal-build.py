#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to automate creating builds of libyal libraries.
#
# Copyright (c) 2013-2014, Joachim Metz <joachim.metz@gmail.com>
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

import abc
import argparse
import fileinput
import glob
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib2
from distutils import sysconfig


LIBYAL_LIBRARIES = frozenset([
    'libbde',
    'libesedb',
    'libevt',
    'libevtx',
    'libewf',
    'libexe',
    'libfwsi',
    'liblnk',
    'libmsiecf',
    'libolecf',
    'libpff',
    'libqcow',
    'libregf',
    'libsmdev',
    'libsmraw',
    'libvhdi',
    'libvmdk',
    'libvshadow',
    'libwrc',
])


class DownloadHelper(object):
  """Class that helps in downloading."""

  def __init__(self):
    """Initializes the build helper."""
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


class GoogleCodeDownloadHelper(DownloadHelper):
  """Class that helps in downloading a Google Code project."""

  def GetGoogleCodeDownloadsUrl(self, project_name):
    """Retrieves the Download URL from the Google Code project page.

    Args:
      project_name: the name of the project.

    Returns:
      The downloads URL or None on error.
    """
    download_url = u'https://code.google.com/p/{0:s}/'.format(project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return

    # The format of the project downloads URL is:
    # https://googledrive.com/host/{random string}/
    expression_string = (
        u'<a href="(https://googledrive.com/host/[^/]*/)"[^>]*>Downloads</a>')
    matches = re.findall(expression_string, page_content)

    if not matches or len(matches) != 1:
      return

    return matches[0]

  def GetLatestVersion(self, project_name):
    """Retrieves the latest version number for a given project name.

    Args:
      project_name: the name of the project.

    Returns:
      The latest version number or 0 on error.
    """
    download_url = self.GetGoogleCodeDownloadsUrl(project_name)

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
    download_url = self.GetGoogleCodeDownloadsUrl(project_name)

    page_content = self.DownloadPageContent(download_url)
    if not page_content:
      return

    # The format of the project download URL is:
    # /host/{random string}/{project name}-{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = u'/host/[^/]*/{0:s}-[a-z-]*{1:d}[.]tar[.]gz'.format(
        project_name, project_version)
    matches = re.findall(expression_string, page_content)

    if len(matches) != 1:
      # Try finding a match without the status in case the project provides
      # multiple versions with a different status.
      expression_string = u'/host/[^/]*/{0:s}-{1:d}[.]tar[.]gz'.format(
          project_name, project_version)
      matches = re.findall(expression_string, page_content)

    if not matches or len(matches) != 1:
      return

    return u'https://googledrive.com{0:s}'.format(matches[0])


class BuildHelper(object):
  """Base class that helps in building."""

  LOG_FILENAME = u'build.log'

  def __init__(self):
    """Initializes the build helper."""
    super(BuildHelper, self).__init__()

  def Extract(self, source_filename):
    """Extracts the given source filename.

    Args:
      source_filename: the name of the source package file.

    Returns:
      The name of the directory the files were extracted to if successful
      or None on error.
    """
    if not source_filename or not os.path.exists(source_filename):
      return

    archive = tarfile.open(source_filename, 'r:gz', encoding='utf-8')
    directory_name = ''

    for tar_info in archive.getmembers():
      filename = getattr(tar_info, 'name', None)
      if filename is None:
        logging.warning(
            u'Missing filename in tar file: {0:s}'.format(source_filename))
        continue

      if not directory_name:
        # Note that this will set directory name to an empty string
        # if filename start with a /.
        directory_name, _, _ = filename.partition(u'/')
        if not directory_name or directory_name.startswith(u'..'):
          logging.error(
              u'Unsuppored directory name in tar file: {0:s}'.format(
                  source_filename))
          return
        if os.path.exists(directory_name):
          break
        logging.info(u'Extracting: {0:s}'.format(source_filename))

      elif not filename.startswith(directory_name):
        logging.warning(
            u'Skipping: {0:s} in tar file: {1:s}'.format(
                filename, source_filename))
        continue

      archive.extract(tar_info)
    archive.close()

    return directory_name


class DpkgBuildHelper(BuildHelper):
  """Class that helps in building dpkg packages (.deb)."""

  def __init__(self):
    """Initializes the build helper."""
    super(DpkgBuildHelper, self).__init__()

  def _BuildPrepare(self, source_directory):
    """Make the necassary preperations before building the dpkg packages.

    Args:
      source_directory: the name of the source directory.

    Returns:
      True if the preparations were successful, False otherwise.
    """
    # Script to run before building, e.g. to change the dpkg packing files.
    if os.path.exists(u'prep-dpkg.sh'):
      command = u'sh ../prep-dpkg.sh'
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

    return True

  def _BuildFinalize(self, source_directory):
    """Make the necassary finalizations after building the dpkg packages.

    Args:
      source_directory: the name of the source directory.

    Returns:
      True if the finalizations were successful, False otherwise.
    """
    # Script to run after building, e.g. to automatically upload the dpkg
    # package files to an apt repository.
    if os.path.exists(u'post-dpkg.sh'):
      command = u'sh ../post-dpkg.sh'
      exit_code = subprocess.call(
          u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

    return True

  def Build(self, source_filename):
    """Builds the dpkg packages.

    Args:
      source_filename: the name of the source package file.

    Returns:
      True if the build was successful, False otherwise.
    """
    source_directory = self.Extract(source_filename)
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

    if not self._BuildPrepare(source_directory):
      return False

    command = u'dpkg-buildpackage -rfakeroot > {0:s} 2>&1'.format(
        os.path.join(u'..', self.LOG_FILENAME))
    exit_code = subprocess.call(
        u'(cd {0:s} && {1:s})'.format(source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    if not self._BuildFinalize(source_directory):
      return False

    return True


class LibyalDpkgBuildHelper(DpkgBuildHelper):
  """Class that helps in building libyal dpkg packages (.deb)."""

  # TODO: determine BUILD_DEPENDENCIES from spec files?
  BUILD_DEPENDENCIES = frozenset([
      'build-essential',
      'autoconf',
      'automake',
      'autopoint',
      'libtool',
      'gettext',
      'debhelper',
      'fakeroot',
      'quilt',
      'autotools-dev',
      'zlib1g-dev',
      'libssl-dev',
      'libfuse-dev',
      'python-dev',
      'python-setuptools',
  ])

  def __init__(self):
    """Initializes the build helper."""
    super(LibyalDpkgBuildHelper, self).__init__()
    self.architecture = platform.machine()

    if self.architecture == 'i686':
      self.architecture = 'i386'
    elif self.architecture == 'x86_64':
      self.architecture = 'amd64'

  def CheckBuildEnvironment(self):
    """Checks if the build environment is sane."""
    # TODO: allow to pass additional dependencies or determine them
    # from the dpkg files.

    # TODO: check if build environment has all the dependencies.
    # sudo dpkg -l <package>

  def Clean(self, library_name, library_version):
    """Cleans the dpkg packages in the current directory.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.
    """
    filenames_to_ignore = re.compile(
        u'^{0:s}[-_].*{1:d}'.format(library_name, library_version))

    # Remove files of previous versions in the format:
    # library[-_]version-1_architecture.*
    filenames = glob.glob(
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1_'
        u'{1:s}.*'.format(library_name, self.architecture))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove files of previous versions in the format:
    # library[-_]*version-1.*
    filenames = glob.glob(
        u'{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1.*'.format(
            library_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, library_name, library_version):
    """Retrieves the filename of one of the resulting files.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      A filename of one of the resulting dpkg packages.
    """
    return u'{0:s}_{1:d}-1_{2:s}.deb'.format(
        library_name, library_version, self.architecture)


class PkgBuildHelper(BuildHelper):
  """Class that helps in building MacOS-X packages (.pkg)."""

  def __init__(self):
    """Initializes the build helper."""
    super(PkgBuildHelper, self).__init__()
    self._pkgbuild = os.path.join(u'/', u'usr', u'bin', u'pkgbuild')

  def Build(self, source_filename, library_name, library_version):
    """Builds the pkg package and distributable disk image (.dmg).

    Args:
      source_filename: the name of the source package file.
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      True if the build was successful, False otherwise.
    """
    source_directory = self.Extract(source_filename)
    if not source_directory:
      logging.error(
          u'Extraction of source package: {0:s} failed'.format(source_filename))
      return False

    dmg_filename = u'{0:s}.dmg'.format(source_directory)
    pkg_filename = u'{0:s}.pkg'.format(source_directory)
    log_filename = os.path.join(u'..', self.LOG_FILENAME)

    sdks_path = os.path.join(
        u'/', u'Applications', u'Xcode.app', u'Contents', u'Developer', u'Platforms',
        u'MacOSX.platform', u'Developer', u'SDKs')

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
          source_directory, u'tmp', u'usr', u'share', u'doc', library_name)
      if not os.path.exists(share_doc_path):
        os.makedirs(share_doc_path)

      shutil.copy(os.path.join(source_directory, u'AUTHORS'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'COPYING'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'NEWS'), share_doc_path)
      shutil.copy(os.path.join(source_directory, u'README'), share_doc_path)

      command = (
          u'{0:s} --root {1:s}/tmp/ '
          u'--identifier com.google.code.p.{2:s} '
          u'--version {3:d} --ownership recommended {4:s}').format(
              self._pkgbuild, source_directory, library_name,
              library_version, pkg_filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

    command = (
        u'hdiutil create {0:s} -srcfolder {1:s} -fs HFS+').format(
            dmg_filename, pkg_filename)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True

  def Clean(self, library_name, library_version):
    """Cleans the MacOS-X packages in the current directory.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.
    """
    filenames_to_ignore = re.compile(
        u'^{0:s}-.*{1:d}'.format(library_name, library_version))

    # Remove files of previous versions in the format:
    # library-*version.dmg
    filenames = glob.glob(
        u'{0:s}-*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].dmg'.format(
            library_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

    # Remove files of previous versions in the format:
    # library-*version.pkg
    filenames = glob.glob(
        u'{0:s}-*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].pkg'.format(
            library_name))

    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        shutil.rmtree(filename)

  def GetOutputFilename(self, library_name, library_version):
    """Retrieves the filename of one of the resulting files.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      A filename of one of the resulting MacOS-X package.
    """
    return u'{0:s}-{1:d}.dmg'.format(library_name, library_version)


class RpmBuildHelper(BuildHelper):
  """Class that helps in building rpm packages (.rpm)."""

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

  def Clean(self, project_name, project_version):
    """Cleans the rpmbuild directory.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.
    """
    # Remove previous versions build directories.
    filenames_to_ignore = re.compile(
        u'{0:s}-{1:d}'.format(project_name, project_version))

    filenames = glob.glob(os.path.join(
        self.rpmbuild_path, u'BUILD', u'{0:s}-*'.format(project_name)))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        shutil.rmtree(filename)

    # Remove previous versions of rpms.
    filenames_to_ignore = re.compile(
        u'{0:s}-.*{1:d}-1.{2:s}.rpm'.format(
            project_name, project_version, self.architecture))

    rpm_filenames_glob = u'{0:s}-*-1.{1:s}.rpm'.format(
        project_name, self.architecture)

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
    filenames_to_ignore = re.compile(
        u'{0:s}-.*{1:d}-1.src.rpm'.format(project_name, project_version))

    filenames = glob.glob(os.path.join(
        self.rpmbuild_path, u'SRPMS',
        u'{0:s}-*-1.src.rpm'.format(project_name)))
    for filename in filenames:
      if not filenames_to_ignore.match(filename):
        logging.info(u'Removing: {0:s}'.format(filename))
        os.remove(filename)

  def GetOutputFilename(self, project_name, project_version):
    """Retrieves the filename of one of the resulting files.

    Args:
      project_name: the name of the project.
      project_version: the version of the project.

    Returns:
      A filename of one of the resulting rpms.
    """
    return u'{0:s}-{1!s}-1.{2:s}.rpm'.format(
        project_name, project_version, self.architecture)


class LibyalRpmBuildHelper(RpmBuildHelper):
  """Class that helps in building libyal rpm packages (.rpm)."""

  def Build(self, source_filename, library_name, library_version):
    """Builds the rpms.

    Args:
      source_filename: the name of the source package file.
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      True if the build was successful, False otherwise.
    """
    if not self._BuildFromSourcePackage(source_filename):
      return False

    # Move the rpms to the build directory.
    self._MoveRpms(library_name, library_version)

    return True


class VisualStudioBuildHelper(BuildHelper):
  """Class that helps in building using Visual Studio."""

  LOG_FILENAME = u'msbuild.log'

  def __init__(self, version='2008'):
    """Initializes the build helper.

    Args:
      version: the version of Visual Studio.
    """
    super(VisualStudioBuildHelper, self).__init__()
    self.version = version

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
    msvscpp_convert = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), u'msvscpp-convert.py')

    if not os.path.exists(msvscpp_convert):
      logging.error(u'Unable to find msvscpp-convert.py')
      return False

    os.chdir(source_directory)

    solution_filenames = glob.glob(os.path.join(u'msvscpp', u'*.sln'))
    if len(solution_filenames) != 1:
      logging.error(u'Unable to find Visual Studio solution file')
      return False

    solution_filename = solution_filenames[0]

    if not os.path.exists(u'vs2008'):
      command = u'{0:s} {1:s} --to {2:s} {3:s}'.format(
          sys.executable, msvscpp_convert, self.version, solution_filename)
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

  def Build(self, source_filename):
    """Builds using Visual Studio.

    Args:
      source_filename: the name of the source package file.

    Returns:
      True if the build was successful, False otherwise.
    """
    source_directory = self.Extract(source_filename)
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

      command = u'{0:s} setup.py bdist_msi'.format(sys.executable)
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        return False

      msi_filename = glob.glob(os.path.join(
          u'dist', u'{0:s}-*.1.*.msi'.format(python_module_name)))

      shutil.copy(msi_filename[0], build_directory)

      os.chdir(build_directory)

    return True

  def Clean(self, library_name, library_version):
    """Cleans the Visual Studio build directory.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.
    """

  def GetOutputFilename(self, library_name, library_version):
    """Retrieves the filename of one of the resulting files.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      A filename of one of the resulting build directory.
    """
    return os.path.join(
        u'{0:s}-{1:d}'.format(library_name, library_version), u'msvscpp',
        u'Release')


class LibyalBuilder(object):
  """Class that helps in building libyal libaries."""

  def __init__(self, build_target):
    """Initializes the dependency builder.

    Args:
      build_target: the build target.
    """
    super(LibyalBuilder, self).__init__()
    self._build_target = build_target
    self._download_helper = GoogleCodeDownloadHelper()

  def Build(self, project_name):
    """Builds a libyal library.

    Args:
      project_name: the project name.

    Returns:
      True if the build is successful or False on error.
    """
    project_version = self._download_helper.GetLatestVersion(project_name)
    project_filename = self._download_helper.Download(
        project_name, project_version)

    if project_filename:
      filenames_to_ignore = re.compile(
          u'^{0:s}-.*{1:d}'.format(project_name, project_version))

      # Remove files of previous versions in the format:
      # library-*.tar.gz
      filenames = glob.glob(u'{0:s}-*.tar.gz'.format(project_name))
      for filename in filenames:
        if not filenames_to_ignore.match(filename):
          logging.info(u'Removing: {0:s}'.format(filename))
          os.remove(filename)

      # Remove directories of previous versions in the format:
      # library-{version}
      filenames = glob.glob(
          u'{0:s}-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'.format(
          project_name))
      for filename in filenames:
        if os.path.isdir(filename) and not filenames_to_ignore.match(filename):
          logging.info(u'Removing: {0:s}'.format(filename))
          shutil.rmtree(filename)

      build_helper = None
      if self._build_target == 'dpkg':
        build_helper = LibyalDpkgBuildHelper()
        deb_filename = build_helper.GetOutputFilename(
            project_name, project_version)

        build_helper.Clean(project_name, project_version)

        if not os.path.exists(deb_filename):
          # TODO: add call to CheckBuildEnvironment or only do this once?

          logging.info(u'Building deb of: {0:s}'.format(project_filename))
          if not build_helper.Build(project_filename):
            logging.ingo(
                u'Build of: {0:s} failed for more info check {1:s}'.format(
                    project_filename, build_helper.LOG_FILENAME))
            return False

      elif self._build_target == 'download':
        # If available run the script post-download.sh after download.
        if os.path.exists(u'post-download.sh'):
          command = u'sh ./post-download.sh {0:s}'.format(project_filename)
          exit_code = subprocess.call(command, shell=True)
          if exit_code != 0:
            logging.error(u'Running: "{0:s}" failed.'.format(command))
            return False

      elif self._build_target == 'pkg':
        build_helper = PkgBuildHelper()
        dmg_filename = build_helper.GetOutputFilename(
            project_name, project_version)

        build_helper.Clean(project_name, project_version)

        if not os.path.exists(dmg_filename):
          logging.info(u'Building pkg of: {0:s}'.format(project_filename))
          if not build_helper.Build(
              project_filename, project_name, project_version):
            logging.info(
                u'Build of: {0:s} failed for more info check {1:s}'.format(
                    project_filename, build_helper.LOG_FILENAME))
            return False

      elif self._build_target == 'rpm':
        build_helper = LibyalRpmBuildHelper()
        rpm_filename = build_helper.GetOutputFilename(
            project_name, project_version)

        build_helper.Clean(project_name, project_version)

        if not os.path.exists(rpm_filename):
          # TODO: move the rename into the builder class?

          # rpmbuild wants the library filename without the status indication.
          source_filename = u'{0:s}-{1:d}.tar.gz'.format(
              project_name, project_version)
          os.rename(project_filename, source_filename)

          logging.info(u'Building rpm of: {0:s}'.format(project_filename))
          build_successful = build_helper.Build(
              source_filename, project_name, project_version)

          # Change the library filename back to the original.
          os.rename(source_filename, project_filename)

          if not build_successful:
            logging.info(
                u'Build of: {0:s} failed for more info check {1:s}'.format(
                    project_filename, build_helper.LOG_FILENAME))
            return False

      elif self._build_target in ['vs2008', 'vs2010', 'vs2012', 'vs2013']:
        if self._build_target == 'vs2013':
          logging.warning(u'Untested experimental build target: vs2013.')

        build_helper = VisualStudioBuildHelper(self._build_target[2:])
        release_directory = build_helper.GetOutputFilename(
            project_name, project_version)

        build_helper.Clean(project_name, project_version)

        if not os.path.exists(release_directory):
          logging.info(u'Building: {0:s} with Visual Studio {1:s}'.format(
              project_filename, build_helper.version))
          if not build_helper.Build(project_filename):
            logging.info(
                u'Build of: {0:s} failed for more info check {1:s}'.format(
                    project_filename, build_helper.LOG_FILENAME))
            return False

      if build_helper and os.path.exists(build_helper.LOG_FILENAME):
        logging.info(u'Removing: {0:s}'.format(build_helper.LOG_FILENAME))
        os.remove(build_helper.LOG_FILENAME)

    return True


def Main():
  build_targets = frozenset([
      'download', 'dpkg', 'pkg', 'rpm', 'vs2008', 'vs2010', 'vs2012', 'vs2013'])

  args_parser = argparse.ArgumentParser(description=(
      'Downloads and builds the latest versions of the libyal libraries.'))

  args_parser.add_argument(
      'build_target', choices=sorted(build_targets), action='store',
      metavar='BUILD_TARGET', default=None, help='The build target.')

  # TODO allow to set msbuild, packagemaker, python path

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

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  libyal_builder = LibyalBuilder(options.build_target)

  result = True
  for project_name in LIBYAL_LIBRARIES:
    if not libyal_builder.Build(project_name):
      print u'Failed building: {0:s}'.format(project_name)
      result = False
      break

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)