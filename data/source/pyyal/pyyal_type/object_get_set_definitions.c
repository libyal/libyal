PyGetSetDef ${python_module_name}_${type_name}_object_get_set_definitions[] = {

	{ "ascii_codepage",
	  (getter) ${python_module_name}_${type_name}_get_ascii_codepage,
	  (setter) ${python_module_name}_${type_name}_set_ascii_codepage_setter,
	  "The codepage used for ASCII strings in the file.",
	  NULL },

	/* Sentinel */
	{ NULL, NULL, NULL, NULL, NULL }
};

