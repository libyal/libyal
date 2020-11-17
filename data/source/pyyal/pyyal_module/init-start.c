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
	PyObject *module           = NULL;
	PyGILState_STATE gil_state = 0;

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
#if PY_VERSION_HEX < 0x03070000
	PyEval_InitThreads();
#endif
	gil_state = PyGILState_Ensure();

