#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to automate (re)installation of libyal packages in the current
# directory.
#
# Copyright (c) 2014, Joachim Metz <joachim.metz@gmail.com>
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
import logging
import os
import platform
import subprocess
import sys

if platform.system() == 'Windows':
  import wmi


# TODO: add support for com.github.libyal.


LIBYAL_PACKAGES = frozenset([
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


def Main():
  # TODO: add 'dmg'.
  install_targets = frozenset(['deb', 'msi', 'pkg', 'rpm'])

  args_parser = argparse.ArgumentParser(description=(
      'Installs the latest versions of libyal packages in the current '
      'directory.'))

  args_parser.add_argument(
      'install_target', choices=sorted(install_targets), action='store',
      metavar='INSTALL_TARGET', default=None, help='The install target.')

  options = args_parser.parse_args()

  if not options.install_target:
    print 'Installation target missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  if options.install_target not in install_targets:
    print 'Unsupported install target: {0:s}.'.format(options.install_target)
    print ''
    args_parser.print_help()
    print ''
    return False

  operating_system = platform.system()

  package_filenames = {}
  package_versions = {}
  for directory_entry in os.listdir(u'.'):
    if directory_entry.endswith(u'.{0:s}'.format(options.install_target)):
      name, _, version = directory_entry.partition(u'-')
      version, _, _ = version.partition(u'.')

      # For msi the package name start with py.
      if name.startswith(u'py'):
        name = u'lib{0:s}'.format(name[2:])

      if name in LIBYAL_PACKAGES:
        if name not in package_versions or package_versions[name] < version:
          package_filenames[name] = directory_entry
          package_versions[name] = version

  if options.install_target == 'msi':
    if operating_system != 'Windows':
      logging.error(u'Operating system: {0:s} not supported.'.format(
          operating_system))
      return False

    connection = wmi.WMI()

    query = 'SELECT Name FROM Win32_Product'
    for product in connection.query(query):
      name = getattr(product, 'Name', u'')
      if name.startswith('Python '):
        _, _, name = name.rpartition(u' ')
        name, _, version = name.partition(u'-')

        if name.startswith('py'):
          version, _, _ = version.partition(u'.')
          name = u'lib{0:s}'.format(name[2:])

          if name in LIBYAL_PACKAGES:
            if name in package_versions and version >= package_versions[name]:
              # The latest or newer version is already installed.
              del package_versions[name]

            elif name in package_versions and version < package_versions[name]:
              print 'Removing: {0:s} {1:s}'.format(name, version)
              product.Uninstall()

  elif options.install_target in ['dmg', 'pkg']:
    if operating_system != 'Darwin':
      logging.error(u'Operating system: {0:s} not supported.'.format(
          operating_system))
      return False

    result = True

    command = u'/usr/sbin/pkgutil --packages'
    print 'Running: "{0:s}"'.format(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    if process.returncode is None:
      packages, _ = process.communicate()
    else:
      packages = '' 

    if process.returncode != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    for package_name in packages.split('\n'):
      if not package_name:
        continue

      if package_name.startswith(u'com.google.code.p.'):
        # Detect the PackageMaker naming convention.
        if package_name.endswith(u'.pkg'):
          name, _, _ = package_name[18:].partition(u'.')
          _, _, sub_name = package_name[:-4].rpartition(u'.')
          is_package_maker_pkg = True
        else:
          _, _, name = package_name.rpartition(u'.')
          is_package_maker_pkg = False

        if name in LIBYAL_PACKAGES:
          # Determine the package version.
          command = u'/usr/sbin/pkgutil --pkg-info {0:s}'.format(package_name)
          print 'Running: "{0:s}"'.format(command)
          process = subprocess.Popen(
              command, stdout=subprocess.PIPE, shell=True)
          if process.returncode is None:
            package_info, _ = process.communicate()
          else:
            package_info = '' 

          if process.returncode != 0:
            logging.error(u'Running: "{0:s}" failed.'.format(command))
            result = False
            continue

          location = None
          version = None
          volume = None
          for attribute in package_info.split('\n'):
            if attribute.startswith(u'location: '):
              _, _, location = attribute.rpartition(u'location: ')

            elif attribute.startswith(u'version: '):
              _, _, version = attribute.rpartition(u'version: ')

            elif attribute.startswith(u'volume: '):
              _, _, volume = attribute.rpartition(u'volume: ')

          if name in package_versions and version >= package_versions[name]:
            # The latest or newer version is already installed.
            del package_versions[name]

          elif name in package_versions and version < package_versions[name]:
            # Determine the files in the package.
            command = u'/usr/sbin/pkgutil --files {0:s}'.format(package_name)
            print 'Running: "{0:s}"'.format(command)
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, shell=True)
            if process.returncode is None:
              package_files, _ = process.communicate()
            else:
              package_files = '' 

            if process.returncode != 0:
              logging.error(u'Running: "{0:s}" failed.'.format(command))
              result = False
              continue

            directories = []
            files = []
            for filename in package_files.split('\n'):
              if is_package_maker_pkg:
                filename = u'{0:s}{1:s}/{2:s}/{3:s}'.format(
                    volume, location, sub_name, filename)
              else:
                filename = u'{0:s}{1:s}'.format(location, filename)

              if os.path.isdir(filename):
                directories.append(filename)
              else:
                files.append(filename)

            print 'Removing: {0:s} {1:s}'.format(name, version)
            for filename in files:
              if os.path.exists(filename):
                os.remove(filename)

            for filename in directories:
              if os.path.exists(filename):
                try:
                  os.rmdir(filename)
                except OSError:
                  # Ignore directories that are not empty.
                  pass

            command = u'/usr/sbin/pkgutil --forget {0:s}'.format(
                package_name)
            exit_code = subprocess.call(command, shell=True)
            if exit_code != 0:
              logging.error(u'Running: "{0:s}" failed.'.format(command))
              result = False

    if not result:
      return False

  elif options.install_target in ['deb', 'rpm']:
    if operating_system != 'Linux':
      logging.error(u'Operating system: {0:s} not supported.'.format(
          operating_system))
      return False

  result = True
  for name, version in package_versions.iteritems():
    print 'Installing: {0:s} {1:s}'.format(name, version)
    package_filename = package_filenames[name]

    if options.install_target == 'deb':
      command = u'dpkg -i {0:s}'.format(package_filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'dmg':
      # TODO: test.
      command = u'/usr/bin/hdiutil attach {0:s}'.format(package_filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False
        continue

      volume_path = u'/Volumes/{0:s}.pkg'.format(package_filename[:-4])
      if not os.path.exists(volume_path):
        logging.error(u'Missing volume: {0:s}.'.format(volume_path))
        result = False
        continue

      pkg_file = u'{0:s}/{1:s}.pkg'.format(volume_path, package_filename[:-4])
      if not os.path.exists(pkg_file):
        logging.error(u'Missing pkg file: {0:s}.'.format(pkg_file))
        result = False
        continue

      command = u'/usr/sbin/installer -target / -pkg {0:s}'.format(pkg_file)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

      command = u'/usr/bin/hdiutil detach {0:s}'.format(volume_path)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'msi':
      command = u'msiexec.exe /i {0:s} /q'.format(package_filename)
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'pkg':
      command = u'/usr/sbin/installer -target / -pkg {0:s}'.format(
          package_filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'rpm':
      command = u'rpm -U {0:s}'.format(package_filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
