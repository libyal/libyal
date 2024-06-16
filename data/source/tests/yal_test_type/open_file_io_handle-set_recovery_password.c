	if( recovery_password != NULL )
	{
		string_length = system_string_length(
		                 recovery_password );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = ${library_name}_${type_name}_set_utf16_recovery_password(
		          ${type_name},
		          (uint16_t *) recovery_password,
		          string_length,
		          &error );
#else
		result = ${library_name}_${type_name}_set_utf8_recovery_password(
		          ${type_name},
		          (uint8_t *) recovery_password,
		          string_length,
		          &error );
#endif
		${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
		 error );
	}
