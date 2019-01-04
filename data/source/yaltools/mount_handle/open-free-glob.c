	if( globbed_filenames != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( ${library_name}_glob_wide_free(
		     globbed_filenames,
		     number_of_filenames,
		     error ) != 1 )
#else
		if( ${library_name}_glob_free(
		     globbed_filenames,
		     number_of_filenames,
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free globbed filenames.",
			 function );

			goto on_error;
		}
	}
