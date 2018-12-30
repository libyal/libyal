/* Sets the keys
 * Returns 1 if successful or -1 on error
 */
int mount_handle_set_keys(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error )
{
	system_character_t *string_segment               = NULL;
	static char *function                            = "mount_handle_set_keys";
	size_t string_length                             = 0;
	size_t string_segment_size                       = 0;
	uint32_t base16_variant                          = 0;
	int number_of_segments                           = 0;
	int result                                       = 0;

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	libcsplit_wide_split_string_t *string_elements   = NULL;
#else
	libcsplit_narrow_split_string_t *string_elements = NULL;
#endif

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
	string_length = system_string_length(
	                 string );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = libcsplit_wide_string_split(
	          string,
	          string_length + 1,
	          (wchar_t) ':',
	          &string_elements,
	          error );
#else
	result = libcsplit_narrow_string_split(
	          string,
	          string_length + 1,
	          (char) ':',
	          &string_elements,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to split string.",
		 function );

		goto on_error;
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = libcsplit_wide_split_string_get_number_of_segments(
	          string_elements,
	          &number_of_segments,
	          error );
#else
	result = libcsplit_narrow_split_string_get_number_of_segments(
	          string_elements,
	          &number_of_segments,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of segments.",
		 function );

		goto on_error;
	}
	if( ( number_of_segments == 0 )
	 || ( number_of_segments > 2 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported number of segments.",
		 function );

		goto on_error;
	}
	if( memory_set(
	     mount_handle->key_data,
	     0,
	     64 ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear key data.",
		 function );

		goto on_error;
	}
	base16_variant = LIBUNA_BASE16_VARIANT_RFC4648;

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( _BYTE_STREAM_HOST_IS_ENDIAN_BIG )
	{
		base16_variant |= LIBUNA_BASE16_VARIANT_ENCODING_UTF16_BIG_ENDIAN;
	}
	else
	{
		base16_variant |= LIBUNA_BASE16_VARIANT_ENCODING_UTF16_LITTLE_ENDIAN;
	}
	result = libcsplit_wide_split_string_get_segment_by_index(
	          string_elements,
	          0,
	          &string_segment,
	          &string_segment_size,
	          error );
#else
	result = libcsplit_narrow_split_string_get_segment_by_index(
	          string_elements,
	          0,
	          &string_segment,
	          &string_segment_size,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve string segment: 0.",
		 function );

		goto on_error;
	}
	if( string_segment == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing string segment: 0.",
		 function );

		goto on_error;
	}
	if( ( string_segment_size != 33 )
	 && ( string_segment_size != 65 )
	 && ( string_segment_size != 129 ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported string segment: 0 size.",
		 function );

		goto on_error;
	}
	if( string_segment_size == 129 )
	{
		/* Allow the keys to be specified as a single 512-bit stream
		 */
		if( number_of_segments != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported number of segments.",
			 function );

			goto on_error;
		}
		if( libuna_base16_stream_copy_to_byte_stream(
		     (uint8_t *) string_segment,
		     string_segment_size - 1,
		     mount_handle->key_data,
		     64,
		     base16_variant,
		     0,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
			 "%s: unable to copy key data.",
			 function );

			goto on_error;
		}
		mount_handle->full_volume_encryption_key_size = 32;
		mount_handle->tweak_key_size                  = 32;
	}
	else if( ( string_segment_size == 33 )
	      || ( string_segment_size == 65 ) )
	{
		if( libuna_base16_stream_copy_to_byte_stream(
		     (uint8_t *) string_segment,
		     string_segment_size - 1,
		     mount_handle->key_data,
		     32,
		     base16_variant,
		     0,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
			 "%s: unable to copy key data.",
			 function );

			goto on_error;
		}
		if( string_segment_size == 33 )
		{
			mount_handle->full_volume_encryption_key_size = 16;
		}
		else
		{
			mount_handle->full_volume_encryption_key_size = 32;
		}
	}
	if( number_of_segments > 1 )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = libcsplit_wide_split_string_get_segment_by_index(
		          string_elements,
		          1,
		          &string_segment,
		          &string_segment_size,
		          error );
#else
		result = libcsplit_narrow_split_string_get_segment_by_index(
		          string_elements,
		          1,
		          &string_segment,
		          &string_segment_size,
		          error );
#endif
		if( result != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve string segment: 1.",
			 function );

			goto on_error;
		}
		if( string_segment == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
			 "%s: missing string segment: 1.",
			 function );

			goto on_error;
		}
		if( ( string_segment_size != 33 )
		 && ( string_segment_size != 65 ) )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
			 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
			 "%s: unsupported string segment: 1 size.",
			 function );

			goto on_error;
		}
		if( libuna_base16_stream_copy_to_byte_stream(
		     (uint8_t *) string_segment,
		     string_segment_size - 1,
		     &( mount_handle->key_data[ 32 ] ),
		     32,
		     base16_variant,
		     0,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
			 "%s: unable to copy key data.",
			 function );

			goto on_error;
		}
		if( string_segment_size == 33 )
		{
			mount_handle->tweak_key_size = 16;
		}
		else
		{
			mount_handle->tweak_key_size = 32;
		}
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	result = libcsplit_wide_split_string_free(
	          &string_elements,
	          error );
#else
	result = libcsplit_narrow_split_string_free(
	          &string_elements,
	          error );
#endif
	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
		 "%s: unable to free split string.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( string_elements != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		libcsplit_wide_split_string_free(
		 &string_elements,
		 NULL );
#else
		libcsplit_narrow_split_string_free(
		 &string_elements,
		 NULL );
#endif
	}
	memory_set(
	 mount_handle->key_data,
	 0,
	 64 );

	mount_handle->full_volume_encryption_key_size = 0;
	mount_handle->tweak_key_size                  = 0;

	return( -1 );
}

