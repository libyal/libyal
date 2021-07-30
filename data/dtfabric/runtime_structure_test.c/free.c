/* Tests the ${library_name}_${structure_name}_free function
 * Returns 1 if successful or 0 if not
 */
int ${prefix}_test_${structure_name}_free(
     void )
{
	libcerror_error_t *error = NULL;
	int result               = 0;

	/* Test error cases
	 */
	result = ${library_name}_${structure_name}_free(
	          NULL,
	          &error );

	${prefix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	${prefix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

