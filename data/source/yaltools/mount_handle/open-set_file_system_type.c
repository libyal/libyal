	if( mount_file_system_set_${mount_tool_file_system_type}(
	     mount_handle->file_system,
	     ${mount_tool_file_system_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set ${mount_tool_file_system_type_description} in file system.",
		 function );

		goto on_error;
	}
