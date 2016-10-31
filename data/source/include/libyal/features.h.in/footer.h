#if !defined( ${library_name_upper_case}_DEPRECATED )
#if defined( __GNUC__ ) && __GNUC__ >= 3
#define ${library_name_upper_case}_DEPRECATED	__attribute__ ((__deprecated__))
#elif defined( _MSC_VER )
#define ${library_name_upper_case}_DEPRECATED	__declspec(deprecated)
#else
#define ${library_name_upper_case}_DEPRECATED
#endif
#endif

#endif /* !defined( _${library_name_upper_case}_FEATURES_H ) */

