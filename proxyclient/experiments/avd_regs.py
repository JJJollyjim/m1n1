#!/usr/bin/env python3

from m1n1.setup import *
from m1n1.hw.dart import DART, DARTRegs
from m1n1.hw.i2c import I2C
from m1n1.hw.pmgr import PMGR
from m1n1.hw.nco import NCO
from m1n1.hw.admac import *
from m1n1.hw.mca import *


p.pmgr_adt_clocks_enable("/arm-io/avd0")

base,length = u.adt["/arm-io/avd0"].get_reg(0)

ranges = [
    # (0x000_0000, 0x4000), # angry!
    (0x100_0000, 0x4000),
    # (0x101_0000, 0x4000), # dart skipped
    # (0x102_0000, 0x4000)
    (0x107_0000, 0x4000), # piodma
    (0x10a_0000, 0x4000), # mailbox
    (0x110_0000, 0x4000), # avd regs
    (0x110_4000, 0x4000), # avd regs
    (0x110_c000, 0x4000), # avd regs
]

for start, l in ranges:
    for addr in range(base+start, base+start+l, 4):
        initial = p.read32(addr)
        p.write32(addr, 0xffffffff)
        maximum = p.read32(addr)
        p.write32(addr, 0x00000000)
        minimum = p.read32(addr)

        if initial != 0 or maximum != minimum:
            print(hex(addr-base), ": ", end="")
            if initial != 0:
                print("init={}, ".format(hex(initial)), end="")
            if maximum != minimum:
                print("writable:min={},max={}".format(hex(minimum), hex(maximum)), end="")
            print()




# first page at 0 exists


# ======== new range: 0 =========
# 0x0 : init=0x10,
# # writable:min=0x0,max=0x3ff0713
# 0x4 : init=0xfff,
# writable:min=0x0,max=0xff0fff
# crash!
# it seems to contain something wacky which makes reads then fail and uarttimeout and m1n1 die
