	return( 0 );

on_error:
	if( ${mount_tool_file_system_type_name} != NULL )
	{
		${library_name}_${mount_tool_file_system_type}_free(
		 &${mount_tool_file_system_type_name},
		 NULL );
	}
	return( -1 );
}

