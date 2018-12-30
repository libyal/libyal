	if( mount_handle->key_size > 0 )
	{
		if( ${library_name}_${mount_tool_file_system_type}_set_keys(
		     ${mount_tool_file_system_type},
		     mount_handle->key_data,
		     mount_handle->key_size,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set keys.",
			 function );

			goto on_error;
		}
	}
