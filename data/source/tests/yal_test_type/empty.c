/* Tests the lib${library_name_suffix}_${type_name}_empty function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_empty(
     void )
{
	libcerror_error_t *error                               = NULL;
	lib${library_name_suffix}_${type_name}_t *${type_name} = NULL;
	int result                                             = 0;

	/* Initialize test
	 */
	result = lib${library_name_suffix}_${type_name}_initialize(
	          &${type_name},
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

	/* Test ${library_name}_test_${type_name}_empty
	 */
	result = lib${library_name_suffix}_${type_name}_empty(
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
	result = lib${library_name_suffix}_${type_name}_empty(
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

