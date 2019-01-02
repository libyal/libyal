		if( mount_file_entry_initialize(
		     file_entry,
		     mount_handle->file_system,
		     filename,
		     filename_length,
		     ${mount_tool_file_entry_type_name},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
			 "%s: unable to initialize file entry.",
			 function );

			goto on_error;
		}
