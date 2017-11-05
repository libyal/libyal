/* Initializes the ${python_module_name} module
 */
#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_${python_module_name}(
                void )
#else
PyMODINIT_FUNC init${python_module_name}(
                void )
#endif
{
	PyObject *module                 = NULL;
	PyTypeObject *handle_type_object = NULL;
	PyGILState_STATE gil_state       = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	${library_name}_notify_set_stream(
	 stderr,
	 NULL );
	${library_name}_notify_set_verbose(
	 1 );
#endif

	/* Create the module
	 * This function must be called before grabbing the GIL
	 * otherwise the module will segfault on a version mismatch
	 */
#if PY_MAJOR_VERSION >= 3
	module = PyModule_Create(
	          &${python_module_name}_module_definition );
#else
	module = Py_InitModule3(
	          "${python_module_name}",
	          ${python_module_name}_module_methods,
	          "Python ${library_name} module (${python_module_name})." );
#endif
	if( module == NULL )
	{
#if PY_MAJOR_VERSION >= 3
		return( NULL );
#else
		return;
#endif
	}
	PyEval_InitThreads();

	gil_state = PyGILState_Ensure();

	/* Setup the handle type object
	 */
	${python_module_name}_handle_type_object.tp_new = PyType_GenericNew;

	if( PyType_Ready(
	     &${python_module_name}_handle_type_object ) < 0 )
	{
		goto on_error;
	}
	Py_IncRef(
	 (PyObject * ) &${python_module_name}_handle_type_object );

	handle_type_object = &${python_module_name}_handle_type_object;

	PyModule_AddObject(
	 module,
	 "handle",
	 (PyObject *) handle_type_object );

	PyGILState_Release(
	 gil_state );

#if PY_MAJOR_VERSION >= 3
	return( module );
#else
	return;
#endif

on_error:
	PyGILState_Release(
	 gil_state );

#if PY_MAJOR_VERSION >= 3
	return( NULL );
#else
	return;
#endif
}

