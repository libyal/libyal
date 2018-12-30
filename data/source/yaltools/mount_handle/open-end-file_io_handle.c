	mount_handle->file_io_handle = file_io_handle;

	return( 1 );

on_error:
	if( ${mount_tool_file_system_type} != NULL )
	{
		${library_name}_${mount_tool_file_system_type}_free(
		 &${mount_tool_file_system_type},
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

