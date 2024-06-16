dnl Function to check if DLL support is needed
AC_DEFUN([AX_${library_name:upper_case}_CHECK_DLL_SUPPORT],
  [AS_IF(
    [test "x$$enable_shared" = xyes],
    [AS_CASE(
      [$$host],
      [*cygwin* | *mingw* | *msys*],
      [AC_DEFINE(
        [HAVE_DLLMAIN],
        [1],
        [Define to 1 to enable the DllMain function.])
      AC_SUBST(
        [HAVE_DLLMAIN],
        [1])

      AC_SUBST(
        [${library_name:upper_case}_DLL_EXPORT],
        ["-D${library_name:upper_case}_DLL_EXPORT"])

      AC_SUBST(
        [${library_name:upper_case}_DLL_IMPORT],
        ["-D${library_name:upper_case}_DLL_IMPORT"])
      ])
    ])
  ])

