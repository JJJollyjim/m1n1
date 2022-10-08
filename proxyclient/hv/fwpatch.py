#!/usr/bin/env python3


import subprocess
import pathlib
import struct

def patch(filename="firmware_dump.bin"):
    firmware = open(filename, "rb").read()
    while firmware[-16:] == (b"\x00"*16):
        firmware = firmware[:-16]
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
        f'{pathlib.Path(__file__).resolve().parents[1]}/hv/pre_init.S'])
    assert ret == 0
    ret = subprocess.call([
        'arm-none-eabi-objcopy',
        '-O', 'binary',
        'pre_init.elf',
        'pre_init.bin'])
    assert ret == 0
    pre_init_code = open("pre_init.bin", "rb").read()
    pre_init_code += b'\x00' * (0x10 - (len(pre_init_code) % 0x10))
    assert len(pre_init_code) % 0x10 == 0

    ret = subprocess.call([
        'arm-none-eabi-gcc',
        '-mthumb',
        '-mcpu=cortex-m3',
        '-ggdb',
        '-nostdlib',
        f'-Wl,-Ttext,{hex(len(firmware)+len(pre_init_code))}',
        '-o', 'debugmonitor.elf',
        f'{pathlib.Path(__file__).resolve().parents[1]}/hv/debugmonitor.c'])
    assert ret == 0

    ret = subprocess.call([
        'arm-none-eabi-objcopy',
        '-O', 'binary',
        'debugmonitor.elf',
        'debugmonitor.bin'])
    assert ret == 0
    debug_mon_code = open("debugmonitor.bin", "rb").read()

    new_fw = firmware[0:4] + (len(firmware)+1).to_bytes(4, "little") + firmware[8:48] + (len(firmware)+len(pre_init_code)+1).to_bytes(4, "little") + firmware[52:] + pre_init_code + debug_mon_code
    new_fw += b"\x00"*(0x1_0000-len(new_fw))
    open("patched_firwmare.bin", "wb").write(new_fw)
    return new_fw

if __name__ == "__main__":
    patch()
