#if PY_MAJOR_VERSION >= 3
	value_object = PyLong_FromLong(
	                ${library_name:upper_case}_${definition_name:upper_case}_${constant_name:upper_case} );
#else
	value_object = PyInt_FromLong(
	                ${library_name:upper_case}_${definition_name:upper_case}_${constant_name:upper_case} );
#endif
	if( PyDict_SetItemString(
	     type_object->tp_dict,
	     "${constant_name:upper_case}",
	     value_object ) != 0 )
	{
		goto on_error;
	}
