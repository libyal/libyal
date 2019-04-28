		if( ${library_name}_debug_print_utf16_string_value(
		     function,
		     "${member_name_description}${tab_alignment}",
		     data,
		     string_size,
		     LIBUNA_ENDIAN_LITTLE,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_PRINT_FAILED,
			 "%s: unable to print ${member_name_description} UTF-16 string value.",
			 function );

			goto on_error;
		}
