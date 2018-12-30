#if defined( WINAPI )

/* Retrieves the sanitized filename
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_sanitized_filename(
     mount_file_system_t *file_system,
     const system_character_t *item_name,
     size_t item_name_length,
     system_character_t **sanitized_name,
     size_t *sanitized_name_size,
     libcerror_error_t **error )
{
	system_character_t *safe_sanitized_name = NULL;
	static char *function                   = "mount_file_system_get_sanitized_filename";
	system_character_t character_value      = 0;
	system_character_t hex_digit            = 0;
	size_t item_name_index                  = 0;
	size_t safe_sanitized_name_size         = 0;
	size_t sanitized_name_index             = 0;

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
	if( item_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid item name.",
		 function );

		return( -1 );
	}
	if( item_name_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid item name length value exceeds maximum.",
		 function );

		return( -1 );
	}
	if( sanitized_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid sanitized name.",
		 function );

		return( -1 );
	}
	if( sanitized_name_size == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid sanitized name size.",
		 function );

		return( -1 );
	}
	*sanitized_name      = NULL;
	*sanitized_name_size = 0;

	safe_sanitized_name_size = ( item_name_length * 4 ) + 1;

	if( safe_sanitized_name_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid sanitized name size value exceeds maximum.",
		 function );

		goto on_error;
	}
	safe_sanitized_name = system_string_allocate(
	                       safe_sanitized_name_size );

	if( safe_sanitized_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create sanitized name.",
		 function );

		goto on_error;
	}
	sanitized_name_index = 0;

	for( item_name_index = 0;
	     item_name_index < item_name_length;
	     item_name_index++ )
	{
		character_value = item_name[ item_name_index ];

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
			if( ( sanitized_name_index + 4 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '^';
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'x';

			hex_digit = character_value >> 4;

			if( hex_digit <= 0x09 )
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
			hex_digit = character_value & 0x0f;

			if( hex_digit <= 0x09 )
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
		}
		else if( character_value == (system_character_t) '^' )
		{
			if( ( sanitized_name_index + 2 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '^';
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '^';
		}
		else
		{
			if( ( sanitized_name_index + 1 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = character_value;
		}
	}
	if( sanitized_name_index >= safe_sanitized_name_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid sanitized name index value out of bounds.",
		 function );

		goto on_error;
	}
	safe_sanitized_name[ sanitized_name_index ] = 0;

	*sanitized_name      = safe_sanitized_name;
	*sanitized_name_size = safe_sanitized_name_size;

	return( 1 );

on_error:
	if( safe_sanitized_name != NULL )
	{
		memory_free(
		 safe_sanitized_name );
	}
	return( -1 );
}

#else

/* Retrieves the sanitized filename
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_sanitized_filename(
     mount_file_system_t *file_system,
     const system_character_t *item_name,
     size_t item_name_length,
     system_character_t **sanitized_name,
     size_t *sanitized_name_size,
     libcerror_error_t **error )
{
	system_character_t *safe_sanitized_name = NULL;
	static char *function                   = "mount_file_system_get_sanitized_filename";
	system_character_t character_value      = 0;
	system_character_t hex_digit            = 0;
	size_t item_name_index                  = 0;
	size_t safe_sanitized_name_size         = 0;
	size_t sanitized_name_index             = 0;

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
	if( item_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid item name.",
		 function );

		return( -1 );
	}
	if( item_name_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid item name length value exceeds maximum.",
		 function );

		return( -1 );
	}
	if( sanitized_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid sanitized name.",
		 function );

		return( -1 );
	}
	if( sanitized_name_size == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid sanitized name size.",
		 function );

		return( -1 );
	}
	*sanitized_name      = NULL;
	*sanitized_name_size = 0;

	safe_sanitized_name_size = ( item_name_length * 4 ) + 1;

	if( safe_sanitized_name_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid sanitized name size value exceeds maximum.",
		 function );

		goto on_error;
	}
	safe_sanitized_name = system_string_allocate(
	                       safe_sanitized_name_size );

	if( safe_sanitized_name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create sanitized name.",
		 function );

		goto on_error;
	}
	sanitized_name_index = 0;

	for( item_name_index = 0;
	     item_name_index < item_name_length;
	     item_name_index++ )
	{
		character_value = item_name[ item_name_index ];

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
			if( ( sanitized_name_index + 4 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '\\';
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'x';

			hex_digit = character_value >> 4;

			if( hex_digit <= 0x09 )
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
			hex_digit = character_value & 0x0f;

			if( hex_digit <= 0x09 )
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
		}
		else if( character_value == (system_character_t) '\\' )
		{
			if( ( sanitized_name_index + 2 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '\\';
			safe_sanitized_name[ sanitized_name_index++ ] = (system_character_t) '\\';
		}
		else
		{
			if( ( sanitized_name_index + 1 ) > safe_sanitized_name_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid sanitized name index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_sanitized_name[ sanitized_name_index++ ] = character_value;
		}
	}
	if( sanitized_name_index >= safe_sanitized_name_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid sanitized name index value out of bounds.",
		 function );

		goto on_error;
	}
	safe_sanitized_name[ sanitized_name_index ] = 0;

	*sanitized_name      = safe_sanitized_name;
	*sanitized_name_size = safe_sanitized_name_size;

	return( 1 );

on_error:
	if( safe_sanitized_name != NULL )
	{
		memory_free(
		 safe_sanitized_name );
	}
	return( -1 );
}

#endif /* defined( WINAPI ) */

