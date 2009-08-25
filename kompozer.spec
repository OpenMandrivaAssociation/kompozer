# underlinking.patch fixes an external underlinking issue, but there's
# also an internal one that looks hard to fix - AdamW 2008/09
%define _disable_ld_as_needed		1
%define _disable_ld_no_undefined	1

%define pre a4
%if %pre
%define release %mkrel -c %pre 1
%else
%define release	%mkrel 1
%endif

%define mozillalibdir %{_libdir}/%{name}

#warning: always end release date with 00
# (it should be the hour of build but it is not significant for rpm)
# MOZ_BUILD_DATE = perl -Imozilla/config mozilla/config/bdate.pl minus one ?
%define mozdate 2009082500

Summary:	Web authoring system (unofficial successor to nvu)
Name:		kompozer
Version:	0.8
Release:	%{release}
License:	GPLv2+ and LGPLv2+ and MPLv1.1
Group:		Development/Other
URL:		http://www.kompozer.net
%if %pre
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}%{pre}-src.tar.bz2
%else
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}-src.tar.bz2
%endif
Source1:	nvu-rebuild-databases.pl.in.generatechrome.bz2
Source2:	nvu-generate-chrome.sh.bz2
Patch0:		nvu-freetype2.patch
Patch4:		nvu-locale.patch
# (fc) 1.0.2-2mdk add env variable to disable GNOME uri handler (Fedora)
Patch10:	nvu-0.81-gnome-uriloader.patch
# (fc) 1.0-3mdk fix user agent (rediffed aw 2008/12)
Patch13:	kompozer-0.7.10-mandriva.patch
# (couriousous) fix gcc 4.1 build
Patch16:	nvu-gcc4.1-fix.patch
# Fix underlinking - AdamW 2008/09
Patch17:	kompozer-0.7.10-underlinking.patch
# Fix an overflow (which causes app to fail to run when built with
# fortification, #44830) - thanks Willem van Engen - AdamW 2008/12
Patch18:	kompozer-0.7.10-overflow.patch
Patch19:	kompozer-0.8-format_not_a_string_literal_and_no_format_arguments.diff
Patch21:	kompozer-0.7.10-CVE-2009-XXXX.diff
BuildRequires:	autoconf2.1
BuildRequires:	gnome-vfs2-devel
BuildRequires:	gtk+2-devel >= 2.4.0
BuildRequires:	imagemagick
BuildRequires:	libgnome2-devel
BuildRequires:	libgnomeui2-devel
BuildRequires:	libIDL-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libxft-devel
BuildRequires:	libxp-devel
BuildRequires:	libxt-devel
BuildRequires:	nspr-devel >= 2:4.7.5
BuildRequires:	nss-devel >= 2:3.12.3.1
BuildRequires:	nss-static-devel >= 2:3.12.3.1
BuildRequires:	pango >= 1.5.0
BuildRequires:	tcsh
BuildRequires:	zip
Obsoletes:	nvu
Provides:	nvu
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

# do not provides mozilla lib
%define _provides_exceptions libnspr4.so\\|libplc4.so\\|libplds4.so\\|libnss\\|libsmime3\\|libsoftokn\\|libssl3\\|libgtkembedmoz.so\\|libxp.*
%define _requires_exceptions libnspr4.so\\|libplc4.so\\|libplds4.so\\|libnss\\|libsmime3\\|libsoftokn\\|libssl3\\|libgtkembedmoz.so\\|libxp.*

%description
Kompozer is a complete Web authoring system that combines web file management
and easy-to-use WYSIWYG web page editing. Kompozer is designed to be extremely
easy to use, making it ideal for non-technical computer users who want to
create an attractive, professional-looking web site without needing to know
HTML or web coding. 

