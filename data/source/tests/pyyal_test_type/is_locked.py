
  def test_is_locked(self):
    """Tests the is_locked function."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      raise unittest.SkipTest("missing source")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    ${library_name_suffix}_${type_name}.open(test_source)

    result = ${library_name_suffix}_${type_name}.is_locked()
    self.assertTrue(result)

    ${library_name_suffix}_${type_name}.close()

    test_password = getattr(unittest, "password", None)
    if test_password:
      ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
      ${library_name_suffix}_${type_name}.set_password(test_password)

      ${library_name_suffix}_${type_name}.open(test_source)

      result = ${library_name_suffix}_${type_name}.is_locked()
      self.assertFalse(result)

      ${library_name_suffix}_${type_name}.close()
