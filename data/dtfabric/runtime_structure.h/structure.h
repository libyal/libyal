typedef struct ${library_name}_${structure_name} ${library_name}_${structure_name}_t;

struct ${library_name}_${structure_name}
{
${structure_members}
};

int ${library_name}_${structure_name}_initialize(
     ${library_name}_${structure_name}_t **${structure_name},
     libcerror_error_t **error );

int ${library_name}_${structure_name}_free(
     ${library_name}_${structure_name}_t **${structure_name},
     libcerror_error_t **error );

int ${library_name}_${structure_name}_read_data(
     ${library_name}_${structure_name}_t *${structure_name},
     const uint8_t *data,
     size_t data_size,
     libcerror_error_t **error );

int ${library_name}_${structure_name}_read_file_io_handle(
     ${library_name}_${structure_name}_t *${structure_name},
     libbfio_handle_t *file_io_handle,
     off64_t file_offset,
     libcerror_error_t **error );

