
      ${library_name_suffix}_${type_name}.open_file_object(file_object)

      with self.assertRaises(IOError):
        ${library_name_suffix}_${type_name}.open_file_object(file_object)

      ${library_name_suffix}_${type_name}.close()

      # TODO: change IOError into TypeError
      with self.assertRaises(IOError):
        ${library_name_suffix}_${type_name}.open_file_object(None)

      with self.assertRaises(ValueError):
        ${library_name_suffix}_${type_name}.open_file_object(file_object, mode="w")
