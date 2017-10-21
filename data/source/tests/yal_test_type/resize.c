/* Tests the lib${library_name_suffix}_${type_name}_resize function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_resize(
     void )
{
	libcerror_error_t *error                               = NULL;
	lib${library_name_suffix}_${type_name}_t *${type_name} = NULL;
	int result                                             = 0;

	/* Initialize test
	 */
	result = lib${library_name_suffix}_${type_name}_initialize(
	          &${type_name},
	          2,
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
	          NULL,
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

	/* Clean up
	 */
	result = lib${library_name_suffix}_${type_name}_free(
	          &${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${type_name} != NULL )
	{
		lib${library_name_suffix}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	return( 0 );
}

