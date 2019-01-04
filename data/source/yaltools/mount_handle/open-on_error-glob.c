	if( globbed_filenames != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		${library_name}_glob_wide_free(
		 globbed_filenames,
		 number_of_filenames,
		 NULL );
#else
		${library_name}_glob_free(
		 globbed_filenames,
		 number_of_filenames,
		 NULL );
#endif
	}
