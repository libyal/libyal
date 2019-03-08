dnl Checks for libftxf required headers and functions
dnl
dnl Version: 20190308

dnl Function to detect if libftxf is available
dnl ac_libftxf_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBFTXF_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libftxf" = xno],
    [ac_cv_libftxf=no],
    [ac_cv_libftxf=check
    dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libftxf" != x && test "x$ac_cv_with_libftxf" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libftxf"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libftxf}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libftxf}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libftxf],
          [1])
        ])
      ],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libftxf],
          [libftxf >= 20180725],
          [ac_cv_libftxf=yes],
          [ac_cv_libftxf=check])
        ])
      AS_IF(
        [test "x$ac_cv_libftxf" = xyes],
        [ac_cv_libftxf_CPPFLAGS="$pkg_cv_libftxf_CFLAGS"
        ac_cv_libftxf_LIBADD="$pkg_cv_libftxf_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libftxf" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libftxf.h])

      AS_IF(
        [test "x$ac_cv_header_libftxf_h" = xno],
        [ac_cv_libftxf=no],
        [dnl Check for the individual functions
        ac_cv_libftxf=yes

        AC_CHECK_LIB(
          ftxf,
          libftxf_get_version,
          [ac_cv_libftxf_dummy=yes],
          [ac_cv_libftxf=no])

        dnl Record functions
        AC_CHECK_LIB(
          ftxf,
          libftxf_record_initialize,
          [ac_cv_libftxf_dummy=yes],
          [ac_cv_libftxf=no])
        AC_CHECK_LIB(
          ftxf,
          libftxf_record_free,
          [ac_cv_libftxf_dummy=yes],
          [ac_cv_libftxf=no])

        AC_CHECK_LIB(
          ftxf,
          libftxf_record_copy_from_byte_stream,
          [ac_cv_libftxf_dummy=yes],
          [ac_cv_libftxf=no])

        ac_cv_libftxf_LIBADD="-lftxf"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libftxf" != x && test "x$ac_cv_with_libftxf" != xauto-detect && test "x$ac_cv_libftxf" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libftxf in directory: $ac_cv_with_libftxf],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libftxf" = xyes],
    [AC_DEFINE(
      [HAVE_LIBFTXF],
      [1],
      [Define to 1 if you have the `ftxf' library (-lftxf).])
    ])

  AS_IF(
    [test "x$ac_cv_libftxf" = xyes],
    [AC_SUBST(
      [HAVE_LIBFTXF],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBFTXF],
      [0])
    ])
  ])

dnl Function to detect if libftxf dependencies are available
AC_DEFUN([AX_LIBFTXF_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libftxf_CPPFLAGS="-I../libftxf";
  ac_cv_libftxf_LIBADD="../libftxf/libftxf.la";

  ac_cv_libftxf=local
  ])

dnl Function to detect how to enable libftxf
AC_DEFUN([AX_LIBFTXF_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libftxf],
    [libftxf],
    [search for libftxf in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBFTXF_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libftxf" != xyes],
    [AX_LIBFTXF_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBFTXF],
      [1],
      [Define to 1 if the local version of libftxf is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBFTXF],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBFTXF],
    [test "x$ac_cv_libftxf" = xlocal])
  AS_IF(
    [test "x$ac_cv_libftxf_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBFTXF_CPPFLAGS],
      [$ac_cv_libftxf_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libftxf_LIBADD" != "x"],
    [AC_SUBST(
      [LIBFTXF_LIBADD],
      [$ac_cv_libftxf_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libftxf" = xyes],
    [AC_SUBST(
      [ax_libftxf_pc_libs_private],
      [-lftxf])
    ])

  AS_IF(
    [test "x$ac_cv_libftxf" = xyes],
    [AC_SUBST(
      [ax_libftxf_spec_requires],
      [libftxf])
    AC_SUBST(
      [ax_libftxf_spec_build_requires],
      [libftxf-devel])
    ])
  ])

