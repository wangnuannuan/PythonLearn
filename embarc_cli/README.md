#embARC cli 

##Installation

```
python setup.py build
python setup.py install

```

## How to use
There are 7 subcommands:

- `new`, create a new example
- `appconfig`, get the informations of example
- `list`, get build configurations including the boards, board verions, cores, toolchain
- `build`, compile example
- `toolchain`, get information of toolchain
- `osp`, download embarc_osp and list the paths of osp root
- `ide`, generate ide project

### new
parameters
```
--application, Application to be created
--toolchain, Choose toolchain and the default id gnu
--middleware(optional), Choose middleware and the default is “.”
--csrc(optional), Set c source path and the default is “.”
--asmsrc(optional), Set asm source path and the default is “.”
--include(optional), Set include files path and the default is “.”
--defines(optional), Set defines files path and the default is “.”
--os, choose os
--library, choose library

```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli> embarc new
[embARC] Input application name: testcli
+-----------------------------------------------------------------+
| osp                                                             |
+-----------------------------------------------------------------+
| path1                                                           |
|  git: None                                                      |
|  local: C:/Users/jingru/Documents/embarc_application/embarc_osp |
+-----------------------------------------------------------------+
[embARC] Choose osp root or set another path as osp root: path1
[embARC] Current osp root is: C:/Users/jingru/Documents/embarc_application/ embarc_osp
[embARC] Support board : axs  emsk  hsdk  iotdk  nsim
[embARC] Choose board: emsk
[embARC] emsk support versions : 11  22  23
[embARC] Choose board version: 11
[embARC] emsk with versions 11 support cores : arcem4  arcem4cr16  arcem6  arcem6gp
[embARC] choose core: arcem4
[embARC] Support toolchains: gnu  mw
[embARC] Choose toolchain: gnu
[embARC] Current configuration
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| APPL    | BOARD | BD_VER | CUR_CORE | TOOLCHAIN | EMBARC_OSP_ROOT                                         |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| testcli | emsk  | 11     | arcem4   | gnu       | C:\Users\jingru\Documents\embarc_application\embarc_osp |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
[embARC] Start to generate makefile and main.c
[embARC] Finish generate makefile and main.c, and they are in C:\Users\jingru\Documents\embarc_application\testcli\testcli
```

A file `.embarc_cli/osp.yaml` in User folder , it will record the osp root path. After you installing the embARC cli, there is no this file, so at step
```
[embARC] Choose osp root or set another path as osp root:
```
please input a valid osp root path.

### build
parameters
```
--path, Application path
--outdir, Copy all files to this exported directory
--osp(optional) , embARC OSP path
--board(optional) , Set board
--bd_ver(optional), Set board version
--core(optional) , Set core
--toolchain, Set toolchain
--elf, Build elf
--bin, Build bin
--hex, Build hex
--size, Get build size
--info, Get build information
--target, Set build target

```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli>make build
"Clean Workspace For Selected Configuration : emsk_11-gnu_arcem4"
C:\Windows\system32\cmd.exe /C if exist  obj_emsk_11\gnu_arcem4   C:\Windows\system32\cmd.exe /C rd /S /Q obj_emsk_11\gnu_arcem4
C:\Windows\system32\cmd.exe /C if exist  .sc.project   
...
emsk/configs/11/tcf/arcem4.tcf to obj_emsk_11/gnu_arcem4/embARC_generated/arc.tcf"
"Generate Metaware compiler argument file obj_emsk_11/gnu_arcem4/embARC_generated/ccac.arg"
"Generate ARC GNU compiler argument file obj_emsk_11/gnu_arcem4/embARC_generated/gcc.arg"
"Generate nSIM properties file obj_emsk_11/gnu_arcem4/embARC_generated/nsim.props"
"Generate Metaware Debugger argument file obj_emsk_11/gnu_arcem4/embARC_generated/mdb.arg"
"Generate ARC core config header file obj_emsk_11/gnu_arcem4/embARC_generated/core_config.h"
"Generate ARC core config assembler file obj_emsk_11/gnu_arcem4/embARC_generated/core_config.s"
"Generating Linkfile   : " obj_emsk_11/gnu_arcem4/linker_gnu.ldf
arc-elf32-gcc: warning: .: linker input file unused because linking not done
"Compiling             : " main.c
arc-elf32-gcc: warning: .: linker input file unused because linking not done
...
embarc_osp/library/clib/embARC_target.c
arc-elf32-gcc: warning: .: linker input file unused because linking not done
"Archiving             : " obj_emsk_11/gnu_arcem4/liblibclib.a
"Archiving             : " obj_emsk_11/gnu_arcem4/libembarc.a
"Linking               : " obj_emsk_11/gnu_arcem4/testcli_gnu_arcem4.elf
```

