
  def test_open(self):
    """Tests the open function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")
