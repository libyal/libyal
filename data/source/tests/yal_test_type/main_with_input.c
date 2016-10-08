/* The main program
 */
#if defined( LIBCSTRING_HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc,
     wchar_t * const argv[] )
#else
int main(
     int argc ,
     char * const argv[] )
#endif
{
	libcerror_error_t *error              = NULL;
	libcstring_system_character_t *source = NULL;
	${library_name}_${library_type}_t *${library_type}                   = NULL;
	libcstring_system_integer_t option    = 0;
	int result                            = 0;

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
#if defined( HAVE_DEBUG_OUTPUT ) && defined( ${library_name_suffix_upper_case}_TEST_FILE_VERBOSE )
	${library_name}_notify_set_verbose(
	 1 );
	${library_name}_notify_set_stream(
	 stderr,
	 NULL );
#endif

	${test_to_run}

#if !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 )
	if( source != NULL )
	{
		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${library_type}_open",
		 ${library_name_suffix}_test_${library_type}_open,
		 source );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

		${library_name_suffix_upper_case}_TEST_RUN_WITH_ARGS(
		 "${library_name}_${library_type}_open_wide",
		 ${library_name_suffix}_test_${library_type}_open_wide,
		 source );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

#if defined( ${library_name_upper_case}_HAVE_BFIO )

		/* TODO add test for ${library_name}_${library_type}_open_file_io_handle */

#endif /* defined( ${library_name_upper_case}_HAVE_BFIO ) */

		/* TODO add test for ${library_name}_${library_type}_close */

		/* Initialize test
		 */
		result = ${library_name_suffix}_test_${library_type}_open_source(
		          &${library_type},
		          source,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	         "${library_type}",
	         ${library_type} );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );

		${tests_to_run_with_input}

		/* Clean up
		 */
		result = ${library_name_suffix}_test_${library_type}_close_source(
		          &${library_type},
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 0 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "${library_type}",
	         ${library_type} );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );
	}
#endif /* !defined( __BORLANDC__ ) || ( __BORLANDC__ >= 0x0560 ) */

	return( EXIT_SUCCESS );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${library_type} != NULL )
	{
		${library_name_suffix}_test_${library_type}_close_source(
		 &${library_type},
		 NULL );
	}
	return( EXIT_FAILURE );
}

