	result = ${library_name}_${type_name}_open_file_io_${bfio_type}(
	          *${type_name},
	          file_io_${bfio_type},
	          ${library_name_upper_case}_OPEN_READ,
	          error );

	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${type_name}.",
		 function );

		goto on_error;
	}
