/*
 * ${structure_description} functions
 *
 * Copyright (C) ${copyright}, ${authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this software.  If not, see <http://www.gnu.org/licenses/>.
 */

#if !defined( _${library_name_upper_case}_${structure_name_upper_case}_H )
#define _${library_name_upper_case}_${structure_name_upper_case}_H

#include <common.h>
#include <types.h>

#include "${library_name}_libbfio.h"
#include "${library_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

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

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_${structure_name_upper_case}_H ) */

