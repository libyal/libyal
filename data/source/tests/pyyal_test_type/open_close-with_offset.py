
    test_offset = getattr(unittest, "offset", None)
    if test_offset:
      raise unittest.SkipTest("unsupported source with offset")
