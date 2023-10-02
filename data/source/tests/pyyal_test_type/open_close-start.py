
  def test_open_close(self):
    """Tests the open and close functions."""
    test_source = getattr(unittest, "source", None)
    if not test_source:
      return
