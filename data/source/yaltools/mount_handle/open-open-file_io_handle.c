	result = ${library_name}_${mount_tool_base_type}_open_file_io_handle(
	          ${mount_tool_base_type_name},
	          file_io_handle,
	          ${library_name_upper_case}_OPEN_READ,
	          error );

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${mount_tool_base_type_description}.",
		 function );

		goto on_error;
	}
