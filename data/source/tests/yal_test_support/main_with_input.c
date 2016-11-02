/* The main program
 */
#if defined( LIBCSTRING_HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc,
     wchar_t * const argv[] )
#else
int main(
     int argc,
     char * const argv[] )
#endif
{
	libcstring_system_character_t *source = NULL;
	libcstring_system_integer_t option    = 0;

	while( ( option = libcsystem_getopt(
	                   argc,
	                   argv,
	                   _LIBCSTRING_SYSTEM_STRING( "" ) ) ) != (libcstring_system_integer_t) -1 )
	{
		switch( option )
		{
			case (libcstring_system_integer_t) '?':
			default:
				fprintf(
				 stderr,
				 "Invalid argument: %" PRIs_LIBCSTRING_SYSTEM ".\n",
				 argv[ optind - 1 ] );

				return( EXIT_FAILURE );
		}
	}
	if( optind < argc )
	{
		source = argv[ optind ];
	}

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_get_version",
	 ${library_name_suffix}_test_get_version );

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_get_access_flags_read",
	 ${library_name_suffix}_test_get_access_flags_read );

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_get_codepage",
	 ${library_name_suffix}_test_get_codepage );

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_set_codepage",
	 ${library_name_suffix}_test_set_codepage );

#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )
	if( source != NULL )
	{
		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_check_file_signature",
		 ${library_name_suffix}_test_check_file_signature,
		 source );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_check_file_signature_wide",
		 ${library_name_suffix}_test_check_file_signature_wide,
		 source );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

#if defined( LIB${library_name_suffix_upper_case}_HAVE_BFIO )

		/* TODO add test for ${library_name}_file_open_file_io_handle */

#endif /* defined( LIB${library_name_suffix_upper_case}_HAVE_BFIO ) */
	}
#endif /* !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 ) */

	return( EXIT_SUCCESS );

on_error:
	return( EXIT_FAILURE );
}

