/*
 * Python object definition of the sequence and iterator object of ${sequence_type_description}
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

#if !defined( _${python_module_name_upper_case}_${sequence_type_name_upper_case}_H )
#define _${python_module_name_upper_case}_${sequence_type_name_upper_case}_H

#include <common.h>
#include <types.h>

#include "${python_module_name}_${library_name}.h"
#include "${python_module_name}_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct ${python_module_name}_${sequence_type_name} ${python_module_name}_${sequence_type_name}_t;

struct ${python_module_name}_${sequence_type_name}
{
	/* Python object initialization
	 */
	PyObject_HEAD

	/* The parent object
	 */
	PyObject *parent_object;

	/* The get item by index callback function
	 */
	PyObject* (*get_item_by_index)(
	             PyObject *parent_object,
	             int index );

	/* The current index
	 */
	int current_index;

	/* The number of items
	 */
	int number_of_items;
};

extern PyTypeObject ${python_module_name}_${sequence_type_name}_type_object;

PyObject *${python_module_name}_${sequence_type_name}_new(
           PyObject *parent_object,
           PyObject* (*get_item_by_index)(
                        PyObject *parent_object,
                        int index ),
           int number_of_items );

int ${python_module_name}_${sequence_type_name}_init(
     ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object );

void ${python_module_name}_${sequence_type_name}_free(
      ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object );

Py_ssize_t ${python_module_name}_${sequence_type_name}_len(
            ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object );

PyObject *${python_module_name}_${sequence_type_name}_getitem(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object,
           Py_ssize_t item_index );

PyObject *${python_module_name}_${sequence_type_name}_iter(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object );

PyObject *${python_module_name}_${sequence_type_name}_iternext(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${python_module_name_upper_case}_${sequence_type_name_upper_case}_H ) */

