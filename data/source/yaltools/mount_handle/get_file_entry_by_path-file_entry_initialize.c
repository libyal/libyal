		if( mount_file_entry_initialize(
		     file_entry,
		     mount_handle->file_system,
		     filename,
		     ${mount_tool_file_entry_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
			 "%s: unable to initialize file entry for ${mount_tool_file_entry_type_description}.",
			 function );

			goto on_error;
		}
