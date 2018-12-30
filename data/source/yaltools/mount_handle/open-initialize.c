	if( ${library_name}_${mount_tool_file_system_type}_initialize(
	     &${mount_tool_file_system_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize ${mount_tool_file_system_type_description}.",
		 function );

		goto on_error;
	}
