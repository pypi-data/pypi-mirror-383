# Logging

Logging is controlled by the `--debug` (or `-d`) option.

<details>
  <summary>Examples</summary>

Enable `geometry` debugging with a client:
```shell
xpra attach -d geometry
```

***

Start a seamless server with `focus` debugging enabled:
```shell
xpra start -d focus --start=xterm
```
</details>


## Logging Categories
Use the special category value `all` to enable all logging. (this will be very verbose and should be avoided)\
You can also prefix a logging category with a dash "`-`" to disable debug logging for it.
<details>
  <summary>example</summary>

To log everything except the `window` and `focus` categories:
```shell
xpra start :10 -d all,-window,-focus
```
</details>

***

Each logging category can also be enabled using environment variables. \
This can be useful if you cannot modify the command line, or if the logging should happen
very early on, or if you aren't calling the code from its normal wrappers.
<details>
  <summary>example using an environment variable</summary>

to enable "geometry" debugging with the `attach` subcommand use:
```shell
XPRA_GEOMETRY_DEBUG=1 xpra attach
```
</details>

***

The full list of categories can be shown using `xpra -d help`, to see this list now, click on:
<details>
  <summary>complete list of categories</summary>

| Area                                 | Description                                                        |
|--------------------------------------|--------------------------------------------------------------------|
| **Client:**                          |                                                                    |
| client                               | all client code                                                    |
| paint                                | client window paint code                                           |
| draw                                 | client draw packets processing                                     |
| cairo                                | calls to the cairo drawing library                                 |
| opengl                               | [OpenGL rendering](Client-OpenGL.md)                               |
| info                                 | `About` and `Session info` dialogs                                 |
| launcher                             | client launcher program                                            |
| **General:**                         |                                                                    |
| clipboard                            | all [clipboard](../Features/Clipboard.md) operations               |
| notify                               | [notifications forwarding](../Features/Notifications.md)           |
| tray                                 | [system tray forwarding](../Features/System-Tray.md)               |
| printing                             | [printer forwarding](../Features/Printing.md)                      |
| file                                 | [file transfers](../Features/File-Transfers.md)                    |
| keyboard                             | [keyboard](../Features/Keyboard.md) mapping and key event handling |
| screen                               | screen and workarea dimensions                                     |
| fps                                  | Frames per second                                                  |
| xsettings                            | XSettings synchronization                                          |
| dbus                                 | DBUS calls                                                         |
| rpc                                  | Remote Procedure Calls                                             |
| menu                                 | Menus                                                              |
| events                               | System and window events                                           |
| **Window:**                          |                                                                    |
| window                               | all window code                                                    |
| damage                               | X11 repaint events                                                 |
| geometry                             | window geometry                                                    |
| shape                                | window shape forwarding (`XShape`)                                 |
| focus                                | window focus                                                       |
| workspace                            | window workspace synchronization                                   |
| metadata                             | window metadata                                                    |
| alpha                                | window Alpha channel (transparency)                                |
| state                                | window state changes                                               |
| icon                                 | window icons                                                       |
| frame                                | window frame                                                       |
| grab                                 | window grabs (both keyboard and mouse)                             |
| dragndrop                            | window drag-n-drop events                                          |
| filters                              | window filters                                                     |
| **[Encoding](Encodings.md):**        |                                                                    |
| codec                                | all codecs                                                         |
| loader                               | codec loader                                                       |
| video                                | video encoding and decoding                                        |
| score                                | video pipeline scoring and selection                               |
| encoding                             | encoding selection and compression                                 |
| scaling                              | picture scaling                                                    |
| scroll                               | scrolling detection and compression                                |
| subregion                            | video subregion processing                                         |
| regiondetect                         | video region detection                                             |
| regionrefresh                        | video region refresh                                               |
| refresh                              | refresh of lossy screen updates                                    |
| compress                             | pixel compression                                                  |
| **[Codec](Encodings.md):**           |                                                                    |
| csc                                  | colourspace conversion codecs                                      |
| cuda                                 | CUDA device access (nvenc)                                         |
| cython                               | Cython CSC module                                                  |
| swscale                              | swscale CSC module                                                 |
| libyuv                               | libyuv CSC module                                                  |
| decoder                              | all decoders                                                       |
| encoder                              | all encoders                                                       |
| pillow                               | pillow encoder and decoder                                         |
| jpeg                                 | JPEG codec                                                         |
| vpx                                  | libvpx encoder and decoder                                         |
| nvenc                                | nvenc hardware encoder                                             |
| nvfbc                                | nfbc screen capture                                                |
| x264                                 | libx264 encoder                                                    |
| webp                                 | libwebp encoder and decoder                                        |
| webcam                               | webcam access                                                      |
| **Pointer:**                         |                                                                    |
| mouse                                | mouse motion                                                       |
| cursor                               | mouse cursor shape                                                 |
| **Misc:**                            |                                                                    |
| gtk                                  | all GTK code: bindings, client, etc                                |
| util                                 | all utility functions                                              |
| gobject                              | command line clients                                               |
| test                                 | test code                                                          |
| verbose                              | very verbose flag                                                  |
| **[Network](../Network/README.md):** |                                                                    |
| network                              | all network code                                                   |
| bandwidth                            | bandwidth detection and management                                 |
| ssh                                  | [SSH](../Network/SSH.md) connections                               |
| ssl                                  | [SSL](../Network/SSL.md) connections                               |
| http                                 | HTTP requests                                                      |
| rfb                                  | RFB Protocol                                                       |
| mmap                                 | mmap transfers                                                     |
| protocol                             | packet input and output                                            |
| websocket                            | WebSocket layer                                                    |
| named-pipe                           | Named pipe                                                         |
| crypto                               | [encryption](../Network/Encryption.md)                             |
| auth                                 | [authentication](Authentication.md)                                |
| upnp                                 | UPnP                                                               |
| **Server:**                          |                                                                    |
| server                               | all server code                                                    |
| proxy                                | [proxy server](Proxy-Server.md)                                    |
| shadow                               | [shadow server](Shadow.md)                                         |
| command                              | server control channel                                             |
| timeout                              | server timeouts                                                    |
| exec                                 | executing commands                                                 |
| mdns                                 | [mDNS](../Network/Multicast-DNS.md) session publishing             |
| stats                                | server statistics                                                  |
| xshm                                 | XShm pixel capture                                                 |
| **Audio:**                           |                                                                    |
| audio                                | all audio                                                          |
| gstreamer                            | GStreamer internal messages                                        |
| av-sync                              | Audio-video sync                                                   |
| **X11:**                             |                                                                    |
| x11                                  | all X11 code                                                       |
| xinput                               | XInput bindings                                                    |
| bindings                             | X11 Cython bindings                                                |
| core                                 | X11 core bindings                                                  |
| randr                                | X11 RandR bindings                                                 |
| ximage                               | X11 XImage bindings                                                |
| error                                | X11 errors                                                         |
| **Platform:**                        |                                                                    |
| platform                             | all platform support code                                          |
| import                               | platform support imports                                           |
| osx                                  | MacOS platform support                                             |
| win32                                | Microsoft Windows platform support                                 |
| posix                                | Posix platform                                                     |
</details>

***

## Runtime changes

Logging settings can be modified at runtime:
<details>
  <summary>via the control subcommand</summary>

Using the `control` channel:
```shell
xpra control :DISPLAY debug enable CATEGORY
```
This can be used to control both servers and clients (using the client's socket path: #2406).

The server can also forward debug control commands to the clients connected to it using `client debug`:
```shell
xpra control :DISPLAY client debug enable geometry
```

***

You can enable many categories at once:
```shell
xpra control :2 debug enable window geometry screen
```
Or only enable loggers that match multiple categories with `+`:
```shell
xpra control :2  debug disable focus+grab
```
</details>
<details>
  <summary>the server's dbus interface</summary>

The debug control commands are also available through the server's dbus interface, see [#904](https://github.com/Xpra-org/xpra/issues/904).
</details>

***

## Extra Detailed Logging
Some subsystems require special environment variables to enable logging, this is done to minimize the cost of logging in performance critical paths.\
In particular the X11 bindings, as those can process thousands of events per second.

Log all X11 events:
```shell
XPRA_X11_DEBUG_EVENTS="*" xpra start :10
```
or just specific events:
```shell
XPRA_X11_DEBUG_EVENTS="EnterNotify,CreateNotify" xpra start :10
```
