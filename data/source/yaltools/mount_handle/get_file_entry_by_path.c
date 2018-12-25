/* Retrieves a file entry for a specific path
 * Returns 1 if successful, 0 if no such file entry or -1 on error
 */
int mount_handle_get_file_entry_by_path(
     mount_handle_t *mount_handle,
     const system_character_t *path,
     mount_file_entry_t **file_entry,
     libcerror_error_t **error )
{
	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type} = NULL;
	const system_character_t *filename                                             = NULL;
	static char *function                                                          = "mount_handle_get_file_entry_by_path";
	size_t path_length                                                             = 0;
	int ${mount_tool_file_entry_type}_index                                        = 0;
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
	if( path == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path.",
		 function );

		return( -1 );
	}
	path_length = system_string_length(
	               path );

	if( path_length == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid path length value out of bounds.",
		 function );

		return( -1 );
	}
	result = mount_file_system_get_${mount_tool_file_entry_type}_index_from_path(
	          mount_handle->file_system,
	          path,
	          path_length,
	          &${mount_tool_file_entry_type}_index,
	          error );

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description} index.",
		 function );

		return( -1 );
	}
	else if( result == 0 )
	{
		return( 0 );
	}
	if( ${mount_tool_file_entry_type}_index != -1 )
	{
		if( mount_file_system_get_${mount_tool_file_entry_type}_by_index(
		     mount_handle->file_system,
		     ${mount_tool_file_entry_type}_index,
		     &${mount_tool_file_entry_type},
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve ${mount_tool_file_entry_type_description}: %d.",
			 function,
			 ${mount_tool_file_entry_type}_index );

			return( -1 );
		}
		if( ${mount_tool_file_entry_type} == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
			 "%s: missing ${mount_tool_file_entry_type_description}: %d.",
			 function,
			 ${mount_tool_file_entry_type}_index );

			return( -1 );
		}
		filename = &( path[ 0 ] );
	}
	if( mount_file_entry_initialize(
	     file_entry,
	     mount_handle->file_system,
	     ${mount_tool_file_entry_type}_index,
	     filename,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize file entry for ${mount_tool_file_entry_type_description}: %d.",
		 function,
		 ${mount_tool_file_entry_type}_index );

		return( -1 );
	}
	return( 1 );
}

