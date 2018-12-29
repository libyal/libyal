	if( libcdata_array_initialize(
	     &( ( *file_system )->${mount_tool_file_entry_type}s_array ),
	     0,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize ${mount_tool_file_entry_type_description}s array.",
		 function );

		goto on_error;
	}
