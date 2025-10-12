%global tarball xf86-video-dummy
%global moduledir %(pkg-config xorg-server --variable=moduledir)
%global driverdir %{moduledir}/drivers
%{!?make_build: %global make_build make}

%define _disable_source_fetch 0
%undefine _hardened_build

Summary:   Xorg X11 dummy video driver
Name:      xorg-x11-drv-dummy
Version:   0.4.1

Release:   1.xpra2%{?dist}
URL:       http://www.x.org
License:   MIT
Group:     User Interface/X Hardware Support

Source0:   https://xorg.freedesktop.org/archive/individual/driver/%{tarball}-%{version}.tar.xz
Patch2:    0002-Constant-DPI.patch
Patch6:    0006-Dummy-Disconnect.patch

ExcludeArch: s390 s390x

BuildRequires: make
BuildRequires: xorg-x11-server-devel >= 1.10.99.902
BuildRequires: autoconf automake libtool

Requires: Xorg %(xserver-sdk-abi-requires ansic 2> /dev/null)
Requires: Xorg %(xserver-sdk-abi-requires videodrv 2> /dev/null)

%description
X.Org X11 dummy video driver.

%prep
sha256=`sha256sum %{SOURCE0} | awk '{print $1}'`
if [ "${sha256}" != "351920a7fd0f759a3ac972a5999b3ffed46f07fb52a99f319bfb5b6a59d3dfaf" ]; then
	echo "invalid checksum for %{SOURCE0}"
	exit 1
fi
%setup -q -n %{tarball}-%{version}
%patch -P 2 -p1
%patch -P 6 -p1
autoreconf -vif

%build
%configure --disable-static
%make_build

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -regex ".*\.la$" | xargs rm -f --

%files
%{driverdir}/dummy_drv.so

%changelog
* Sat Jul 13 2024 Antoine Martin <antoine@xpra.org> - 0.4.1-1.xpra2
- force rebuild

* Mon May 08 2023 Antoine Martin <antoine@xpra.org> - 0.4.1-1.xpra1
- new upstream release

* Fri Apr 15 2022 Antoine Martin <antoine@xpra.org> - 0.4.0-3.xpra1
- add disconnect patch

* Sun Apr 10 2022 Antoine Martin <antoine@xpra.org> - 0.4.0-2.xpra1
- remove redundant pointer limits patch

* Wed Apr 06 2022 Antoine Martin <antoine@xpra.org> - 0.4.0-1.xpra3
- new upstream release

* Wed Feb 17 2021 Antoine Martin <antoine@xpra.org> - 0.3.8-1.xpra3
- verify source checksum

* Fri Nov 16 2018 Antoine Martin <antoine@xpra.org> - 0.3.8-1.xpra2
- rebuild

* Fri Dec 23 2016 Antoine Martin <antoine@xpra.org> - 0.3.8-1.xpra1
- new upstream release

* Thu Nov 24 2016 Antoine Martin <antoine@xpra.org> - 0.3.7-1.xpra1
- merge upstream updates

* Wed Nov  9 2016 Hans de Goede <hdegoede@redhat.com> - 0.3.7-1
- New upstream release 0.7.3
- Fix undefined symbol error with xserver-1.19 (rhbz#1393114)

* Sun Oct 30 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-26.xpra3
- force rebuild against updated headers

* Wed Oct 26 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-26.xpra2
- fix change-window-property API call

* Fri Oct 21 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-26.xpra1
- rebuild for Fedora 25

* Tue Sep 20 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-25.xpra3
- updated 30 bit patch

* Tue Sep 20 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-25.xpra2
- add support for 30 bit depth

* Mon Apr 18 2016 Antoine Martin <antoine@xpra.org> - 0.3.6-25.xpra1
- Rebuilt with xpra fixes: DAC, DPI and pointer limits
