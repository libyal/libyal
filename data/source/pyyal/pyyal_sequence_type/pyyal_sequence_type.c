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

#include <common.h>
#include <types.h>

#if defined( HAVE_STDLIB_H ) || defined( HAVE_WINAPI )
#include <stdlib.h>
#endif

${python_module_includes}

PySequenceMethods ${python_module_name}_${sequence_type_name}_sequence_methods = {
	/* sq_length */
	(lenfunc) ${python_module_name}_${sequence_type_name}_len,
	/* sq_concat */
	0,
	/* sq_repeat */
	0,
	/* sq_item */
	(ssizeargfunc) ${python_module_name}_${sequence_type_name}_getitem,
	/* sq_slice */
	0,
	/* sq_ass_item */
	0,
	/* sq_ass_slice */
	0,
	/* sq_contains */
	0,
	/* sq_inplace_concat */
	0,
	/* sq_inplace_repeat */
	0
};

PyTypeObject ${python_module_name}_${sequence_type_name}_type_object = {
	PyVarObject_HEAD_INIT( NULL, 0 )

	/* tp_name */
	"${python_module_name}._${sequence_type_name}",
	/* tp_basicsize */
	sizeof( ${python_module_name}_${sequence_type_name}_t ),
	/* tp_itemsize */
	0,
	/* tp_dealloc */
	(destructor) ${python_module_name}_${sequence_type_name}_free,
	/* tp_print */
	0,
	/* tp_getattr */
	0,
	/* tp_setattr */
	0,
	/* tp_compare */
	0,
	/* tp_repr */
	0,
	/* tp_as_number */
	0,
	/* tp_as_sequence */
	&${python_module_name}_${sequence_type_name}_sequence_methods,
	/* tp_as_mapping */
	0,
	/* tp_hash */
	0,
	/* tp_call */
	0,
	/* tp_str */
	0,
	/* tp_getattro */
	0,
	/* tp_setattro */
	0,
	/* tp_as_buffer */
	0,
	/* tp_flags */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
	/* tp_doc */
	"${python_module_name} internal sequence and iterator object of ${sequence_type_description}",
	/* tp_traverse */
	0,
	/* tp_clear */
	0,
	/* tp_richcompare */
	0,
	/* tp_weaklistoffset */
	0,
	/* tp_iter */
	(getiterfunc) ${python_module_name}_${sequence_type_name}_iter,
	/* tp_iternext */
	(iternextfunc) ${python_module_name}_${sequence_type_name}_iternext,
	/* tp_methods */
	0,
	/* tp_members */
	0,
	/* tp_getset */
	0,
	/* tp_base */
	0,
	/* tp_dict */
	0,
	/* tp_descr_get */
	0,
	/* tp_descr_set */
	0,
	/* tp_dictoffset */
	0,
	/* tp_init */
	(initproc) ${python_module_name}_${sequence_type_name}_init,
	/* tp_alloc */
	0,
	/* tp_new */
	0,
	/* tp_free */
	0,
	/* tp_is_gc */
	0,
	/* tp_bases */
	NULL,
	/* tp_mro */
	NULL,
	/* tp_cache */
	NULL,
	/* tp_subclasses */
	NULL,
	/* tp_weaklist */
	NULL,
	/* tp_del */
	0
};

/* Creates a new ${sequence_type_description} object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${sequence_type_name}_new(
           PyObject *parent_object,
           PyObject* (*get_item_by_index)(
                        PyObject *parent_object,
                        int index ),
           int number_of_items )
{
	${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object = NULL;
	static char *function                                                       = "${python_module_name}_${sequence_type_name}_new";

	if( parent_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid parent object.",
		 function );

		return( NULL );
	}
	if( get_item_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid get item by index function.",
		 function );

		return( NULL );
	}
	/* Make sure the ${sequence_type_description} values are initialized
	 */
	${sequence_type_name}_object = PyObject_New(
	                                struct ${python_module_name}_${sequence_type_name},
	                                &${python_module_name}_${sequence_type_name}_type_object );

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create ${sequence_type_description} object.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${sequence_type_name}_init(
	     ${sequence_type_name}_object ) != 0 )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${sequence_type_description} object.",
		 function );

		goto on_error;
	}
	${sequence_type_name}_object->parent_object     = parent_object;
	${sequence_type_name}_object->get_item_by_index = get_item_by_index;
	${sequence_type_name}_object->number_of_items   = number_of_items;

	Py_IncRef(
	 (PyObject *) ${sequence_type_name}_object->parent_object );

	return( (PyObject *) ${sequence_type_name}_object );

