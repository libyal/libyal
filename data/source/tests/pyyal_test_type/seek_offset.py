
  def test_seek_offset(self):
    """Tests the seek_offset function."""
    if not unittest.source:
      raise unittest.SkipTest('missing source')

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open(unittest.source)

    file_size = ${library_name_suffix}_${type_name}.get_size()

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_SET)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 16)

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_CUR)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 32)

    ${library_name_suffix}_${type_name}.seek_offset(-16, os.SEEK_CUR)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 16)

    ${library_name_suffix}_${type_name}.seek_offset(-16, os.SEEK_END)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, file_size - 16)

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_END)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, file_size + 16)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-1, os.SEEK_SET)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-32 - file_size, os.SEEK_CUR)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-32 - file_size, os.SEEK_END)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(0, -1)

    ${library_name_suffix}_${type_name}.close()

    # Test the seek without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_SET)
