/* Retrieves the filename from an ${mount_tool_file_entry_type_description}
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_filename_from_${mount_tool_file_entry_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type},
     system_character_t **filename,
     size_t *filename_size,
     libcerror_error_t **error )
{
	system_character_t *${mount_tool_file_entry_type}_name = NULL;
	static char *function                                  = "mount_file_system_get_filename_from_${mount_tool_file_entry_type}";
	size_t ${mount_tool_file_entry_type}_name_size         = 0;
	int result                                             = 0;

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
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf16_name_size(
	          ${mount_tool_file_entry_type},
	          &${mount_tool_file_entry_type}_name_size,
	          error );
#else
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf8_name_size(
	          ${mount_tool_file_entry_type},
	          &${mount_tool_file_entry_type}_name_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description} name size.",
		 function );

		goto on_error;
	}
	if( ( ${mount_tool_file_entry_type}_name_size == 0 )
	 || ( ${mount_tool_file_entry_type}_name_size > SSIZE_MAX ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid ${mount_tool_file_entry_type_description} name size value out of bounds.",
		 function );

		goto on_error;
	}
	${mount_tool_file_entry_type}_name = system_string_allocate(
	                                      ${mount_tool_file_entry_type}_name_size );

	if( ${mount_tool_file_entry_type}_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create ${mount_tool_file_entry_type_description} name string.",
		 function );

		goto on_error;
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf16_name(
	          ${mount_tool_file_entry_type},
	          (uint16_t *) ${mount_tool_file_entry_type}_name,
	          ${mount_tool_file_entry_type}_name_size,
	          error );
#else
	result = ${library_name}_${mount_tool_file_entry_type}_get_utf8_name(
	          ${mount_tool_file_entry_type},
	          (uint8_t *) ${mount_tool_file_entry_type}_name,
	          ${mount_tool_file_entry_type}_name_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve ${mount_tool_file_entry_type_description} name.",
		 function );

		goto on_error;
	}
	if( mount_file_system_get_filename_from_name(
	     file_system,
	     ${mount_tool_file_entry_type}_name,
	     ${mount_tool_file_entry_type}_name_size - 1,
	     filename,
	     filename_size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve a filename from the ${mount_tool_file_entry_type_description} name.",
		 function );

		goto on_error;
	}
	memory_free(
	 ${mount_tool_file_entry_type}_name );

	return( 1 );

on_error:
	if( ${mount_tool_file_entry_type}_name != NULL )
	{
		memory_free(
		 ${mount_tool_file_entry_type}_name );
	}
	return( -1 );
}

