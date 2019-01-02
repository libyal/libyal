	}
	return( result );

on_error:
	if( ${mount_tool_file_entry_type_name} != NULL )
	{
		${library_name}_${mount_tool_file_entry_type}_free(
		 &${mount_tool_file_entry_type_name},
		 NULL );
	}
	return( -1 );
}

