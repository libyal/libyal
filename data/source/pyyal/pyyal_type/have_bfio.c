#if !defined( ${library_name_upper_case}_HAVE_BFIO )

${library_name_upper_case}_EXTERN \
int ${library_name}_${type_name}_open_file_io_handle(
     ${library_name}_${type_name}_t *${type_name},
     libbfio_handle_t *file_io_handle,
     int access_flags,
     ${library_name}_error_t **error );

#endif /* !defined( ${library_name_upper_case}_HAVE_BFIO ) */

