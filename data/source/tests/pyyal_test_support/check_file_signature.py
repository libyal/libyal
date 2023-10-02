
  def test_check_file_signature(self):
    """Tests the check_file_signature function."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      raise unittest.SkipTest("missing source")

    result = ${python_module_name}.check_file_signature(test_source)
    self.assertTrue(result)

  def test_check_file_signature_file_object(self):
    """Tests the check_file_signature_file_object function."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      raise unittest.SkipTest("missing source")

    with open(test_source, "rb") as file_object:
      result = ${python_module_name}.check_file_signature_file_object(file_object)
      self.assertTrue(result)
