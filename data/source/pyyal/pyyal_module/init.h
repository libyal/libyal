#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_${python_module_name}(
                void );
#else
PyMODINIT_FUNC init${python_module_name}(
                void );
#endif

