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
	     file_entry->${mount_tool_file_entry_type},
	     number_of_sub_file_entries,
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
	${library_name}_${mount_tool_file_entry_type}_t *sub_${mount_tool_file_entry_type} = NULL;
	system_character_t *name                                                           = NULL;
	system_character_t *sub_${mount_tool_file_entry_type}_name                         = NULL;
	static char *function                                                              = "mount_file_entry_get_sub_file_entry_by_index";
	size_t name_size                                                                   = 0; 
	size_t sub_${mount_tool_file_entry_type}_name_size                                 = 0; 
	int result                                                                         = 0;

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
	     file_entry->${mount_tool_file_entry_type},
	     sub_file_entry_index,
	     &sub_${mount_tool_file_entry_type},
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
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf16_name_size(
	          sub_${mount_tool_file_entry_type},
	          &sub_${mount_tool_file_entry_type}_name_size,
	          error );
#else
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf8_name_size(
	          sub_${mount_tool_file_entry_type},
	          &sub_${mount_tool_file_entry_type}_name_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve sub ${mount_tool_file_entry_type_description} name size.",
		 function );

		goto on_error;
	}
	sub_${mount_tool_file_entry_type}_name = system_string_allocate(
	                                          sub_${mount_tool_file_entry_type}_name_size );

	if( sub_${mount_tool_file_entry_type}_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create sub ${mount_tool_file_entry_type_description} name string.",
		 function );

		goto on_error;
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf16_name(
	          sub_${mount_tool_file_entry_type},
	          (uint16_t *) sub_${mount_tool_file_entry_type}_name,
	          sub_${mount_tool_file_entry_type}_name_size,
	          error );
#else
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf8_name(
	          sub_${mount_tool_file_entry_type},
	          (uint8_t *) sub_${mount_tool_file_entry_type}_name,
	          sub_${mount_tool_file_entry_type}_name_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve sub ${mount_tool_file_entry_type_description} name.",
		 function );

		goto on_error;
	}
	if( mount_file_system_get_sanitized_filename(
	     file_entry->file_system,
	     sub_${mount_tool_file_entry_type}_name,
	     sub_${mount_tool_file_entry_type}_name_size - 1,
	     &name,
	     &name_size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve sub file entry name.",
		 function );

		goto on_error;
	}
	memory_free(
	 sub_${mount_tool_file_entry_type}_name );

	sub_${mount_tool_file_entry_type}_name = NULL;

	if( mount_file_entry_initialize(
	     sub_file_entry,
	     file_entry->file_system,
	     name,
	     sub_${mount_tool_file_entry_type},
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
	memory_free(
	 name );

	return( 1 );

on_error:
	if( sub_${mount_tool_file_entry_type}_name != NULL )
	{
		memory_free(
		 sub_${mount_tool_file_entry_type}_name );
	}
	if( name != NULL )
	{
		memory_free(
		 name );
	}
	if( sub_${mount_tool_file_entry_type} != NULL )
	{
		${library_name}_${mount_tool_file_entry_type}_free(
		 &sub_${mount_tool_file_entry_type},
		 NULL );
	}
	return( -1 );
}

