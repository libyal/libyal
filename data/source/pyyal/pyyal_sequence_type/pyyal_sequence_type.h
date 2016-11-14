/*
 * Python object definition of the sequence and iterator object of ${type_description}s
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

#if !defined( _${python_module_name_upper_case}_${type_name_upper_case}S_H )
#define _${python_module_name_upper_case}_${type_name_upper_case}S_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_${library_name}.h"
#include "${python_module_name}_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct ${python_module_name}_${type_name}s ${python_module_name}_${type_name}s_t;

struct ${python_module_name}_${type_name}s
{
	/* Python object initialization
	 */
	PyObject_HEAD

	/* The parent object
	 */
	PyObject *parent_object;

	/* The get ${type_name} by index callback function
	 */
	PyObject* (*get_${type_name}_by_index)(
	             PyObject *parent_object,
	             int ${type_name}_index );

	/* The (current) ${type_name} index
	 */
	int ${type_name}_index;

	/* The number of ${type_name}s
	 */
	int number_of_${type_name}s;
};

extern PyTypeObject ${python_module_name}_${type_name}s_type_object;

PyObject *${python_module_name}_${type_name}s_new(
           PyObject *parent_object,
           PyObject* (*get_${type_name}_by_index)(
                        PyObject *parent_object,
                        int ${type_name}_index ),
           int number_of_${type_name}s );

int ${python_module_name}_${type_name}s_init(
     ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s );

void ${python_module_name}_${type_name}s_free(
      ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s );

Py_ssize_t ${python_module_name}_${type_name}s_len(
            ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s );

PyObject *${python_module_name}_${type_name}s_getitem(
           ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s,
           Py_ssize_t item_index );

PyObject *${python_module_name}_${type_name}s_iter(
           ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s );

PyObject *${python_module_name}_${type_name}s_iternext(
           ${python_module_name}_${type_name}s_t *${python_module_name}_${type_name}s );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name_upper_case}_${type_name_upper_case}S_H ) */

