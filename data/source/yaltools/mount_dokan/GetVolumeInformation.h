#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_GetVolumeInformation(
               wchar_t *volume_name,
               DWORD volume_name_size,
               DWORD *volume_serial_number,
               DWORD *maximum_filename_length,
               DWORD *file_system_flags,
               wchar_t *file_system_name,
               DWORD file_system_name_size,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_GetVolumeInformation(
                    wchar_t *volume_name,
                    DWORD volume_name_size,
                    DWORD *volume_serial_number,
                    DWORD *maximum_filename_length,
                    DWORD *file_system_flags,
                    wchar_t *file_system_name,
                    DWORD file_system_name_size,
                    DOKAN_FILE_INFO *file_info );
#endif

