
  def test_open(self):
    """Tests the open function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    lnk_file = ${python_module_name}.open(unittest.source)
    self.assertIsNotNone(lnk_file)

    lnk_file.close()

    with self.assertRaises(TypeError):
      ${python_module_name}.open(None)

    with self.assertRaises(ValueError):
      ${python_module_name}.open(unittest.source, mode="w")

  def test_open_file_object(self):
    """Tests the open_file_object function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    if not os.path.isfile(unittest.source):
      raise unittest.SkipTest("source not a regular file")

    with open(unittest.source, "rb") as file_object:
      lnk_file = ${python_module_name}.open_file_object(file_object)
      self.assertIsNotNone(lnk_file)

      lnk_file.close()

      with self.assertRaises(TypeError):
        ${python_module_name}.open_file_object(None)

      with self.assertRaises(ValueError):
        ${python_module_name}.open_file_object(file_object, mode="w")
