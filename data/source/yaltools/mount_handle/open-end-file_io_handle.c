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
	mount_handle->file_io_handle = file_io_handle;

	return( 1 );

on_error:
	if( ${mount_tool_source_type} != NULL )
	{
		${library_name}_${mount_tool_library_type}_free(
		 &${mount_tool_source_type},
		 NULL );
	}
	if( file_io_handle != NULL )
	{
		libbfio_handle_free(
		 &file_io_handle,
		 NULL );
	}
	return( -1 );
}

