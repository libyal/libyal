	if( memory_copy(
	     ${structure_name}->${structure_member.name},
	     ( (${prefix}_${structure_name}_t *) data )->${structure_member.name},
	     16 ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to copy ${structure_member.description}.",
		 function );

		return( -1 );
	}
