		if( ${library_name}_debug_print_filetime_value(
		     function,
		     "${member_name_description}${tab_alignment}",
		     ( (${prefix}_${structure_name}_t *) data )->${member_name},
		     8,
		     LIBFDATETIME_ENDIAN_LITTLE,
		     LIBFDATETIME_STRING_FORMAT_TYPE_CTIME | LIBFDATETIME_STRING_FORMAT_FLAG_DATE_TIME_NANO_SECONDS,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_PRINT_FAILED,
			 "%s: unable to print FILETIME value.",
			 function );

			return( -1 );
		}
