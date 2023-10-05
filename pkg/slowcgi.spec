# Linux port of OpenBSD slowcgi
#
# spec file for SUSE & Red Hat distros
# Tested with:
#   openSUSE Leap (15.5)
#   SLES (12 SP5, 15 SP5)
#   CentOS 7.5
#
# SLES 12:	enable PackageHub extension for libbsd (and nginx)
# CentOS 7:	use EPEL 7 for libbsd (and nginx)

Name:		slowcgi
Version:	7.2
Release:	1
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
%if %suse_version < 1500
# systemd_post definition is incorrect in older releases, before this patch
# https://build.opensuse.org/request/show/576778
BuildRequires:	systemd-rpm-macros >= 3-10.9.1
%else
# Leap 15.0 is good, but its version tag (e.g. 3-lp150.5.20) complicates version comparisons
BuildRequires:	systemd-rpm-macros
%endif

# compat for _fillupdir location change
%if ! %{defined _fillupdir}
%define _fillupdir /var/adm/fillup-templates
%endif

# build a debuginfo package
%debug_package

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
install -D -m 644 pkg/tmpfiles_slowcgi-nginx.conf %{buildroot}%{_tmpfilesdir}/slowcgi-nginx.conf

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
%tmpfiles_create %{_tmpfilesdir}/slowcgi-nginx.conf
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
%{_tmpfilesdir}/slowcgi-nginx.conf
%doc README

%changelog
* Thu Oct 05 2023 adaugherity@tamu.edu 7.2-1
- Sync upstream sources with OpenBSD 7.4 (no changes since 7.2):
  * Just a bit of KNF.
  * Allow specifying -d multiple times. Only print the fcgi header data if
    debug > 1 (-dd) since it adds a lot of noise to the output.
  * accept_reserve() counter function argument doesn't need to be volatile.
  * Ignore SIGPIPE by default and restore default behaviour before executing
    the CGI.
  * Use LIST instead of SLIST for requests. The way SLIST_REMOVE was used did
    a double traverse of the list which now is replaced with no traversal at
    all.  Also stop double wrapping requests just for the list.
  * Stop sending debug logging to syslog (which would then drop it on the
    floor) all the time. Instead debug logging must be requested with the
    new -v flag.
  * list -v with -d in SYNOPSIS, instead of seperately, and add -v to usage()
  * add a -t flag to change the request timeout
  * zap extra space in usage added by mistake in last commit.

* Mon Aug 05 2019 adaugherity@tamu.edu 6.5-1
- Sync upstream sources with OpenBSD 6.5:
  * Make the owner of fcgi socket configurable.
  * Call daemon with 0 as first argument so that it changes the cwd to /.
  * When calculating the fd limit before accepting a new connection also
    account for the inflight fds caused by the new connection.
- Dropped patch for socket user (committed upstream).

* Mon Sep 24 2018 adaugherity@tamu.edu 6.3-5
- %%systemd_post has been fixed on 42.3/SLES 12 SP3, so buildreq the fixed
  version instead of redefining the macro.
  * Reorder if suse_version stuff -- %%debug_package needs to come later, since
    it defines a subpackage.

* Fri Aug 10 2018 adaugherity@tamu.edu 6.3-4
- Default to the nginx user for both socket & CGI, since slowcgi is more likely
  to be used with nginx, than with other web servers (e.g. apache) that
  natively support CGI.
  * This also allows the same "distro defaults" patch to be used on both SUSE
    and Red Hat, as both use an 'nginx' user with home directory
    /var/lib/nginx, whereas the apache users are different.
- Add tmpfiles.d entry to create a /run/nginx directory; placing the socket
  here resolves SELinux issues on RHEL 7.

* Thu Aug 09 2018 adaugherity@tamu.edu 6.3-3
- Update from upstream -- add '-U socket_user' option.

* Tue Aug 07 2018 adaugherity@tamu.edu 6.3-2
- Build on CentOS 7 also.
- Switch to upstream %%systemd_* macros; the SUSE %%service_* macros also
  handle upgrades from SysV init scripts, but we don't care about that.

* Mon Jul 30 2018 adaugherity@tamu.edu 6.3-1
- Initial port to Linux, built on openSUSE Leap 15.0.
