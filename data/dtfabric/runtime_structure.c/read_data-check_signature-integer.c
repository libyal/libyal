	byte_stream_copy_to_uint${bit_size}_little_endian(
	 ( (${prefix}_${structure_name}_t *) data )->${member_name},
	 ${member_name} );

	if( ${member_name} != ${member_value} )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported ${member_name_description}: %" PRIu${bit_size} ".",
		 function,
		 ${member_name} );

		return( -1 );
	}
