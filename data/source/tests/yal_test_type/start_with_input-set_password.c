	if( password != NULL )
	{
		string_length = system_string_length(
		                 password );

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = ${library_name}_${type_name}_set_utf16_password(
		          *${type_name},
		          (uint16_t *) password,
		          string_length,
		          error );
#else
		result = ${library_name}_${type_name}_set_utf8_password(
		          *${type_name},
		          (uint8_t *) password,
		          string_length,
		          error );
#endif
		if( result != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set password.",
			 function );

			goto on_error;
		}
	}
