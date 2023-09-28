## cygwin build Micropython unix port

## 1. the build enviroment
### 1.1 get cygwin and basic building components
  ```cmd
  > curl https://cygwin.com/setup-x86_64.exe --output setup.exe
  : components to install: git, make, gcc-core, python3.9, wget
  ```
### 1.2 get cygwin package manager
  ```
  https://github.com/transcode-open/apt-cyg to your path(/usr/local/bin)
  ```

### 1.3 install library and other component

in cygwin shell(launch {CYGWIN}\Cygwin.bat)
  ```shell
  $ apt-cyg install autoconf bison pkgconf pkg-config libffi6 libffi8 libffi-devel libtool libpkgconf3 libpkgconf4  libSDL2 libSDL2-devel
  ```

### 1.4 optional settings 
  ```shell
  export PKG_CONFIG_PATH="/lib/pkgconfig"
  host_ip=127.0.0.1
  export ALL_PROXY="http://$host_ip:3120"
  export ALL_PROXY="socks5://$host_ip:3128"
  ```

## 2 build micropython

### 2.1 get micropython and build mpy-cross
  ```shell
  $ git clone https://github.com/micropython/micropython.git
  $ cd micropython/mpy-cross
  $ make
  ```

### 2.2 build unix port
  ```shell
  $ cd micropython/ports/unix
  $ make MICROPY_STANDALONE=1 submodules
  $ make libffi
  $ make -j4 MICROPY_STANDALONE=1
  ```

  > MICROPY_STANDALONE to get libffi static linked

  > the result is build-standard/micropython.exe

if you want to build MPY_efont, just clone it, and build with the following command like

  ```shell
  make USER_C_MODULES=../../../mod_efont/  DEBUG=1 -j4 CWARN="-Wno-error=unused-variable" FROZEN_MANIFEST=../../../mod_efont/unix_std_manifest.py
  ```

### 2.3 run micropython standalone

some DLLs should be come with micropython.exe

  ```shell
  cygffi-6.dll
  cygffi-8.dll
  cyggcc_s-seh-1.dll
  cygstdc++-6.dll
  cygwin1.dll
  SDL2.dll
  ```

to launch a script by double click, we can create a batch file, like:

  ```bat
  @echo off
  set MPYBASE=%~dp0
  set PATH=%MPYBASE%;%PATH%
  set MICROPYPATH=.frozen:%MPYBASE%\examples:%MPYBASE%\examples\lib

  cd examples
  micropython -X heapsize=8m main_demo.py
  ```


TODO. 
1. static linking cygwin1.dll, cyggcc_s-seh-1.dll, SDL2.dll


*2023/09/29*