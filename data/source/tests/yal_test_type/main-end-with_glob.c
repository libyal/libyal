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
	if( file_io_handle != NULL )
	{
		libbfio_handle_free(
		 &file_io_handle,
		 NULL );
	}
	if( filenames != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		${library_name}_glob_wide_free(
		 filenames,
		 number_of_filenames,
		 NULL );
#else
		${library_name}_glob_free(
		 filenames,
		 number_of_filenames,
		 NULL );
#endif
	}
	return( EXIT_FAILURE );
}

