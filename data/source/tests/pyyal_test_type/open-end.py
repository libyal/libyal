
    ${library_name_suffix}_${type_name}.open(unittest.source)

    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.open(unittest.source)

    ${library_name_suffix}_${type_name}.close()

    with self.assertRaises(TypeError):
      ${library_name_suffix}_${type_name}.open(None)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.open(unittest.source, mode="w")
