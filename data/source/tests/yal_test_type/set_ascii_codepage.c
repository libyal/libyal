/* Tests the ${library_name}_${type_name}_set_ascii_codepage functions
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_set_ascii_codepage(
     void )
{
	int supported_codepages[ 15 ] = {
		${library_name_upper_case}_CODEPAGE_ASCII,
		${library_name_upper_case}_CODEPAGE_WINDOWS_874,
		${library_name_upper_case}_CODEPAGE_WINDOWS_932,
		${library_name_upper_case}_CODEPAGE_WINDOWS_936,
		${library_name_upper_case}_CODEPAGE_WINDOWS_949,
		${library_name_upper_case}_CODEPAGE_WINDOWS_950,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1250,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1251,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1252,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1253,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1254,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1255,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1256,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1257,
		${library_name_upper_case}_CODEPAGE_WINDOWS_1258 };

	int unsupported_codepages[ 17 ] = {
		${library_name_upper_case}_CODEPAGE_ISO_8859_1,
		${library_name_upper_case}_CODEPAGE_ISO_8859_2,
		${library_name_upper_case}_CODEPAGE_ISO_8859_3,
		${library_name_upper_case}_CODEPAGE_ISO_8859_4,
		${library_name_upper_case}_CODEPAGE_ISO_8859_5,
		${library_name_upper_case}_CODEPAGE_ISO_8859_6,
		${library_name_upper_case}_CODEPAGE_ISO_8859_7,
		${library_name_upper_case}_CODEPAGE_ISO_8859_8,
		${library_name_upper_case}_CODEPAGE_ISO_8859_9,
		${library_name_upper_case}_CODEPAGE_ISO_8859_10,
		${library_name_upper_case}_CODEPAGE_ISO_8859_11,
		${library_name_upper_case}_CODEPAGE_ISO_8859_13,
		${library_name_upper_case}_CODEPAGE_ISO_8859_14,
		${library_name_upper_case}_CODEPAGE_ISO_8859_15,
		${library_name_upper_case}_CODEPAGE_ISO_8859_16,
		${library_name_upper_case}_CODEPAGE_KOI8_R,
		${library_name_upper_case}_CODEPAGE_KOI8_U };

	libcerror_error_t *error = NULL;
	${library_name}_${type_name}_t *${type_name}      = NULL;
	int codepage             = 0;
	int index                = 0;
	int result               = 0;

	/* Initialize test
	 */
	result = ${library_name}_${type_name}_initialize(
	          &${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "${type_name}",
         ${type_name} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Test set ASCII codepage
	 */
	for( index = 0;
	     index < 15;
	     index++ )
	{
		codepage = supported_codepages[ index ];

		result = ${library_name}_${type_name}_set_ascii_codepage(
		          ${type_name},
		          codepage,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
	         "error",
	         error );
	}
	/* Test error cases
	 */
	result = ${library_name}_${type_name}_set_ascii_codepage(
	          NULL,
	          ${library_name_upper_case}_CODEPAGE_ASCII,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "error",
         error );

	libcerror_error_free(
	 &error );

	for( index = 0;
	     index < 17;
	     index++ )
	{
		codepage = unsupported_codepages[ index ];

		result = ${library_name}_${type_name}_set_ascii_codepage(
		          ${type_name},
		          codepage,
		          &error );

		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

	        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
	         "error",
	         error );

		libcerror_error_free(
		 &error );
	}
	/* Clean up
	 */
	result = ${library_name}_${type_name}_free(
	          &${type_name},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "${type_name}",
         ${type_name} );

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
	if( ${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 &${type_name},
		 NULL );
	}
	return( 0 );
}

