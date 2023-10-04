#!/bin/bash

#
# based on micropython/tools/ci.sh
#

if which nproc > /dev/null; then
    MAKEOPTS="-j$(nproc)"
else
    MAKEOPTS="-j$(sysctl -n hw.ncpu)"
fi

########################################################################################
# general helper functions

function ci_gcc_arm_setup {
    sudo apt-get install gcc-arm-none-eabi libnewlib-arm-none-eabi
    arm-none-eabi-gcc --version
}

########################################################################################
# code formatting

function ci_code_formatting_setup {
    sudo apt-get install uncrustify
    pip3 install black
    uncrustify --version
    black --version
}

function ci_code_formatting_run {
    tools/codeformat.py -v
}

########################################################################################
# code spelling

function ci_code_spell_setup {
    pip3 install codespell tomli
}

function ci_code_spell_run {
    codespell
}

########################################################################################
# ports/esp32

function ci_esp32_idf50_setup {
    pip3 install pyelftools
    git clone https://github.com/espressif/esp-idf.git
    git -C esp-idf checkout v5.0.2
    ./esp-idf/install.sh
}

function ci_esp32_build {
    source esp-idf/export.sh
    make ${MAKEOPTS} -C micropython/mpy-cross
    make ${MAKEOPTS} -C micropython/ports/esp32 submodules
    make ${MAKEOPTS} -C micropython/ports/esp32 \
        USER_C_MODULES=../../../../mod_efont/source/micropython.cmake \
        BOARD_DIR=../../../mod_efont/boards/EFORE_S3 \
        CWARN="-Wno-error=unused-variable"
}

########################################################################################
# ports/esp8266

function ci_esp8266_setup {
    sudo pip install pyserial esptool==3.3.1
    wget https://github.com/jepler/esp-open-sdk/releases/download/2018-06-10/xtensa-lx106-elf-standalone.tar.gz
    zcat xtensa-lx106-elf-standalone.tar.gz | tar x
    # Remove this esptool.py so pip version is used instead
    rm xtensa-lx106-elf/bin/esptool.py
}

function ci_esp8266_path {
    echo $(pwd)/xtensa-lx106-elf/bin
}

function ci_esp8266_build {
    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/esp8266 submodules
    make ${MAKEOPTS} -C ports/esp8266 BOARD=ESP8266_GENERIC
    make ${MAKEOPTS} -C ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_512K
    make ${MAKEOPTS} -C ports/esp8266 BOARD=ESP8266_GENERIC BOARD_VARIANT=FLASH_1M
}

########################################################################################
# ports/webassembly

function ci_webassembly_setup {
    git clone https://github.com/emscripten-core/emsdk.git
    (cd emsdk && ./emsdk install latest && ./emsdk activate latest)
}

function ci_webassembly_build {
    source emsdk/emsdk_env.sh
    make ${MAKEOPTS} -C ports/webassembly
}

function ci_webassembly_run_tests {
    # This port is very slow at running, so only run a few of the tests.
    (cd tests && MICROPY_MICROPYTHON=../ports/webassembly/node_run.sh ./run-tests.py -j1 basics/builtin_*.py)
}


########################################################################################
# ports/unix

CI_UNIX_OPTS_SYS_SETTRACE=(
    MICROPY_PY_BTREE=0
    MICROPY_PY_FFI=0
    MICROPY_PY_SSL=0
    CFLAGS_EXTRA="-DMICROPY_PY_SYS_SETTRACE=1"
)

CI_UNIX_OPTS_SYS_SETTRACE_STACKLESS=(
    MICROPY_PY_BTREE=0
    MICROPY_PY_FFI=0
    MICROPY_PY_SSL=0
    CFLAGS_EXTRA="-DMICROPY_STACKLESS=1 -DMICROPY_STACKLESS_STRICT=1 -DMICROPY_PY_SYS_SETTRACE=1"
)

CI_UNIX_OPTS_QEMU_MIPS=(
    CROSS_COMPILE=mips-linux-gnu-
    VARIANT=coverage
    MICROPY_STANDALONE=1
    LDFLAGS_EXTRA="-static"
)

