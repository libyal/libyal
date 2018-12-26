#if !defined( ${library_name_upper_case}_HAVE_BFIO )

extern \
int ${library_name}_${mount_tool_file_entry_type}_open_file_io_handle(
     ${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type},
     libbfio_handle_t *file_io_handle,
     int access_flags,
     ${library_name}_error_t **error );

#endif /* !defined( ${library_name_upper_case}_HAVE_BFIO ) */

