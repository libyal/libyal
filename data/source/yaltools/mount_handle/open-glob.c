	if( number_of_filenames == 1 )
	{
		filename_length = system_string_length(
		                   filenames[ 0 ] );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = ${library_name}_glob_wide(
		          filenames[ 0 ],
		          filename_length,
		          &globbed_filenames,
		          &number_of_filenames,
		          error );
#else
		result = ${library_name}_glob(
		          filenames[ 0 ],
		          filename_length,
		          &globbed_filenames,
		          &number_of_filenames,
		          error );
#endif
		if( result != 1 )
		{
			libcerror_error_free(
			 error );

			number_of_filenames = 1;
		}
		else
		{
			filenames = (system_character_t * const *) globbed_filenames;
		}
	}