CI_UNIX_OPTS_QEMU_ARM=(
    CROSS_COMPILE=arm-linux-gnueabi-
    VARIANT=coverage
    MICROPY_STANDALONE=1
)

function ci_unix_build_helper {
    make ${MAKEOPTS} -C micropython/mpy-cross
    make ${MAKEOPTS} -C micropython/ports/unix "$@" submodules
    make ${MAKEOPTS} -C micropython/ports/unix "$@" deplibs
    make ${MAKEOPTS} -C micropython/ports/unix "$@"
}

function ci_unix_build_cygwin {
    git config --global --add safe.directory ${PWD}/micropython
    make ${MAKEOPTS} -C micropython/mpy-cross
    make ${MAKEOPTS} -C micropython/ports/unix "$@" MICROPY_STANDALONE=1 submodules
    make ${MAKEOPTS} -C micropython/ports/unix libffi
    make ${MAKEOPTS} -C micropython/ports/unix "$@" MICROPY_STANDALONE=1 deplibs
    make ${MAKEOPTS} -C micropython/ports/unix "$@" MICROPY_STANDALONE=1 \
         USER_C_MODULES=../../../mod_efont/ \
         FROZEN_MANIFEST=../../../mod_efont/unix_std_manifest.py
}

function ci_unix_build_ffi_lib_helper {
    $1 $2 -shared -o tests/unix/ffi_lib.so tests/unix/ffi_lib.c
}

function ci_unix_run_tests_helper {
    make -C ports/unix "$@" test
}

