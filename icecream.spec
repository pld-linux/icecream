Summary:	Program to distribute compilation of C or C++
Summary(pl.UTF-8):	Program do rozdzielania kompilacji programów w C lub C++
Name:		icecream
Version:	0.9.1
Release:	1
License:	GPL v2
Group:		Development/Languages
Source0:	ftp://ftp.suse.com/pub/projects/icecream/icecc-%{version}.tar.bz2
# Source0-md5:	d8f65259ef2f72d36c157b64a2ff11d5
Source1:	%{name}.sysconfig
Source2:	%{name}-iceccd.init
URL:		http://en.opensuse.org/Icecream
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	rc-scripts
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

install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}
install -d $RPM_BUILD_ROOT%{_libdir}/icecc/bin

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/icecream
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/iceccd

for i in cc gcc c++ g++; do
	ln -sf %{_bindir}/icecc $RPM_BUILD_ROOT%{_libdir}/icecc/bin/$i
	rm -f $RPM_BUILD_ROOT%{_bindir}/$i
done

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 197 icecream
%useradd -u 197 -s /bin/false -d /var/cache/icecream -c "Icecream User" -g icecream icecream

%post 
/sbin/ldconfig
/sbin/chkconfig --add iceccd
%service iceccd restart

%preun
if [ "$1" = "0" ]; then
	%service iceccd stop
	/sbin/chkconfig --del iceccd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove icecream
	%groupremove icecream
fi
/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README TODO
%attr(754,root,root) /etc/rc.d/init.d/iceccd
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/icecream
%attr(755,root,root) %{_bindir}/icecc
%attr(755,root,root) %{_sbindir}/iceccd
%attr(755,root,root) %{_sbindir}/scheduler
%attr(755,root,root) %{_libdir}/libicecc.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libicecc.so.0
%dir %{_libdir}/icecc
%dir %{_libdir}/icecc/bin
%attr(755,root,root) %{_libdir}/icecc/bin/cc
%attr(755,root,root) %{_libdir}/icecc/bin/gcc
%attr(755,root,root) %{_libdir}/icecc/bin/c++
%attr(755,root,root) %{_libdir}/icecc/bin/g++
%attr(755,root,root) %{_libdir}/icecc/icecc-create-env

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libicecc.so
%{_libdir}/libicecc.la
%{_includedir}/icecc
%{_pkgconfigdir}/icecc.pc
