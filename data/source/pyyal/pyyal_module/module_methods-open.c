	{ "open",
	  (PyCFunction) ${python_module_name}_handle_new_open,
	  METH_VARARGS | METH_KEYWORDS,
	  "open(filenames, mode='r') -> Object\n"
	  "\n"
          "Opens file(s) from a sequence (list) of all the segment filenames.\n"
          "Use ${python_module_name}.glob() to determine the segment filenames from first (E01)." },

/* TODO: open file-like object using pool - list of file objects */

