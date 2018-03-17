/* The ${python_module_name} module methods
 */
PyMethodDef ${python_module_name}_module_methods[] = {
	{ "get_version",
	  (PyCFunction) ${python_module_name}_get_version,
	  METH_NOARGS,
	  "get_version() -> String\n"
	  "\n"
	  "Retrieves the version." },

