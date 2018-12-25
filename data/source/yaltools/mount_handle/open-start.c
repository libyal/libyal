/* Opens a mount handle
 * Returns 1 if successful, 0 if not or -1 on error
 */
int mount_handle_open(
     mount_handle_t *mount_handle,
     const system_character_t *filename,
     libcerror_error_t **error )
{
	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type} = NULL;
	system_character_t *basename_end                                               = NULL;
	static char *function                                                          = "mount_handle_open";
	size_t basename_length                                                         = 0;
	size_t filename_length                                                         = 0;
	int result                                                                     = 0;

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
	if( filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid filename.",
		 function );

		return( -1 );
	}
