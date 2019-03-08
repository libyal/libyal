dnl Checks for libfwsi required headers and functions
dnl
dnl Version: 20190308

dnl Function to detect if libfwsi is available
dnl ac_libfwsi_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBFWSI_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libfwsi" = xno],
    [ac_cv_libfwsi=no],
    [ac_cv_libfwsi=check
    dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libfwsi" != x && test "x$ac_cv_with_libfwsi" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libfwsi"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libfwsi}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libfwsi}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libfwsi],
          [1])
        ])
      ],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libfwsi],
          [libfwsi >= 20140827],
          [ac_cv_libfwsi=yes],
          [ac_cv_libfwsi=check])
        ])
      AS_IF(
        [test "x$ac_cv_libfwsi" = xyes],
        [ac_cv_libfwsi_CPPFLAGS="$pkg_cv_libfwsi_CFLAGS"
        ac_cv_libfwsi_LIBADD="$pkg_cv_libfwsi_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libfwsi" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libfwsi.h])

      AS_IF(
        [test "x$ac_cv_header_libfwsi_h" = xno],
        [ac_cv_libfwsi=no],
        [dnl Check for the individual functions
        ac_cv_libfwsi=yes

        AC_CHECK_LIB(
          fwsi,
          libfwsi_get_version,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])

        dnl Item functions
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_initialize,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_free,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_copy_from_byte_stream,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])

        dnl Item list functions
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_list_initialize,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_list_free,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])
        AC_CHECK_LIB(
          fwsi,
          libfwsi_item_list_copy_from_byte_stream,
          [ac_cv_libfwsi_dummy=yes],
          [ac_cv_libfwsi=no])

        ac_cv_libfwsi_LIBADD="-lfwsi"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libfwsi" != x && test "x$ac_cv_with_libfwsi" != xauto-detect && test "x$ac_cv_libfwsi" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libfwsi in directory: $ac_cv_with_libfwsi],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libfwsi" = xyes],
    [AC_DEFINE(
      [HAVE_LIBFWSI],
      [1],
      [Define to 1 if you have the `fwsi' library (-lfwsi).])
    ])

  AS_IF(
    [test "x$ac_cv_libfwsi" = xyes],
    [AC_SUBST(
      [HAVE_LIBFWSI],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBFWSI],
      [0])
    ])
  ])

dnl Function to detect if libfwsi dependencies are available
AC_DEFUN([AX_LIBFWSI_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libfwsi_CPPFLAGS="-I../libfwsi";
  ac_cv_libfwsi_LIBADD="../libfwsi/libfwsi.la";

  ac_cv_libfwsi=local
  ])

dnl Function to detect how to enable libfwsi
AC_DEFUN([AX_LIBFWSI_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libfwsi],
    [libfwsi],
    [search for libfwsi in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBFWSI_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libfwsi" != xyes],
    [AX_LIBFWSI_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBFWSI],
      [1],
      [Define to 1 if the local version of libfwsi is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBFWSI],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBFWSI],
    [test "x$ac_cv_libfwsi" = xlocal])
  AS_IF(
    [test "x$ac_cv_libfwsi_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBFWSI_CPPFLAGS],
      [$ac_cv_libfwsi_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libfwsi_LIBADD" != "x"],
    [AC_SUBST(
      [LIBFWSI_LIBADD],
      [$ac_cv_libfwsi_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libfwsi" = xyes],
    [AC_SUBST(
      [ax_libfwsi_pc_libs_private],
      [-lfwsi])
    ])

  AS_IF(
    [test "x$ac_cv_libfwsi" = xyes],
    [AC_SUBST(
      [ax_libfwsi_spec_requires],
      [libfwsi])
    AC_SUBST(
      [ax_libfwsi_spec_build_requires],
      [libfwsi-devel])
    ])
  ])

