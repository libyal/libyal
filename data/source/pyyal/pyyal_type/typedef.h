#if defined( __cplusplus )
extern "C" {
#endif

typedef struct ${python_module_name}_${type_name} ${python_module_name}_${type_name}_t;

struct ${python_module_name}_${type_name}
{
	/* Python object initialization
	 */
	PyObject_HEAD

	/* The ${library_name} ${type_description}
	 */
	${library_name}_${type_name}_t *${type_name};
};

extern PyMethodDef ${python_module_name}_${type_name}_object_methods[];
extern PyTypeObject ${python_module_name}_${type_name}_type_object;

