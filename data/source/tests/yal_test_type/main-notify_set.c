#if defined( HAVE_DEBUG_OUTPUT ) && defined( ${library_name_suffix:upper_case}_TEST_${type_name:upper_case}_VERBOSE )
	${library_name}_notify_set_verbose(
	 1 );
	${library_name}_notify_set_stream(
	 stderr,
	 NULL );
#endif

