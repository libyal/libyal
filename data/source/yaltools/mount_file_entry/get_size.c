/* Retrieves the size
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_size(
     mount_file_entry_t *file_entry,
     size64_t *size,
     libcerror_error_t **error )
{
	static char *function = "mount_file_entry_get_size";

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
	if( file_entry->${mount_tool_file_entry_type_name} == NULL )
	{
		if( size == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
			 "%s: invalid size.",
			 function );

			return( -1 );
		}
		*size = 0;
	}
	else
	{
		if( ${library_name}_${mount_tool_file_entry_type}_get_${mount_tool_file_entry_type_size_value}(
		     file_entry->${mount_tool_file_entry_type_name},
		     size,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve ${mount_tool_file_entry_type_size_value_description} from ${mount_tool_file_entry_type_description}.",
			 function );

			return( -1 );
		}
	}
	return( 1 );
}

