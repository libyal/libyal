/*
 * Integer functions
 *
 * Copyright (C) ${python_module_copyright}, ${python_module_authors}
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

#if !defined( _${python_module_name_upper_case}_INTEGER_H )
#define _${python_module_name_upper_case}_INTEGER_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_libcerror.h"
#include "${python_module_name}_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

PyObject *${python_module_name}_integer_signed_new_from_64bit(
           int64_t value_64bit );

PyObject *${python_module_name}_integer_unsigned_new_from_64bit(
           uint64_t value_64bit );

int ${python_module_name}_integer_signed_copy_to_64bit(
     PyObject *integer_object,
     int64_t *value_64bit,
     libcerror_error_t **error );

int ${python_module_name}_integer_unsigned_copy_to_64bit(
     PyObject *integer_object,
     uint64_t *value_64bit,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name_upper_case}_INTEGER_H ) */

