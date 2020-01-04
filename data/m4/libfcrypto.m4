dnl Checks for libfcrypto required headers and functions
dnl
dnl Version: 20200104

dnl Function to detect if libfcrypto is available
dnl ac_libfcrypto_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBFCRYPTO_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libfcrypto" = xno],
    [ac_cv_libfcrypto=no],
    [dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libfcrypto" != x && test "x$ac_cv_with_libfcrypto" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libfcrypto"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libfcrypto}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libfcrypto}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libfcrypto],
          [1])
        ])
        ac_cv_libfcrypto=check],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libfcrypto],
          [libfcrypto >= 20200104],
          [ac_cv_libfcrypto=yes],
          [ac_cv_libfcrypto=check])
        ])
      AS_IF(
        [test "x$ac_cv_libfcrypto" = xyes],
        [ac_cv_libfcrypto_CPPFLAGS="$pkg_cv_libfcrypto_CFLAGS"
        ac_cv_libfcrypto_LIBADD="$pkg_cv_libfcrypto_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libfcrypto" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libfcrypto.h])

      AS_IF(
        [test "x$ac_cv_header_libfcrypto_h" = xno],
        [ac_cv_libfcrypto=no],
        [dnl Check for the individual functions
        ac_cv_libfcrypto=yes

        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_get_version,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        dnl RC4 context functions
        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_rc4_context_initialize,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])
        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_rc4_context_free,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_rc4_context_set_key,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_rc4_crypt,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        dnl Serpent context functions
        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_serpent_context_initialize,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])
        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_serpent_context_free,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_serpent_context_set_key,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_serpent_crypt_cbc,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])
        AC_CHECK_LIB(
          fcrypto,
          libfcrypto_serpent_crypt_ecb,
          [ac_cv_libfcrypto_dummy=yes],
          [ac_cv_libfcrypto=no])

        ac_cv_libfcrypto_LIBADD="-lfcrypto"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libfcrypto" != x && test "x$ac_cv_with_libfcrypto" != xauto-detect && test "x$ac_cv_libfcrypto" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libfcrypto in directory: $ac_cv_with_libfcrypto],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libfcrypto" = xyes],
    [AC_DEFINE(
      [HAVE_LIBFCRYPTO],
      [1],
      [Define to 1 if you have the `fcrypto' library (-lfcrypto).])
    ])

  AS_IF(
    [test "x$ac_cv_libfcrypto" = xyes],
    [AC_SUBST(
      [HAVE_LIBFCRYPTO],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBFCRYPTO],
      [0])
    ])
  ])

dnl Function to detect if libfcrypto dependencies are available
AC_DEFUN([AX_LIBFCRYPTO_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libfcrypto_CPPFLAGS="-I../libfcrypto";
  ac_cv_libfcrypto_LIBADD="../libfcrypto/libfcrypto.la";

  ac_cv_libfcrypto=local
  ])

dnl Function to detect how to enable libfcrypto
AC_DEFUN([AX_LIBFCRYPTO_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libfcrypto],
    [libfcrypto],
    [search for libfcrypto in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBFCRYPTO_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libfcrypto" != xyes],
    [AX_LIBFCRYPTO_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBFCRYPTO],
      [1],
      [Define to 1 if the local version of libfcrypto is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBFCRYPTO],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBFCRYPTO],
    [test "x$ac_cv_libfcrypto" = xlocal])
  AS_IF(
    [test "x$ac_cv_libfcrypto_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBFCRYPTO_CPPFLAGS],
      [$ac_cv_libfcrypto_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libfcrypto_LIBADD" != "x"],
    [AC_SUBST(
      [LIBFCRYPTO_LIBADD],
      [$ac_cv_libfcrypto_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libfcrypto" = xyes],
    [AC_SUBST(
      [ax_libfcrypto_pc_libs_private],
      [-lfcrypto])
    ])

  AS_IF(
    [test "x$ac_cv_libfcrypto" = xyes],
    [AC_SUBST(
      [ax_libfcrypto_spec_requires],
      [libfcrypto])
    AC_SUBST(
      [ax_libfcrypto_spec_build_requires],
      [libfcrypto-devel])
    ])
  ])

