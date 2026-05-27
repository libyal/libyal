dnl Functions for testing
dnl
dnl Version: 20260527

dnl Function to detect whether code coverage support should be enabled
AC_DEFUN([AX_TESTS_CHECK_ENABLE_CODE_COVERAGE],
  [AX_COMMON_ARG_ENABLE(
    [code-coverage],
    [code_coverage],
    [build for code coverage)],
    [no])

  AS_IF(
    [test "x$ac_cv_enable_code_coverage" != xno],
    [AX_COMMON_CHECK_COMPILER_FLAG(-fno-builtin-memcpy)

    AS_IF(
      [test "x$ac_cv_with_fno_builtin_memcpy" != xno],
      [AC_DEFINE(
        [HAVE_NO_BUILTIN_MEMCPY],
        [1],
        [Define to 1 if the compiler supports -fno-builtin-memcpy.])

      CFLAGS="$CFLAGS --coverage -fno-builtin-memcpy -O0"],
      [CFLAGS="$CFLAGS --coverage -O0"])

    CPPFLAGS="$CPPFLAGS -DOPTIMIZATION_DISABLED"
    LDFLAGS="--coverage"

    enable_shared=no])
  ])

dnl Function to detect if tests dependencies are available
AC_DEFUN([AX_TESTS_CHECK_LOCAL],
  [AC_CHECK_HEADERS([dlfcn.h])

  AC_CHECK_FUNCS([fmemopen getopt mkstemp setenv tzset unlink])

  AC_CHECK_LIB(
    dl,
    dlsym)

  AS_IF(
    [test "x$lt_cv_prog_gnu_ld" = xyes && test "x$ac_cv_lib_dl_dlsym" = xyes],
    [AC_DEFINE(
      [HAVE_GNU_DL_DLSYM],
      [1],
      [Define to 1 if dlsym function is available in GNU dl.])
    ])
  ])

dnl Function to detect if OSS-Fuzz build environment is available
AC_DEFUN([AX_TESTS_CHECK_OSSFUZZ],
  [AM_CONDITIONAL(
    HAVE_LIB_FUZZING_ENGINE,
    [test "x${LIB_FUZZING_ENGINE}" != x])
  AC_SUBST(
    [LIB_FUZZING_ENGINE],
    ["${LIB_FUZZING_ENGINE}"])
  ])

