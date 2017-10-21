	}
	if( result != 0 )
	{
		/* Initialize ${type_name} for tests
		 */
		result = ${library_name_suffix}_test_${type_name}_open_source(
		          &${type_name},
${test_options_open_source_arguments},
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "${type_name}",
		 ${type_name} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "error",
		 error );

