%global bootstrap 1
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}
%global patchdate 20200504

Summary:        MiNT cross-compiler (GCC) for C.
Name:           m68k-atari-mint-gcc
Version:        4.6.4
Release:        1%{?dist}
License:        GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions
Group:          Development/Languages
URL:            http://gcc.gnu.org
Source0:        https://ftp.gnu.org/pub/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.bz2
Patch0:         http://vincent.riviere.free.fr/soft/m68k-atari-mint/archives/gcc-%{version}-mint-%{patchdate}.patch.bz2
# fix ppc64le build - Altivec routine in libcpp works only on big endian systems
Patch1:         gcc-4.6.4-lex-altivec.patch

BuildRequires:  m68k-atari-mint-binutils
%if ! 0%{?bootstrap}
BuildRequires:  m68k-atari-mint-mintlib
BuildRequires:  m68k-atari-mint-pml
%endif
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  libmpc-devel
BuildRequires:  zlib-devel
BuildRequires:  libgomp
BuildRequires:  flex

Requires:       m68k-atari-mint-binutils
%if ! 0%{?bootstrap}
Requires:       m68k-atari-mint-mintlib
Requires:       m68k-atari-mint-pml
%endif


%description
MiNT cross-compiler (GCC) for C.


%prep
%setup -q -n gcc-%{version}
%patch0 -p1
%patch1 -p1


%build
mkdir -p build
pushd build

CC=gcc
OPT_FLAGS=`echo %{optflags}|sed -e 's/\(-Wp,\)\?-D_FORTIFY_SOURCE=[12]//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-flto=auto//g;s/-flto//g;s/-ffat-lto-objects//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-m64//g;s/-m32//g;s/-m31//g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-mfpmath=sse/-mfpmath=sse -msse2/g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/ -pipe / /g'`
OPT_FLAGS=`echo $OPT_FLAGS|sed -e 's/-Werror=format-security/-Wformat-security/g'`


CC="$CC" CFLAGS="$OPT_FLAGS" \
../configure \
    --prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --includedir=%{_includedir} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
    --datadir=%{_datadir} \
    --build=%_build --host=%_host \
    --with-gnu-as --with-gnu-ld --verbose \
    --disable-plugin \
    --with-system-zlib \
    --disable-nls --without-included-gettext \
    --disable-lto \
%if 0%{?bootstrap}
    --with-newlib --without-headers \
    --enable-languages="c" \
%else
    --without-newlib \
    --enable-languages="c,c++" \
    --with-gxx-include-dir=%{mint_includedir}/c++ \
%endif
    --target=%{mint_target} \
    --with-sysroot=%{mint_sysroot} \
    CFLAGS_FOR_TARGET="-O2 -fomit-frame-pointer" \
    CXXFLAGS_FOR_TARGET="-O2 -fomit-frame-pointer"


%if 0%{?bootstrap}
make %{?_smp_mflags} all-gcc all-target-libgcc
%else
make %{?_smp_mflags} all
%endif

popd


%install
pushd build

%if 0%{?bootstrap}
make DESTDIR=$RPM_BUILD_ROOT install-gcc install-target-libgcc
%else
make DESTDIR=$RPM_BUILD_ROOT install
%endif

popd

# fix some things
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty.a
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/*
rm -rf $RPM_BUILD_ROOT%{_libdir}/gcc/%{mint_target}/%{version}/plugin
rm -rf $RPM_BUILD_ROOT%{_datadir}/gcc-%{version}/python

%if ! 0%{?bootstrap}
mkdir -p $RPM_BUILD_ROOT%{mint_libdir}
mv $RPM_BUILD_ROOT%{_prefix}/%{mint_target}/lib/* $RPM_BUILD_ROOT%{mint_libdir}
%endif

# Don't want the *.la files.
find $RPM_BUILD_ROOT -name '*.la' -delete


%files
%doc
%{_bindir}/%{mint_target}-*
%{_mandir}/man1/%{mint_target}-*.1*
%{_libexecdir}/gcc/%{mint_target}
%{_libdir}/gcc/%{mint_target}
%if ! 0%{?bootstrap}
%{mint_libdir}/*
%{mint_includedir}/c++
%endif


%changelog
* Thu Jun 16 2022 Dan Horák <dan[at]danny.cz> - 4.6.4-2
- update to 20200504 patch
- fix build on ppc64le host

* Wed May 14 2014 Dan Horák <dan[at]danny.cz> - 4.6.4-1
- update to 4.6.4

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> - 4.6.3-2
- non-bootstrap build

* Sun Mar 25 2012 Dan Horák <dan[at]danny.cz> - 4.6.3-1
- update to 4.6.3

* Thu Aug 04 2011 Dan Horák <dan[at]danny.cz> - 4.5.3-1
- bootstrap enabled
- initial Fedora version
