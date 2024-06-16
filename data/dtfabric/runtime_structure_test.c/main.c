/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc ${prefix:upper_case}_TEST_ATTRIBUTE_UNUSED,
     wchar_t * const argv[] ${prefix:upper_case}_TEST_ATTRIBUTE_UNUSED )
#else
int main(
     int argc ${prefix:upper_case}_TEST_ATTRIBUTE_UNUSED,
     char * const argv[] ${prefix:upper_case}_TEST_ATTRIBUTE_UNUSED )
#endif
{
	${prefix:upper_case}_TEST_UNREFERENCED_PARAMETER( argc )
	${prefix:upper_case}_TEST_UNREFERENCED_PARAMETER( argv )

#if defined( __GNUC__ ) && !defined( ${library_name:upper_case}_DLL_IMPORT )

	${prefix:upper_case}_TEST_RUN(
	 "${library_name}_${structure_name}_initialize",
	 ${prefix}_test_${structure_name}_initialize );

	${prefix:upper_case}_TEST_RUN(
	 "${library_name}_${structure_name}_free",
	 ${prefix}_test_${structure_name}_free );

	${prefix:upper_case}_TEST_RUN(
	 "${library_name}_${structure_name}_read_data",
	 ${prefix}_test_${structure_name}_read_data );

	${prefix:upper_case}_TEST_RUN(
	 "${library_name}_${structure_name}_read_file_io_handle",
	 ${prefix}_test_${structure_name}_read_file_io_handle );

#endif /* defined( __GNUC__ ) && !defined( ${library_name:upper_case}_DLL_IMPORT ) */

	return( EXIT_SUCCESS );

#if defined( __GNUC__ ) && !defined( ${library_name:upper_case}_DLL_IMPORT )

on_error:
	return( EXIT_FAILURE );

#endif /* defined( __GNUC__ ) && !defined( ${library_name:upper_case}_DLL_IMPORT ) */
}

