# -*- coding: utf-8 -*-
"""Generator resources."""


class GeneratorOperation(object):
  """Generator operation.

  Attributes:
    condition (str): condition under which the operation applies.
    file (str): path of a template file related to the operation.
    identifier (str): identifier of the generator operation.
    mappings (str): template mappings related to the operation.
    operations (str): names of sub operations.
    type (str): operation type.
  """

  def __init__(self, identifier=None, type=None):
    """Initializes a generator operation.

    Args:
      identifier (Optional[str]): identifier of the generator operation.
      type (Optional[str]): operation type.
    """
    super(GeneratorOperation, self).__init__()
    self.condition = None
    self.file = None
    self.identifier = identifier
    self.mappings = None
    self.operations = None
    self.type = type
