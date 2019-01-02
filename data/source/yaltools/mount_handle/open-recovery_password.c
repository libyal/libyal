	if( mount_handle->recovery_password != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( ${library_name}_${mount_tool_file_system_type}_set_utf16_recovery_password(
		     ${mount_tool_file_system_type_name},
		     (uint16_t *) mount_handle->recovery_password,
		     mount_handle->recovery_password_length,
		     error ) != 1 )
#else
		if( ${library_name}_${mount_tool_file_system_type}_set_utf8_recovery_password(
		     ${mount_tool_file_system_type_name},
		     (uint8_t *) mount_handle->recovery_password,
		     mount_handle->recovery_password_length,
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set recovery password.",
			 function );

			goto on_error;
		}
	}
