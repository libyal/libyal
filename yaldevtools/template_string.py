# -*- coding: utf-8 -*-
"""Template string generator."""

import io
import string


class TemplateStringGenerator(object):
  """Template string generator."""

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename (str): name of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    with io.open(filename, 'r', encoding='utf8') as file_object:
      file_data = file_object.read()

    return string.Template(file_data)

  def Generate(self, template_filename, template_mappings):
    """Generates output based on the template string.

    Args:
      template_filename (str): path of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.

    Returns:
      str: output based on the template string.

    Raises:
      RuntimeError: if the template cannot be formatted.
    """
    template_string = self._ReadTemplateFile(template_filename)

    try:
      return template_string.substitute(template_mappings)

    except (KeyError, ValueError) as exception:
      raise RuntimeError(
          u'Unable to format template: {0:s} with error: {1!s}'.format(
              template_filename, exception))