Here the subcommand `build` ,you can you it just like the make command,  
```
example: embarc build BOARD=emsk BD_VER=22 CUR_CORE=arcem7d TOOLAHIN=gnu all
```

or you can add parameter by using `--`
```
example: embarc build --board emsk --target all
```
### ide
parameter
```
--generate ,start to generate ide project
```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli>embarc ide --generate
[embARC] Start to generate IDE project
[embARC] Read makefile and get configuration
[embARC] Get inculdes and defines
[embARC] Current configuration
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| APPL    | BOARD | BD_VER | CUR_CORE | TOOLCHAIN | EMBARC_OSP_ROOT                                         |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| testcli | emsk  | 11     | arcem4   | gnu       | C:\Users\jingru\Documents\embarc_application\embarc_osp |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
[embARC] Start to generate IDE project accroding to templates (.project.tmpl and .cproject.tmpl)
[embARC] Finish generate IDE project and the files are in C:\Users\jingru\Documents\embarc_application\testcli\testcli
[embARC] Open ARC GNU IDE (version) Eclipse - >File >Open Projects from File System >Paste C:\Users\jingru\Documents\embarc_application\testcli\testcli
```

### toolchain
parameters
```
--toolchain, Choose a toolchain
--check_version, Check the version of the current toolchain
--install, Install the specified version of the toolchain
--version, Use it with the --install
--download_path, Toolchain file will be download to this path
--extract_path, Toolchain file will be extracted to this path
```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli>embarc toolchain --toolchain gnu --check_version
[embARC] current toolchain is (gnu)
[embARC] the toolchain verion is (2018.03)
```
### list
parameter
```
--board, List support boards
--bd_ver, List support boards and the corresponding versions
--core , List support boards ,the board versions, and the cores
--toolchain, List the support toolchains
--middleware, List the support middleware
--libraries, List support libraries
```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli>embarc list --board
[embARC] here choose C:/Users/jingru/Documents/embarc_application/embarc_ospas osp root
[embARC] support board : axs  emsk  hsdk  iotdk  nsim

C:\Users\jingru\Documents\embarc_application\testcli\testcli>embarc list --board --bd_ver
[embARC] here choose C:/Users/jingru/Documents/embarc_application/embarc_ospas osp root
[embARC] support board : axs  emsk  hsdk  iotdk  nsim
[embARC] support board version
+-------+------------+
| board | version    |
+-------+------------+
| axs   | 103        |
| emsk  | 11 22 23   |
| hsdk  | 10         |
| iotdk | 10 openocd |
| nsim  | 10         |
+-------+------------+
```
### appconfig
parameter
```
--application, Path of example
--verbose 
```

```
C:\Users\jingru\Documents\embarc_application\testcli\testcli>embarc appconfig
[embARC] Read makefile and get configuration
[embARC] Current configuration
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| APPL    | BOARD | BD_VER | CUR_CORE | TOOLCHAIN | EMBARC_OSP_ROOT                                         |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
| testcli | emsk  | 11     | arcem4   | gnu       | C:\Users\jingru\Documents\embarc_application\embarc_osp |
+---------+-------+--------+----------+-----------+---------------------------------------------------------+
```

### osp
parameters
```
--clone, download embarc_osp from https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_osp
--list, list records in .embarc/osp.yaml
```