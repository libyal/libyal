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
           PyObject* (*get_${type_name}_by_index)(
                        PyObject *parent_object,
                        int ${type_name}_index ),
           int number_of_${sequence_type_name} )
{
	${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} = NULL;
	static char *function                                                                      = "${python_module_name}_${sequence_type_name}_new";

	if( parent_object == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid parent object.",
		 function );

		return( NULL );
	}
	if( get_${type_name}_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid get ${type_description} by index function.",
		 function );

		return( NULL );
	}
	/* Make sure the ${sequence_type_description} values are initialized
	 */
	${python_module_name}_${sequence_type_name} = PyObject_New(
	                                               struct ${python_module_name}_${sequence_type_name},
	                                               &${python_module_name}_${sequence_type_name}_type_object );

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${sequence_type_description}.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${sequence_type_name}_init(
	     ${python_module_name}_${sequence_type_name} ) != 0 )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${sequence_type_description}.",
		 function );

		goto on_error;
	}
	${python_module_name}_${sequence_type_name}->parent_object                   = parent_object;
	${python_module_name}_${sequence_type_name}->get_${type_name}_by_index       = get_${type_name}_by_index;
	${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} = number_of_${sequence_type_name};

	Py_IncRef(
	 (PyObject *) ${python_module_name}_${sequence_type_name}->parent_object );

	return( (PyObject *) ${python_module_name}_${sequence_type_name} );

on_error:
	if( ${python_module_name}_${sequence_type_name} != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${sequence_type_name} );
	}
	return( NULL );
}

/* Intializes a ${sequence_type_description} object
 * Returns 0 if successful or -1 on error
 */
int ${python_module_name}_${sequence_type_name}_init(
     ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} )
{
	static char *function = "${python_module_name}_${sequence_type_name}_init";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return( -1 );
	}
	/* Make sure the ${sequence_type_description} values are initialized
	 */
	${python_module_name}_${sequence_type_name}->parent_object                   = NULL;
	${python_module_name}_${sequence_type_name}->get_${type_name}_by_index       = NULL;
	${python_module_name}_${sequence_type_name}->${type_name}_index              = 0;
	${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} = 0;

	return( 0 );
}

/* Frees a ${sequence_type_description} object
 */
void ${python_module_name}_${sequence_type_name}_free(
      ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} )
{
	struct _typeobject *ob_type = NULL;
	static char *function       = "${python_module_name}_${sequence_type_name}_free";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return;
	}
	ob_type = Py_TYPE(
	           ${python_module_name}_${sequence_type_name} );

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
	if( ${python_module_name}_${sequence_type_name}->parent_object != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${sequence_type_name}->parent_object );
	}
	ob_type->tp_free(
	 (PyObject*) ${python_module_name}_${sequence_type_name} );
}

/* The ${sequence_type_description} len() function
 */
Py_ssize_t ${python_module_name}_${sequence_type_name}_len(
            ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} )
{
	static char *function = "${python_module_name}_${sequence_type_name}_len";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return( -1 );
	}
	return( (Py_ssize_t) ${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} );
}

/* The ${sequence_type_description} getitem() function
 */
PyObject *${python_module_name}_${sequence_type_name}_getitem(
           ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name},
           Py_ssize_t item_index )
{
	PyObject *${type_name}_object = NULL;
	static char *function         = "${python_module_name}_${sequence_type_name}_getitem";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->get_${type_name}_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} - missing get ${type_description} by index function.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} - invalid number of ${sequence_type_description}.",
		 function );

		return( NULL );
	}
	if( ( item_index < 0 )
	 || ( item_index >= (Py_ssize_t) ${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid invalid item index value out of bounds.",
		 function );

		return( NULL );
	}
	${type_name}_object = ${python_module_name}_${sequence_type_name}->get_${type_name}_by_index(
	                       ${python_module_name}_${sequence_type_name}->parent_object,
	                       (int) item_index );

	return( ${type_name}_object );
}

/* The ${sequence_type_description} iter() function
 */
PyObject *${python_module_name}_${sequence_type_name}_iter(
           ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} )
{
	static char *function = "${python_module_name}_${sequence_type_name}_iter";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return( NULL );
	}
	Py_IncRef(
	 (PyObject *) ${python_module_name}_${sequence_type_name} );

	return( (PyObject *) ${python_module_name}_${sequence_type_name} );
}

/* The ${sequence_type_description} iternext() function
 */
PyObject *${python_module_name}_${sequence_type_name}_iternext(
           ${python_module_name}_${sequence_type_name}_t *${python_module_name}_${sequence_type_name} )
{
	PyObject *${type_name}_object = NULL;
	static char *function         = "${python_module_name}_${sequence_type_name}_iternext";

	if( ${python_module_name}_${sequence_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description}.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->get_${type_name}_by_index == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} - missing get ${type_description} by index function.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->${type_name}_index < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} - invalid ${type_description} index.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} < 0 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${sequence_type_description} - invalid number of ${sequence_type_description}.",
		 function );

		return( NULL );
	}
	if( ${python_module_name}_${sequence_type_name}->${type_name}_index >= ${python_module_name}_${sequence_type_name}->number_of_${sequence_type_name} )
	{
		PyErr_SetNone(
		 PyExc_StopIteration );

		return( NULL );
	}
	${type_name}_object = ${python_module_name}_${sequence_type_name}->get_${type_name}_by_index(
	                       ${python_module_name}_${sequence_type_name}->parent_object,
	                       ${python_module_name}_${sequence_type_name}->${type_name}_index );

	if( ${type_name}_object != NULL )
	{
		${python_module_name}_${sequence_type_name}->${type_name}_index++;
	}
	return( ${type_name}_object );
}

