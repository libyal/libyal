
    test_offset = getattr(unittest, "offset", None)

    with DataRangeFileObject(
        test_source, test_offset or 0, None) as file_object:
