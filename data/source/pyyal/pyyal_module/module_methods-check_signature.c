	{ "check_${signature_type}_signature",
	  (PyCFunction) ${python_module_name}_check_${signature_type}_signature,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_${signature_type}_signature(filename) -> Boolean\n"
	  "\n"
	  "Checks if a ${signature_type} has ${signature_desription} signature." },

	{ "check_${signature_type}_signature_file_object",
	  (PyCFunction) ${python_module_name}_check_${signature_type}_signature_file_object,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_${signature_type}_signature_file_object(filename) -> Boolean\n"
	  "\n"
	  "Checks if a ${signature_type} has ${signature_desription} signature using a file-like object." },

