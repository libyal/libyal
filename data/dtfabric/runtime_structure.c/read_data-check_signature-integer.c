	byte_stream_copy_to_uint${bit_size}_little_endian(
	 ( (${prefix}_${structure_name}_t *) data )->${structure_member.name},
	 ${structure_member.name} );

	if( ${structure_member.name} != ${structure_member.value} )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported ${structure_member.description}: %" PRIu${bit_size} ".",
		 function,
		 ${structure_member.name} );

		return( -1 );
	}
