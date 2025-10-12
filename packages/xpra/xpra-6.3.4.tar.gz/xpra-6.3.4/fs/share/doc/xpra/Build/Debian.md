# ![Debian](../images/icons/debian.png)   ![Ubuntu](../images/icons/ubuntu.png) Building DEB packages

The debian packaging files can be found here: [packaging/debian](https://github.com/Xpra-org/xpra/blob/master/packaging/debian).

Debian and Ubuntu also ships xpra packages, though their _stable_ versions are completely out of date, broken and unsupported, [they should not be used](https://github.com/Xpra-org/xpra/wiki/Distribution-Packages).

For general information, see [building](README.md).

## Build requirements
The easiest way to install the build dependencies
is using the `dev-env` build subcommand which will honour setup arguments. ie:
```shell
./setup.py dev-env --minimal --with-openh264
```
_(available in xpra v6.1 onwards)_


Alternatively, you can install these sets yourself:
<details>
  <summary>Common dependencies</summary>

To be able to run xpra, you are likely to need:
```shell
apt-get install xvfb python3-cairo python3-gi-cairo \
    python3-opengl python3-pil
```
</details>
<details>
  <summary>X11</summary>

```shell
apt-get install libx11-dev libxtst-dev libxcomposite-dev libxdamage-dev libxres-dev \
                libxkbfile-dev \
                python3-dev \
                pandoc \
                libsystemd-dev \
                liblz4-dev
```

These X11 utilities are usually required at runtime:
```shell
apt-get install xauth x11-xkb-utils
```
</details>
<details>
  <summary>GTK3</summary>

GTK3 toolkit for the server and GUI client:
```shell
apt-get install libgtk-3-dev python3-dev python3-cairo-dev python-gi-dev cython3
```
</details>

### Optional:
<details>
  <summary>Extra codecs</summary>

See [picture codecs](../Usage/Encodings.md)
Basic picture codecs
```shell
apt-get install libturbojpeg-dev libwebp-dev python3-pil
```
for video support (x264 and vpx)
```shell
apt-get install libx264-dev libvpx-dev yasm
```
for using [NVENC](../Usage/NVENC.md)
```shell
apt-get install libnvidia-encode1 python3-numpy
```
</details>

<details>
  <summary>HTML5 client</summary>

for more details, see [html5 client](https://github.com/Xpra-org/xpra-html5)
```shell
apt-get install uglifyjs brotli libjs-jquery libjs-jquery-ui gnome-backgrounds
```
</details>

<details>
  <summary>Client OpenGL acceleration</summary>

[OpenGL](../Usage/Client-OpenGL.md)
```shell
apt-get install python3-opengl
```
</details>

<details>
  <summary>Network layer</summary>

For more details, see [network](../Network/README.md).
```shell
apt-get install python3-dbus python3-cryptography \
                python3-netifaces python3-yaml
```
[SSH](../Network/SSH.md):
```shell
apt-get install openssh-client sshpass python3-paramiko
```
</details>

<details>
  <summary>misc extras</summary>

python libraries:
```shell
apt-get install python3-setproctitle python3-xdg
```
X11:
```shell
apt-get install libpam-dev quilt xserver-xorg-dev xutils-dev xserver-xorg-video-dummy xvfb keyboard-configuration
```
</details>

<details>
  <summary>authentication modules</summary>

For more details, see [authentication](../Usage/Authentication.md).
```shell
apt-get install python3-kerberos python3-gssapi
```
</details>

<details>
  <summary>audio forwarding</summary>

See [audio](../Features/Audio.md) support and codecs
```shell
apt-get install gstreamer1.0-pulseaudio gstreamer1.0-alsa \
                gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
                gstreamer1.0-plugins-ugly
```
</details>

<details>
  <summary>printer forwarding</summary>

See [printing](../Features/Printing.md)
```shell
apt-get install cups-filters cups-common cups-pdf python3-cups
```
</details>

## Local Installation

Please make sure to remove any packages before installing from source.
```shell
./setup.py install --prefix=/usr --install-layout=deb
# the executable scripts may have been mangled, so overwrite them:
cp fs/bin/* /bin/
```
You may also need to `export SETUPTOOLS_USE_DISTUTILS=stdlib`

## DEB Packaging
Install the packaging tools
```shell
apt-get install devscripts build-essential lintian debhelper pandoc
```

Build DEBs
```shell
git clone https://github.com/Xpra-org/xpra
cd xpra
debuild -us -uc -b
```
This builds fresh packages from git master.
You can also use other branches, tags or download a [source snapshot](https://xpra.org/src/) instead.
