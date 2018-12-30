#if defined( WINAPI )

/* Retrieves the ${mount_tool_file_entry_type_description} path from the path
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_path_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     system_character_t **${mount_tool_file_entry_type}_path,
     size_t *${mount_tool_file_entry_type}_path_size,
     size_t *last_${mount_tool_file_entry_type}_path_seperator_index,
     libcerror_error_t **error )
{
	system_character_t *safe_${mount_tool_file_entry_type}_path = NULL;
	static char *function                                       = "mount_file_system_get_${mount_tool_file_entry_type}_path_from_path";
	system_character_t character_value                          = 0;
	size_t ${mount_tool_file_entry_type}_path_index             = 0;
	size_t path_index                                           = 0;
	size_t safe_${mount_tool_file_entry_type}_path_size         = 0;

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
	if( last_${mount_tool_file_entry_type}_path_seperator_index == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid last ${mount_tool_file_entry_type_description} path seperator index.",
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
	${mount_tool_file_entry_type}_path_index = 0;

	path_index = 0;

	while( path_index < path_length )
	{
		character_value = path[ path_index ];

		if( character_value == 0x00 )
		{
			break;
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
		/* Replace:
		 *   ^^ by ^
		 *   ^x5c by \
		 *   ^x## by values <= 0x1f and 0x7f
		 */
		if( character_value == (system_character_t) '\\' )
		{
			*last_${mount_tool_file_entry_type}_path_seperator_index = ${mount_tool_file_entry_type}_path_index;

			safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = (system_character_t) '\\';
		}
		else if( character_value == (system_character_t) '^' )
		{
			if( ( ( path_index + 1 ) <= path_length )
			 && ( path[ path_index + 1 ] == (system_character_t) '^' ) )
			{
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = (system_character_t) '^';

				path_index += 1;
			}
			else if( ( ( path_index + 3 ) <= path_length )
			      && ( path[ path_index + 1 ] == (system_character_t) 'x' ) )
			{
				if( ( path[ path_index + 2 ] >= (system_character_t) '0' )
				 && ( path[ path_index + 2 ] <= (system_character_t) '9' ) )
				{
					character_value = path[ path_index + 2 ] - (system_character_t) '0';
				}
				else if( ( path[ path_index + 2 ] >= (system_character_t) 'a' )
				      && ( path[ path_index + 2 ] <= (system_character_t) 'f' ) )
				{
					character_value = path[ path_index + 2 ] - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				character_value <<= 4;

				if( ( path[ path_index + 3 ] >= (system_character_t) '0' )
				 && ( path[ path_index + 3 ] <= (system_character_t) '9' ) )
				{
					character_value |= path[ path_index + 3 ] - (system_character_t) '0';
				}
				else if( ( path[ path_index + 3 ] >= (system_character_t) 'a' )
				      && ( path[ path_index + 3 ] <= (system_character_t) 'f' ) )
				{
					character_value |= path[ path_index + 3 ] - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				if( ( character_value == 0 )
				 || ( ( character_value > 0x1f )
				  &&  ( character_value != 0x5c )
				  &&  ( character_value != 0x7f ) ) )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = character_value;

				path_index += 3;
			}
			else
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid escaped character value out of bounds.",
				 function );

				goto on_error;
			}
		}
		else
		{
			safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = character_value;
		}
		path_index++;
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

#else

/* Retrieves the ${mount_tool_file_entry_type_description} path from the path
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_${mount_tool_file_entry_type}_path_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     system_character_t **${mount_tool_file_entry_type}_path,
     size_t *${mount_tool_file_entry_type}_path_size,
     size_t *last_${mount_tool_file_entry_type}_path_seperator_index,
     libcerror_error_t **error )
{
	system_character_t *safe_${mount_tool_file_entry_type}_path = NULL;
	static char *function                                       = "mount_file_system_get_${mount_tool_file_entry_type}_path_from_path";
	system_character_t character_value                          = 0;
	size_t ${mount_tool_file_entry_type}_path_index             = 0;
	size_t path_index                                           = 0;
	size_t safe_${mount_tool_file_entry_type}_path_size         = 0;

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
	if( last_${mount_tool_file_entry_type}_path_seperator_index == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid last ${mount_tool_file_entry_type_description} path seperator index.",
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
	${mount_tool_file_entry_type}_path_index = 0;

	path_index = 0;

	while( path_index < path_length )
	{
		character_value = path[ path_index ];

		if( character_value == 0x00 )
		{
			break;
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
		/* Replace:
		 *   / by \
		 *   \\ by \
		 *   \x2f by /
		 *   \x## by values <= 0x1f and 0x7f
		 */
		if( character_value == (system_character_t) '/' )
		{
			*last_${mount_tool_file_entry_type}_path_seperator_index = ${mount_tool_file_entry_type}_path_index;

			safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = (system_character_t) '\\';
		}
		else if( character_value == (system_character_t) '\\' )
		{
			if( ( ( path_index + 1 ) <= path_length )
			 && ( path[ path_index + 1 ] == (system_character_t) '\\' ) )
			{
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = (system_character_t) '\\';

				path_index += 1;
			}
			else if( ( ( path_index + 3 ) <= path_length )
			      && ( path[ path_index + 1 ] == (system_character_t) 'x' ) )
			{
				if( ( path[ path_index + 2 ] >= (system_character_t) '0' )
				 && ( path[ path_index + 2 ] <= (system_character_t) '9' ) )
				{
					character_value = path[ path_index + 2 ] - (system_character_t) '0';
				}
				else if( ( path[ path_index + 2 ] >= (system_character_t) 'a' )
				      && ( path[ path_index + 2 ] <= (system_character_t) 'f' ) )
				{
					character_value = path[ path_index + 2 ] - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				character_value <<= 4;

				if( ( path[ path_index + 3 ] >= (system_character_t) '0' )
				 && ( path[ path_index + 3 ] <= (system_character_t) '9' ) )
				{
					character_value |= path[ path_index + 3 ] - (system_character_t) '0';
				}
				else if( ( path[ path_index + 3 ] >= (system_character_t) 'a' )
				      && ( path[ path_index + 3 ] <= (system_character_t) 'f' ) )
				{
					character_value |= path[ path_index + 3 ] - (system_character_t) 'a' + 10;
				}
				else
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				if( ( character_value == 0 )
				 || ( ( character_value > 0x1f )
				  &&  ( character_value != 0x2f )
				  &&  ( character_value != 0x7f ) ) )
				{
					libcerror_error_set(
					 error,
					 LIBCERROR_ERROR_DOMAIN_RUNTIME,
					 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
					 "%s: invalid escaped character value out of bounds.",
					 function );

					goto on_error;
				}
				safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = character_value;

				path_index += 3;
			}
			else
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_RUNTIME,
				 LIBCERROR_RUNTIME_ERROR_VALUE_OUT_OF_BOUNDS,
				 "%s: invalid escaped character value out of bounds.",
				 function );

				goto on_error;
			}
		}
		else
		{
			safe_${mount_tool_file_entry_type}_path[ ${mount_tool_file_entry_type}_path_index++ ] = character_value;
		}
		path_index++;
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

#endif /* defined( WINAPI ) */

