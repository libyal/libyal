	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
	          &source_${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "source_${type_name}",
	 source_${type_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	result = ${library_name}_${initialize_value_type}_free(
	          &${initialize_value_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "${initialize_value_name}",
	 ${initialize_value_name} );

	${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	 "error",
	 error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
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
	if( ${initialize_value_name} != NULL )
	{
		${library_name}_${initialize_value_type}_free(
		 &${initialize_value_name},
		 NULL );
	}
	return( 0 );
}

