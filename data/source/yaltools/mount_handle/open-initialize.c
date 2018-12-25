	if( ${library_name}_${mount_tool_file_entry_type}_initialize(
	     &${mount_tool_file_entry_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize ${mount_tool_file_entry_type_description}.",
		 function );

		goto on_error;
	}
