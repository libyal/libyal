	return( EXIT_SUCCESS );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	if( file_io_${bfio_type} != NULL )
	{
		libbfio_${bfio_type}_free(
		 &file_io_${bfio_type},
		 NULL );
	}
	return( EXIT_FAILURE );
}

