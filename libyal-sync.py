#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to automate creating builds of libyal libraries.
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

import argparse
import fileinput
import glob
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import urllib2


MSBUILD = '{0:s}:{1:s}{2:s}'.format(
    'C', os.sep, os.path.join(
    'Windows', 'Microsoft.NET', 'Framework', 'v3.5', 'MSBuild.exe'))

PACKAGEMAKER = os.path.join(
    'Applications', 'PackageMaker.app', 'Contents', 'MacOS', 'PackageMaker')

PYTHON_WINDOWS = '{0:s}:{1:s}{2:s}'.format(
    'C', os.sep, os.path.join('Python27', 'python.exe'))

PYTHON_SITE_PACKAGES_WINDOWS = '{0:s}:{1:s}{2:s}'.format(
    'C', os.sep, os.path.join('Python27', 'Lib', 'site-packages'))


class LibyalBuildHelper(object):
  """Class that helps in building libyal libraries."""

  def __init__(self):
    self._cached_url = ''
    self._cached_page_content = ''

  def GetGoogleCodeDownloadsUrl(self, library_name):
    """Retrieves the Download URL from the Google Code library page.

    Args:
      library_name: the name of the library.

    Returns:
      The downloads URL or None on error.
    """
    url = 'https://code.google.com/p/{0:s}/'.format(library_name)

    if self._cached_url != url:
      url_object = urllib2.urlopen(url)

      if url_object.code != 200:
        return None

      self._cached_page_content = url_object.read()
      self._cached_url = url

    # The format of the library downloads URL is:
    # https://googledrive.com/host/{random string}/
    expression_string = (
        '<a href="(https://googledrive.com/host/[^/]*/)"[^>]*>Downloads</a>')
    matches = re.findall(expression_string, self._cached_page_content)

    if not matches or len(matches) != 1:
      return None

    return matches[0]

  def GetGoogleDrivePageContent(self, library_name):
    """Retrieves the Google Drive page content for a given library name.

    Args:
      library_name: the name of the library.

    Returns:
      The page content or None on error.
    """
    url = self.GetGoogleCodeDownloadsUrl(library_name)

    if not url:
      return None

    if self._cached_url != url:
      url_object = urllib2.urlopen(url)

      if url_object.code != 200:
        return None

      self._cached_page_content = url_object.read()
      self._cached_url = url

    return self._cached_page_content

  def GetLatestVersion(self, library_name):
    """Retrieves the latest version number for a given library name.

    Args:
      library_name: the name of the library.

    Returns:
      The latest version number or 0 on error.
    """
    data = self.GetGoogleDrivePageContent(library_name)

    if not data:
      return 0

    # The format of the library download URL is:
    # /host/{random string}/{library name}-{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = '/host/[^/]*/{0:s}-[a-z-]*([0-9]+)[.]tar[.]gz'.format(
        library_name)
    matches = re.findall(expression_string, data)

    if not matches:
      return 0

    return int(max(matches))

  def GetDownloadUrl(self, library_name, library_version):
    """Retrieves the download URL for a given library name and version.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      The download URL of the library or None on error.
    """
    data = self.GetGoogleDrivePageContent(library_name)

    if not data:
      return None

    # The format of the library download URL is:
    # /host/{random string}/{library name}-{status-}{version}.tar.gz
    # Note that the status is optional and will be: beta, alpha or experimental.
    expression_string = '/host/[^/]*/{0:s}-[a-z-]*{1:d}[.]tar[.]gz'.format(
        library_name, library_version)
    matches = re.findall(expression_string, data)

    if not matches or len(matches) != 1:
      return None

    return 'https://googledrive.com{0:s}'.format(matches[0])

  def Download(self, library_name, library_version):
    """Downloads the library for a given library name and version.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.

    Returns:
      The filename if successful also if the file was already downloaded
      or None on error.
    """
    download_url = self.GetDownloadUrl(library_name, library_version)

    filename = download_url.split('/')[-1]

    if not os.path.exists(filename):
      print 'Downloading: {0:s}'.format(download_url)
      url = urllib2.urlopen(download_url)

      if url.code != 200:
        return None

      file_object = open(filename, 'wb')
      file_object.write(url.read())
      file_object.close()

    return filename

  def Extract(self, library_name, library_version, library_filename):
    """Extracts the library file for a given library name and version.

    Args:
      library_name: the name of the library.
      library_version: the version of the library.
      library_filename: the filename of the library.

    Returns:
      The name of the directory the files were extracted to if successful
      or None on error.
    """
    if not library_filename or not os.path.exists(library_filename):
      return None

    directory_name = '{0:s}-{1:d}'.format(library_name, library_version)

    if not os.path.exists(directory_name):
      print 'Extracting: {0:s}'.format(library_filename)

      archive = tarfile.open(library_filename, 'r:gz')
      archive.extractall()
      archive.close()

    return directory_name


