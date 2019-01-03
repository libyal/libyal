	if( option_encrypted_root_plist_path != NULL )
	{
		if( mount_handle_set_encrypted_root_plist(
		     ${mount_tool_name}_mount_handle,
		     option_encrypted_root_plist_path,
		     &error ) != 1 )
		{
			fprintf(
			 stderr,
			 "Unable to set encrypted root plist.\n" );

			goto on_error;
		}
	}
