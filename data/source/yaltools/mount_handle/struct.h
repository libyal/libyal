typedef struct mount_handle mount_handle_t;

struct mount_handle
{
	/* The basename
	 */
	system_character_t *basename;

	/* The basename size
	 */
	size_t basename_size;

	/* The ${mount_tool_source_type}s array
	 */
	libcdata_array_t *${mount_tool_source_type}s_array;

	/* The key data
	 */
	uint8_t key_data[ 16 ];

	/* Value to indicate the key data is set
	 */
	uint8_t key_data_is_set;

	/* The password
	 */
	const system_character_t *password;

	/* The password length
	 */
	size_t password_length;

	/* The notification output stream
	 */
	FILE *notify_stream;
};