function ci_unix_run_tests_full_helper {
    variant=$1
    shift
    micropython=../ports/unix/build-$variant/micropython
    make -C ports/unix VARIANT=$variant "$@" test_full
    (cd tests && MICROPY_CPYTHON3=python3 MICROPY_MICROPYTHON=$micropython ./run-multitests.py multi_net/*.py)
    (cd tests && MICROPY_CPYTHON3=python3 MICROPY_MICROPYTHON=$micropython ./run-perfbench.py 1000 1000)
}

function ci_native_mpy_modules_build {
    if [ "$1" = "" ]; then
        arch=x64
    else
        arch=$1
    fi
    make -C examples/natmod/features1 ARCH=$arch
    make -C examples/natmod/features2 ARCH=$arch
    make -C examples/natmod/features3 ARCH=$arch
    make -C examples/natmod/features4 ARCH=$arch
    make -C examples/natmod/btree ARCH=$arch
    make -C examples/natmod/deflate ARCH=$arch
    make -C examples/natmod/framebuf ARCH=$arch
    make -C examples/natmod/heapq ARCH=$arch
    make -C examples/natmod/random ARCH=$arch
    make -C examples/natmod/re ARCH=$arch
}

function ci_native_mpy_modules_32bit_build {
    ci_native_mpy_modules_build x86
}

function ci_unix_minimal_build {
    make ${MAKEOPTS} -C ports/unix VARIANT=minimal
}

function ci_unix_minimal_run_tests {
    (cd tests && MICROPY_CPYTHON3=python3 MICROPY_MICROPYTHON=../ports/unix/build-minimal/micropython ./run-tests.py -e exception_chain -e self_type_check -e subclass_native_init -d basics)
}

function ci_unix_standard_build {
    ci_unix_build_helper VARIANT=standard
    # ci_unix_build_ffi_lib_helper gcc
}

function ci_unix_coverage_setup {
    sudo pip3 install setuptools
    sudo pip3 install pyelftools
    gcc --version
    python3 --version
}

function ci_unix_coverage_build {
    ci_unix_build_helper VARIANT=coverage
    ci_unix_build_ffi_lib_helper gcc
}

function ci_unix_coverage_run_tests {
    ci_unix_run_tests_full_helper coverage
}

function ci_unix_coverage_run_mpy_merge_tests {
    mptop=$(pwd)
    outdir=$(mktemp -d)
    allmpy=()

    # Compile a selection of tests to .mpy and execute them, collecting the output.
    # None of the tests should SKIP.
    for inpy in $mptop/tests/basics/[acdel]*.py; do
        test=$(basename $inpy .py)
        echo $test
        outmpy=$outdir/$test.mpy
        $mptop/mpy-cross/build/mpy-cross -o $outmpy $inpy
        (cd $outdir && $mptop/ports/unix/build-coverage/micropython -m $test >> out-individual)
        allmpy+=($outmpy)
    done

    # Merge all the tests into one .mpy file, and then execute it.
    python3 $mptop/tools/mpy-tool.py --merge -o $outdir/merged.mpy ${allmpy[@]}
    (cd $outdir && $mptop/ports/unix/build-coverage/micropython -m merged > out-merged)

    # Make sure the outputs match.
    diff $outdir/out-individual $outdir/out-merged && /bin/rm -rf $outdir
}

function ci_unix_coverage_run_native_mpy_tests {
    MICROPYPATH=examples/natmod/features2 ./ports/unix/build-coverage/micropython -m features2
    (cd tests && ./run-natmodtests.py "$@" extmod/{btree*,deflate*,framebuf*,heapq*,random*,re*}.py)
}

function ci_unix_32bit_setup {
    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install gcc-multilib g++-multilib libffi-dev:i386
    sudo pip3 install setuptools
    sudo pip3 install pyelftools
    gcc --version
    python3 --version
}

function ci_unix_coverage_32bit_build {
    ci_unix_build_helper VARIANT=coverage MICROPY_FORCE_32BIT=1
    ci_unix_build_ffi_lib_helper gcc -m32
}

function ci_unix_coverage_32bit_run_tests {
    ci_unix_run_tests_full_helper coverage MICROPY_FORCE_32BIT=1
}

function ci_unix_coverage_32bit_run_native_mpy_tests {
    ci_unix_coverage_run_native_mpy_tests --arch x86
}

function ci_unix_nanbox_build {
    # Use Python 2 to check that it can run the build scripts
    ci_unix_build_helper PYTHON=python2 VARIANT=nanbox CFLAGS_EXTRA="-DMICROPY_PY_MATH_CONSTANTS=1"
    ci_unix_build_ffi_lib_helper gcc -m32
}

function ci_unix_nanbox_run_tests {
    ci_unix_run_tests_full_helper nanbox PYTHON=python2
}

function ci_unix_float_build {
    ci_unix_build_helper VARIANT=standard CFLAGS_EXTRA="-DMICROPY_FLOAT_IMPL=MICROPY_FLOAT_IMPL_FLOAT"
    ci_unix_build_ffi_lib_helper gcc
}

function ci_unix_float_run_tests {
    # TODO get this working: ci_unix_run_tests_full_helper standard CFLAGS_EXTRA="-DMICROPY_FLOAT_IMPL=MICROPY_FLOAT_IMPL_FLOAT"
    ci_unix_run_tests_helper CFLAGS_EXTRA="-DMICROPY_FLOAT_IMPL=MICROPY_FLOAT_IMPL_FLOAT"
}

function ci_unix_clang_setup {
    sudo apt-get install clang
    clang --version
}

function ci_unix_stackless_clang_build {
    make ${MAKEOPTS} -C mpy-cross CC=clang
    make ${MAKEOPTS} -C ports/unix submodules
    make ${MAKEOPTS} -C ports/unix CC=clang CFLAGS_EXTRA="-DMICROPY_STACKLESS=1 -DMICROPY_STACKLESS_STRICT=1"
}

function ci_unix_stackless_clang_run_tests {
    ci_unix_run_tests_helper CC=clang
}

function ci_unix_float_clang_build {
    make ${MAKEOPTS} -C mpy-cross CC=clang
    make ${MAKEOPTS} -C ports/unix submodules
    make ${MAKEOPTS} -C ports/unix CC=clang CFLAGS_EXTRA="-DMICROPY_FLOAT_IMPL=MICROPY_FLOAT_IMPL_FLOAT"
}

function ci_unix_float_clang_run_tests {
    ci_unix_run_tests_helper CC=clang
}

function ci_unix_settrace_build {
    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/unix submodules
    make ${MAKEOPTS} -C ports/unix "${CI_UNIX_OPTS_SYS_SETTRACE[@]}"
}

function ci_unix_settrace_run_tests {
    ci_unix_run_tests_full_helper standard "${CI_UNIX_OPTS_SYS_SETTRACE[@]}"
}

function ci_unix_settrace_stackless_build {
    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/unix submodules
    make ${MAKEOPTS} -C ports/unix "${CI_UNIX_OPTS_SYS_SETTRACE_STACKLESS[@]}"
}

function ci_unix_settrace_stackless_run_tests {
    ci_unix_run_tests_full_helper standard "${CI_UNIX_OPTS_SYS_SETTRACE_STACKLESS[@]}"
}

function ci_unix_macos_build {
    # Install pkg-config to configure libffi paths.
    brew install pkg-config

    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/unix submodules
    #make ${MAKEOPTS} -C ports/unix deplibs
    make ${MAKEOPTS} -C ports/unix
    # check for additional compiler errors/warnings
    make ${MAKEOPTS} -C ports/unix VARIANT=coverage submodules
    make ${MAKEOPTS} -C ports/unix VARIANT=coverage
}

function ci_unix_macos_run_tests {
    # Issues with macOS tests:
    # - import_pkg7 has a problem with relative imports
    # - random_basic has a problem with getrandbits(0)
    (cd tests && MICROPY_MICROPYTHON=../ports/unix/build-standard/micropython ./run-tests.py --exclude 'import_pkg7.py' --exclude 'random_basic.py')
}

function ci_unix_qemu_mips_setup {
    sudo apt-get update
    sudo apt-get install gcc-mips-linux-gnu g++-mips-linux-gnu
    sudo apt-get install qemu-user
    qemu-mips --version
}

function ci_unix_qemu_mips_build {
    # qemu-mips on GitHub Actions will seg-fault if not linked statically
    ci_unix_build_helper "${CI_UNIX_OPTS_QEMU_MIPS[@]}"
}

function ci_unix_qemu_mips_run_tests {
    # Issues with MIPS tests:
    # - (i)listdir does not work, it always returns the empty list (it's an issue with the underlying C call)
    # - ffi tests do not work
    file ./ports/unix/build-coverage/micropython
    (cd tests && MICROPY_MICROPYTHON=../ports/unix/build-coverage/micropython ./run-tests.py --exclude 'vfs_posix.*\.py' --exclude 'ffi_(callback|float|float2).py')
}

function ci_unix_qemu_arm_setup {
    sudo apt-get update
    sudo apt-get install gcc-arm-linux-gnueabi g++-arm-linux-gnueabi
    sudo apt-get install qemu-user
    qemu-arm --version
}

function ci_unix_qemu_arm_build {
    ci_unix_build_helper "${CI_UNIX_OPTS_QEMU_ARM[@]}"
    ci_unix_build_ffi_lib_helper arm-linux-gnueabi-gcc
}

function ci_unix_qemu_arm_run_tests {
    # Issues with ARM tests:
    # - (i)listdir does not work, it always returns the empty list (it's an issue with the underlying C call)
    export QEMU_LD_PREFIX=/usr/arm-linux-gnueabi
    file ./ports/unix/build-coverage/micropython
    (cd tests && MICROPY_MICROPYTHON=../ports/unix/build-coverage/micropython ./run-tests.py --exclude 'vfs_posix.*\.py')
}

########################################################################################
# ports/windows

function ci_windows_setup {
    sudo apt-get install gcc-mingw-w64
}

function ci_windows_build {
    make ${MAKEOPTS} -C mpy-cross
    make ${MAKEOPTS} -C ports/windows submodules
    make ${MAKEOPTS} -C ports/windows CROSS_COMPILE=i686-w64-mingw32-
}
