
    # Test open and close.
    ${library_name_suffix}_${type_name}.open(test_source)
    ${library_name_suffix}_${type_name}.close()

    # Test open and close a second time to validate clean up on close.
    ${library_name_suffix}_${type_name}.open(test_source)
    ${library_name_suffix}_${type_name}.close()

    if os.path.isfile(test_source):
      with open(test_source, "rb") as file_object:

        # Test open_file_object and close.
        ${library_name_suffix}_${type_name}.open_file_object(file_object)
        ${library_name_suffix}_${type_name}.close()

        # Test open_file_object and close a second time to validate clean up on close.
        ${library_name_suffix}_${type_name}.open_file_object(file_object)
        ${library_name_suffix}_${type_name}.close()

        # Test open_file_object and close and dereferencing file_object.
        ${library_name_suffix}_${type_name}.open_file_object(file_object)
        del file_object
        ${library_name_suffix}_${type_name}.close()
