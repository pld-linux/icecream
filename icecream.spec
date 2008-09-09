Summary:	Program to distribute compilation of C or C++
Summary(pl.UTF-8):	Program do rozdzielania kompilacji programów w C lub C++
Name:		icecream
Version:	0.9.1
Release:	1
License:	GPL v2
Group:		Development/Languages
Source0:	ftp://ftp.suse.com/pub/projects/icecream/icecc-%{version}.tar.bz2
# Source0-md5:	d8f65259ef2f72d36c157b64a2ff11d5
URL:		http://en.opensuse.org/Icecream
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Icecream is the next generation distcc.

%description -l pl.UTF-8
Icecream jest kompilatorem distcc nowej generacji.

%package devel
Summary:	Header files for icecream
Summary(pl.UTF-8):	Pliki nagłówkowe icecream
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for icecream.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla icecream.

%prep
%setup -q -n icecc-%{version}

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--enable-shared \
	--disable-static

%{__make} \
	CFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc COPYING NEWS README TODO
%attr(755,root,root) %{_bindir}/icecc
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/lib*.so.*.*
%attr(755,root,root) %{_libdir}/libicecc.so.0
%{_libdir}/icecc

%files devel
%defattr(644,root,root,755)
%{_includedir}/icecc
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/libicecc.la
%{_pkgconfigdir}/*.pc
