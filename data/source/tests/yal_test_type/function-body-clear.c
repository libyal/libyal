	/* Test regular cases
	 */
	result = ${library_name}_${type_name}_clear(
	          ${type_name},
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
	result = ${library_name}_${type_name}_clear(
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

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )

	/* Test lib${library_name_suffix}_${type_name}_clear with memset failing
	 */
	${library_name_suffix}_test_memset_attempts_before_fail = 0;

	result = lib${library_name_suffix}_${type_name}_clear(
	          ${type_name},
	          &error );

	if( ${library_name_suffix}_test_memset_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_memset_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY ) */