def Main():
  args_parser = argparse.ArgumentParser(description=(
      'Downloads and builds the latest versions of the libyal libraries.'))

  # TODO add a list of supported build targets.
  args_parser.add_argument(
      'build_target', nargs='?', action='store', metavar='BUILD_TARGET',
      default=None, help='The build target.')

  # TODO allow to set msbuild, packagemaker, python path

  options = args_parser.parse_args()

  if not options.build_target:
    print 'Build target missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  libyal_libraries = [
      'libbde',
      'libesedb',
      'libevt',
      'libevtx',
      'libewf',
      'libexe',
      'libfvde',
      'liblnk',
      'libmsiecf',
      'libolecf',
      'libpff',
      'libqcow',
      'libregf',
      'libsmraw',
      'libvhdi',
      'libvmdk',
      'libvshadow',
      'libwrc']

  libyal_helper = LibyalBuildHelper()

  for libyal_name in libyal_libraries:
    libyal_version = libyal_helper.GetLatestVersion(libyal_name)

    libyal_filename = libyal_helper.Download(libyal_name, libyal_version)

    if libyal_filename:
      # Remove previous versions.
      filenames = glob.glob('{0:s}-*.tar.gz'.format(libyal_name))
      for filename in filenames:
        if filename != libyal_filename:
          print 'Removing: {0:s}'.format(filename)
          os.remove(filename)

      exit_code = 0

      if options.build_target in ['dpkg', 'macosx', 'vs2008']:
        libyal_directory = libyal_helper.Extract(
            libyal_name, libyal_version, libyal_filename)

        # Remove previous versions.
        directory_names = glob.glob(
            '{0:s}-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'.format(libyal_name))
        for directory_name in directory_names:
          if directory_name != libyal_directory:
            print 'Removing: {0:s}'.format(directory_name)
            shutil.rmtree(directory_name)

      if options.build_target == 'dpkg':
        architecture = platform.machine()
        if architecture == 'i686':
          architecture = 'i386'
        elif architecture == 'x86_64':
          architecture = 'amd64'

        # File names to ignore while removing previous versions.
        ignore_filename = re.compile(
            "^{0:s}[-_].*{1:d}".format(libyal_name, libyal_version))

        # Remove files of previous versions in the format:
        # library[-_]version-1_architecture.*
        filenames = glob.glob(
            '{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1_{1:s}.*'.format(
                libyal_name, architecture))

        for filename in filenames:
          if not ignore_filename.match(filename):
            print 'Removing: {0:s}'.format(filename)
            os.remove(filename)

        # Remove files of previous versions in the format:
        # library[-_]version-1.*
        filenames = glob.glob(
            '{0:s}[-_]*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-1.*'.format(
                libyal_name))

        for filename in filenames:
          if not ignore_filename.match(filename):
            print 'Removing: {0:s}'.format(filename)
            os.remove(filename)

        deb_filename = '{0:s}_{1:d}-1_{2:s}.deb'.format(
            libyal_name, libyal_version, architecture)

        if libyal_directory and not os.path.exists(deb_filename):
          dpkg_directory = os.path.join(libyal_directory, 'dpkg')

          if os.path.exists(dpkg_directory):
            debian_directory = os.path.join(libyal_directory, 'debian')

            # If there is a debian directory remove it
            # and recreate it from the dpkg directory.
            if os.path.exists(debian_directory):
              print 'Removing: {0:s}'.format(directory_name)
              shutil.rmtree(debian_directory)
            shutil.copytree(dpkg_directory, debian_directory)

            # Script to prepare the dpkg files before building.
            if os.path.exists('prep-dpkg.sh'):
              command = 'sh ../prep-dpkg.sh'
              exit_code = subprocess.call(
                  '(cd {0:s} && {1:s})'.format(libyal_directory, command),
                   shell=True)

            print 'Building deb of: {0:s}'.format(libyal_filename)
            command = 'dpkg-buildpackage -rfakeroot > ../build.log 2>&1'
            exit_code = subprocess.call(
                '(cd {0:s} && {1:s})'.format(libyal_directory, command), shell=True)

            if exit_code != 0:
              print 'Build of: {0:s} failed for more info check build.log'.format(
                  libyal_filename)
              return False

            pass

      elif options.build_target == 'macosx':
        # TODO: check for existing dmg
        # TODO: remove older packaging files

        command = (
            './configure --prefix=$PWD/macosx/tmp/ --enable-python '
            '> ../build.log 2>&1')
        exit_code = subprocess.call(
            '(cd {0:s} && {1:s})'.format(libyal_directory, command), shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

        command = 'make >> ../build.log 2>&1'
        exit_code = subprocess.call(
            '(cd {0:s} && {1:s})'.format(libyal_directory, command), shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

        command = 'make install >> ../build.log 2>&1'
        exit_code = subprocess.call(
            '(cd {0:s} && {1:s})'.format(libyal_directory, command), shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

        # TODO: notify about running sudo

        command = 'sudo chown -R root:wheel macosx/tmp/'
        exit_code = subprocess.call(
            '(cd {0:s} && {1:s})'.format(libyal_directory, command), shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

        command = (
            '{0:s} --doc {1:s}/macosx/{2:s}.pmdoc '
            '--out {2:s}-{3:d}.pkg').format(
            PACKAGEMAKER, libyal_directory, libyal_name, libyal_version)
        exit_code = subprocess.call(command, shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

        command = (
            'hdiutil create {0:s}-{1:d}.dmg -srcfolder {0:s}-{1:d}.pkg '
            '-fs HFS+').format(libyal_name, libyal_version)
        exit_code = subprocess.call(command, shell=True)

        if exit_code != 0:
          print 'Build of: {0:s} failed for more info check build.log'.format(
              libyal_filename)
          return False

      elif options.build_target == 'rpm':
        architecture = platform.machine()

        rpms_path = os.path.join('~', 'rpmbuild', 'RPMS', architecture)
        rpms_path = os.path.expanduser(rpms_path)
        rpm_filename = '{0:s}-{1:d}-1.{2:s}.rpm'.format(
            libyal_name, libyal_version, architecture)
        rpm_filename = os.path.join(rpms_path, rpm_filename)

        if not os.path.exists(rpm_filename):
          # TODO: remove:
          # ~/rpmbuild/BUILD/libevt-*/
          # ~/rpmbuild/RPMS/x86_64/libevt-*.rpm
          # ~/rpmbuild/SRPMS/libevt-*.rpm

          # Remove previous versions.
          rpm_filename = '{0:s}-*-1.{1:s}.rpm'.format(libyal_name, architecture)
          rpm_filename = os.path.join(rpms_path, rpm_filename)

          filenames = glob.glob('{0:s}-*.tar.gz'.format(libyal_name))
          for filename in filenames:
            if filename != libyal_filename:
              print 'Removing: {0:s}'.format(filename)
              os.remove(filename)

          filename = '{0:s}-{1:d}.tar.gz'.format(libyal_name, libyal_version)
          # rpmbuild wants the library filename without the status indication.
          os.rename(libyal_filename, filename)

          print 'Building rpm of: {0:s}'.format(libyal_filename)
          command = 'rpmbuild -ta {0:s} > build.log 2>&1'.format(filename)
          exit_code = subprocess.call(command, shell=True)

          # Change the library filename back to the original.
          os.rename(filename, libyal_filename)

          if exit_code != 0:
            print 'Build of: {0:s} failed for more info check build.log'.format(
                libyal_filename)
            return False

      elif options.build_target == 'vs2008':
        if not os.path.exists(MSBUILD):
          print 'Cannot find MSBuild.exe'
          return False

        if not os.path.exists(PYTHON_WINDOWS):
          print 'Cannot find python.exe'
          return False

        force_build = False

        config_filename = os.path.join(
            libyal_directory, 'common', 'config_winapi.h')

        # If the WINAPI config file is not available use the MS C compiler one.
        if not os.path.exists(config_filename):
          config_filename = os.path.join(
              libyal_directory, 'common', 'config_msc.h')

        # Add a line to the config file that sets WINVER to 0x0501.
        parsing_mode = 0

        for line in fileinput.input(config_filename, inplace=1):
          # Remove trailing whitespace and end-of-line characters.
          line = line.rstrip()

          if parsing_mode != 2 or line:
            if parsing_mode == 1:
              if not line.startswith('#define WINVER 0x0501'):
                print '#define WINVER 0x0501'
                print ''
                force_build = True
              parsing_mode = 2

            elif line.startswith('#define _CONFIG_'):
              parsing_mode = 1

          print line

        release_directory = os.path.join(
            libyal_directory, 'msvscpp', 'Release')

        if not os.path.exists(release_directory) or force_build:
          print 'Building: {0:s}'.format(libyal_name)

          solution_filename = os.path.join(
              libyal_directory, 'msvscpp', '{0:s}.sln'.format(libyal_name))
          command = (
              '{0:s} /p:Configuration=Release /noconsolelogger '
              '/fileLogger {1:s}').format(MSBUILD, solution_filename)

          exit_code = subprocess.call(command, shell=False)

          if exit_code != 0:
            print (
                'Build of: {0:s} failed for more info check '
                'msbuild.log').format(libyal_filename)
            return False

          python_module_name = 'py{0:s}'.format(libyal_name[3:])
          python_module_directory = os.path.join(
              libyal_directory, python_module_name)
          python_module_dist_directory = os.path.join(
              python_module_directory, 'dist')
  
          if not os.path.exists(python_module_dist_directory) or force_build:
            build_directory = os.path.join('..', '..')
  
            os.chdir(python_module_directory)
  
            # TODO: redirect the output to build.log?
            command = '{0:s} setup.py bdist_msi'.format(
                PYTHON_WINDOWS)
  
            exit_code = subprocess.call(command, shell=False)
  
            if exit_code != 0:
              print (
                  'Build of: msi failed for more info check '
                  'build.log').format(libyal_filename)
              return False
  
            msi_filename = glob.glob(os.path.join(
                'dist', '{0:s}-{1:d}.1.*.msi'.format(
                python_module_name, libyal_version)))
  
            shutil.copy(msi_filename[0], build_directory)
  
            os.chdir(build_directory)

      else:
        print 'Unsupported build target: {0:s}.'.format(options.build_target)
        print ''
        args_parser.print_help()
        print ''
        return False

      if os.path.exists('build.log'):
        print 'Removing: build.log'
        os.remove('build.log')
      if os.path.exists('msbuild.log'):
        print 'Removing: msbuild.log'
        os.remove('msbuild.log')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
