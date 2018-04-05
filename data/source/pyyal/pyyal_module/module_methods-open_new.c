	{ "open",
	  (PyCFunction) pylnk_open_new_${signature_type},
	  METH_VARARGS | METH_KEYWORDS,
	  "open(filename, mode='r') -> Object\n"
	  "\n"
	  "Opens a ${signature_type}." },

	{ "open_file_object",
	  (PyCFunction) pylnk_open_new_${signature_type}_with_file_object,
	  METH_VARARGS | METH_KEYWORDS,
	  "open_file_object(file_object, mode='r') -> Object\n"
	  "\n"
	  "Opens a ${signature_type} using a file-like object." },

