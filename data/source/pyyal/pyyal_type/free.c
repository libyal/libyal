/* Frees a ${type_description} object
 */
void ${python_module_name}_${type_name}_free(
      ${python_module_name}_${type_name}_t *${python_module_name}_${type_name} )
{
	struct _typeobject *ob_type = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_free";
	int result                  = 0;

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return;
	}
	ob_type = Py_TYPE(
	           ${python_module_name}_${type_name} );

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
	if( ${python_module_name}_${type_name}->${type_name} != NULL )
	{
		Py_BEGIN_ALLOW_THREADS

		result = ${library_name}_${type_name}_free(
		          &( ${python_module_name}_${type_name}->${type_name} ),
		          &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			${python_module_name}_error_raise(
			 error,
			 PyExc_MemoryError,
			 "%s: unable to free ${library_name} ${type_description}.",
			 function );

			libcerror_error_free(
			 &error );
		}
	}
	ob_type->tp_free(
	 (PyObject*) ${python_module_name}_${type_name} );
}

