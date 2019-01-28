#!/bin/sh
die() {
    echo " *** ERROR: " $*
    exit 1
}

echo "${EXAMPLE[0]}"

TOOLCHAIN_CACHE_FOLDER=".cache/toolchain"
ARC_DEV_GNU_ROOT="/u/arcgnu_verif/gnu_builds"

ARC_DEV_TOOL_ROOT="${ARC_DEV_GNU_ROOT}/${TOOLCHAIN_VER}/elf32_le_linux"


python .ci/toolchain.py -v $TOOLCHAIN_VER -c $TOOLCHAIN_CACHE_FOLDER  || die
if [ -d $TOOLCHAIN_CACHE_FOLDER ] ; then
    if [ -d $TOOLCHAIN_CACHE_FOLDER/$TOOLCHAIN_VER ] ; then
        ARC_DEV_TOOL_ROOT="${TOOLCHAIN_CACHE_FOLDER}/${TOOLCHAIN_VER}"
    fi
fi


