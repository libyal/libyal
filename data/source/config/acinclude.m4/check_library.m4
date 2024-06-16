dnl Function to detect if ${library_name} dependencies are available
AC_DEFUN([AX_${library_name:upper_case}_CHECK_LOCAL],
  [dnl Check for internationalization functions in ${library_name}/${library_name}_i18n.c
  AC_CHECK_FUNCS([bindtextdomain])
])

