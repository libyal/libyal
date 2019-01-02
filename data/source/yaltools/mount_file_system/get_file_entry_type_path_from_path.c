/* Retrieves the ${mount_tool_file_entry_type_description} path from the path
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_path_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     system_character_t **${mount_tool_file_entry_type}_path,
     size_t *${mount_tool_file_entry_type}_path_size,
     libcerror_error_t **error )
{
	system_character_t *safe_${mount_tool_file_entry_type}_path = NULL;
	static char *function                                       = "mount_file_system_get_${mount_tool_file_entry_type}_path_from_path";
	libuna_unicode_character_t unicode_character                = 0;
	system_character_t character                                = 0;
	system_character_t escape_character                         = 0;
	system_character_t hex_digit                                = 0;
	system_character_t hex_value                                = 0;
	size_t ${mount_tool_file_entry_type}_path_index             = 0;
	size_t path_index                                           = 0;
	size_t safe_${mount_tool_file_entry_type}_path_size         = 0;
	int result                                                  = 0;

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
	if( path_length == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid path length.",
		 function );

		return( -1 );
	}
	if( path_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid path length value exceeds maximum.",
		 function );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type}_path == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_entry_type_description} path.",
		 function );

		return( -1 );
	}
	if( ${mount_tool_file_entry_type}_path_size == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${mount_tool_file_entry_type_description} path size.",
		 function );

		return( -1 );
	}
	if( path[ 0 ] != (system_character_t) LIBCPATH_SEPARATOR )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported path - path is not absolute.",
		 function );

		return( -1 );
	}
	*${mount_tool_file_entry_type}_path      = NULL;
	*${mount_tool_file_entry_type}_path_size = 0;

	safe_${mount_tool_file_entry_type}_path_size = path_length + 1;

	if( safe_${mount_tool_file_entry_type}_path_size > (size_t) ( SSIZE_MAX / sizeof( system_character_t ) ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid ${mount_tool_file_entry_type_description} path size value exceeds maximum.",
		 function );

		goto on_error;
	}
	safe_${mount_tool_file_entry_type}_path = system_string_allocate(
	                                           safe_${mount_tool_file_entry_type}_path_size );

	if( safe_${mount_tool_file_entry_type}_path == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create ${mount_tool_file_entry_type_description} path.",
		 function );

		goto on_error;
	}
#if defined( WINAPI )
	escape_character = (system_character_t) '^';
#else
	escape_character = (system_character_t) '\\';
#endif

	while( path_index < path_length )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = libuna_unicode_character_copy_from_utf16(
		          &unicode_character,
		          (libuna_utf16_character_t *) path,
		          path_length,
		          &path_index,
		          error );
#else
		result = libuna_unicode_character_copy_from_utf8(
		          &unicode_character,
		          (libuna_utf8_character_t *) path,
		          path_length,
		          &path_index,
		          error );
#endif
		if( result != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_CONVERSION,
			 LIBCERROR_CONVERSION_ERROR_INPUT_FAILED,
			 "%s: unable to copy Unicode character from path.",
			 function );

			goto on_error;
		}
		/* On Windows replaces:
		 *   ^^ by ^
		 *   ^x5c by \
		 *   ^x## by values <= 0x1f and 0x7f
		 *
		 * On other platforms replaces:
		 *   \\ by \
		 *   \x2f by /
		 *   \x## by values <= 0x1f and 0x7f
		 *   / by \
		 */
		if( unicode_character == escape_character )
		{
			if( ( path_index + 1 ) > path_length )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid path index value out of bounds.",
				 function );

				goto on_error;
			}
			character = path[ path_index++ ];

#if defined( WINAPI )
			if( ( character != escape_character )
			 && ( character != (system_character_t) 'X' )
			 && ( character != (system_character_t) 'x' ) )
#else
			if( ( character != escape_character )
			 && ( character != (system_character_t) 'x' ) )
#endif
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
				 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
				 "%s: unsupported path - invalid character: %" PRIc_SYSTEM " after escape character.",
				 function,
				 character );

				goto on_error;
			}
			if( character == escape_character )
			{
				if( ( ${mount_tool_file_entry_type}_path_index + 1 ) > safe_${mount_tool_file_entry_type}_path_size )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid ${mount_tool_file_entry_type_description} path index value out of bounds.",
					 function );

					goto on_error;
				}
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = escape_character;
			}
			else
			{
				if( ( path_index + 2 ) > path_length )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid path index value out of bounds.",
					 function );

					goto on_error;
				}
				hex_digit = path[ path_index++ ];

				if( ( hex_digit >= (system_character_t) '0' )
				 && ( hex_digit <= (system_character_t) '9' ) )
				{
					hex_value = hex_digit - (system_character_t) '0';
				}
