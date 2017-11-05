#if PY_MAJOR_VERSION >= 3

/* The ${python_module_name} module definition
 */
PyModuleDef ${python_module_name}_module_definition = {
	PyModuleDef_HEAD_INIT,

	/* m_name */
	"${python_module_name}",
	/* m_doc */
	"Python ${library_name} module (${python_module_name}).",
	/* m_size */
	-1,
	/* m_methods */
	${python_module_name}_module_methods,
	/* m_reload */
	NULL,
	/* m_traverse */
	NULL,
	/* m_clear */
	NULL,
	/* m_free */
	NULL,
};

#endif /* PY_MAJOR_VERSION >= 3 */

