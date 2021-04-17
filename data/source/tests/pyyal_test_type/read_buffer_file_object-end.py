
    with open(test_source, "rb") as file_object:
      ${library_name_suffix}_${type_name}.open_file_object(file_object)

      ${type_size_name} = ${library_name_suffix}_${type_name}.get_${type_size_name}()

      # Test normal read.
      data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), min(${type_size_name}, 4096))

      ${library_name_suffix}_${type_name}.close()
