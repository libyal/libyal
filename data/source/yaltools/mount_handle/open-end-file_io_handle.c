	mount_handle->file_io_handle = file_io_handle;

	return( 1 );

on_error:
	if( ${mount_tool_base_type_name} != NULL )
	{
		${library_name}_${mount_tool_base_type}_free(
		 &${mount_tool_base_type_name},
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

