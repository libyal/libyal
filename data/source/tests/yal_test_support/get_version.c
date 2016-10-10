/* Tests the ${library_name}_get_version function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_get_version(
     void )
{
	const char *version_string = NULL;
	int result                 = 0;

	version_string = ${library_name}_get_version();

	result = libcstring_narrow_string_compare(
	          version_string,
	          ${library_name_upper_case}_VERSION_STRING,
	          9 );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 0 );

	return( 1 );

on_error:
	return( 0 );
}

