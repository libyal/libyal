		/* Ignore the name of the root item
		 */
		if( path_length > 1 )
		{
			if( mount_file_system_get_filename_from_item(
			     mount_handle->file_system,
			     ${mount_tool_file_entry_type},
			     &filename,
			     &filename_size,
			     error ) != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
				 "%s: unable to retrieve filename.",
				 function );

				goto on_error;
			}
		}
