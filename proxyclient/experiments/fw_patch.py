#!/usr/bin/env python3

import subprocess
import pathlib
infile = "/home/jamie/m3.bin"

firmware = open(infile, "rb").read()

init = int.from_bytes(firmware[4:8], "little")
print("Original init at: ", hex(init))
print("File length:", hex(len(firmware)))

assert len(firmware) % 16 == 0

ret = subprocess.call([
    'arm-none-eabi-gcc',
    '-ggdb',
    '-nostdlib',
    f'-Wl,-Ttext,{hex(len(firmware))}',
    f'-DORIGINIT=#{hex(init)}',
    '-o', 'pre_init.elf',
    f'{pathlib.Path(__file__).resolve().parents[0]}/pre_init.S'])
assert ret == 0
ret = subprocess.call([
    'arm-none-eabi-objcopy',
    '-O', 'binary',
    'pre_init.elf',
    'pre_init.bin'])
assert ret == 0

pre_init_code = open("pre_init.bin", "rb").read()

new_fw = firmware[0:4] + (len(firmware)+1).to_bytes(4, "little") + firmware[8:] + pre_init_code

open("patched_firwmare", "wb").write(new_fw)
