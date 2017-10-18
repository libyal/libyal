/* Opens a parent ${mount_tool_source_type}
 * Returns 1 if successful, 0 if no parent or -1 on error
 */
int mount_handle_open_parent(
     mount_handle_t *mount_handle,
     ${library_name}_file_t *${mount_tool_source_type},
     libcerror_error_t **error )
{
	uint8_t guid[ 16 ];

	${library_name}_file_t *parent_${mount_tool_source_type}            = NULL;
	system_character_t *parent_basename_end = NULL;
	system_character_t *parent_filename     = NULL;
	system_character_t *parent_path         = NULL;
	static char *function                   = "mount_handle_open_parent";
	size_t parent_basename_length           = 0;
	size_t parent_filename_size             = 0;
	size_t parent_path_size                 = 0;
	int entry_index                         = 0;
	int result                              = 0;

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
	result = ${library_name}_file_get_parent_identifier(
	          ${mount_tool_source_type},
	          guid,
	          16,
	          error );

	if( result == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve parent content identifier.",
		 function );

		goto on_error;
	}
	else if( result != 1 )
	{
		return( 0 );
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_file_get_utf16_parent_filename_size(
		  ${mount_tool_source_type},
		  &parent_filename_size,
		  error );
#else
	result = ${library_name}_file_get_utf8_parent_filename_size(
		  ${mount_tool_source_type},
		  &parent_filename_size,
		  error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve parent filename size.",
		 function );

		goto on_error;
	}
	if( parent_filename_size == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing parent filename.",
		 function );

		goto on_error;
	}
	if( ( parent_filename_size > (size_t) SSIZE_MAX )
	 || ( ( sizeof( system_character_t ) * parent_filename_size ) > (size_t) SSIZE_MAX ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid parent filename size value exceeds maximum.",
		 function );

		goto on_error;
	}
	parent_filename = system_string_allocate(
			   parent_filename_size );

	if( parent_filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create parent filename string.",
		 function );

		goto on_error;
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = ${library_name}_file_get_utf16_parent_filename(
		  ${mount_tool_source_type},
		  (uint16_t *) parent_filename,
		  parent_filename_size,
		  error );
#else
	result = ${library_name}_file_get_utf8_parent_filename(
		  ${mount_tool_source_type},
		  (uint8_t *) parent_filename,
		  parent_filename_size,
		  error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve parent filename.",
		 function );

		goto on_error;
	}
	parent_basename_end = system_string_search_character_reverse(
	                       parent_filename,
	                       (system_character_t) '\\',
	                       parent_filename_size );

	if( parent_basename_end != NULL )
	{
		parent_basename_length = (size_t) ( parent_basename_end - parent_filename ) + 1;
	}
	if( mount_handle->basename == NULL )
	{
		parent_path      = &( parent_filename[ parent_basename_length ] );
		parent_path_size = parent_filename_size - ( parent_basename_length + 1 );
	}
	else
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( libcpath_path_join_wide(
		     &parent_path,
		     &parent_path_size,
		     mount_handle->basename,
		     mount_handle->basename_size - 1,
		     &( parent_filename[ parent_basename_length ] ),
		     parent_filename_size - ( parent_basename_length + 1 ),
		     error ) != 1 )
#else
		if( libcpath_path_join(
		     &parent_path,
		     &parent_path_size,
		     mount_handle->basename,
		     mount_handle->basename_size - 1,
		     &( parent_filename[ parent_basename_length ] ),
		     parent_filename_size - ( parent_basename_length + 1 ),
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
			 "%s: unable to create parent path.",
			 function );

			goto on_error;
		}
	}
	if( ${library_name}_file_initialize(
	     &parent_${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize parent ${mount_tool_source_type}.",
		 function );

		goto on_error;
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( ${library_name}_file_open_wide(
	     parent_${mount_tool_source_type},
	     parent_path,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#else
	if( ${library_name}_file_open(
	     parent_${mount_tool_source_type},
	     parent_path,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#endif
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open parent ${mount_tool_source_type}: %" PRIs_SYSTEM ".",
		 function,
		 parent_path );

		goto on_error;
	}
	if( mount_handle_open_input_parent_${mount_tool_source_type}(
	     mount_handle,
	     parent_${mount_tool_source_type},
	     error ) == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open parent ${mount_tool_source_type}.",
		 function );

		return( -1 );
	}
	if( ${library_name}_file_set_parent_file(
	     ${mount_tool_source_type},
	     parent_${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set parent file.",
		 function );

		goto on_error;
	}
	if( libcdata_array_append_entry(
	     mount_handle->inputs_array,
	     &entry_index,
	     (intptr_t *) parent_${mount_tool_source_type},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append parent ${mount_tool_source_type} to array.",
		 function );

		goto on_error;
	}
	if( parent_path != NULL )
	{
		if( mount_handle->basename != NULL )
		{
			memory_free(
			 parent_path );
		}
		parent_path = NULL;
	}
	if( parent_filename != NULL )
	{
		memory_free(
		 parent_filename );

		parent_filename = NULL;
	}
	return( 1 );

on_error:
	if( parent_${mount_tool_source_type} != NULL )
	{
		${library_name}_file_free(
		 &parent_${mount_tool_source_type},
		 NULL );
	}
	if( ( parent_path != NULL )
	 && ( mount_handle->basename != NULL ) )
	{
		memory_free(
		 parent_path );
	}
	if( parent_filename != NULL )
	{
		memory_free(
		 parent_filename );
	}
	return( -1 );
}

