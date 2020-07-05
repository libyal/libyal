
  def test_check_file_signature(self):
    """Tests the check_file_signature function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    result = ${python_module_name}.check_file_signature(unittest.source)
    self.assertTrue(result)

  def test_check_file_signature_file_object(self):
    """Tests the check_file_signature_file_object function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    with open(unittest.source, "rb") as file_object:
      result = ${python_module_name}.check_file_signature_file_object(file_object)
      self.assertTrue(result)
