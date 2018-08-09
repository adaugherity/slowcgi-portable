# Linux port of OpenBSD slowcgi
#
# spec file for SUSE & Red Hat distros
# Tested with:
#   openSUSE Leap (42.3, 15.0)
#   SLES (12 SP3, 15)
#   CentOS 7.5
#
# SLES 12:	enable PackageHub extension for libbsd (and nginx)
# CentOS 7:	use EPEL 7 for libbsd (and nginx)

Name:		slowcgi
Version:	6.3
Release:	3
Summary:	OpenBSD FastCGI to CGI wrapper server
License:	ISC
Group:		Productivity/Networking/Web/Servers
Url:		https://github.com/adaugherity/slowcgi-portable
Source0:	%{name}-%{version}.tar.gz
BuildRequires:	pkgconfig(libbsd-overlay)
BuildRequires:	pkgconfig(libevent)
BuildRequires:	make
BuildRequires:	gcc
#Requires:
%{?systemd_requires}
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

%if 0%{?suse_version}
BuildRequires: systemd-rpm-macros
# build a debuginfo package
%debug_package
# compat for _fillupdir location change
%if ! %{defined _fillupdir}
%define _fillupdir /var/adm/fillup-templates
%endif

%if %suse_version < 1500
# systemd_post definition is incorrect in older versions
# https://build.opensuse.org/request/show/576778
%define systemd_post() \
if [ $1 -eq 1 ] ; then \
        # Initial installation \
        systemctl preset %{?*} >/dev/null 2>&1 || : \
fi \
%{nil}
%endif

%else
%if 0%{?rhel}
BuildRequires:	systemd
# debuginfo packages are on by default
%endif
%endif

%description
slowcgi is a simple server that translates FastCGI requests to the CGI
protocol.  It executes the requested CGI script and translates its output back
to the FastCGI protocol.

%prep
%setup -q
make patch

%build
make %{?_smp_mflags}

%install
%make_install prefix=/usr mandir=%{_mandir}
install -D -m 644 pkg/slowcgi.service %{buildroot}%{_unitdir}/slowcgi.service

%if 0%{?suse_version}
ln -s service %{buildroot}/usr/sbin/rcslowcgi
install -D -m 644 pkg/sysconfig.slowcgi %{buildroot}%{_fillupdir}/sysconfig.slowcgi
%else
%if 0%{?rhel}
install -D -m 644 pkg/sysconfig.slowcgi %{buildroot}/etc/sysconfig/slowcgi
%endif
%endif


%post
%systemd_post slowcgi.service
%if 0%{?suse_version}
%fillup_only
%endif

%preun
%systemd_preun slowcgi.service

%postun
%systemd_postun_with_restart slowcgi.service

%files
%defattr(-,root,root)

%if 0%{?suse_version}
/usr/sbin/rcslowcgi
%{_fillupdir}/sysconfig.slowcgi
%else
%if 0%{?rhel}
%config(noreplace) /etc/sysconfig/slowcgi
%endif
%endif

/usr/sbin/slowcgi
# man page is automatically compressed
%{_mandir}/man8/slowcgi.8.gz
%{_unitdir}/slowcgi.service
%doc README

%changelog
* Tue Aug 09 2018 adaugherity@tamu.edu 6.3-3
- Update from upstream -- add '-U socket_user' option.
* Tue Aug 07 2018 adaugherity@tamu.edu 6.3-2
- Build on CentOS 7 also.
- Switch to upstream %%systemd_* macros; the SUSE %%service_* macros also
  handle upgrades from SysV init scripts, but we don't care about that.
* Mon Jul 30 2018 adaugherity@tamu.edu 6.3-1
- Initial port to Linux, built on openSUSE Leap 15.0.
