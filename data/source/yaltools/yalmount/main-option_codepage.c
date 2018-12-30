	if( option_codepage != NULL )
	{
		result = mount_handle_set_ascii_codepage(
		          ${mount_tool_name}_mount_handle,
		          option_codepage,
		          &error );

		if( result == -1 )
		{
			fprintf(
			 stderr,
			 "Unable to set ASCII codepage in mount handle.\n" );

			goto on_error;
		}
		else if( result == 0 )
		{
			fprintf(
			 stderr,
			 "Unsupported ASCII codepage defaulting to: windows-1252.\n" );
		}
	}
