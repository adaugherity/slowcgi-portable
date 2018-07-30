Name:           slowcgi
Version:        6.3
Release:        1
Summary:        FastCGI to CGI wrapper server
License:        ISC
#Group:          
#Url:            
Source0:        %{name}-%{version}.tar.gz
BuildRequires:  pkgconfig(libbsd-overlay)
BuildRequires:	pkgconfig(libevent)
BuildRequires:	make
BuildRequires:	gcc
#Requires:       
BuildRequires: systemd-rpm-macros
%{?systemd_requires}
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%debug_package

# compat for _fillupdir
%if ! %{defined _fillupdir}
%define _fillupdir /var/adm/fillup-templates
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
install -D -m 644 pkg/sysconfig.slowcgi %{buildroot}%{_fillupdir}/sysconfig.slowcgi


%pre
%service_add_pre slowcgi.service

%post
%service_add_post slowcgi.service
%fillup_only

%preun
%service_del_preun slowcgi.service

%postun
%service_del_postun slowcgi.service

%files
%defattr(-,root,root)
/usr/sbin/slowcgi
# man page is automatically compressed
%{_mandir}/man8/slowcgi.8.gz
%{_unitdir}/slowcgi.service
%{_fillupdir}/sysconfig.slowcgi
%doc README

%changelog
* Mon Jul 30 2018 adaugherity@tamu.edu 6.3-1
- Initial port to Linux, built on openSUSE Leap 15.0.
