/* Signals the mount ${mount_tool_file_system_type} system to abort
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_signal_abort(
     mount_file_system_t *file_system,
     libcerror_error_t **error )
{
	static char *function = "mount_file_system_signal_abort";

	if( file_system == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file system.",
		 function );

		return( -1 );
	}
	if( file_system->${mount_tool_file_system_type} != NULL )
	{
		if( ${library_name}_${mount_tool_file_system_type}_signal_abort(
		     file_system->${mount_tool_file_system_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to signal ${mount_tool_file_system_type_description} to abort.",
			 function );

			return( -1 );
		}
	}
	return( 1 );
}

