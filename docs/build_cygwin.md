
1. https://cygwin.com/setup-x86_64.exe
2. run it and install: git, make, gcc-core, python3.9, wget
3. https://github.com/transcode-open/apt-cyg to your path

4. ./apt-cyg install autoconf bison pkgconf pkg-config libffi6 libffi8 libffi-devel libtool libpkgconf3 libpkgconf4  libSDL2 libSDL2-devel
5. optional  export PKG_CONFIG_PATH="/lib/pkgconfig"
host_ip=127.0.0.1
export ALL_PROXY="http://$host_ip:3120"
export ALL_PROXY="socks5://$host_ip:3128"

6. git clone https://github.com/micropython/micropython.git
cd micropython/mpy-cross
make

7. cd ~/mpy/micropython/ports/unix
make MICROPY_STANDALONE=1 submodules
  * MICROPY_STANDALONE to get libffi as static linked
8. make libffi

9. make -j4 MICROPY_STANDALONE=1

TODO. 
1. static linking cygwin1.dll, cyggcc_s-seh-1.dll, SDL2.dll


*2023/09/28*