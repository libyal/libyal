/* Retrieves the number of sub file entries
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_number_of_sub_file_entries(
     mount_file_entry_t *file_entry,
     int *number_of_sub_file_entries,
     libcerror_error_t **error )
{
	static char *function                        = "mount_file_entry_get_number_of_sub_file_entries";
	int number_of_${mount_tool_file_entry_type}s = 0;

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
	if( number_of_sub_file_entries == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid number of sub file entries.",
		 function );

		return( -1 );
	}
	if( file_entry->${mount_tool_file_entry_type_name} == NULL )
	{
		if( mount_file_system_get_number_of_${mount_tool_file_entry_type}s(
		     file_entry->file_system,
		     &number_of_${mount_tool_file_entry_type}s,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve number of ${mount_tool_file_entry_type_description}s.",
			 function );

			return( -1 );
		}
		if( ( number_of_${mount_tool_file_entry_type}s < 0 )
		 || ( number_of_${mount_tool_file_entry_type}s > 999 ) )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported number of ${mount_tool_file_entry_type_description}s.",
			 function );

			return( -1 );
		}
	}
	*number_of_sub_file_entries = number_of_${mount_tool_file_entry_type}s;

	return( 1 );
}

/* Retrieves the sub file entry for the specific index
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_sub_file_entry_by_index(
     mount_file_entry_t *file_entry,
     int sub_file_entry_index,
     mount_file_entry_t **sub_file_entry,
     libcerror_error_t **error )
{
	system_character_t path[ 32 ];

	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type_name} = NULL;
	static char *function                                                               = "mount_file_entry_get_sub_file_entry_by_index";
	size_t path_length                                                                  = 0;
	int number_of_sub_file_entries                                                      = 0;

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
	if( sub_file_entry == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid sub file entry.",
		 function );

		return( -1 );
	}
	if( *sub_file_entry != NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid sub file entry value already set.",
		 function );

		return( -1 );
	}
	if( mount_file_entry_get_number_of_sub_file_entries(
	     file_entry,
	     &number_of_sub_file_entries,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of sub file entries.",
		 function );

		return( -1 );
	}
	if( ( sub_file_entry_index < 0 )
	 || ( sub_file_entry_index >= number_of_sub_file_entries ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid sub file entry index value out of bounds.",
		 function );

		return( -1 );
	}
	if( mount_file_system_get_path_from_${mount_tool_file_entry_type}_index(
	     file_entry->file_system,
	     sub_file_entry_index,
	     path,
	     32,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve path for file entry: %d.",
		 function,
		 sub_file_entry_index );

		return( -1 );
	}
	if( mount_file_system_get_${mount_tool_file_entry_type}_by_index(
	     file_entry->file_system,
	     sub_file_entry_index,
	     &${mount_tool_file_entry_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description}: %d from file system.",
		 function,
		 sub_file_entry_index );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing ${mount_tool_file_entry_type_description}: %d.",
		 function,
		 sub_file_entry_index );

		return( -1 );
	}
	path_length = system_string_length(
	               path );

	if( mount_file_entry_initialize(
	     sub_file_entry,
	     file_entry->file_system,
	     &( path[ 1 ] ),
	     path_length - 1,
	     ${mount_tool_file_entry_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize sub file entry: %d.",
		 function,
		 sub_file_entry_index );

		return( -1 );
	}
	return( 1 );
}

