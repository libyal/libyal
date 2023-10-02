    test_pasword = getattr(unittest, "password", None)
    if test_pasword:
      ${library_name_suffix}_${type_name}.set_password(test_pasword)
