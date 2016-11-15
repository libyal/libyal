/* Tests the ${library_name}_${type_name}_get_ascii_codepage function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_get_ascii_codepage(
     ${library_name}_${type_name}_t *${type_name} )
{
	libcerror_error_t *error = NULL;
	int codepage             = 0;
	int result               = 0;

	result = ${library_name}_${type_name}_get_ascii_codepage(
	          ${type_name},
	          &codepage,
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
	result = ${library_name}_${type_name}_get_ascii_codepage(
	          NULL,
	          &codepage,
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

	result = ${library_name}_${type_name}_get_ascii_codepage(
	          ${type_name},
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

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

