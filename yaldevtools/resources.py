# -*- coding: utf-8 -*-
"""Generator resources."""

import ast


class GeneratorOperation(object):
  """Generator operation.

  Attributes:
    condition (str): condition under which the operation applies.
    default (str): default operation of a selection.
    fallback (str): fallback operation of template file if condition does not
        apply.
    file (str): path of a template file related to the operation.
    identifier (str): identifier of the generator operation.
    operations (str): names of sub operations.
    options (dict[str, str]): operation per selection value.
    placeholders (str): name of the template placeholders related to the
        operation.
    modifiers (str): names of modifiers.
    type (str): operation type.
  """

  def __init__(self, identifier=None, type=None):
    """Initializes a generator operation.

    Args:
      identifier (Optional[str]): identifier of the generator operation.
      type (Optional[str]): operation type.
    """
    super(GeneratorOperation, self).__init__()
    self._condition_expression = None
    self.condition = None
    self.default = None
    self.fallback = None
    self.file = None
    self.identifier = identifier
    self.modifiers = None
    self.operations = None
    self.options = {}
    self.placeholders = None
    self.type = type

  def GetConditionExpression(self):
    """Retrieves the condition as as expression.

    Returns:
      code: condition expression or None if not available.
    """
    if not self._condition_expression:
      expression_ast = ast.parse(self.condition, mode='eval')
      self._condition_expression = compile(
          expression_ast, '<string>', mode='eval')
    return self._condition_expression
