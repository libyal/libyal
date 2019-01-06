	if( ${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &${type_name},
	          &${library_name_suffix}_test_${type_name}_${value_name}_free_function,
		 NULL );
	}
