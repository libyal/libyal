	if( memory_copy(
	     ${structure_name}->${member_name},
	     ( (${prefix}_${structure_name}_t *) data )->${member_name},
	     16 ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to copy ${member_name_description}.",
		 function );

		return( -1 );
	}
