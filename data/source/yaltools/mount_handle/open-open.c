#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_library_type}_open_wide(
	          ${mount_tool_source_type},
	          filename,
	          ${library_name_upper_case}_OPEN_READ,
	          error );
#else
	result = ${library_name}_${mount_tool_library_type}_open(
	          ${mount_tool_source_type},
	          filename,
	          ${library_name_upper_case}_OPEN_READ,
	          error );
#endif

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${mount_tool_source_type}.",
		 function );

		goto on_error;
	}
