dnl Checks for libfole required headers and functions
dnl
dnl Version: 20190308

dnl Function to detect if libfole is available
dnl ac_libfole_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBFOLE_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libfole" = xno],
    [ac_cv_libfole=no],
    [ac_cv_libfole=check
    dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libfole" != x && test "x$ac_cv_with_libfole" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libfole"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libfole}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libfole}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libfole],
          [1])
        ])
      ],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libfole],
          [libfole >= 20120426],
          [ac_cv_libfole=yes],
          [ac_cv_libfole=check])
        ])
      AS_IF(
        [test "x$ac_cv_libfole" = xyes],
        [ac_cv_libfole_CPPFLAGS="$pkg_cv_libfole_CFLAGS"
        ac_cv_libfole_LIBADD="$pkg_cv_libfole_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libfole" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libfole.h])

      AS_IF(
        [test "x$ac_cv_header_libfole_h" = xno],
        [ac_cv_libfole=no],
        [dnl Check for the individual functions
        ac_cv_libfole=yes

        AC_CHECK_LIB(
          fole,
          libfole_get_version,
          [ac_cv_libfole_dummy=yes],
          [ac_cv_libfole=no])

        dnl TODO add functions

        ac_cv_libfole_LIBADD="-lfole"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libfole" != x && test "x$ac_cv_with_libfole" != xauto-detect && test "x$ac_cv_libfole" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libfole in directory: $ac_cv_with_libfole],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libfole" = xyes],
    [AC_DEFINE(
      [HAVE_LIBFOLE],
      [1],
      [Define to 1 if you have the `fole' library (-lfole).])
    ])

  AS_IF(
    [test "x$ac_cv_libfole" = xyes],
    [AC_SUBST(
      [HAVE_LIBFOLE],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBFOLE],
      [0])
    ])
  ])

dnl Function to detect if libfole dependencies are available
AC_DEFUN([AX_LIBFOLE_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libfole_CPPFLAGS="-I../libfole";
  ac_cv_libfole_LIBADD="../libfole/libfole.la";

  ac_cv_libfole=local
  ])

dnl Function to detect how to enable libfole
AC_DEFUN([AX_LIBFOLE_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libfole],
    [libfole],
    [search for libfole in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBFOLE_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libfole" != xyes],
    [AX_LIBFOLE_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBFOLE],
      [1],
      [Define to 1 if the local version of libfole is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBFOLE],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBFOLE],
    [test "x$ac_cv_libfole" = xlocal])
  AS_IF(
    [test "x$ac_cv_libfole_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBFOLE_CPPFLAGS],
      [$ac_cv_libfole_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libfole_LIBADD" != "x"],
    [AC_SUBST(
      [LIBFOLE_LIBADD],
      [$ac_cv_libfole_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libfole" = xyes],
    [AC_SUBST(
      [ax_libfole_pc_libs_private],
      [-lfole])
    ])

  AS_IF(
    [test "x$ac_cv_libfole" = xyes],
    [AC_SUBST(
      [ax_libfole_spec_requires],
      [libfole])
    AC_SUBST(
      [ax_libfole_spec_build_requires],
      [libfole-devel])
    ])
  ])

