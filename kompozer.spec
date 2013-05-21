%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%define name    kompozer
%define version 0.8
%define pre b3
%if %pre
%define release %mkrel -c %pre 3
%else
%define release  3
%endif

%define cairo_version 0.5

%define minimum_build_nspr_version 4.7.2
%define minimum_build_nss_version 3.12


Name:           %{name}
Version:        %{version}
Release:        %{release}
Summary:        Web Authoring System
Group:          Development/Other
License:        GPLv2+ or LGPLv2+ or MPL
URL:            http://www.kompozer.net/
%if %pre
Source0:    http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}%{pre}-src.tar.bz2
%else
Source0:    http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}-src.tar.bz2
%endif
Source1:        kompozer-debian-manpage.bz2
Patch0:	kompozer-0.7.10-CVE-2009-XXXX.diff
Patch1:	kompozer-0.8b1-CVE-2009-3560.diff
Patch2:	kompozer-0.8-png15-build.patch
BuildRequires:  nspr-devel >= %{minimum_build_nspr_version}
BuildRequires:  nss-devel >= %{minimum_build_nss_version}
BuildRequires:  nss-static-devel >= %{minimum_build_nss_version}
BuildRequires:  cairo-devel >= %{cairo_version}
BuildRequires:  pkgconfig(pangox)
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(gtk+-2.0) libxt-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  pkgconfig(xft)
BuildRequires:  pkgconfig(libIDL-2.0)
BuildRequires:	zip
Provides:       nvu = 1
Obsoletes:      nvu < 1

%description
A complete Web authoring system for Linux Desktop users, similar to
Microsoft Windows programs like FrontPage and Dreamweaver.

KompoZer is an unofficial branch of Nvu, previously developed by
Linspire Inc.

It makes managing a Web site a snap. Now anyone can create Web pages
and manage a Web site with no technical expertise or HTML knowledge.

Features

* WYSIWYG editing of pages, making Web creation as easy as typing a
   letter with your word processor.

* Integrated file management via FTP.  Simply log in to your Web
   site and navigate through your files, editing Web pages on the
   fly, directly from your site.

* Reliable HTML code creation that works with today's most popular
   browsers.

* Jump between WYSIWYG editing mode and HTML using tabs.

* Tabbed editing to make working on multiple pages a snap.

* Powerful support for frames, forms, tables, and templates.


%prep
%setup -q -c %{name}-%{version}
# %patch0 -p0 -b .CVE-2009-XXXX
%patch1 -p0 -b .CVE-2009-3560
%patch2 -p1 -b .png15-build

%build
cd mozilla/
cp composer/config/mozconfig.fedora .mozconfig
#echo "mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-kompozer" >> .mozconfig
# this is for x64 and x32 compatibility when installing: 
# echo "mk_add_options \"CONFIGURE_ARGS= --libdir %{_libdir}\"" >> .mozconfig
echo "ac_add_options --libdir %{_libdir}" >> .mozconfig
echo "ac_add_options --with-default-mozilla-five-home=%{_libdir}/kompozer" >> .mozconfig

make -f client.mk build_all


%install
rm -rf $RPM_BUILD_ROOT

pushd obj-kompozer/xpfe/components && %__make ; popd
pushd obj-kompozer && %__make install DESTDIR=$RPM_BUILD_ROOT ;popd

