	if( option_file_system_index != NULL )
	{
		if( mount_handle_set_file_system_index(
		     fsapfsmount_mount_handle,
		     option_file_system_index,
		     &error ) != 1 )
		{
			libcnotify_print_error_backtrace(
			 error );
			libcerror_error_free(
			 &error );

			fprintf(
			 stderr,
			 "Unsupported file system index defaulting to: all.\n" );
		}
	}
