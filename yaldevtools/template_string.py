# -*- coding: utf-8 -*-
"""Template string generator."""

import string


class TemplateStringGenerator(object):
  """Template string generator."""

  def _ReadTemplateFile(self, path):
    """Reads a template string from file.

    Args:
      path (str): path of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    with open(path, 'r', encoding='utf8') as file_object:
      file_data = file_object.read()

    return string.Template(file_data)

  def Generate(self, template_path, template_mappings):
    """Generates output based on the template string.

    Args:
      template_path (str): path of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.

    Returns:
      str: output based on the template string.

    Raises:
      RuntimeError: if the template cannot be formatted.
    """
    template_string = self._ReadTemplateFile(template_path)

    try:
      return template_string.substitute(template_mappings)

    except (KeyError, ValueError) as exception:
      raise RuntimeError((
          f'Unable to format template: {template_path:s} with error: '
          f'{exception!s}'))
