/* Sets the format
 * Returns 1 if successful, 0 if unsupported value or -1 on error
 */
int mount_handle_set_format(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_set_format";
	size_t string_length  = 0;
	int result            = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	string_length = system_string_length(
	                 string );

	if( string_length == 3 )
	{
		if( system_string_compare(
		     string,
		     _SYSTEM_STRING( "raw" ),
		     3 ) == 0 )
		{
			mount_handle->input_format = MOUNT_HANDLE_INPUT_FORMAT_RAW;
			result                     = 1;
		}
	}
	else if( string_length == 5 )
	{
		if( system_string_compare(
		     string,
		     _SYSTEM_STRING( "files" ),
		     5 ) == 0 )
		{
			mount_handle->input_format = MOUNT_HANDLE_INPUT_FORMAT_FILES;
			result                     = 1;
		}
	}
	return( result );
}

