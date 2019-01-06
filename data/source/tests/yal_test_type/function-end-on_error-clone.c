	if( destination_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &destination_${type_name},
		 NULL );
	}
	if( source_${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &source_${type_name},
		 NULL );
	}
