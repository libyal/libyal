
  def test_get_${value_name}(self):
    """Tests the get_${value_name} function and ${value_name} property."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
