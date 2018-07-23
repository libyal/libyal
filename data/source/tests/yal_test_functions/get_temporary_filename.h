int ${library_name_suffix}_test_get_temporary_filename(
     char *temporary_filename,
     size_t temporary_filename_size,
     libcerror_error_t **error );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

int ${library_name_suffix}_test_get_temporary_filename_wide(
     wchar_t *temporary_filename,
     size_t temporary_filename_size,
     libcerror_error_t **error );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

