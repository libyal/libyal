dnl Checks for libwrc required headers and functions
dnl
dnl Version: 20200716

dnl Function to detect if libwrc is available
dnl ac_libwrc_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBWRC_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libwrc" = xno],
    [ac_cv_libwrc=no],
    [ac_cv_libwrc=check
    dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libwrc" != x && test "x$ac_cv_with_libwrc" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libwrc"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libwrc}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libwrc}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libwrc],
          [1])
        ])
      ],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libwrc],
          [libwrc >= 20120425],
          [ac_cv_libwrc=yes],
          [ac_cv_libwrc=check])
        ])
      AS_IF(
        [test "x$ac_cv_libwrc" = xyes],
        [ac_cv_libwrc_CPPFLAGS="$pkg_cv_libwrc_CFLAGS"
        ac_cv_libwrc_LIBADD="$pkg_cv_libwrc_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libwrc" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libwrc.h])

      AS_IF(
        [test "x$ac_cv_header_libwrc_h" = xno],
        [ac_cv_libwrc=no],
        [dnl Check for the individual functions
        ac_cv_libwrc=yes

        AC_CHECK_LIB(
          wrc,
          libwrc_get_version,
          [ac_cv_libwrc_dummy=yes],
          [ac_cv_libwrc=no])

        dnl TODO add functions

        ac_cv_libwrc_LIBADD="-lwrc"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libwrc" != x && test "x$ac_cv_with_libwrc" != xauto-detect && test "x$ac_cv_libwrc" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libwrc in directory: $ac_cv_with_libwrc],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libwrc" = xyes],
    [AC_DEFINE(
      [HAVE_LIBWRC],
      [1],
      [Define to 1 if you have the `wrc' library (-lwrc).])
    ])

  AS_IF(
    [test "x$ac_cv_libwrc" = xyes],
    [AC_SUBST(
      [HAVE_LIBWRC],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBWRC],
      [0])
    ])
  ])

dnl Function to detect if libwrc dependencies are available
AC_DEFUN([AX_LIBWRC_CHECK_LOCAL],
  [ac_cv_libwrc_CPPFLAGS="-I../libwrc";
  ac_cv_libwrc_LIBADD="../libwrc/libwrc.la";

  ac_cv_libwrc=local
  ])

dnl Function to detect how to enable libwrc
AC_DEFUN([AX_LIBWRC_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libwrc],
    [libwrc],
    [search for libwrc in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBWRC_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libwrc" != xyes],
    [AX_LIBWRC_CHECK_LOCAL

  AC_DEFINE(
    [HAVE_LOCAL_LIBWRC],
    [1],
    [Define to 1 if the local version of libwrc is used.])
  AC_SUBST(
    [HAVE_LOCAL_LIBWRC],
    [1])
  ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBWRC],
    [test "x$ac_cv_libwrc" = xlocal])
  AS_IF(
    [test "x$ac_cv_libwrc_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBWRC_CPPFLAGS],
      [$ac_cv_libwrc_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libwrc_LIBADD" != "x"],
    [AC_SUBST(
      [LIBWRC_LIBADD],
      [$ac_cv_libwrc_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libwrc" = xyes],
    [AC_SUBST(
      [ax_libwrc_pc_libs_private],
      [-lwrc])
    ])

  AS_IF(
    [test "x$ac_cv_libwrc" = xyes],
    [AC_SUBST(
      [ax_libwrc_spec_requires],
      [libwrc])
    AC_SUBST(
      [ax_libwrc_spec_build_requires],
      [libwrc-devel])
    ])
  ])
