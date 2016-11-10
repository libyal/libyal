	return( EXIT_SUCCESS );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${type_name} != NULL )
	{
		${library_name_suffix}_test_${type_name}_close_source(
		 &${type_name},
		 NULL );
	}
	return( EXIT_FAILURE );
}

