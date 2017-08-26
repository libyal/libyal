/* Tests the ${library_name}_${type_name}_open and ${library_name}_${type_name}_close functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_open_close(
     const system_character_t *source )
{
	libcerror_error_t *error = NULL;
	${library_name}_${type_name}_t *${type_name}      = NULL;
	int result               = 0;

	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
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

	/* Test open and close
	 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${type_name}_open_wide(
	          ${type_name},
	          source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );
#else
	result = ${library_name}_${type_name}_open(
	          ${type_name},
	          source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );
#endif

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_close(
	          ${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Test open and close a second time to validate clean up on close
	 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${type_name}_open_wide(
	          ${type_name},
	          source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );
#else
	result = ${library_name}_${type_name}_open(
	          ${type_name},
	          source,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );
#endif

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${type_name}_close(
	          ${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
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
		${library_name}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	return( 0 );
}

