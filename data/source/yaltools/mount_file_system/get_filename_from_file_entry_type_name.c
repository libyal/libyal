#if defined( WINAPI )

/* Retrieves a filename from the ${mount_tool_file_entry_type_description} name
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_filename_from_${mount_tool_file_entry_type}_name(
     mount_file_system_t *file_system,
     const system_character_t *${mount_tool_file_entry_type}_name,
     size_t ${mount_tool_file_entry_type}_name_length,
     system_character_t **filename,
     size_t *filename_size,
     libcerror_error_t **error )
{
	system_character_t *safe_filename               = NULL;
	static char *function                           = "mount_file_system_get_filename_from_${mount_tool_file_entry_type}_name";
	system_character_t character_value              = 0;
	system_character_t hex_digit                    = 0;
	size_t ${mount_tool_file_entry_type}_name_index = 0;
	size_t filename_index                           = 0;
	size_t safe_filename_size                       = 0;

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
	if( ${mount_tool_file_entry_type}_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_entry_type_description} name.",
		 function );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type}_name_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid ${mount_tool_file_entry_type_description} name length value exceeds maximum.",
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
	if( filename_size == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid filename size.",
		 function );

		return( -1 );
	}
	*filename      = NULL;
	*filename_size = 0;

	safe_filename_size = ( ${mount_tool_file_entry_type}_name_length * 4 ) + 1;

	if( safe_filename_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid filename size value exceeds maximum.",
		 function );

		goto on_error;
	}
	safe_filename = system_string_allocate(
	                 safe_filename_size );

	if( safe_filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create filename.",
		 function );

		goto on_error;
	}
	filename_index = 0;

	for( ${mount_tool_file_entry_type}_name_index = 0;
	     ${mount_tool_file_entry_type}_name_index < ${mount_tool_file_entry_type}_name_length;
	     ${mount_tool_file_entry_type}_name_index++ )
	{
		character_value = ${mount_tool_file_entry_type}_name[ ${mount_tool_file_entry_type}_name_index ];

		if( character_value == 0x00 )
		{
			break;
		}
		/* Replace:
		 *   values <= 0x1f and 0x7f by ^x##
		 *   \ by ^x5c
		 *   ^ by ^^
		 */
		if( ( character_value <= 0x1f )
		 || ( character_value == (system_character_t) '\\' )
		 || ( character_value == 0x7f ) )
		{
			if( ( filename_index + 4 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = (system_character_t) '^';
			safe_filename[ filename_index++ ] = (system_character_t) 'x';

			hex_digit = character_value >> 4;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
			hex_digit = character_value & 0x0f;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
		}
		else if( character_value == (system_character_t) '^' )
		{
			if( ( filename_index + 2 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = (system_character_t) '^';
			safe_filename[ filename_index++ ] = (system_character_t) '^';
		}
		else
		{
			if( ( filename_index + 1 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = character_value;
		}
	}
	if( filename_index >= safe_filename_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid filename index value out of bounds.",
		 function );

		goto on_error;
	}
	safe_filename[ filename_index ] = 0;

	*filename      = safe_filename;
	*filename_size = safe_filename_size;

	return( 1 );

on_error:
	if( safe_filename != NULL )
	{
		memory_free(
		 safe_filename );
	}
	return( -1 );
}

#else

/* Retrieves a filename from the ${mount_tool_file_entry_type_description} name
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_filename_from_${mount_tool_file_entry_type}_name(
     mount_file_system_t *file_system,
     const system_character_t *${mount_tool_file_entry_type}_name,
     size_t ${mount_tool_file_entry_type}_name_length,
     system_character_t **filename,
     size_t *filename_size,
     libcerror_error_t **error )
{
	system_character_t *safe_filename               = NULL;
	static char *function                           = "mount_file_system_get_filename_from_${mount_tool_file_entry_type}_name";
	system_character_t character_value              = 0;
	system_character_t hex_digit                    = 0;
	size_t ${mount_tool_file_entry_type}_name_index = 0;
	size_t filename_index                           = 0;
	size_t safe_filename_size                       = 0;

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
	if( ${mount_tool_file_entry_type}_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_entry_type_description} name.",
		 function );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type}_name_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid ${mount_tool_file_entry_type_description} name length value exceeds maximum.",
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
	if( filename_size == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid filename size.",
		 function );

		return( -1 );
	}
	*filename      = NULL;
	*filename_size = 0;

	safe_filename_size = ( ${mount_tool_file_entry_type}_name_length * 4 ) + 1;

	if( safe_filename_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid filename size value exceeds maximum.",
		 function );

		goto on_error;
	}
	safe_filename = system_string_allocate(
	                 safe_filename_size );

	if( safe_filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create filename.",
		 function );

		goto on_error;
	}
	filename_index = 0;

	for( ${mount_tool_file_entry_type}_name_index = 0;
	     ${mount_tool_file_entry_type}_name_index < ${mount_tool_file_entry_type}_name_length;
	     ${mount_tool_file_entry_type}_name_index++ )
	{
		character_value = ${mount_tool_file_entry_type}_name[ ${mount_tool_file_entry_type}_name_index ];

		if( character_value == 0x00 )
		{
			break;
		}
		/* Replace:
		 *   values <= 0x1f and 0x7f by \x##
		 *   / by \x2f
		 *   \ by \\
		 */
		if( ( character_value <= 0x1f )
		 || ( character_value == (system_character_t) '/' )
		 || ( character_value == 0x7f ) )
		{
			if( ( filename_index + 4 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = (system_character_t) '\\';
			safe_filename[ filename_index++ ] = (system_character_t) 'x';

			hex_digit = character_value >> 4;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
			hex_digit = character_value & 0x0f;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
		}
		else if( character_value == (system_character_t) '\\' )
		{
			if( ( filename_index + 2 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = (system_character_t) '\\';
			safe_filename[ filename_index++ ] = (system_character_t) '\\';
		}
		else
		{
			if( ( filename_index + 1 ) > safe_filename_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid filename index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_filename[ filename_index++ ] = character_value;
		}
	}
	if( filename_index >= safe_filename_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid filename index value out of bounds.",
		 function );

		goto on_error;
	}
	safe_filename[ filename_index ] = 0;

	*filename      = safe_filename;
	*filename_size = safe_filename_size;

	return( 1 );

on_error:
	if( safe_filename != NULL )
	{
		memory_free(
		 safe_filename );
	}
	return( -1 );
}

#endif /* defined( WINAPI ) */

