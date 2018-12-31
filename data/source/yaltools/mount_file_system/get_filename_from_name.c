/* Retrieves a filename from the name
 * Returns 1 if successful or -1 on error
 */
int mount_file_system_get_filename_from_name(
     mount_file_system_t *file_system,
     const system_character_t *name,
     size_t name_length,
     system_character_t **filename,
     size_t *filename_size,
     libcerror_error_t **error )
{
	system_character_t *safe_filename            = NULL;
	static char *function                        = "mount_file_system_get_filename_from_name";
	libuna_unicode_character_t unicode_character = 0;
	system_character_t escape_character          = 0;
	system_character_t hex_digit                 = 0;
	size_t filename_index                        = 0;
	size_t name_index                            = 0;
	size_t safe_filename_size                    = 0;
	int result                                   = 0;

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
	if( name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid name.",
		 function );

		return( -1 );
	}
	if( name_length > (size_t) ( SSIZE_MAX - 1 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid name length value exceeds maximum.",
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

	safe_filename_size = ( name_length * 4 ) + 1;

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
#if defined( WINAPI )
	escape_character = (system_character_t) '^';
#else
	escape_character = (system_character_t) '\\';
#endif

	while( name_index < name_length )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = libuna_unicode_character_copy_from_utf16(
		          &unicode_character,
		          (libuna_utf16_character_t *) name,
		          name_length,
		          &name_index,
		          error );
#else
		result = libuna_unicode_character_copy_from_utf8(
		          &unicode_character,
		          (libuna_utf8_character_t *) name,
		          name_length,
		          &name_index,
		          error );
#endif
		if( result != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_CONVERSION,
			 LIBCERROR_CONVERSION_ERROR_INPUT_FAILED,
			 "%s: unable to copy Unicode character from name.",
			 function );

			goto on_error;
		}
		if( unicode_character == 0 )
		{
			break;
		}
		/* On Windows replaces:
		 *   values <= 0x1f and 0x7f by ^x##
		 *   \ by ^x5c
		 *   ^ by ^^
		 *
		 * On other platforms replaces:
		 *   values <= 0x1f and 0x7f by \x##
		 *   / by \x2f
		 *   \ by \\
		 */
#if defined( WINAPI )
		if( ( unicode_character <= 0x1f )
		 || ( unicode_character == 0x5c )
		 || ( unicode_character == 0x7f ) )
#else
		if( ( unicode_character <= 0x1f )
		 || ( unicode_character == 0x2f )
		 || ( unicode_character == 0x7f ) )
#endif
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
			safe_filename[ filename_index++ ] = escape_character;
			safe_filename[ filename_index++ ] = (system_character_t) 'x';

			hex_digit = unicode_character >> 4;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
			hex_digit = unicode_character & 0x0f;

			if( hex_digit <= 0x09 )
			{
				safe_filename[ filename_index++ ] = (system_character_t) '0' + hex_digit;
			}
			else
			{
				safe_filename[ filename_index++ ] = (system_character_t) 'a' + hex_digit - 10;
			}
		}
		else if( unicode_character == escape_character )
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
			safe_filename[ filename_index++ ] = escape_character;
			safe_filename[ filename_index++ ] = escape_character;
		}
		else
		{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			result = libuna_unicode_character_copy_to_utf16(
			          unicode_character,
			          (libuna_utf16_character_t *) safe_filename,
			          safe_filename_size,
			          &filename_index,
			          error );
#else
			result = libuna_unicode_character_copy_to_utf8(
			          unicode_character,
			          (libuna_utf8_character_t *) safe_filename,
			          safe_filename_size,
			          &filename_index,
			          error );
#endif
			if( result != 1 )
			{
				libcerror_error_set(
				 error,
				 LIBCERROR_ERROR_DOMAIN_CONVERSION,
				 LIBCERROR_CONVERSION_ERROR_INPUT_FAILED,
				 "%s: unable to copy Unicode character to filename.",
				 function );

				goto on_error;
			}
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

