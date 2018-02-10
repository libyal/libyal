int ${library_name_suffix}_test_open_file_io_handle(
     libbfio_handle_t **file_io_handle,
     uint8_t *data,
     size_t data_size,
     libcerror_error_t **error );

int ${library_name_suffix}_test_close_file_io_handle(
     libbfio_handle_t **file_io_handle,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_FUNCTIONS_H ) */

