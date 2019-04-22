	if( memory_compare(
	     ( (${prefix}_${structure_name}_t *) data )->${member_name},
	     "${member_value}",
	     ${member_value_size} ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_UNSUPPORTED_VALUE,
		 "%s: invalid ${member_name_description}.",
		 function );

		return( -1 );
	}
