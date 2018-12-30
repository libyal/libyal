	if( mount_file_system_append_${mount_tool_file_system_type}(
	     mount_handle->file_system,
	     ${mount_tool_file_system_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append ${mount_tool_file_system_type_description} to file system.",
		 function );

		goto on_error;
	}
