# http://trac.wildfiregames.com/wiki/BuildInstructions#Linux

# enable special maintainer debug build ?
%define with_debug 0
%if %{with_debug}
%define config debug
%define dbg _dbg
%else
%define config release
%define dbg %{nil}
%endif

%global with_system_nvtt 0
%global without_nvtt 1

Summary:	Cross-Platform RTS Game of Ancient Warfare
Name:		0ad
Version:	0.0.23
Release:	1
Epoch:		1
License:	GPLv2+ and BSD and MIT and IBM
Group:		Games/Strategy
Url:		http://play0ad.com
Source0:	http://releases.wildfiregames.com/%{name}-%{version}-alpha-unix-build.tar.xz
# adapted from binaries/system/readme.txt
# It is advisable to review this file at on newer versions, to update the
# version field and check for extra options. Note that windows specific,
# and disabled options were not added to the manual page.
Source1:	%{name}.6
# http://trac.wildfiregames.com/ticket/1421
Patch0:		0ad-rpath.patch
# Only do fcollada debug build with enabling debug maintainer mode
# It also prevents assumption there that it is building in x86
Patch1:		0ad-0.0.19-debug.patch
Patch2:		0ad-mozjs-incompatible.patch
# After some trial&error this corrects a %%check failure with gcc 4.9 on i686
Patch3:		0ad-check.patch

BuildRequires:	cmake
BuildRequires:	desktop-file-utils
BuildRequires:	nasm
BuildRequires:	subversion
BuildRequires:	boost-devel
BuildRequires:	jpeg-devel
BuildRequires:	libdnet-devel
BuildRequires:	miniupnpc-devel
%if %{with_system_nvtt}
BuildRequires:	nvidia-texture-tools-devel
%endif
BuildRequires:	wxgtku3.0-devel
BuildRequires:	pkgconfig(gloox)
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(IL)
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libenet)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libsodium)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(libzip)
BuildRequires:	pkgconfig(mozjs-31)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(openal)
BuildRequires:	pkgconfig(sdl2)
BuildRequires:	pkgconfig(vorbis)
Requires:	%{name}-data
ExclusiveArch:	%{ix86} x86_64

%description
0 A.D. (pronounced "zero ey-dee") is a free, open-source, cross-platform
real-time strategy (RTS) game of ancient warfare. In short, it is a
historically-based war/economy game that allows players to relive or rewrite
the history of Western civilizations, focusing on the years between 500 B.C.
and 500 A.D. The project is highly ambitious, involving state-of-the-art 3D
graphics, detailed artwork, sound, and a flexible and powerful custom-built
game engine.

The game has been in development by Wildfire Games (WFG), a group of volunteer,
hobbyist game developers, since 2001.

%files
%doc README.txt LICENSE.txt
%doc license_gpl-2.0.txt license_lgpl-2.1.txt
%{_gamesbindir}/0ad
%{_gamesbindir}/pyrogenesis%{dbg}
%{_libdir}/%{name}
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/appdata/0ad.appdata.xml
%{_datadir}/applications/%{name}.desktop
%{_gamesdatadir}/%{name}
%{_mandir}/man6/*.6*

#----------------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}-alpha
%patch0 -p1
%if !%{with_debug}
# disable debug build, and "int 0x3" to trap to debugger (x86 only)
%patch1 -p1
%endif
%patch2 -p1
%patch3 -p1

%if %{with_system_nvtt}
rm -fr libraries/nvtt
%endif

%build
export CC=%{__cc}
export CFLAGS="%{optflags}"
# avoid warnings with gcc 4.7 due to _FORTIFY_SOURCE in CPPFLAGS
export CPPFLAGS="`echo %{optflags} | sed -e 's/-Wp,-D_FORTIFY_SOURCE=2//'`"
build/workspaces/update-workspaces.sh \
	--bindir %{_gamesbindir} \
	--datadir %{_gamesdatadir}/%{name} \
	--libdir %{_libdir}/%{name} \
	--with-system-mozjs38 \
%if %{with_system_nvtt}
	--with-system-nvtt \
%endif
%if %{without_nvtt}
	--without-nvtt \
%endif
	%{?_smp_mflags}

%make -C build/workspaces/gcc config=%{config} verbose=1

%install
export CC=%{__cc}
install -d -m 755 %{buildroot}%{_gamesbindir}
install -m 755 binaries/system/pyrogenesis%{dbg} %{buildroot}%{_gamesbindir}/pyrogenesis%{dbg}

install -d -m 755 %{buildroot}%{_libdir}/%{name}
for name in AtlasUI%{dbg} Collada%{dbg}; do
	install -m 755 binaries/system/lib${name}.so  %{buildroot}%{_libdir}/%{name}/lib${name}.so
done

%if !%{without_nvtt} && !%{with_system_nvtt}
for name in nvcore nvimage nvmath nvtt; do
	install -p -m 755 binaries/system/lib${name}.so %{buildroot}%{_libdir}/%{name}/lib${name}.so
done
%endif

install -d -m 755 %{buildroot}%{_datadir}/appdata
install -p -m 644 build/resources/0ad.appdata.xml %{buildroot}%{_datadir}/appdata

install -d -m 755 %{buildroot}%{_gamesdatadir}/applications
install -m 644 build/resources/0ad.desktop %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop
perl -pi -e 's|%{_bindir}/0ad|%{_gamesbindir}/0ad|;' \
	%{buildroot}%{_gamesdatadir}/applications/%{name}.desktop

install -d -m 755 %{buildroot}%{_gamesdatadir}/pixmaps
install -m 644 build/resources/0ad.png %{buildroot}%{_gamesdatadir}/pixmaps/%{name}.png

install -d -m 755 %{buildroot}%{_gamesdatadir}/%{name}
cp -a binaries/data/* %{buildroot}%{_gamesdatadir}/%{name}

install -d -m 755 %{buildroot}%{_mandir}/man6
install -p -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man6/%{name}.6
ln -sf %{name}.6 %{buildroot}%{_mandir}/man6/pyrogenesis.6

desktop-file-validate %{buildroot}%{_gamesdatadir}/applications/%{name}.desktop

mkdir -p %{buildroot}%{_datadir}
mv -f %{buildroot}%{_gamesdatadir}/{pixmaps,applications} %{buildroot}%{_datadir}

cat > %{buildroot}%{_gamesbindir}/0ad <<EOF
#!/bin/sh

cd %{_gamesdatadir}/0ad
LD_LIBRARY_PATH=%{_libdir}/0ad %{_gamesbindir}/pyrogenesis%{dbg} "\$@"
EOF
chmod +x %{buildroot}%{_gamesbindir}/0ad

%if %{with debug}
export EXCLUDE_FROM_FULL_STRIP="libAtlasUI_dbg.so libCollada_dbg.so pyrogenesis_dbg"
%endif

# Depends on availablity of nvtt
%if !%{without_nvtt}
%check
export CC=%{__cc}
LD_LIBRARY_PATH=binaries/system binaries/system/test%{dbg}
%endif
