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


LIBYAL_PACKAGES = frozenset([
    'pybde',
    'pyevt',
    'pyevtx',
    'pyewf',
    'pyexe',
    'pylnk',
    'pymsiecf',
    'pyolecf',
    'pypff',
    'pyqcow',
    'pyregf',
    'pysmdev',
    'pysmraw',
    'pyvhdi',
    'pyvmdk',
    'pyvshadow',
    'pywrc',
])


def Main():
  install_targets = frozenset(['deb', 'rpm', 'msi'])

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
  if operating_system != 'Windows':
    logging.error(u'Operating system: {0:s} not supported.'.format(
        operating_system))
    return False

  package_filenames = {}
  package_versions = {}
  for directory_entry in os.listdir(u'.'):
    if directory_entry.endswith(u'.{0:s}'.format(options.install_target)):
      name, _, version = directory_entry.partition(u'-')
      version, _, _ = version.partition(u'.')

      if name in LIBYAL_PACKAGES:
        if name not in package_versions or package_versions[name] < version:
          package_filenames[name] = directory_entry
          package_versions[name] = version

  if options.install_target == 'msi':
    connection = wmi.WMI()

    query = 'SELECT Name FROM Win32_Product'
    for product in connection.query(query):
      name = getattr(product, 'Name', u'')
      if name.startswith('Python '):
        _, _, name = name.rpartition(u' ')
        name, _, version = name.partition(u'-')

        if name.startswith('py'):
          version, _, _ = version.partition(u'.')

          if name in LIBYAL_PACKAGES:
            if name in package_versions and version < package_versions[name]:
              print 'Removing: {0:s} {1:s}'.format(name, version)
              product.Uninstall()

  result = True
  for name, version in package_versions.iteritems():
    print 'Installing: {0:s} {1:s}'.format(name, version)

    if options.install_target == 'deb':
      command = u'dpkg -i {0:s}'.format(package_filenames[name])
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'msi':
      command = u'msiexec.exe /i {0:s} /q'.format(package_filenames[name])
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

    elif options.install_target == 'rpm':
      command = u'rpm -U {0:s}'.format(package_filenames[name])
      exit_code = subprocess.call(command, shell=False)
      if exit_code != 0:
        logging.error(u'Running: "{0:s}" failed.'.format(command))
        result = False

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
