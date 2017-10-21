	return( 1 );

on_error:
	if( *${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 ${type_name},
		 NULL );
	}
	return( -1 );
}

