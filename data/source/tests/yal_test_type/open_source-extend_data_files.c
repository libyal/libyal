	if( ${library_name}_${type_name}_open_extent_data_files(
	     *${type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open extent data files.",
		 function );

		goto on_error;
	}
