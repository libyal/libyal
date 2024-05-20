#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_CreateFile(
               const wchar_t *path,
               DWORD desired_access,
               DWORD share_mode,
               DWORD creation_disposition,
               DWORD attribute_flags,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_ZwCreateFile(
                    const wchar_t *path,
                    DOKAN_IO_SECURITY_CONTEXT *security_context,
                    ACCESS_MASK desired_access,
                    ULONG file_attributes,
                    ULONG share_access,
                    ULONG creation_disposition,
                    ULONG creation_options,
                    DOKAN_FILE_INFO *file_info );
#endif

