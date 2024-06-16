/*
 * Python object definition of the ${library_name} ${definitions_description}
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

#if !defined( _${python_module_name:upper_case}_${definitions_name:upper_case}_H )
#define _${python_module_name:upper_case}_${definitions_name:upper_case}_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_${library_name}.h"
#include "${python_module_name}_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct ${python_module_name}_${definitions_name} ${python_module_name}_${definitions_name}_t;

struct ${python_module_name}_${definitions_name}
{
	/* Python object initialization
	 */
	PyObject_HEAD
};

extern PyTypeObject ${python_module_name}_${definitions_name}_type_object;

int ${python_module_name}_${definitions_name}_init_type(
     PyTypeObject *type_object );

PyObject *${python_module_name}_${definitions_name}_new(
           void );

int ${python_module_name}_${definitions_name}_init(
     ${python_module_name}_${definitions_name}_t *definitions_object );

void ${python_module_name}_${definitions_name}_free(
      ${python_module_name}_${definitions_name}_t *definitions_object );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name:upper_case}_${definitions_name:upper_case}_H ) */

