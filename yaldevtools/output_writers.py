# -*- coding: utf-8 -*-
"""The output writers."""


class FileWriter(object):
  """File output writer."""

  def __init__(self, output_directory):
    """Initializes a file output writer.

    Args:
      output_directory (str): path of the output directory.
    """
    super(FileWriter, self).__init__()
    self._output_directory = output_directory

  def WriteFile(self, file_path, file_data, access_mode='w'):
    """Writes the data to file.

    Args:
      file_path (str): path of the file to write.
      file_data (bytes): to write.
      access_mode (Optional[str]): output file access mode.
    """
    with open(file_path, access_mode, encoding='utf8') as file_object:
      file_object.write(file_data)


class StdoutWriter(object):
  """Stdout output writer."""

  # pylint: disable=unused-argument
  def WriteFile(self, file_path, file_data, access_mode='w'):
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
