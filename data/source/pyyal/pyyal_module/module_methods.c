/* The ${python_module_name} module methods
 */
PyMethodDef ${python_module_name}_module_methods[] = {
	{ "get_version",
	  (PyCFunction) ${python_module_name}_get_version,
	  METH_NOARGS,
	  "get_version() -> String\n"
	  "\n"
	  "Retrieves the version." },

	{ "check_file_signature",
	  (PyCFunction) ${python_module_name}_check_file_signature,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_file_signature(filename) -> Boolean\n"
	  "\n"
	  "Checks if a file has an Expert Witness Compression Format (EWF) signature." },

	{ "check_file_signature_file_object",
	  (PyCFunction) ${python_module_name}_check_file_signature_file_object,
	  METH_VARARGS | METH_KEYWORDS,
	  "check_file_signature_file_object(filename) -> Boolean\n"
	  "\n"
	  "Checks if a file has an Expert Witness Compression Format (EWF) signature using a file-like object." },

	{ "glob",
	  (PyCFunction) ${python_module_name}_glob,
	  METH_VARARGS | METH_KEYWORDS,
	  "glob(filename) -> Object\n"
	  "\n"
	  "Globs filenames according to the Expert Witness Compression Format (EWF) segment file naming schema\n"
	  "based on the extension (e.g. E01) and returns a sequence (list) of all the segment filenames." },

	{ "open",
	  (PyCFunction) ${python_module_name}_handle_new_open,
	  METH_VARARGS | METH_KEYWORDS,
	  "open(filenames, mode='r') -> Object\n"
	  "\n"
          "Opens file(s) from a sequence (list) of all the segment filenames.\n"
          "Use ${python_module_name}.glob() to determine the segment filenames from first (E01)." },

/* TODO: open file-like object using pool - list of file objects */

	/* Sentinel */
	{ NULL,
	  NULL,
	  0,
	  NULL}
};

