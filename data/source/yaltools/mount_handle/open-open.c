#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( ${library_name}_file_open_wide(
	     ${mount_tool_source_type},
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#else
	if( ${library_name}_file_open(
	     ${mount_tool_source_type},
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#endif
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${mount_tool_source_type}.",
		 function );

		goto on_error;
	}
