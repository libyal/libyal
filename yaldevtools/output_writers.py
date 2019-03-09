# -*- coding: utf-8 -*-
"""The output writers."""

from __future__ import print_function
from __future__ import unicode_literals

import io


class FileWriter(object):
  """File output writer."""

  def __init__(self, output_directory):
    """Initializes a file output writer.

    Args:
      output_directory (str): path of the output directory.
    """
    super(FileWriter, self).__init__()
    self._output_directory = output_directory

  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to file.

    Args:
      file_path (str): path of the file to write.
      file_data (bytes): to write.
      access_mode (Optional[str]): output file access mode.
    """
    with open(file_path, access_mode) as file_object:
      file_object.write(file_data)


class StdoutWriter(object):
  """Stdout output writer."""

  def __init__(self):
    """Initializes a stdout output writer."""
    super(StdoutWriter, self).__init__()

  # pylint: disable=unused-argument
  def WriteFile(self, file_path, file_data, access_mode='wb'):
    """Writes the data to stdout (without the default trailing newline).

    Args:
      file_path (str): path of the file to write.
      file_data (bytes): to write.
      access_mode (Optional[str]): output file access mode.
    """
    print('-' * 80)
    print('{0: ^80}'.format(file_path))
    print('-' * 80)
    print('')
    print(file_data, end='')
