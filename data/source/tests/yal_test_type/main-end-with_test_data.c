	return( EXIT_SUCCESS );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${type_name} != NULL )
	{
		lib${library_name_suffix}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	return( EXIT_FAILURE );
}

