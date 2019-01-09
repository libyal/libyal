	if( mount_handle->input_format == MOUNT_HANDLE_INPUT_FORMAT_FILES )
	{
		if( ${library_name}_handle_get_root_file_entry(
		     mount_handle->input_handle,
		     &( mount_handle->root_file_entry ),
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve root file entry.",
			 function );

			return( -1 );
		}
	}
