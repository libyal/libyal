/*
 * Error functions
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

#if !defined( _${python_module_name_upper_case}_ERROR_H )
#define _${python_module_name_upper_case}_ERROR_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_libcerror.h"
#include "${python_module_name}_python.h"

#define ${python_module_name_upper_case}_ERROR_STRING_SIZE	2048

#if defined( __cplusplus )
extern "C" {
#endif

void ${python_module_name}_error_fetch(
      libcerror_error_t **error,
      int error_domain,
      int error_code,
      const char *format_string,
      ... );

void ${python_module_name}_error_fetch_and_raise(
      PyObject *exception_object,
      const char *format_string,
      ... );

void ${python_module_name}_error_raise(
      libcerror_error_t *error,
      PyObject *exception_object,
      const char *format_string,
      ... );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name_upper_case}_ERROR_H ) */

