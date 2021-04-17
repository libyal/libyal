
    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
      ${library_name_suffix}_${type_name}.open_file_object(file_object)

      ${value_name} = ${library_name_suffix}_${type_name}.get_${value_name}()
      self.assertIsNotNone(${value_name})

      self.assertIsNotNone(${library_name_suffix}_${type_name}.${value_name})

      ${library_name_suffix}_${type_name}.close()
