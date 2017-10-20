	if( option_offset != NULL )
	{
		string_length = system_string_length(
		                 option_offset );

		result = ${library_name_suffix}_test_system_string_copy_from_64_bit_in_decimal(
		          option_offset,
		          string_length + 1,
		          (uint64_t *) &${type_name}_offset,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );
	}
