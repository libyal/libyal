#if defined( HAVE_WIDE_CHARACTER_TYPE )

/* Tests the ${library_name}_${type_name}_open_wide function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_wide(
${test_options_function_arguments} )
{
	wchar_t wide_source[ 256 ];

	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
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

