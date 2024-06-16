/*
 * Python file objects IO pool functions
 *
 * Copyright (C) ${python_module_copyright}, ${python_module_authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _${python_module_name:upper_case}_FILE_OBJECTS_IO_POOL_H )
#define _${python_module_name:upper_case}_FILE_OBJECTS_IO_POOL_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_libbfio.h"
#include "${python_module_name}_libcerror.h"
#include "${python_module_name}_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

int ${python_module_name}_file_objects_pool_initialize(
     libbfio_pool_t **pool,
     PyObject *sequence_object,
     int access_flags,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name:upper_case}_FILE_OBJECTS_IO_POOL_H ) */

