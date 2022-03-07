#
# Conditional build:
%bcond_without	systemd		# without systemd units

Summary:	Program to distribute compilation of C or C++
Summary(pl.UTF-8):	Program do rozdzielania kompilacji programów w C lub C++
Name:		icecream
Version:	1.4
Release:	1
License:	GPL v2
Group:		Development/Languages
Source0:	https://github.com/icecc/icecream/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	3aaecba85978a61cae2739a48ca05ca3
Source1:	%{name}.sysconfig
Source2:	%{name}-iceccd.init
Source3:	%{name}-scheduler.init
Source4:	%{name}.tmpfiles
Source5:	iceccd.service
Source6:	icecc-scheduler.service
URL:		http://en.opensuse.org/Icecream
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.11
BuildRequires:	docbook-dtd45-xml
BuildRequires:	docbook2X
BuildRequires:	libarchive-devel
BuildRequires:	libcap-ng-devel
BuildRequires:	librsync-devel
BuildRequires:	libstdc++-devel >= 6:4.8.1
BuildRequires:	libtool
BuildRequires:	lzo-devel
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	zstd-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Icecream is a distributed compile system. It allows parallel compiling
by distributing the compile jobs to several nodes of a compile network
running the icecc daemon. The icecc scheduler routes the jobs and
provides status and statistics information to the icecc monitor. Each
compile node can accept one or more compile jobs depending on the
number of processors and the settings of the daemon. Link jobs and
other jobs which cannot be distributed are executed locally on the
node where the compilation is started.

%package daemon
Summary:	Program to distribute compilation of C or C++ (daemon)
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-libs = %{version}-%{release}
Requires:	bash
Requires:	binutils
Requires:	coreutils
Requires:	file
Requires:	glibc-misc
Requires:	grep
Requires:	ldconfig
Requires:	rc-scripts
Requires:	sed
%{?with_systemd:Requires:	systemd-units >= 38}
Requires:	tar
Suggests:	bzip2
Suggests:	gzip
Suggests:	xz
Suggests:	zstd
Obsoletes:	icecream < 1.3.1-2

%description daemon
Icecream is a distributed compile system. It allows parallel compiling
by distributing the compile jobs to several nodes of a compile network
running the icecc daemon. The icecc scheduler routes the jobs and
provides status and statistics information to the icecc monitor. Each
compile node can accept one or more compile jobs depending on the
number of processors and the settings of the daemon. Link jobs and
other jobs which cannot be distributed are executed locally on the
node where the compilation is started.

This package contains icecream daemon.

%package scheduler
Summary:	Program to distribute compilation of C or C++ (scheduler)
Requires:	%{name}-common = %{version}-%{release}
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts
%{?with_systemd:Requires:	systemd-units >= 38}
Conflicts:	icecream < 1.3.1-2

%description scheduler
Icecream is a distributed compile system. It allows parallel compiling
by distributing the compile jobs to several nodes of a compile network
running the icecc daemon. The icecc scheduler routes the jobs and
provides status and statistics information to the icecc monitor. Each
compile node can accept one or more compile jobs depending on the
number of processors and the settings of the daemon. Link jobs and
other jobs which cannot be distributed are executed locally on the
node where the compilation is started.

This package contains icecream scheduler.

%package common
Summary:	Common files for Icecream daemon and scheduler
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Conflicts:	icecream < 1.3.1-2
BuildArch:	noarch

%description common
Common files for Icecream daemon and scheduler.

%package libs
Summary:	Icecream shared library
Group:		Libraries
Conflicts:	icecream < 1.3.1-2

%description libs
Icecream shared library.

%package devel
Summary:	Header files for icecream
Summary(pl.UTF-8):	Pliki nagłówkowe icecream
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for icecream.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla icecream.

%prep
%setup -q

%{__sed} -E -i -e '1s,#!\s*/usr/bin/env\s+bash(\s|$),#!%{__bash}\1,' \
	client/icecc-create-env.in