Kompozer is an unofficial continuation of nvu, which was apparently abandoned
in 2005.

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
%patch4
%patch10 -p1 -b .gnome-uriloader
%patch13 -p1 -b .mandriva
%patch16 -p0 -b .gcc4.1
%patch17 -p1 -b .underlink
%patch18 -p1 -b .overflow
%patch19 -p1 -b .format_not_a_string_literal_and_no_format_arguments
%patch21 -p0 -b .CVE-2009-XXXX

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
    --enable-application=composer \
    --with-system-nspr \
    --with-system-nss \
    --enable-optimize="%{optflags}" \
    --disable-debug \
    --disable-svg \
    --without-system-mng \
    --with-system-png \
    --with-system-jpeg \
    --disable-ldap \
    --disable-mailnews \
    --disable-installer \
    --disable-activex \
    --disable-activex-scripting \
    --disable-tests \
    --disable-oji \
    --disable-necko-disk-cache \
    --enable-single-profile \
    --disable-profilesharing \
    --enable-extensions=wallet,spellcheck,xmlextras,pref,universalchardet,inspector \
    --enable-image-decoders=png,gif,jpeg \
    --enable-necko-protocols=http,ftp,file,jar,viewsource,res,data \
    --disable-pedantic \
    --disable-short-wchar \
    --enable-xprint \
    --enable-crypto \
    --disable-mathml \
    --with-system-zlib \
    --enable-toolkit=gtk2 \
    --enable-default-toolkit=gtk2 \
    --enable-xft \
    --disable-updater \
    --enable-system-cairo \
    --with-default-mozilla-five-home=%{mozillalibdir}

make

%install
rm -rf %{buildroot}

%makeinstall_std

# multiarch files
%multiarch_binaries %{buildroot}%{_bindir}/kompozer-config
%multiarch_includes %{buildroot}%{_includedir}/%{name}/mozilla-config.h
%multiarch_includes %{buildroot}%{_includedir}/%{name}/js/jsautocfg.h

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Kompozer
Comment=Web authoring system
Exec=%{_bindir}/%{name} %u
Icon=%{name}
Terminal=false
Type=Application
Categories=GTK;Development;WebDevelopment;X-Mandriva-CrossDesktop;
EOF

mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
install -m 644 %{buildroot}%{mozillalibdir}/icons/mozicon16.xpm  %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png
convert -scale 32x32  %{buildroot}%{mozillalibdir}/icons/mozicon50.xpm %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png 
convert -scale 48x48  %{buildroot}%{mozillalibdir}/icons/mozicon50.xpm %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png 

# install our rebuild file
bzcat %{SOURCE1} | sed -e "s|mozilla-MOZILLA_VERSION|%{name}-%{version}|g;s|LIBDIR|%{_libdir}|g" > \
  %{buildroot}%{mozillalibdir}/mozilla-rebuild-databases.pl
chmod 755 %{buildroot}%{mozillalibdir}/mozilla-rebuild-databases.pl

# install our file to rebuild the chrome registry so that we can
# produce Kompozer extentions in RPM
mkdir -p %{buildroot}%{mozillalibdir}/chrome/rc.d
bzcat %{SOURCE2} > \
  %{buildroot}%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

chmod 755 %{buildroot}%{mozillalibdir}/chrome/rc.d/generate-chrome.sh

# remove unpackaged files
rm -f %{buildroot}%{mozillalibdir}/{libnspr4.so,libplc4.so,libplds4.so,libnss3.so,libnssckbi.so,libsmime3.so,libsoftokn3.so,libssl3.so,libsoftokn3.chk,TestGtkEmbed}

#ghost files
mkdir -p %{buildroot}%{mozillalibdir}/extensions
touch %{buildroot}%{mozillalibdir}/chrome/chrome.rdf
for overlay in {"browser","communicator","editor","inspector","messenger","navigator"}; do
  %{__mkdir_p} %{buildroot}%{mozillalibdir}/chrome/overlayinfo/$overlay/content
  touch %{buildroot}%{mozillalibdir}/chrome/overlayinfo/$overlay/content/overlays.rdf
done
touch %{buildroot}%{mozillalibdir}/extensions/installed-extensions-processed.txt
touch %{buildroot}%{mozillalibdir}/extensions/Extensions.rdf
touch %{buildroot}%{mozillalibdir}/components.ini
touch %{buildroot}%{mozillalibdir}/defaults.ini
touch %{buildroot}%{mozillalibdir}/components/compreg.dat
touch %{buildroot}%{mozillalibdir}/components/xpti.dat

%post
%if %mdkversion < 200900
%update_menus
%update_icon_cache hicolor
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
%clean_menus
%clean_icon_cache hicolor
%endif

%clean
rm -rf %{buildroot}

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
%multiarch %{multiarch_includedir}/* 
