
  def test_get_${value_name}(self):
    """Tests the get_${value_name} function and ${value_name} property."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
    ${library_name_suffix}_${type_name}.open(unittest.source)

    ${value_name} = ${library_name_suffix}_${type_name}.get_${value_name}()
    self.assertIsNotNone(${value_name})

    self.assertIsNotNone(${library_name_suffix}_${type_name}.${value_name})

    ${library_name_suffix}_${type_name}.close()
