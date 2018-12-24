	if( mount_file_system_append_${mount_tool_source_type}(
	     mount_handle->file_system,
	     ${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append ${mount_tool_source_type} to file system.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( ${mount_tool_source_type} != NULL )
	{
		${library_name}_file_free(
		 &${mount_tool_source_type},
		 NULL );
	}
	return( -1 );
}

