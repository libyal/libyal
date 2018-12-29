int mount_file_system_get_mounted_timestamp(
     mount_file_system_t *file_system,
     uint64_t *mounted_timestamp,
     libcerror_error_t **error );

int mount_file_system_get_number_of_${mount_tool_file_entry_type}s(
     mount_file_system_t *file_system,
     int *number_of_${mount_tool_file_entry_type}s,
     libcerror_error_t **error );

int mount_file_system_get_${mount_tool_file_entry_type}_by_index(
     mount_file_system_t *file_system,
     int ${mount_tool_file_entry_type}_index,
     ${library_name}_${mount_tool_file_entry_type}_t **${mount_tool_file_entry_type},
     libcerror_error_t **error );

int mount_file_system_append_${mount_tool_file_entry_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type},
     libcerror_error_t **error );

int mount_file_system_get_${mount_tool_file_entry_type}_index_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     int *${mount_tool_file_entry_type}_index,
     libcerror_error_t **error );

int mount_file_system_get_path_from_${mount_tool_file_entry_type}_index(
     mount_file_system_t *file_system,
     int ${mount_tool_file_entry_type}_index,
     system_character_t *path,
     size_t path_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _MOUNT_FILE_SYSTEM_H ) */

