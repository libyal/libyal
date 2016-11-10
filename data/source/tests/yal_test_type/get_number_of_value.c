/* Tests the ${library_name}_${type_name}_get_number_of_${value_name} functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_get_number_of_${value_name}(
     ${library_name}_${type_name}_t *${type_name} )
{
	libcerror_error_t *error = NULL;
	int number_of_${value_name}    = 0;
	int result               = 0;

	result = ${library_name}_${type_name}_get_number_of_${value_name}(
	          ${type_name},
	          &number_of_${value_name},
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
	result = ${library_name}_${type_name}_get_number_of_${value_name}(
	          NULL,
	          &number_of_${value_name},
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

	result = ${library_name}_${type_name}_get_number_of_${value_name}(
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

