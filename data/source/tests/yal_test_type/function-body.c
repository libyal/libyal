	/* Test regular cases
	 */
/* TODO: implement */

	/* Test error cases
	 */
	result = ${library_name}_${type_name}_${type_function}(
	          NULL,
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

