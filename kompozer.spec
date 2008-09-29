# underlinking.patch fixes an external underlnking issue, but there's
# also an internal one that looks hard to fix - AdamW 2008/09
%define _disable_ld_as_needed		1
%define _disable_ld_no_undefined	1

%define name	kompozer
%define version	0.7.10
%define pre	0
%if %pre
%define release %mkrel -c %pre 1
%else
%define release	%mkrel 3
%endif

%define mozillalibdir %{_libdir}/%{name}

#warning: always end release date with 00
# (it should be the hour of build but it is not significant for rpm)
%define mozdate 2007091700


Summary:	Web authoring system (unofficial successor to nvu)
Name:		%{name}
Version:	%{version}
Release:	%{release}
Url:		http://www.kompozer.net
%if %pre
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}%{pre}-src.tar.bz2
%else
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}-src.tar.bz2
%endif
Source1:	nvu-rebuild-databases.pl.in.generatechrome.bz2
Source2:	nvu-generate-chrome.sh.bz2
Patch0:		nvu-freetype2.patch
Patch1:		nvu-myspell.patch
Patch4:		nvu-locale.patch
Patch5:		nvu-0.81-systemnspr.patch
# (fc) 0.81-3mdk fix extension manager (from Firefox package)
Patch7:		nvu-0.81-fixextensionmanager.patch
# (fc) 0.81-4mdk fix GIF vulnerability CAN-2005-0399
Patch8:		nvu-0.81-gifvulnerability.patch
# (fc) 1.0.2-2mdk fix JS vulnerability (CVS) (Moz bug #288688)
Patch9:		nvu-0.81-jsvulnerability.patch
# (fc) 1.0.2-2mdk add env variable to disable GNOME uri handler (Fedora)
Patch10:	nvu-0.81-gnome-uriloader.patch
# (fc) 1.0-3mdk fix user agent
Patch13:	nvu-1.0-mandriva.patch
# (fc) 1.0-3mdk fix default app for www/ftp
Patch14:	kompozer-0.7.10-browser.patch
# (couriousous) fix gcc 4.1 build
Patch16:	nvu-gcc4.1-fix.patch
# Fix underlinking - AdamW 2008/09
Patch17:	kompozer-0.7.10-underlinking.patch

License: GPLv2+ and LGPLv2+ and MPLv1.1
Group: Development/Other
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	ImageMagick
BuildRequires:  zip tcsh
BuildRequires:	libIDL-devel
BuildRequires:  libjpeg-devel
BuildRequires:	libgnome2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  gtk+2-devel >= 2.2.0
BuildRequires:	libnspr-devel
BuildRequires:	libnss-devel
BuildRequires:	libpng-devel
BuildRequires:	libxp-devel
BuildRequires:	libxt-devel
BuildRequires:	autoconf2.1

Obsoletes:	nvu
Provides:	nvu

# do not provides mozilla lib
%define _provides_exceptions libnspr4.so\\|libplc4.so\\|libplds4.so\\|libnss\\|libsmime3\\|libsoftokn\\|libssl3\\|libgtkembedmoz.so\\|libxp.*
%define _requires_exceptions libnspr4.so\\|libplc4.so\\|libplds4.so\\|libnss\\|libsmime3\\|libsoftokn\\|libssl3\\|libgtkembedmoz.so\\|libxp.*

%description
Kompozer is a complete Web authoring system that combines web file 
management and easy-to-use WYSIWYG web page editing. Kompozer is 
designed to be extremely easy to use, making it ideal for 
non-technical computer users who want to create an attractive, 
professional-looking web site without needing to know HTML or web 
coding. 

Kompozer is an unofficial continuation of nvu, which was apparently
abandoned in 2005.

%package devel
Summary:        Kompozer development files
Group:          Development/Other
Requires:       %{name} = %{version}
Conflicts:	%mklibname -d js 1

%description devel
Kompozer development files.


%prep
%setup -q -c %{name}-%{version}
%setup -T -D -n %{name}-%{version}/mozilla
%patch0 -p1
%patch1 -p1
%patch4
%patch5 -p1 -b .systemnspr
%patch7 -p1 -b .fixextensionmanager
%patch8 -p1 -b .gifvulnerability
%patch9 -p1 -b .jsvulnerability
%patch10 -p1 -b .gnome-uriloader
%patch13 -p1 -b .mandriva
%patch14 -p1 -b .launcher
%patch16 -p0 -b .gcc4.1
%patch17 -p1 -b .underlink
# let jars get compressed
%__perl -p -i -e 's|\-0|\-9|g' config/make-jars.pl

%build
# required by underlinking.patch
autoconf-2.13

export MOZILLA_OFFICIAL=1
export BUILD_OFFICIAL=1
export MOZ_STANDALONE_COMPOSER=1
export MOZ_BUILD_DATE=%{mozdate}

%define __libtoolize /bin/true
%define __cputoolize /bin/true

%configure \
  --without-system-nspr \
  --without-system-nss \
  --enable-optimize="$RPM_OPT_FLAGS" --disable-debug --disable-svg --without-system-mng --with-system-png --with-system-jpeg --disable-ldap --disable-mailnews --disable-installer --disable-activex --disable-activex-scripting --disable-tests --disable-oji --disable-necko-disk-cache --enable-single-profile --disable-profilesharing --enable-extensions=wallet,spellcheck,xmlextras,pref,universalchardet,inspector --enable-image-decoders=png,gif,jpeg --enable-necko-protocols=http,ftp,file,jar,viewsource,res,data --disable-pedantic --disable-short-wchar --enable-xprint --enable-strip-libs --enable-crypto --disable-mathml --with-system-zlib --enable-toolkit=gtk2 --enable-default-toolkit=gtk2 --enable-xft --enable-freetype2 --with-default-mozilla-five-home=%{mozillalibdir}

