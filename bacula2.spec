######################################################
# SpecFile: bacula2.spec 
# Generato: http://www.mandrivausers.ro/
# Build for Stella Linux by Nux
# http://li.nux.ro/stella/
# MRB-Falticska Florin
######################################################


%define _hardened_build 1
%define working_dir	/var/spool/bacula2
%define script_dir	/usr/libexec/bacula2
%define group		Archiving/Backup

Summary: 	Backup client for bacula version 2 server
Name: 		bacula2
Version: 	2.4.4
Release: 	1
License: 	GPLv2 
Group:   	%{group}

URL: 		http://www.bacula.org
Source0: 	http://downloads.sf.net/bacula/bacula-%{version}.tar.gz
Source1: 	bacula2-fd.service
Source100: 	%{name}.rpmlintrc

Patch0:		bacula2-2.4.4-utf8.patch
Patch1: 	bacula2-config.patch
Patch2: 	bacula2-3.0.2-openssl.patch
Patch3: 	bacula2-2.4.4-python27.patch
Patch4: 	bacula2-2.4.4-daemon-name.patch

BuildRequires: pkgconfig(openssl)
BuildRequires: perl
BuildRequires: acl-devel
BuildRequires: pkgconfig(zlib)
BuildRequires: pkgconfig(python) 
BuildRequires: stdc++-devel
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig
BuildRequires: glibc-devel
BuildRequires: sed
BuildRequires: systemd-units
BuildRequires: tcp_wrappers-devel


%description
Bacula is a set of programs that allow you to manage the backup, recovery,
and verification of computer data across a network of different computers.
It is based on a client/server architecture and is efficient and relatively
easy to use, while offering many advanced storage management features that
make it easy to find and recover lost or damaged files.

The bacula2 packages are clients suitable for use with a bacula version
2.x server (director), since later clients are incompatible.

#-----------client-------------
%package 	client
Summary: 	Bacula backup client
Group:   	%{group}
Requires: 	bacula2-common = %{EVRD}
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units


%description 	client
Bacula is a set of programs that allow you to manage the backup, recovery,
and verification of computer data across a network of different computers.
It is based on a client/server architecture.

This package contains the bacula version 2 client, the daemon running on
the system to be backed up to a bacula version 2 server (director).

#--------common----------------
%package 	common
Summary: 	Common Bacula utilities
Group:   	%{group}
Requires(pre): 	shadow-utils

%description common
Bacula is a set of programs that allow you to manage the backup, recovery,
and verification of computer data across a network of different computers.
It is based on a client/server architecture.

The bacula2 packages are clients suitable for use with a bacula version
2.x server (director), since later clients are incompatible.

%prep
%setup -q -n bacula-%{version}

%patch0 -p1
%patch1 -p1
%patch2 -p2
%patch3 -p0


# Fix attr
find examples -type f | xargs chmod -x
find updatedb -type f | xargs chmod -x
chmod -x src/console/conio.c

%build
# TODO: ugly but works..if smbody can do it better be my guest Sflo
CFLAGS="$(echo %{optflags}|sed s/-D_FORTIFY_SOURCE=./-U_FORTIFY_SOURCE/)" \
  %configure \
	--sysconfdir=%{_sysconfdir}/bacula2 \
	--with-fd-user=root \
	--with-fd-group=root \
	--with-fd-password=@@FD_PASSWORD@@ \
	--with-mon-dir-password=@@MON_DIR_PASSWORD@@ \
	--with-mon-fd-password=@@MON_FD_PASSWORD@@ \
	--with-mon-sd-password=@@MON_SD_PASSWORD@@ \
	--with-working-dir=%{working_dir} \
	--with-scriptdir=%{script_dir} \
	--with-smtp-host=localhost \
	--with-subsys-dir=%{_localstatedir}/lock/subsys \
	--with-pid-dir=%{_localstatedir}/run \
	--enable-client-only \
	--enable-largefile \
	--with-openssl \
	--with-tcp-wrappers \
	--with-python \
	--enable-smartalloc \
	--enable-tray-monitor
	
	
%{make}

%install
%{makeinstall_std}

# Desktop Integration for the console apps and the traymonitor
mkdir -p %{buildroot}%{_bindir}

# Initscript
install -m 755 -D %{SOURCE1}  %{buildroot}%{_unitdir}/bacula2-fd.service

# Create the bacula user's home directory
mkdir -p %{buildroot}%{_localstatedir}/spool/bacula2

# workaround so files from bacula2 screw the main bacula package Sflo
mv %{buildroot}%{_sbindir}/bacula-fd %{buildroot}%{_sbindir}/bacula2-fd
mv %{buildroot}%{_mandir}/man8/bacula-fd.8.gz %{buildroot}%{_mandir}/man8/bacula2-fd.8.gz

# Fix some linting Sflo
chmod 755 %{buildroot}%{_sbindir}/*

%pre common
getent group bacula >/dev/null || groupadd -r bacula
getent passwd bacula >/dev/null || \
	useradd -r -s /sbin/nologin -d %{_localstatedir}/spool/bacula2 -M \
		-c 'Bacula Backup System' -g bacula bacula
exit 0

%post client
/sbin/chkconfig --add bacula2-fd

%preun client
if [ $1 = 0 ]; then
	/bin/systemctl --no-reload disable bacula2-fd.service > /dev/null 2>&1 || :
	/bin/systemctl stop bacula2-fd.service > /dev/null 2>&1 || :
fi

%postun client
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ "$1" -ge "1" ]; then
	/bin/systemctl try-restart bacula2-fd.service >/dev/null 2>&1 || :
fi


%files common
%doc AUTHORS ChangeLog COPYING LICENSE README SUPPORT VERIFYING examples/
%dir %{_sysconfdir}/bacula2/
%dir %attr(750, bacula, bacula) %{_localstatedir}/spool/bacula2/
%{script_dir}/*
%{_mandir}/man1/*

%files client
%{_sbindir}/btraceback
%{_sbindir}/bacula2-fd
%{_unitdir}/bacula2-fd.service
%config(noreplace) %{_sysconfdir}/bacula2/bacula-fd.conf
%{_mandir}/man8/*