#if defined( WINAPI )
				else if( ( hex_digit >= (system_character_t) 'A' )
				      && ( hex_digit <= (system_character_t) 'F' ) )
				{
					hex_value = hex_digit - (system_character_t) 'A' + 10;
				}
#endif
				else if( ( hex_digit >= (system_character_t) 'a' )
				      && ( hex_digit <= (system_character_t) 'f' ) )
				{
					hex_value = hex_digit - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
					 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
					 "%s: unsupported path - invalid hexadecimal character: %" PRIc_SYSTEM " after escape character.",
					 function,
					 hex_digit );

					goto on_error;
				}
				hex_value <<= 4;

				hex_digit = path[ path_index++ ];

				if( ( hex_digit >= (system_character_t) '0' )
				 && ( hex_digit <= (system_character_t) '9' ) )
				{
					hex_value |= hex_digit - (system_character_t) '0';
				}
#if defined( WINAPI )
				else if( ( hex_digit >= (system_character_t) 'A' )
				      && ( hex_digit <= (system_character_t) 'F' ) )
				{
					hex_value = hex_digit - (system_character_t) 'A' + 10;
				}
#endif
				else if( ( hex_digit >= (system_character_t) 'a' )
				      && ( hex_digit <= (system_character_t) 'f' ) )
				{
					hex_value |= hex_digit - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
					 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
					 "%s: unsupported path - invalid hexadecimal character: %" PRIc_SYSTEM " after escape character.",
					 function,
					 hex_digit );

					goto on_error;
				}
#if defined( WINAPI )
				if( ( hex_value == 0 )
				 || ( ( hex_value > 0x1f )
				  &&  ( hex_value != 0x5c )
				  &&  ( hex_value != 0x7f ) ) )
#else
				if( ( hex_value == 0 )
				 || ( ( hex_value > 0x1f )
				  &&  ( hex_value != 0x2f )
				  &&  ( hex_value != 0x7f ) ) )
#endif
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				if( ( ${mount_tool_file_entry_type}_path_index + 1 ) > safe_${mount_tool_file_entry_type}_path_size )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid ${mount_tool_file_entry_type_description} path index value out of bounds.",
					 function );

					goto on_error;
				}
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = hex_value;
			}
		}
#if !defined( WINAPI )
		else if( unicode_character == (system_character_t) '\\' )
		{
			if( ( ${mount_tool_file_entry_type}_path_index + 1 ) > safe_${mount_tool_file_entry_type}_path_size )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid ${mount_tool_file_entry_type_description} path index value out of bounds.",
				 function );

				goto on_error;
			}
			safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = (system_character_t) '\\';
		}
#endif
		else
		{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			result = libuna_unicode_character_copy_to_utf16(
			          unicode_character,
			          (libuna_utf16_character_t *) safe_${mount_tool_file_entry_type}_path,
			          safe_${mount_tool_file_entry_type}_path_size,
			          &${mount_tool_file_entry_type}_path_index,
			          error );
#else
			result = libuna_unicode_character_copy_to_utf8(
			          unicode_character,
			          (libuna_utf8_character_t *) safe_${mount_tool_file_entry_type}_path,
			          safe_${mount_tool_file_entry_type}_path_size,
			          &${mount_tool_file_entry_type}_path_index,
			          error );
#endif
			if( result != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_CONVERSION,
				 LIBCERROR_CONVERSION_ERROR_INPUT_FAILED,
				 "%s: unable to copy Unicode character to ${mount_tool_file_entry_type_description} path.",
				 function );

				goto on_error;
			}
		}
	}
	if( ${mount_tool_file_entry_type}_path_index >= safe_${mount_tool_file_entry_type}_path_size )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid ${mount_tool_file_entry_type_description} path index value out of bounds.",
		 function );

		goto on_error;
	}
	safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index ] = 0;

	*${mount_tool_file_entry_type}_path      = safe_${mount_tool_file_entry_type}_path;
	*${mount_tool_file_entry_type}_path_size = safe_${mount_tool_file_entry_type}_path_size;

	return( 1 );

on_error:
	if( safe_${mount_tool_file_entry_type}_path != NULL )
	{
		memory_free(
		 safe_${mount_tool_file_entry_type}_path );
	}
	return( -1 );
}
