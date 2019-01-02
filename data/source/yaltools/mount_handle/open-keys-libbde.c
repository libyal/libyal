	if( mount_handle->full_volume_encryption_key_size > 0 )
	{
		if( ${library_name}_${mount_tool_file_system_type}_set_keys(
		     ${mount_tool_file_system_type_name},
		     mount_handle->key_data,
		     mount_handle->full_volume_encryption_key_size,
		     &( mount_handle->key_data[ 32 ] ),
		     mount_handle->tweak_key_size,
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