# Remove internal myspell directory and myspell dicts.
# dh_install symlinks it to /usr/share/myspell where all myspell-* dicts place their stuff
rm -rf $RPM_BUILD_ROOT/%{_libdir}/kompozer/components/myspell
# Remove exec bit from .js files to prevent lintian warnings.
chmod -x $RPM_BUILD_ROOT/%{_libdir}/kompozer/components/*.js

rm -rf $RPM_BUILD_ROOT/usr/include/
rm -rf $RPM_BUILD_ROOT/%{_datadir}/idl/

#Menu entry
install -d -m755 %{buildroot}%{_datadir}/applications

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop <<EOF
[Desktop Entry]
Name=KompoZer
GenericName=Web Authoring System
Comment=Create Web Pages
Comment[es]=Crea páginas web
Comment[it]=Creare pagine Web
Comment[fr]=Creation de pages Web
Exec=%{_bindir}/%{name} 
Icon=%{_libdir}/kompozer/icons/mozicon50.xpm
Terminal=false
MimeType=text/html;text/xml;text/css;text/x-javascript;text/javascript;application/x-php;text/x-php;application/xhtml+xml;
Type=Application
Categories=GTK;Development;WebDevelopment;X-Mandriva-CrossDesktop;
EOF

## instalar el kompozer.desktop
desktop-file-install  --dir=%{buildroot}%{_datadir}/applications/ %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop 

# manpage:
install -d -m755 %{buildroot}%{_mandir}/man1/
install -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man1/%{name}.1

# spellchecker support:
#install -d -m755 %{buildroot}%{_libdir}/kompozer
install -d -m755 %{buildroot}%{_datadir}/myspell/
rm -rf %{buildroot}%{_libdir}/kompozer/dictionaries/
cd %{buildroot}%{_libdir}/kompozer
#ln -s ../../share/myspell dictionaries
ln -s %{_datadir}/myspell %{buildroot}%{_libdir}/kompozer/dictionaries

# cleaning non used devel and debug files
rm %{buildroot}%{_bindir}/kompozer-config
rm -rf %{buildroot}%{_libdir}/pkgconfig/
rm -rf %{buildroot}%{_libdir}/debug/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc mozilla/LEGAL mozilla/LICENSE mozilla/README.txt
%{_bindir}/*
%{_libdir}/%{name}/*
%{_mandir}/man1/*
%{_datadir}/myspell
%{_datadir}/applications/mandriva-kompozer.desktop


%changelog
* Mon Apr 23 2012 Frank Kober <emuse@mandriva.org> 0.8-0.b3.3mdv2012.0
+ Revision: 792905
- made a patch to fix build against libpng 1.5

  + Oden Eriksson <oeriksson@mandriva.com>
    - mass rebuild

* Wed Mar 09 2011 Zombie Ryushu <ryushu@mandriva.org> 0.8-0.b3.1
+ Revision: 643168
- fix xt dep

  + Stéphane Téletchéa <steletch@mandriva.org>
    - Disable previously CVE patched upstream
    - Fix release
    - Update to 0.8 b3 version

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.8-0.b1.6mdv2011.0
+ Revision: 606269
- rebuild

* Thu Mar 25 2010 Oden Eriksson <oeriksson@mandriva.com> 0.8-0.b1.5mdv2010.1
+ Revision: 527396
- rebuilt against nss-3.12.6

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 0.8-0.b1.4mdv2010.1
+ Revision: 511711
- rebuild

* Sun Jan 10 2010 Oden Eriksson <oeriksson@mandriva.com> 0.8-0.b1.3mdv2010.1
+ Revision: 488614
- bump correct release
- P1: security fix for CVE-2009-3560

* Fri Nov 13 2009 Oden Eriksson <oeriksson@mandriva.com> 0.8-0.b1.2mdv2010.1
+ Revision: 465858
- adjust the patch slightly (duh!)
- fix correct release
- bump release
- P0: security fix related to CVE-2009-2625 (rediffed and re-added, duh!)
- remove %%changelog

* Thu Oct 29 2009 Jerome Martin <jmartin@mandriva.org> 0.8-0.b1.1mdv2010.1
+ Revision: 460133
- Fixed BuildRequires
- Fixed group
- Fixed spec file
- Updated to 0.8b1 using Fedora spec file

  + Oden Eriksson <oeriksson@mandriva.com>
    - 0.8a4 (because 0.7.10 is not compatible with GTK 2.14 and higher, hence the crashes.)
    - fixed build deps
    - nuked redundant patches
    - rediffed patches
    - build against system nss/nspr libs and require the latest ones

* Mon Aug 24 2009 Oden Eriksson <oeriksson@mandriva.com> 0.7.10-6mdv2010.0
+ Revision: 420377
- P21: security fix related to CVE-2009-2625

* Sat Aug 22 2009 Funda Wang <fwang@mandriva.org> 0.7.10-5mdv2010.0
+ Revision: 419660
- fix wformat patch

  + Oden Eriksson <oeriksson@mandriva.com>
    - adjust the two latest patches a bit

  + Christophe Fergeau <cfergeau@mandriva.com>
    - fix -Wformat warnings
    - fix gcc 4.4 compilation (empty #elif)

* Fri Dec 12 2008 Adam Williamson <awilliamson@mandriva.org> 0.7.10-4mdv2009.1
+ Revision: 313552
- add overflow.patch (fixes the buffer overflow that caused kompozer to crash
  immediately on run, thanks Willem van Engen) (#44830)
- rediff mandriva.patch

  + Oden Eriksson <oeriksson@mandriva.com>
    - lowercase ImageMagick

* Mon Sep 29 2008 Adam Williamson <awilliamson@mandriva.org> 0.7.10-3mdv2009.0
+ Revision: 289888
- disable underlinking protection as there's an internal issue which cannot
  be easily fixed
- add underlinking.patch: fixes an external underlinking issue
- rebuild for 2009

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Sun Jan 13 2008 Thierry Vignaud <tv@mandriva.org> 0.7.10-2mdv2008.1
+ Revision: 150433
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Tue Sep 18 2007 Adam Williamson <awilliamson@mandriva.org> 0.7.10-1mdv2008.0
+ Revision: 89389
- adjust some paths due to an upstream change in directory naming
- fix menu categories (#33660)
- correct build date

  + Funda Wang <fwang@mandriva.org>
    - 0.7.10 final

  + Thierry Vignaud <tv@mandriva.org>
    - kill desktop-file-validate's 'warning: key "Encoding" in group "Desktop Entry" is deprecated'

* Mon Aug 20 2007 Adam Williamson <awilliamson@mandriva.org> 0.7.10-0.rc6.1mdv2008.0
+ Revision: 68024
- Import kompozer

