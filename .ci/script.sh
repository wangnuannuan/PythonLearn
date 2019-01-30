#!/bin/sh
die() {
    echo " *** ERROR: " $*
    exit 1
}

echo "${EXAMPLE[0]}"
TOOLCHAIN="gnu"
TOOLCHAIN_VER="latest"
TOOLCHAIN_CACHE_FOLDER=".cache/toolchain"
ARC_DEV_GNU_ROOT="/u/arcgnu_verif/gnu_builds"

ARC_DEV_TOOL_ROOT="${ARC_DEV_GNU_ROOT}/${TOOLCHAIN_VER}/elf32_le_linux"


python .ci/toolchain.py -v $TOOLCHAIN_VER -c $TOOLCHAIN_CACHE_FOLDER  || die
if [ -d $TOOLCHAIN_CACHE_FOLDER ] ; then
    if [ -d $TOOLCHAIN_CACHE_FOLDER/$TOOLCHAIN_VER ] ; then
        ARC_DEV_TOOL_ROOT="${TOOLCHAIN_CACHE_FOLDER}/${TOOLCHAIN_VER}"
    fi
fi

if [ -d $ARC_DEV_TOOL_ROOT ] ; then
    bash .ci/linux_env_set_arc.sh -t $TOOLCHAIN -r $ARC_DEV_TOOL_ROOT || die
    [ ! -e "arctool.env" ] && die "arctool.env doesn't exist"
    source arctool.env || die
    rm -rf arctool.env || die
else
    die "The toolchain path does not exist "
fi
if [ "${TOOLCHAIN}" == "gnu" ] ; then
    arc-elf32-gcc -v || die "ARC GNU toolchain is not installed correctly"
fi
