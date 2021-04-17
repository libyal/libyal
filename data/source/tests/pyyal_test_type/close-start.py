
  def test_close(self):
    """Tests the close function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
