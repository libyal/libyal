	/* Setup the ${type_name} type object
	 */
	${python_module_name}_${type_name}_type_object.tp_new = PyType_GenericNew;

	if( PyType_Ready(
	     &${python_module_name}_${type_name}_type_object ) < 0 )
	{
		goto on_error;
	}
	Py_IncRef(
	 (PyObject * ) &${python_module_name}_${type_name}_type_object );

	PyModule_AddObject(
	 module,
	 "${type_name}",
	 (PyObject *) &${python_module_name}_${type_name}_type_object );

