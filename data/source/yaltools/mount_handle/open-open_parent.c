	if( mount_handle_open_parent(
	     mount_handle,
	     ${mount_tool_base_type_name},
	     error ) == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open parent ${mount_tool_base_type_description}.",
		 function );

		goto on_error;
	}
