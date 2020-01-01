	/* Test regular cases
	 */
	result = lib${library_name_suffix}_${type_name}_empty(
	          ${type_name},
	          &${library_name_suffix}_test_${type_name}_${value_name}_free_function,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test error cases
	 */
	result = lib${library_name_suffix}_${type_name}_empty(
	          NULL,
	          &${library_name_suffix}_test_${type_name}_${value_name}_free_function,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

