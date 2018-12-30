/* Retrieves the file mode
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_file_mode(
     mount_file_entry_t *file_entry,
     uint16_t *file_mode,
     libcerror_error_t **error )
{
	static char *function                            = "mount_file_entry_get_file_mode";
	int number_of_sub_${mount_tool_file_entry_type}s = 0;

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
	if( file_mode == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file mode.",
		 function );

		return( -1 );
	}
	if( ${library_name}_${mount_tool_file_entry_type}_get_number_of_sub_${mount_tool_file_entry_type}s(
	     file_entry->${mount_tool_file_entry_type},
	     &number_of_sub_${mount_tool_file_entry_type}s,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of sub ${mount_tool_file_entry_type_description}s.",
		 function );

		return( -1 );
	}
	if( number_of_sub_${mount_tool_file_entry_type}s > 0 )
	{
		*file_mode = S_IFDIR | 0555;
	}
	else
	{
		*file_mode = S_IFREG | 0444;
	}
	return( 1 );
}