%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

# multiarch files
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/kompozer-config
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{name}/mozilla-config.h
%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{name}/js/jsautocfg.h

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Kompozer
Comment=Web authoring system
Exec=%{_bindir}/%{name} %u
Icon=%{name}
Terminal=false
Type=Application
Categories=GTK;Development;WebDevelopment;X-Mandriva-CrossDesktop;
EOF

mkdir -p $RPM_BUILD_ROOT%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
install -m 644 $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon16.xpm  $RPM_BUILD_ROOT%{_iconsdir}/hicolor/16x16/apps/%{name}.png
convert -scale 32x32  $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon50.xpm $RPM_BUILD_ROOT%{_iconsdir}/hicolor/32x32/apps/%{name}.png 
convert -scale 48x48  $RPM_BUILD_ROOT%{mozillalibdir}/icons/mozicon50.xpm $RPM_BUILD_ROOT%{_iconsdir}/hicolor/48x48/apps/%{name}.png 

# install our rebuild file
bzcat %{SOURCE1} | sed -e "s|mozilla-MOZILLA_VERSION|%{name}-%{version}|g;s|LIBDIR|%{_libdir}|g" > \
  $RPM_BUILD_ROOT%{mozillalibdir}/mozilla-rebuild-databases.pl
chmod 755 $RPM_BUILD_ROOT%{mozillalibdir}/mozilla-rebuild-databases.pl

# install our file to rebuild the chrome registry so that we can
# produce Kompozer extentions in RPM
mkdir -p $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d
bzcat %{SOURCE2} > \
  $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

chmod 755 $RPM_BUILD_ROOT%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{mozillalibdir}/{libnspr4.so,libplc4.so,libplds4.so,libnss3.so,libnssckbi.so,libsmime3.so,libsoftokn3.so,libssl3.so,libsoftokn3.chk,TestGtkEmbed}

#ghost files
mkdir -p $RPM_BUILD_ROOT%{mozillalibdir}/extensions
touch $RPM_BUILD_ROOT%{mozillalibdir}/chrome/chrome.rdf
for overlay in {"browser","communicator","editor","inspector","messenger","navigator"}; do
  %{__mkdir_p} $RPM_BUILD_ROOT%{mozillalibdir}/chrome/overlayinfo/$overlay/content
  touch $RPM_BUILD_ROOT%{mozillalibdir}/chrome/overlayinfo/$overlay/content/overlays.rdf
done
touch $RPM_BUILD_ROOT%{mozillalibdir}/extensions/installed-extensions-processed.txt
touch $RPM_BUILD_ROOT%{mozillalibdir}/extensions/Extensions.rdf
touch $RPM_BUILD_ROOT%{mozillalibdir}/components.ini
touch $RPM_BUILD_ROOT%{mozillalibdir}/defaults.ini
touch $RPM_BUILD_ROOT%{mozillalibdir}/components/compreg.dat
touch $RPM_BUILD_ROOT%{mozillalibdir}/components/xpti.dat


%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %mdkversion < 200900
%{update_menus}
%{update_icon_cache hicolor}
%endif
if [ "$1" == "2" ]; then
  if [ ! -f %{mozillalibdir}/components.ini -o ! -f %{mozillalibdir}/defaults.ini ]; then
	#fix older broken install if needed
	rm -f %{mozillalibdir}/components/*.dat
  fi
fi

export HOME="/root" MOZ_DISABLE_GNOME=1
# force correct umask
umask 022
%{_bindir}/%{name} -register
%{mozillalibdir}/mozilla-rebuild-databases.pl

%if %mdkversion < 200900
%postun
%{clean_menus}
%{clean_icon_cache hicolor}
%endif

%files
%defattr(-,root,root)
%doc LICENSE LEGAL README.txt
%{_bindir}/%{name}
%{_datadir}/applications/*.desktop
%{_iconsdir}/hicolor/16x16/apps/%{name}.png
%{_iconsdir}/hicolor/32x32/apps/%{name}.png
%{_iconsdir}/hicolor/48x48/apps/%{name}.png
%{mozillalibdir}
%ghost %{mozillalibdir}/chrome/chrome.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/browser/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/communicator/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/inspector/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/messenger/content/overlays.rdf
%ghost %{mozillalibdir}/chrome/overlayinfo/navigator/content/overlays.rdf
%ghost %{mozillalibdir}/extensions/Extensions.rdf
%ghost %{mozillalibdir}/extensions/installed-extensions-processed.txt
%ghost %{mozillalibdir}/components.ini
%ghost %{mozillalibdir}/defaults.ini
%ghost %{mozillalibdir}/components/compreg.dat
%ghost %{mozillalibdir}/components/xpti.dat

%files devel
%defattr(-,root,root)
%{_libdir}/pkgconfig/*.pc
%{_bindir}/kompozer-config
%multiarch %{multiarch_bindir}/kompozer-config
%{_datadir}/idl/%{name}
%{_includedir}/%{name}
%{_datadir}/aclocal/nspr.m4
%multiarch %{multiarch_includedir}/* 

