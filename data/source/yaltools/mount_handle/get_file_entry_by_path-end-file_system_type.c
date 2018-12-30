	}
	return( result );

on_error:
	if( ${mount_tool_file_entry_type} != NULL )
	{
		${library_name}_${mount_tool_file_entry_type}_free(
		 &${mount_tool_file_entry_type},
		 NULL );
	}
	return( -1 );
}

