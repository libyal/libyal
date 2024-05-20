/* Retrieves the symbolic link target
 * The size should include the end of string character
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_symbolic_link_target(
     mount_file_entry_t *file_entry,
     system_character_t *string,
     size_t string_size,
     libcerror_error_t **error )
{
	static char *function = "mount_file_entry_get_symbolic_link_target";
	int result            = 0;

	if( file_entry == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file entry.",
		 function );

		return( -1 );
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf16_symbolic_link_target(
	          file_entry->${mount_tool_file_entry_type_name},
	          (uint16_t *) string,
	          string_size,
	          error );
#else
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf8_symbolic_link_target(
	          file_entry->${mount_tool_file_entry_type_name},
	          (uint8_t *) string,
	          string_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve symbolic link target string.",
		 function );

		return( -1 );
	}
	return( 1 );
}

