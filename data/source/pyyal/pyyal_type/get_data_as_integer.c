/* Retrieves the data as an integer value
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_data_as_integer(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *integer_object = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_data_as_integer";
	uint64_t value_64bit     = 0;
	int64_t integer_value    = 0;
	uint32_t value_32bit     = 0;
	uint32_t value_type      = 0;
	uint16_t value_16bit     = 0;
	int result               = 0;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_value_type(
	          ${python_module_name}_${type_name}->${type_name},
	          &value_type,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve value type.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	switch( value_type )
	{
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_16BIT_SIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_16BIT_UNSIGNED:
			Py_BEGIN_ALLOW_THREADS

			result = ${library_name}_${type_name}_get_data_as_16bit_integer(
				  ${python_module_name}_${type_name}->${type_name},
				  &value_16bit,
				  &error );

			Py_END_ALLOW_THREADS

			if( value_type == ${library_name_upper_case}_VALUE_TYPE_INTEGER_16BIT_SIGNED )
			{
				/* Interpret the 16-bit value as signed
				 */
				integer_value = (int16_t) value_16bit;
			}
			else
			{
				integer_value = value_16bit;
			}
			break;

		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_32BIT_SIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_32BIT_UNSIGNED:
			Py_BEGIN_ALLOW_THREADS

			result = ${library_name}_${type_name}_get_data_as_32bit_integer(
				  ${python_module_name}_${type_name}->${type_name},
				  &value_32bit,
				  &error );

			Py_END_ALLOW_THREADS

			if( value_type == ${library_name_upper_case}_VALUE_TYPE_INTEGER_32BIT_SIGNED )
			{
				/* Interpret the 32-bit value as signed
				 */
				integer_value = (int32_t) value_32bit;
			}
			else
			{
				integer_value = value_32bit;
			}
			break;

		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_64BIT_SIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_64BIT_UNSIGNED:
			Py_BEGIN_ALLOW_THREADS

			result = ${library_name}_${type_name}_get_data_as_64bit_integer(
				  ${python_module_name}_${type_name}->${type_name},
				  &value_64bit,
				  &error );

			Py_END_ALLOW_THREADS

			if( value_type == ${library_name_upper_case}_VALUE_TYPE_INTEGER_64BIT_SIGNED )
			{
				/* Interpret the 64-bit value as signed
				 */
				integer_value = (int64_t) value_64bit;
			}
			else
			{
				integer_value = value_64bit;
			}
			break;

		case ${library_name_upper_case}_VALUE_TYPE_FILETIME:
			Py_BEGIN_ALLOW_THREADS

			result = ${library_name}_${type_name}_get_data_as_filetime(
				  ${python_module_name}_${type_name}->${type_name},
				  &value_64bit,
				  &error );

			Py_END_ALLOW_THREADS

			integer_value = value_64bit;

			break;

		default:
			PyErr_Format(
			 PyExc_IOError,
			 "%s: value is not an integer type.",
			 function );

			return( NULL );
	}
	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve integer value.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	switch( value_type )
	{
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_16BIT_SIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_32BIT_SIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_64BIT_SIGNED:
			integer_object = ${python_module_name}_integer_signed_new_from_64bit(
			                  integer_value );
			break;

		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_16BIT_UNSIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_32BIT_UNSIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_INTEGER_64BIT_UNSIGNED:
		case ${library_name_upper_case}_VALUE_TYPE_FILETIME:
			integer_object = ${python_module_name}_integer_unsigned_new_from_64bit(
			                  integer_value );
			break;
	}
	return( integer_object );
}