on_error:
	if( ${sequence_type_name}_object != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${sequence_type_name}_object );
	}
	return( NULL );
}

/* Intializes a ${sequence_type_description} object
 * Returns 0 if successful or -1 on error
 */
int ${python_module_name}_${sequence_type_name}_init(
     ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object )
{
	static char *function = "${python_module_name}_${sequence_type_name}_init";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return( -1 );
	}
	/* Make sure the ${sequence_type_description} values are initialized
	 */
	${sequence_type_name}_object->parent_object     = NULL;
	${sequence_type_name}_object->get_item_by_index = NULL;
	${sequence_type_name}_object->current_index     = 0;
	${sequence_type_name}_object->number_of_items   = 0;

	return( 0 );
}

/* Frees a ${sequence_type_description} object
 */
void ${python_module_name}_${sequence_type_name}_free(
      ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object )
{
	struct _typeobject *ob_type = NULL;
	static char *function       = "${python_module_name}_${sequence_type_name}_free";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return;
	}
	ob_type = Py_TYPE(
	           ${sequence_type_name}_object );

	if( ob_type == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: missing ob_type.",
		 function );

		return;
	}
	if( ob_type->tp_free == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ob_type - missing tp_free.",
		 function );

		return;
	}
	if( ${sequence_type_name}_object->parent_object != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${sequence_type_name}_object->parent_object );
	}
	ob_type->tp_free(
	 (PyObject*) ${sequence_type_name}_object );
}

/* The ${sequence_type_description} len() function
 */
Py_ssize_t ${python_module_name}_${sequence_type_name}_len(
            ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object )
{
	static char *function = "${python_module_name}_${sequence_type_name}_len";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return( -1 );
	}
	return( (Py_ssize_t) ${sequence_type_name}_object->number_of_items );
}

/* The ${sequence_type_description} getitem() function
 */
PyObject *${python_module_name}_${sequence_type_name}_getitem(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object,
           Py_ssize_t item_index )
{
	PyObject *${type_name}_object = NULL;
	static char *function         = "${python_module_name}_${sequence_type_name}_getitem";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->get_item_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object - missing get item by index function.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->number_of_items < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object - invalid number of items.",
		 function );

		return( NULL );
	}
	if( ( item_index < 0 )
	 || ( item_index >= (Py_ssize_t) ${sequence_type_name}_object->number_of_items ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid invalid item index value out of bounds.",
		 function );

		return( NULL );
	}
	${type_name}_object = ${sequence_type_name}_object->get_item_by_index(
	                       ${sequence_type_name}_object->parent_object,
	                       (int) item_index );

	return( ${type_name}_object );
}

/* The ${sequence_type_description} iter() function
 */
PyObject *${python_module_name}_${sequence_type_name}_iter(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object )
{
	static char *function = "${python_module_name}_${sequence_type_name}_iter";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return( NULL );
	}
	Py_IncRef(
	 (PyObject *) ${sequence_type_name}_object );

	return( (PyObject *) ${sequence_type_name}_object );
}

/* The ${sequence_type_description} iternext() function
 */
PyObject *${python_module_name}_${sequence_type_name}_iternext(
           ${python_module_name}_${sequence_type_name}_t *${sequence_type_name}_object )
{
	PyObject *${type_name}_object = NULL;
	static char *function         = "${python_module_name}_${sequence_type_name}_iternext";

	if( ${sequence_type_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->get_item_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object - missing get item by index function.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->current_index < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object - invalid current index.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->number_of_items < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} object - invalid number of items.",
		 function );

		return( NULL );
	}
	if( ${sequence_type_name}_object->current_index >= ${sequence_type_name}_object->number_of_items )
	{
		PyErr_SetNone(
		 PyExc_StopIteration );

		return( NULL );
	}
	${type_name}_object = ${sequence_type_name}_object->get_item_by_index(
	                       ${sequence_type_name}_object->parent_object,
	                       ${sequence_type_name}_object->current_index );

	if( ${type_name}_object != NULL )
	{
		${sequence_type_name}_object->current_index++;
	}
	return( ${type_name}_object );
}

