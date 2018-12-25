	if( mount_file_system_append_${mount_tool_file_entry_type}(
	     mount_handle->file_system,
	     ${mount_tool_file_entry_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append ${mount_tool_file_entry_type_description} to file system.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( ${mount_tool_file_entry_type} != NULL )
	{
		${library_name}_${mount_tool_file_entry_type}_free(
		 &${mount_tool_file_entry_type},
		 NULL );
	}
	return( -1 );
}

