/* Tests the ${library_name}_${type_name}_open and ${library_name}_${type_name}_close functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_close(
${test_options_function_arguments} )
{
	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
	system_character_t **filenames               = NULL;
	size_t source_length                         = 0;
	int number_of_filenames                      = 0;
${test_options_function_variables}

	/* Initialize test
	 */
	source_length = system_string_length(
	                 source );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_glob_wide(
	          source,
	          source_length,
	          &filenames,
	          &number_of_filenames,
	          &error );
#else
	result = ${library_name}_glob(
	          source,
	          source_length,
	          &filenames,
	          &number_of_filenames,
	          &error );
#endif

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix:upper_case}_TEST_ASSERT_IS_NOT_NULL(
	 "filenames",
	 filenames );

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

