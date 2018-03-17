	{ "check_file_signature",
	  (PyCFunction) ${python_module_name}_check_file_signature,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_file_signature(filename) -> Boolean\n"
	  "\n"
	  "Checks if a file has TODO signature." },

	{ "check_file_signature_file_object",
	  (PyCFunction) ${python_module_name}_check_file_signature_file_object,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_file_signature_file_object(filename) -> Boolean\n"
	  "\n"
	  "Checks if a file has TODO signature using a file-like object." },

