Summary: An automated DHCP Registration System
Name: netreg
Version: 1.5.1
Release: 4%{?dist}
License: GPL
Group: System Environment/Daemons
URL: http://netreg.org/
Source0: %{name}-%{version}.tar.gz
Patch1: netreg-pathnames.patch
Patch2: netreg-bindconf.patch
Patch3: netreg-readme.patch
Patch4: netreg-1.5.1-email.patch
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Requires: perl, perl-Mail-POP3Client, perl-Net-IMAP-Simple, perl-Authen-SASL,perl-Convert-ASN1, perl-IO-Socket-SSL, perl-Net-SSLeay, perl-XML-NamespaceSupport, perl-XML-SAX, perl-LDAP, perl-Authen-Radius, httpd, dhcp, bind

Packager: Phil Gold <phil@cs.jhu.edu>

%description
NetReg is an automated network registration system that requires client
computers that use DHCP to register their hardware (MAC) address before
they can gain full network access.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1


%build


%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_var}
%{__cp} -r var/www %{buildroot}%{_var}

%{__mkdir_p} %{buildroot}%{_datarootdir}/doc/%{name}-%{version}
%{__cp} etc/dhcpd.conf %{buildroot}%{_datarootdir}/doc/%{name}-%{version}/dhcpd.conf.example
%{__cp} var/named/chroot/etc/named.conf %{buildroot}%{_datarootdir}/doc/%{name}-%{version}/named.conf.example
%{__cp} README %{buildroot}%{_datarootdir}/doc/%{name}-%{version}
%{__cp} README.RedHat %{buildroot}%{_datarootdir}/doc/%{name}-%{version}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__cp} usr/local/bin/refresh-dhcpdconf %{buildroot}%{_bindir}

%{__mkdir_p} %{buildroot}%{_sysconfdir}
%{__cp} -r usr/local/etc/netreg %{buildroot}%{_sysconfdir}
%{__rm} -rf %{buildroot}%{_sysconfdir}/netreg/dhcpd
%{__cp} var/named/chroot/etc/netreg.zone %{buildroot}%{_sysconfdir}/netreg/
%{__cp} var/named/chroot/etc/zones.conf %{buildroot}%{_sysconfdir}/netreg/

%{__mkdir_p} %{buildroot}%{_libdir}/perl5/vendor_perl/Net
%{__cp} -r usr/lib/perl5/site_perl/Net/NetReg %{buildroot}%{_libdir}/perl5/vendor_perl/Net/
%{__mv} %{buildroot}%{_libdir}/perl5/vendor_perl/Net/NetReg/Variables.pm %{buildroot}%{_sysconfdir}/netreg/
%{__ln_s} %{_sysconfdir}/netreg/Variables.pm %{buildroot}%{_libdir}/perl5/vendor_perl/Net/NetReg/Variables.pm

%{__mkdir_p} %{buildroot}%{_var}/lib/netreg

%{__mkdir_p} %{buildroot}%{_sysconfdir}/httpd/conf.d
%{__cat} >%{buildroot}%{_sysconfdir}/httpd/conf.d/netreg.conf <<EOF
Options +FollowSymlinks
RewriteEngine on
RewriteCond %{REQUEST_URI} !^/registration.html
RewriteCond %{REQUEST_URI} !^/cgi-bin
RewriteCond %{REQUEST_URI} !^/netreg-gfx
RewriteRule ^(.*)$ /registration.html [R=302,L]
<Location />
    Order deny,allow
    Deny from all
    Allow from 10.110 192.168.100 127.0.0.1
</Location>
<Directory "/var/www/cgi-bin">
    AllowOverride AuthConfig
    Options None
</Directory>
EOF

%{__mkdir_p} %{buildroot}%{_sysconfdir}/cron.d
%{__cat} >%{buildroot}%{_sysconfdir}/cron.d/netreg-refresh-dhcpdconf <<EOF
* * * * *  root  /usr/bin/refresh-dhcpdconf
EOF


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc %{_datarootdir}/doc/%{name}-%{version}/*
%{_var}/www/cgi-bin/*
%{_var}/www/html/netreg-gfx
%config(noreplace) %{_var}/www/html/registration.html
%{_libdir}/perl5/vendor_perl/Net/NetReg
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/netreg
%dir %{_var}/lib/netreg
%config(noreplace) %{_sysconfdir}/httpd/conf.d/netreg.conf
%config(noreplace) %{_sysconfdir}/cron.d/netreg-refresh-dhcpdconf


%post
if [ ! -e %{_var}/lib/netreg/netreg.registered ]; then
   touch %{_var}/lib/netreg/netreg.registered
fi
if [ ! -e %{_var}/lib/netreg/netreg.registered.new ]; then
   touch %{_var}/lib/netreg/netreg.registered.new
   chown apache.apache %{_var}/lib/netreg/netreg.registered.new
fi


%changelog
* Tue Mar 26 2013 Phil Gold <phil@cs.jhu.edu> - 1.5.1-4
- Create DHCP file in postinstallation script.
- Change Apache permissions to work.

* Tue Mar 26 2013 Phil Gold <phil@cs.jhu.edu> - 1.5.1-3
- Add email field patch.

* Tue Mar 26 2013 Phil Gold <phil@cs.jhu.edu> - 1.5.1-2
- Fix apache redirect.
- Create netreg.registered files.

* Fri Mar 22 2013 Phil Gold <phil@cs.jhu.edu> - 
- Initial build.

