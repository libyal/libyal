    test_recovery_password = getattr(unittest, "recovery_password", None)
    if test_recovery_password:
      ${library_name_suffix}_${type_name}.set_recovery_password(test_recovery_password)
