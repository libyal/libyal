/* Retrieves a temporary filename
 *
 * On entry temporary_filename should contain a template filename.
 *
 * Returns 1 if successful, 0 if not available or -1 on error
 */
int ${library_name_suffix}_test_get_temporary_filename(
     char *temporary_filename,
     size_t temporary_filename_size,
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_get_temporary_filename";

#if defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE )
	int file_descriptor   = -1;
#endif

	if( temporary_filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid temporary filename.",
		 function );

		return( -1 );
	}
	if( temporary_filename_size > (size_t) SSIZE_MAX )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid temporary filename size value exceeds maximum.",
		 function );

		return( -1 );
	}
#if defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE )
	file_descriptor = mkstemp(
	                   temporary_filename );

	if( file_descriptor == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open temporary file.",
		 function );

		return( -1 );
	}
	if( close(
	     file_descriptor ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_CLOSE_FAILED,
		 "%s: unable to close temporary file.",
		 function );

		return( -1 );
	}
	return( 1 );
#else
	return( 0 );

#endif /* defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE ) */
}

#if defined( HAVE_WIDE_CHARACTER_TYPE )

/* Retrieves a temporary filename
 *
 * On entry temporary_filename should contain a template filename.
 *
 * Returns 1 if successful, 0 if not available or -1 on error
 */
int ${library_name_suffix}_test_get_temporary_filename_wide(
     wchar_t *temporary_filename,
     size_t temporary_filename_size,
     libcerror_error_t **error )
{
	static char *function     = "${library_name_suffix}_test_get_temporary_filename_wide";

#if defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE )
	char *narrow_string       = NULL;
	size_t narrow_string_size = 0;
	int file_descriptor       = -1;
	int result                = 0;
#endif

	if( temporary_filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid temporary filename.",
		 function );

		return( -1 );
	}
	if( temporary_filename_size > (size_t) SSIZE_MAX )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid temporary filename size value exceeds maximum.",
		 function );

		return( -1 );
	}
#if defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE )
	if( libclocale_codepage == 0 )
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_utf8_string_size_from_utf32(
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          &narrow_string_size,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_utf8_string_size_from_utf16(
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          &narrow_string_size,
		          error );
#endif
	}
	else
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_byte_stream_size_from_utf32(
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          libclocale_codepage,
		          &narrow_string_size,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_byte_stream_size_from_utf16(
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          libclocale_codepage,
		          &narrow_string_size,
		          error );
#endif
	}
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_CONVERSION,
		 LIBCERROR_CONVERSION_ERROR_GENERIC,
		 "%s: unable to determine narrow string size.",
		 function );

		return( -1 );
	}
	narrow_string = narrow_string_allocate(
	                 narrow_string_size );

	if( narrow_string == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create narrow string.",
		 function );

		goto on_error;
	}
	if( libclocale_codepage == 0 )
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_utf8_string_copy_from_utf32(
		          (libuna_utf8_character_t *) narrow_string,
		          narrow_string_size,
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_utf8_string_copy_from_utf16(
		          (libuna_utf8_character_t *) narrow_string,
		          narrow_string_size,
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          error );
#endif
	}
	else
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_byte_stream_copy_from_utf32(
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          libclocale_codepage,
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_byte_stream_copy_from_utf16(
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          libclocale_codepage,
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          error );
#endif
	}
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_CONVERSION,
		 LIBCERROR_CONVERSION_ERROR_GENERIC,
		 "%s: unable to set narrow string.",
		 function );

		return( -1 );
	}
	file_descriptor = mkstemp(
	                   narrow_string );

	if( file_descriptor == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open temporary file.",
		 function );

		goto on_error;
	}
	if( close(
	     file_descriptor ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_CLOSE_FAILED,
		 "%s: unable to close temporary file.",
		 function );

		goto on_error;
	}
	if( libclocale_codepage == 0 )
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_utf32_string_copy_from_utf8(
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_utf16_string_copy_from_utf8(
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          error );
#endif
	}
	else
	{
#if SIZEOF_WCHAR_T == 4
		result = libuna_utf32_string_copy_from_byte_stream(
		          (libuna_utf32_character_t *) temporary_filename,
		          temporary_filename_size,
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          libclocale_codepage,
		          error );
#elif SIZEOF_WCHAR_T == 2
		result = libuna_utf16_string_copy_from_byte_stream(
		          (libuna_utf16_character_t *) temporary_filename,
		          temporary_filename_size,
		          (uint8_t *) narrow_string,
		          narrow_string_size,
		          libclocale_codepage,
		          error );
#endif
	}
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_CONVERSION,
		 LIBCERROR_CONVERSION_ERROR_GENERIC,
		 "%s: unable to set temporary filename.",
		 function );

		return( -1 );
	}
	memory_free(
	 narrow_string );

	narrow_string = NULL;

	return( 1 );

on_error:
	if( narrow_string != NULL )
	{
		memory_free(
		 narrow_string );
	}
	return( -1 );
#else
	return( 0 );

#endif /* defined( HAVE_MKSTEMP ) && defined( HAVE_CLOSE ) */
}

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

