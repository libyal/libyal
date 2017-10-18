int mount_handle_get_media_size(
     mount_handle_t *mount_handle,
     int ${mount_tool_source_type}_index,
     size64_t *size,
     libcerror_error_t **error );

int mount_handle_get_number_of_${mount_tool_source_type}s(
     mount_handle_t *mount_handle,
     int *number_of_${mount_tool_source_type}s,
     libcerror_error_t **error );

int mount_handle_set_basename(
     mount_handle_t *mount_handle,
     const system_character_t *basename,
     size_t basename_size,
     libcerror_error_t **error );

