	result = ${library_name}_${mount_tool_library_type}_open_file_io_handle(
	          ${mount_tool_source_type},
	          file_io_handle,
	          ${library_name_upper_case}_OPEN_READ,
	          error );

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${mount_tool_source_type}.",
		 function );

		goto on_error;
	}
