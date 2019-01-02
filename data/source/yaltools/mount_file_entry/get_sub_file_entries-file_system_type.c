/* Retrieves the number of sub file entries
 * Returns 1 if successful or -1 on error
 */
int mount_file_entry_get_number_of_sub_file_entries(
     mount_file_entry_t *file_entry,
     int *number_of_sub_file_entries,
     libcerror_error_t **error )
{
	static char *function = "mount_file_entry_get_number_of_sub_file_entries";

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
	if( ${library_name}_${mount_tool_file_entry_type}_get_number_of_sub_${mount_tool_file_entry_type}s(
	     file_entry->${mount_tool_file_entry_type_name},
	     number_of_sub_file_entries,
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
	${library_name}_${mount_tool_file_entry_type}_t *sub_${mount_tool_file_entry_type_name} = NULL;
	system_character_t *filename                                                            = NULL;
	static char *function                                                                   = "mount_file_entry_get_sub_file_entry_by_index";
	size_t filename_size                                                                    = 0;

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
/* TODO refactor to ${library_name}_${mount_tool_file_entry_type}_get_sub_${mount_tool_file_entry_type}_by_index */
	if( ${library_name}_${mount_tool_file_entry_type}_get_sub_${mount_tool_file_entry_type}(
	     file_entry->${mount_tool_file_entry_type_name},
	     sub_file_entry_index,
	     &sub_${mount_tool_file_entry_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve sub ${mount_tool_file_entry_type_description}: %d.",
		 function,
		 sub_file_entry_index );

		goto on_error;
	}
	if( mount_file_system_get_filename_from_${mount_tool_file_entry_type}(
	     file_entry->file_system,
	     sub_${mount_tool_file_entry_type_name},
	     &filename,
	     &filename_size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve filename of sub file entry: %d.",
		 function,
		 sub_file_entry_index );

		goto on_error;
	}
	if( mount_file_entry_initialize(
	     sub_file_entry,
	     file_entry->file_system,
	     filename,
	     filename_size - 1,
	     sub_${mount_tool_file_entry_type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize sub file entry: %d.",
		 function,
		 sub_file_entry_index );

		goto on_error;
	}
	if( filename != NULL )
	{
		memory_free(
		 filename );
	}
	return( 1 );

on_error:
	if( filename != NULL )
	{
		memory_free(
		 filename );
	}
	if( sub_${mount_tool_file_entry_type_name} != NULL )
	{
		${library_name}_${mount_tool_file_entry_type}_free(
		 &sub_${mount_tool_file_entry_type_name},
		 NULL );
	}
	return( -1 );
}

