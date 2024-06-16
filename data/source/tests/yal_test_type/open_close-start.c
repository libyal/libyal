/* Tests the ${library_name}_${type_name}_open and ${library_name}_${type_name}_close functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_close(
${test_options_function_arguments} )
{
	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
${test_options_function_variables}

	/* Initialize test
	 */
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

