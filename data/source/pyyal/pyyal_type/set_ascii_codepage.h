int ${python_module_name}_${type_name}_set_ascii_codepage_from_string(
     ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
     const char *codepage_string );

PyObject *${python_module_name}_${type_name}_set_ascii_codepage(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords );

int ${python_module_name}_${type_name}_set_ascii_codepage_setter(
     ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
     PyObject *string_object,
     void *closure );

