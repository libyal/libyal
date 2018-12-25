	result = ${library_name}_${mount_tool_library_type}_is_locked(
	          ${mount_tool_source_type},
	          error );

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to determine if ${mount_tool_source_type} is locked.",
		 function );

		goto on_error;
	}
	mount_handle->is_locked = result;