%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	ac_cv_path_DOCBOOK2X=docbook2X2man \
	--enable-clang-wrappers \
	--enable-shared \
	--disable-silent-rules \
	--disable-static

%{__make} \
	CFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_localstatedir}/run/icecc \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/icecream
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/iceccd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/icecc-scheduler

cp -p %{SOURCE4} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

%if %{with systemd}
install -d $RPM_BUILD_ROOT%{systemdunitdir}
cp -p %{SOURCE5} %{SOURCE6} $RPM_BUILD_ROOT%{systemdunitdir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	daemon
/sbin/chkconfig --add iceccd
%service iceccd restart
%{?with_systemd:%systemd_post iceccd.service}

%preun	daemon
if [ "$1" = "0" ]; then
	%service iceccd stop
	/sbin/chkconfig --del iceccd
fi
%{?with_systemd:%systemd_preun iceccd.service}

%postun	daemon
%{?with_systemd:%systemd_reload}

%post	scheduler
%{?with_systemd:%systemd_post icecc-scheduler.service}

%preun	scheduler
%{?with_systemd:%systemd_preun icecc-scheduler.service}

%postun	scheduler
%{?with_systemd:%systemd_reload}

%pre	common
%groupadd -g 197 icecream
%useradd -u 197 -s /bin/false -d /var/cache/icecream -c "Icecream User" -g icecream icecream

%postun	common
if [ "$1" = "0" ]; then
	%userremove icecream
	%groupremove icecream
fi

%triggerpostun common -- icecream < 1.3.1-2
%groupadd -g 197 icecream
%useradd -u 197 -s /bin/false -d /var/cache/icecream -c "Icecream User" -g icecream icecream

%post	libs -p /sbin/ldconfig

%postun	libs -p /sbin/ldconfig

%files daemon
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/iceccd
%attr(755,root,root) %{_bindir}/icecc
%attr(755,root,root) %{_bindir}/icecc-create-env
%attr(755,root,root) %{_bindir}/icecc-test-env
%attr(755,root,root) %{_bindir}/icerun
%attr(755,root,root) %{_sbindir}/iceccd
%dir %{_libexecdir}/icecc
%dir %{_libexecdir}/icecc/bin
%attr(755,root,root) %{_libexecdir}/icecc/bin/c++
%attr(755,root,root) %{_libexecdir}/icecc/bin/cc
%attr(755,root,root) %{_libexecdir}/icecc/bin/clang
%attr(755,root,root) %{_libexecdir}/icecc/bin/clang++
%attr(755,root,root) %{_libexecdir}/icecc/bin/g++
%attr(755,root,root) %{_libexecdir}/icecc/bin/gcc
%attr(755,root,root) %{_libexecdir}/icecc/compilerwrapper
%attr(755,root,root) %{_libexecdir}/icecc/icecc-create-env
%{_mandir}/man1/icecc-create-env.1*
%{_mandir}/man1/icecc.1*
%{_mandir}/man1/iceccd.1*
%{_mandir}/man1/icerun.1*
%if %{with systemd}
%{systemdunitdir}/iceccd.service
%endif
%{systemdtmpfilesdir}/%{name}.conf
%dir %attr(770,icecream,icecream) %{_localstatedir}/run/icecc

%files scheduler
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/icecc-scheduler
%attr(755,root,root) %{_sbindir}/icecc-scheduler
%{_mandir}/man1/icecc-scheduler.1*
%if %{with systemd}
%{systemdunitdir}/icecc-scheduler.service
%endif

%files common
%defattr(644,root,root,755)
%doc NEWS README TODO
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/icecream
%{_mandir}/man7/icecream*.7*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libicecc.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libicecc.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libicecc.so
%{_libdir}/libicecc.la
%{_includedir}/icecc
%{_pkgconfigdir}/icecc.pc
