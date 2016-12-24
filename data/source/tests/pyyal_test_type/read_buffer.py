
  def test_read_buffer(self):
    """Tests the read_buffer function."""
    if not unittest.source:
      return

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open(unittest.source)

    file_size = ${library_name_suffix}_${type_name}.get_size()

    # Test normal read.
    data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(file_size, 4096))

    if file_size < 4096:
      data = ${library_name_suffix}_${type_name}.read_buffer()

      self.assertIsNotNone(data)
      self.assertEqual(len(data), file_size)

    # Test read beyond file size.
    if file_size > 16:
      ${library_name_suffix}_${type_name}.seek_offset(-16, os.SEEK_END)

      data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 16)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer(size=-1)

    ${library_name_suffix}_${type_name}.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.read_buffer(size=4096)

  def test_read_buffer_file_object(self):
    """Tests the read_buffer function on a file-like object."""
    if not unittest.source:
      return

    file_object = open(unittest.source, "rb")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open_file_object(file_object)

    file_size = ${library_name_suffix}_${type_name}.get_size()

    # Test normal read.
    data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(file_size, 4096))

    ${library_name_suffix}_${type_name}.close()

  def test_read_buffer_at_offset(self):
    """Tests the read_buffer_at_offset function."""
    if not unittest.source:
      return

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open(unittest.source)

    file_size = ${library_name_suffix}_${type_name}.get_size()

    # Test normal read.
    data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, 0)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(file_size, 4096))

    # Test read beyond file size.
    if file_size > 16:
      data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, file_size - 16)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 16)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(-1, 0)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, -1)

    ${library_name_suffix}_${type_name}.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, 0)
