	if( mount_handle->startup_key_path != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( ${library_name}_${mount_tool_file_system_type}_read_startup_key_wide(
		     ${mount_tool_file_system_type_name},
		     mount_handle->startup_key_path,
		     error ) != 1 )
#else
		if( ${library_name}_${mount_tool_file_system_type}_read_startup_key(
		     ${mount_tool_file_system_type_name},
		     mount_handle->startup_key_path,
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_IO,
			 LIBCERROR_IO_ERROR_READ_FAILED,
			 "%s: unable to read startup key.",
			 function );

			goto on_error;
		}
	}
