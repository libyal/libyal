
  def test_open(self):
    """Tests the open function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open(unittest.source)

    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.open(unittest.source)

    ${library_name_suffix}_${type_name}.close()

    with self.assertRaises(TypeError):
      ${library_name_suffix}_${type_name}.open(None)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.open(unittest.source, mode="w")

  def test_open_file_object(self):
    """Tests the open_file_object function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    file_object = open(unittest.source, "rb")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open_file_object(file_object)

    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.open_file_object(file_object)

    ${library_name_suffix}_${type_name}.close()

    # TODO: change IOError into TypeError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.open_file_object(None)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.open_file_object(file_object, mode="w")

  def test_close(self):
    """Tests the close function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.close()

  def test_open_close(self):
    """Tests the open and close functions."""
    if not unittest.source:
      return

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    # Test open and close.
    ${library_name_suffix}_${type_name}.open(unittest.source)
    ${library_name_suffix}_${type_name}.close()

    # Test open and close a second time to validate clean up on close.
    ${library_name_suffix}_${type_name}.open(unittest.source)
    ${library_name_suffix}_${type_name}.close()

    file_object = open(unittest.source, "rb")

    # Test open_file_object and close.
    ${library_name_suffix}_${type_name}.open_file_object(file_object)
    ${library_name_suffix}_${type_name}.close()

    # Test open_file_object and close a second time to validate clean up on close.
    ${library_name_suffix}_${type_name}.open_file_object(file_object)
    ${library_name_suffix}_${type_name}.close()

    # Test open_file_object and close and dereferencing file_object.
    ${library_name_suffix}_${type_name}.open_file_object(file_object)
    del file_object
    ${library_name_suffix}_${type_name}.close()
