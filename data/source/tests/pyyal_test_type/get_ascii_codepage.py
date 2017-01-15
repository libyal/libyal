
  def test_get_ascii_codepage(self):
    """Tests the get_ascii_codepage function."""
    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()

    codepage = ${library_name_suffix}_${type_name}.get_ascii_codepage()
    self.assertIsNotNone(codepage)
