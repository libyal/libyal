
  def test_read_buffer_file_object(self):
    """Tests the read_buffer function on a file-like object."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      raise unittest.SkipTest("missing source")

    if not os.path.isfile(test_source):
      raise unittest.SkipTest("source not a regular file")

    ${library_name_suffix}_${type_name} = ${python_module_name}.${type_name}()
