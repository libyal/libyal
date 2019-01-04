	return( 1 );

on_error:
	if( ${mount_tool_base_type_name} != NULL )
	{
		${library_name}_${mount_tool_base_type}_free(
		 &${mount_tool_base_type_name},
		 NULL );
	}
