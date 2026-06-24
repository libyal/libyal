"""Generator resources."""

import ast


class GeneratorOperation:
    """Generator operation.

    Attributes:
      condition (str): condition under which the operation applies.
      default (str): default operation of a selection.
      fallback (str): fallback operation of template file if condition does not apply.
      file (str): path of a template file related to the operation.
      identifier (str): identifier of the generator operation.
      modifiers (str): names of modifiers.
      operations (str): names of sub operations.
      options (dict[str, str]): operation per selection value.
      placeholders (str): name of the template placeholders related to the operation.
      type (str): operation type.
    """

    def __init__(self, identifier=None, operation_type=None):
        """Initializes a generator operation.

        Args:
          identifier (Optional[str]): identifier of the generator operation.
          operation_type (Optional[str]): operation type.
        """
        super().__init__()
        self._condition_expression = None
        self.condition = None
        self.default = None
        self.fallback = None
        self.file = None
        self.identifier = identifier
        self.modifiers = None
        self.operations = None
        self.type = operation_type
        self.options = {}
        self.placeholders = None

    def GetConditionExpression(self):
        """Retrieves the condition as as expression.

        Returns:
          code: condition expression or None if not available.
        """
        if not self._condition_expression:
            expression_ast = ast.parse(self.condition, mode="eval")
            self._condition_expression = compile(
                expression_ast, "<string>", mode="eval"
            )
        return self._condition_expression


class ToolOption:
    """Tool option.

    Tool options are sorted alphabetically with lower case before upper case.

    Attributes:
      guard (str): guard.
      help_text (str): help text.
      identifier (str): identifier.
      name (str): name.
    """

    def __init__(self, identifier, name, help_text, guard=None):
        """Initializes a tool option.

        Args:
          identifier (str): identifier.
          name (str): name.
          help_text (str): help text.
          guard (Optional[str]): condition under which the option should be active.
        """
        super().__init__()
        self.guard = guard
        self.help_text = help_text
        self.identifier = identifier
        self.name = name

    def __lt__(self, other):
        """Determines if the tool options is less than an other tool option.

        Args:
          other (ToolOption): tool option to compare against.
        """
        self_key = (ord(self.identifier.lower()), self.identifier.isupper())
        other_key = (ord(other.identifier.lower()), other.identifier.isupper())

        return self_key < other_key
