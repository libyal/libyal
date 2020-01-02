
    ${library_name_suffix}_${type_name}.open(unittest.source)

    ${type_size_name} = ${library_name_suffix}_${type_name}.get_${type_size_name}()

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_SET)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 16)

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_CUR)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 32)

    ${library_name_suffix}_${type_name}.seek_offset(-16, os.SEEK_CUR)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, 16)

    if ${type_size_name} > 16:
      ${library_name_suffix}_${type_name}.seek_offset(-16, os.SEEK_END)

      offset = ${library_name_suffix}_${type_name}.get_offset()
      self.assertEqual(offset, ${type_size_name} - 16)

    ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_END)

    offset = ${library_name_suffix}_${type_name}.get_offset()
    self.assertEqual(offset, ${type_size_name} + 16)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-1, os.SEEK_SET)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-32 - ${type_size_name}, os.SEEK_CUR)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(-32 - ${type_size_name}, os.SEEK_END)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(0, -1)

    ${library_name_suffix}_${type_name}.close()

    # Test the seek without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.seek_offset(16, os.SEEK_SET)
