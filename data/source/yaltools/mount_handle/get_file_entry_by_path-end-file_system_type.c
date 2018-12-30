		if( filename != NULL )
		{
			memory_free(
			 filename );
		}
	}
	return( result );

on_error:
	if( filename != NULL )
	{
		memory_free(
		 filename );
	}
	if( ${mount_tool_file_entry_type} != NULL )
	{
		libolecf_${mount_tool_file_entry_type}_free(
		 &${mount_tool_file_entry_type},
		 NULL );
	}
	return( -1 );
}

