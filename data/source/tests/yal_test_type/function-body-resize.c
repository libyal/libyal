	/* Test lib${library_name_suffix}_${type_name}_resize to resize to a larger number of entries
	 */
	result = lib${library_name_suffix}_${type_name}_resize(
	          ${type_name},
	          35,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test lib${library_name_suffix}_${type_name}_resize to resize to a smaller number of entries
	 */
	result = lib${library_name_suffix}_${type_name}_resize(
	          ${type_name},
	          4,
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
	result = lib${library_name_suffix}_${type_name}_resize(
	          NULL,
	          10,
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

	result = lib${library_name_suffix}_${type_name}_resize(
	          ${type_name},
	          -10,
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

#if INT_MAX == SSIZE_MAX

	result = lib${library_name_suffix}_${type_name}_resize(
	          ${type_name},
	          INT_MAX,
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

#endif /* INT_MAX == SSIZE_MAX */

