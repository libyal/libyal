
  def test_get_${value_name}(self):
    """Tests the get_${value_name} function."""
    if not unittest.source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
