
    ${library_name_suffix}_${type_name}.open(test_source)

    ${value_name} = ${library_name_suffix}_${type_name}.get_${value_name}()
    self.assertIsNotNone(${value_name})

    self.assertIsNotNone(${library_name_suffix}_${type_name}.${value_name})

    ${library_name_suffix}_${type_name}.close()
