	if( mount_handle->encrypted_root_plist_path != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( ${library_name}_${mount_tool_file_system_type}_read_encrypted_root_plist_wide(
		     ${mount_tool_file_system_type_name},
		     mount_handle->encrypted_root_plist_path,
		     error ) != 1 )
#else
		if( ${library_name}_${mount_tool_file_system_type}_read_encrypted_root_plist(
		     ${mount_tool_file_system_type_name},
		     mount_handle->encrypted_root_plist_path,
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_IO,
			 LIBCERROR_IO_ERROR_READ_FAILED,
			 "%s: unable to read encrypted root plist.",
			 function );

			goto on_error;
		}
	}
