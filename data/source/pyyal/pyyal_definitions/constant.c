#if PY_MAJOR_VERSION >= 3
	value_object = PyLong_FromLong(
	                ${library_name_upper_case}_${definition_name_upper_case}_${constant_name_upper_case} );
#else
	value_object = PyInt_FromLong(
	                ${library_name_upper_case}_${definition_name_upper_case}_${constant_name_upper_case} );
#endif
	if( PyDict_SetItemString(
	     type_object->tp_dict,
	     "${constant_name_upper_case}",
	     value_object ) != 0 )
	{
		goto on_error;
	}
