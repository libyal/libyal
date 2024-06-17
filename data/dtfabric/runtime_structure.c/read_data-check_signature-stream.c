	if( memory_compare(
	     ( (${prefix}_${structure_name}_t *) data )->${structure_member.name},
	     "${structure_member.value}",
	     ${structure_member.value_size} ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported ${structure_member.description}.",
		 function );

		return( -1 );
	}
