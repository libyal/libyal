/* Tests the ${library_name}_get_access_flags_read function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_get_access_flags_read(
     void )
{
	int access_flags = 0;

	access_flags = ${library_name}_get_access_flags_read();

	${library_name_suffix:upper_case}_TEST_ASSERT_EQUAL_INT(
	 "access_flags",
	 access_flags,
	 ${library_name:upper_case}_ACCESS_FLAG_READ );

	return( 1 );

on_error:
	return( 0 );
}

