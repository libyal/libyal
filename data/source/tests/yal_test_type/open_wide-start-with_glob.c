#if defined( HAVE_WIDE_CHARACTER_TYPE )

/* Tests the ${library_name}_${type_name}_open_wide functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_wide(
${test_options_function_arguments} )
{
	wchar_t wide_source[ 256 ];

	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
	wchar_t **filenames                          = NULL;
	size_t wide_source_length                    = 0;
	int number_of_filenames                      = 0;
${test_options_function_variables}

	/* Initialize test
	 */
	result = ${library_name_suffix}_test_get_wide_source(
	          source,
	          wide_source,
	          256,
	          &error );

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	wide_source_length = wide_string_length(
	                      wide_source );

	result = ${library_name}_glob_wide(
	          wide_source,
	          wide_source_length,
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

