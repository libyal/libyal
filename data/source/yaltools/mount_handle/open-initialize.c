	if( ${library_name}_${mount_tool_base_type}_initialize(
	     &${mount_tool_base_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize ${mount_tool_base_type_description}.",
		 function );

		goto on_error;
	}
