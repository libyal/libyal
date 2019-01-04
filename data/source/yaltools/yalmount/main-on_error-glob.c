#if !defined( HAVE_GLOB_H )
	if( glob != NULL )
	{
		${tools_name}_glob_free(
		 &glob,
		 NULL );
	}
#endif
