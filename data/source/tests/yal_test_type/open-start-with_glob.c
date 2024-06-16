/* Tests the ${library_name}_${type_name}_open function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open(
${test_options_function_arguments} )
{
	char narrow_source[ 256 ];

	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
	char **filenames                             = NULL;
	size_t narrow_source_length                  = 0;
	int number_of_filenames                      = 0;
${test_options_function_variables}

	/* Initialize test
	 */
	result = ${library_name_suffix}_test_get_narrow_source(
	          source,
	          narrow_source,
	          256,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	narrow_source_length = narrow_string_length(
	                        narrow_source );

	result = ${library_name}_glob(
	          narrow_source,
	          narrow_source_length,
	          &filenames,
	          &number_of_filenames,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "filenames",
	 filenames );

	${library_name_suffix:upper_case}_TEST_ASSERT_GREATER_THAN_INT(
	 "number_of_filenames",
	 number_of_filenames,
	 0 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "${type_name}",
	 ${type_name} );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

