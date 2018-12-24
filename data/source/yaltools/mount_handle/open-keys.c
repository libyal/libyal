	if( mount_handle->key_data_is_set != 0 )
	{
		if( ${library_name}_file_set_keys(
		     ${mount_tool_source_type},
		     mount_handle->key_data,
		     16,
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
