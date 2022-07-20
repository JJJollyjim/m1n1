#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from m1n1.setup import *
from m1n1.hw.dart8110 import DART8110, DART8110Regs
from m1n1.hw.avd import *
from m1n1.utils import *
import time
from array import array


class Mailbox:
    # Outbound messages are 24 words.
    # We have a range in M3 RAM to store 8 messages, which we use in a ring
    next_outbox = 0

    def init(avd):
        self.avd = avd

    def send(arr):
        arr = arr + ([0] * (24 - len(arr)))

        outbox = self.next_outbox


        self.next_outbox += 1




p.pmgr_adt_clocks_enable(f'/arm-io/dart-avd0')
p.pmgr_adt_clocks_enable(f'/arm-io/avd0')

dart = DART8110.from_adt(u, f'/arm-io/dart-avd0')

def low_startup_sequence():
    # directly from traces, not understood in the slightest

    assert p.read32(0x286000000) == 0x10
    p.write32(0x286000000, 0x11)
    assert p.read32(0x286000010) == 0xfff0000
    p.write32(0x286000010, 0xd0000)
    assert p.read32(0x286000014) == 0x0
    p.write32(0x286000014, 0x1)
    assert p.read32(0x286000018) == 0x0
    p.write32(0x286000018, 0x1)
    assert p.read32(0x28600001c) == 0x0
    p.write32(0x28600001c, 0x3)
    assert p.read32(0x286000020) == 0x0
    p.write32(0x286000020, 0x3)
    assert p.read32(0x286000024) == 0x0
    p.write32(0x286000024, 0x3)
    assert p.read32(0x286000028) == 0x0
    p.write32(0x286000028, 0x3)
    assert p.read32(0x28600002c) == 0x0
    p.write32(0x28600002c, 0x3)
    assert p.read32(0x286000400) == 0xa00004
    p.write32(0x286000400, 0x40a10001)
    assert p.read32(0x286000600) == 0x0
    p.write32(0x286000600, 0x1ffffff)
    assert p.read32(0x286000410) == 0x100
    p.write32(0x286000410, 0x1100)
    assert p.read32(0x286000420) == 0x100
    p.write32(0x286000420, 0x1100)
    assert p.read32(0x286000430) == 0x100
    p.write32(0x286000430, 0x1100)
    assert p.read32(0x286008000) == 0x0
    p.write32(0x286008000, 0x9)
    assert p.read32(0x286000820) == 0x0
    p.write32(0x286000820, 0x80)
    p.write32(0x286008008, 0x7)
    p.write32(0x286008014, 0x1)
    assert p.read32(0x286008018) == 0x0
    p.write32(0x286008018, 0x1)
    assert p.read32(0x2860007a8) == 0x0
    p.write32(0x2860007a8, 0x1)
    p.write32(0x286008208, 0x4)
    p.write32(0x286008280, 0x20)
    p.write32(0x286008288, 0x3)
    p.write32(0x28600828c, 0xc)
    p.write32(0x286008290, 0x18)
    p.write32(0x286008294, 0x30)
    p.write32(0x286008298, 0x78)
    p.write32(0x28600829c, 0xf0)
    assert p.read32(0x2860082b8) == 0x0
    p.write32(0x2860082b8, 0x1)
    p.write32(0x2860082bc, 0x1)
    assert p.read32(0x2860082c0) == 0x0
    p.write32(0x2860082c0, 0x1)
    assert p.read32(0x2860007a8) == 0x1
    p.write32(0x2860007a8, 0x1)
    p.write32(0x28600820c, 0x5)
    p.write32(0x286008284, 0x20)
    p.write32(0x2860082a0, 0x3)
    p.write32(0x2860082a4, 0xc)
    p.write32(0x2860082a8, 0x18)
    p.write32(0x2860082ac, 0x30)
    p.write32(0x2860082b0, 0x78)
    p.write32(0x2860082b4, 0xf0)
    assert p.read32(0x2860082b8) == 0x1
    p.write32(0x2860082b8, 0x3)
    p.write32(0x2860082bc, 0x2)
    assert p.read32(0x2860082c0) == 0x1
    p.write32(0x2860082c0, 0x3)
    p.write32(0x286008210, 0x0)
    p.write32(0x286008408, 0xd)
    p.write32(0x286008418, 0x3)
    p.write32(0x28600841c, 0x0)
    p.write32(0x286008420, 0xffffffff)
    p.write32(0x286008424, 0x0)
    p.write32(0x286008428, 0xfff)
    assert p.read32(0x2860082b8) == 0x3
    p.write32(0x2860082b8, 0x7)
    p.write32(0x2860082bc, 0x4)
    assert p.read32(0x2860082c0) == 0x3
    p.write32(0x2860082c0, 0x7)


low_startup_sequence()

dart.initialize()

DATA_SZ = 0x400_0000
data_phys = u.heap.memalign(0x4000, DATA_SZ)
dart.iomap_at(0, 0, data_phys, DATA_SZ)

DESC_SZ = 0xbc_0000
desc_phys = u.heap.memalign(0x4000, DESC_SZ)
dart.iomap_at(1, 0, desc_phys, DESC_SZ)

avd_base, _ = u.adt[f'/arm-io/avd0'].get_reg(0)
avd = AvdRegs(u, avd_base)

fwdata = open("/home/jamie/Projects/avd/fwblob", "rb").read()
fwdata = fwdata + (b"\x00" * (0x10000 - len(fwdata)))
fwdata = array("I", fwdata)
assert len(fwdata) == 0x4000

for i in range(len(fwdata)):
    avd.M3_FW[i].val = fwdata[i]

# sequence straight from trace
avd.MAILBOX_08.val = 0xe
avd.MAILBOX_10.val = 0
avd.MAILBOX_48.val = 0

apply_avd_tunables(p, avd_base, open("/home/jamie/Projects/avd/tunables_avd", "rb").read())
apply_avd_tunables(p, avd_base, open("/home/jamie/Projects/avd/tunables_avd_wrap_ctrl", "rb").read())
apply_avd_tunables(p, avd_base, open("/home/jamie/Projects/avd/tunables_avd_piodma", "rb").read())

avd.MAILBOX_10.val = 0x0
avd.MAILBOX_48.val = 0x0
avd.MAILBOX_50.val = 0x1
avd.MAILBOX_68.val = 0x1
avd.MAILBOX_5C.val = 0x1
avd.MAILBOX_74.val = 0x1
avd.MAILBOX_10.val = 0x2
avd.MAILBOX_48.val = 0x8
avd.MAILBOX_08.val = 0x1
while avd.MAILBOX_90.val != 1:
    print("not yet...")

for i in range(0x4000):
    avd.M3_RAM[i].val = 0

p.write32(0x287107024, 0x28707000)
p.write32(0x287400018, 0x1)
p.write32(0x287107000, 0x0)
p.write32(0x28710014c, 0x2)
p.write32(0x28710e4d0, 0xffffffff)
p.write32(0x28710e4d4, 0xffffffff)
p.write32(0x28710e510, 0xffffffff)
p.write32(0x28710e514, 0xffffffff)
p.write32(0x28710e308, 0xffffffff)
p.write32(0x28710e300, 0x80023fff)
p.write32(0x28710c900, 0x800113ff)
p.write32(0x28710c940, 0x800113ff)
p.write32(0x28710c980, 0x800113ff)
p.write32(0x28710c9c0, 0x800113ff)

for i in range(0x4000):
    avd.M3_RAM[i].val = 0

for i in range(len(fwdata)):
    avd.M3_FW[i].val = fwdata[i]

avd.MAILBOX_10.val = 0x0
avd.MAILBOX_48.val = 0x0
avd.MAILBOX_50.val = 0x1
avd.MAILBOX_68.val = 0x1
avd.MAILBOX_5C.val = 0x1
avd.MAILBOX_74.val = 0x1
avd.MAILBOX_10.val = 0x2
avd.MAILBOX_48.val = 0x8
avd.MAILBOX_08.val = 0x1
while avd.MAILBOX_90.val != 1:
    print("not yet...")
p.write32(0x287107024, 0x28707000)
assert avd.MAILBOX_48.val == 0x8
avd.MAILBOX_48.val = 9

avd.M3_RAM[3083].val = 0x4020002
avd.M3_RAM[3084].val = 0x20002
avd.M3_RAM[3085].val = 0x4020002
avd.M3_RAM[3086].val = 0x4020002
avd.M3_RAM[3087].val = 0x4020002
avd.M3_RAM[3088].val = 0x70007
avd.M3_RAM[3089].val = 0x70007
avd.M3_RAM[3090].val = 0x70007
avd.M3_RAM[3091].val = 0x70007
avd.M3_RAM[3092].val = 0x70007
avd.M3_RAM[3093].val = 0x0
avd.M3_RAM[3094].val = 0x0
avd.M3_RAM[3095].val = 0x0
avd.M3_RAM[3096].val = 0x0
avd.M3_RAM[3097].val = 0x0
avd.M3_RAM[3098].val = 0x0

assert avd.MAILBOX_48.val == 0x9

avd.MAILBOX_48.val = 9

p.write32(0x287400014, 0x0)

avd.M3_RAM[2867].val = 0x0 # Start Session
avd.M3_RAM[2868].val = 0x0
avd.M3_RAM[2869].val = 0x0
avd.M3_RAM[2870].val = 0x0
avd.M3_RAM[2871].val = 0x0
avd.M3_RAM[2872].val = 0x0
avd.M3_RAM[2873].val = 0x0
avd.M3_RAM[2874].val = 0x0
avd.M3_RAM[2875].val = 0x0
avd.M3_RAM[2876].val = 0x0
avd.M3_RAM[2877].val = 0x0
avd.M3_RAM[2878].val = 0x0
avd.M3_RAM[2879].val = 0x0
avd.M3_RAM[2880].val = 0x0
avd.M3_RAM[2881].val = 0x0
avd.M3_RAM[2882].val = 0x0
avd.M3_RAM[2883].val = 0x0
avd.M3_RAM[2884].val = 0x0
avd.M3_RAM[2885].val = 0x0
avd.M3_RAM[2886].val = 0x0
avd.M3_RAM[2887].val = 0x0
avd.M3_RAM[2888].val = 0x0
avd.M3_RAM[2889].val = 0x0
avd.M3_RAM[2890].val = 0x0

assert avd.MAILBOX_50.val == 0x20001
avd.MAILBOX_A2I_SEND.val = 0x1092ccc

avd.M3_RAM[2891].val = 0x6 # set property
avd.M3_RAM[2892].val = 0x1 # key 1
avd.M3_RAM[2893].val = 0x1 # val 1
avd.M3_RAM[2894].val = 0x0
avd.M3_RAM[2895].val = 0x0
avd.M3_RAM[2896].val = 0x0
avd.M3_RAM[2897].val = 0x0
avd.M3_RAM[2898].val = 0x0
avd.M3_RAM[2899].val = 0x0
avd.M3_RAM[2900].val = 0x0
avd.M3_RAM[2901].val = 0x0
avd.M3_RAM[2902].val = 0x0
avd.M3_RAM[2903].val = 0x0
avd.M3_RAM[2904].val = 0x0
avd.M3_RAM[2905].val = 0x0
avd.M3_RAM[2906].val = 0x0
avd.M3_RAM[2907].val = 0x0
avd.M3_RAM[2908].val = 0x0
avd.M3_RAM[2909].val = 0x0
avd.M3_RAM[2910].val = 0x0
avd.M3_RAM[2911].val = 0x0
avd.M3_RAM[2912].val = 0x0
avd.M3_RAM[2913].val = 0x0
avd.M3_RAM[2914].val = 0x0

assert avd.MAILBOX_50.val == 0x21101
avd.MAILBOX_A2I_SEND.val = 0x1092d2c
assert avd.MAILBOX_48.val == 9
avd.MAILBOX_48.val = 8

assert avd.MAILBOX_5C.val == 0x101
assert avd.MAILBOX_I2A_RECV.val == 0x1091094

avd.MAILBOX_4C.val = 8

assert avd.M3_RAM[1061].val == 0x20
assert avd.M3_RAM[1062].val == 0x0
assert avd.M3_RAM[1063].val == 0x0
assert avd.M3_RAM[1064].val == 0x0
assert avd.M3_RAM[1065].val == 0x0
assert avd.M3_RAM[1066].val == 0x0
assert avd.M3_RAM[1067].val == 0x0
assert avd.M3_RAM[1068].val == 0x0
assert avd.M3_RAM[1069].val == 0x0
assert avd.M3_RAM[1070].val == 0x0
assert avd.M3_RAM[1071].val == 0x0
assert avd.M3_RAM[1072].val == 0x0
assert avd.M3_RAM[1073].val == 0x0
assert avd.M3_RAM[1074].val == 0x0
assert avd.M3_RAM[1075].val == 0x0
assert avd.M3_RAM[1076].val == 0x0
assert avd.M3_RAM[1077].val == 0x0
assert avd.M3_RAM[1078].val == 0x0
assert avd.M3_RAM[1079].val == 0x0
assert avd.M3_RAM[1080].val == 0x0



assert avd.MAILBOX_5C.val == 0x1201
assert avd.MAILBOX_I2A_RECV.val == 0x10910f4
avd.MAILBOX_4C.val = 8
assert avd.M3_RAM[1085].val == 0x26
assert avd.M3_RAM[1086].val == 0x0
assert avd.M3_RAM[1087].val == 0x0
assert avd.M3_RAM[1088].val == 0x0
assert avd.M3_RAM[1089].val == 0x0
assert avd.M3_RAM[1090].val == 0x0
assert avd.M3_RAM[1091].val == 0x0
assert avd.M3_RAM[1092].val == 0x0
assert avd.M3_RAM[1093].val == 0x0
assert avd.M3_RAM[1094].val == 0x0
assert avd.M3_RAM[1095].val == 0x0
assert avd.M3_RAM[1096].val == 0x0
assert avd.M3_RAM[1097].val == 0x0
assert avd.M3_RAM[1098].val == 0x0
assert avd.M3_RAM[1099].val == 0x0
assert avd.M3_RAM[1100].val == 0x0
assert avd.M3_RAM[1101].val == 0x0
assert avd.M3_RAM[1102].val == 0x0
assert avd.M3_RAM[1103].val == 0x0
assert avd.M3_RAM[1104].val == 0x0

p.write32(0x287400014, 0x1)
assert avd.MAILBOX_48.val == 8
avd.MAILBOX_48.val = 9
p.write32(0x287400014, 0x0)

print('mew')
dart.iowrite(1, 0, open("/home/jamie/Projects/avd/good_data/dump_0004_cool_zone", "rb").read()[0:0xbc000])
print('meow')
dart.iowrite(0, 0, open("/home/jamie/Projects/avd/good_data/dump_0004_data", "rb").read())
print('nya')

# deode frame
avd.M3_RAM[2915].val = 0x401
avd.M3_RAM[2916].val = 0x0
avd.M3_RAM[2917].val = 0x0
avd.M3_RAM[2918].val = 0x1
avd.M3_RAM[2919].val = 0xc0003
avd.M3_RAM[2920].val = 0xc
avd.M3_RAM[2921].val = 0x0
avd.M3_RAM[2922].val = 0x1093094
avd.M3_RAM[2923].val = 0x2c8
avd.M3_RAM[2924].val = 0x10930a0
avd.M3_RAM[2925].val = 0x4ac
avd.M3_RAM[2926].val = 0x724
avd.M3_RAM[2927].val = 0x8b504
avd.M3_RAM[2928].val = 0x0
avd.M3_RAM[2929].val = 0x10930c8
avd.M3_RAM[2930].val = 0x10932d0
avd.M3_RAM[2931].val = 0x109332c
avd.M3_RAM[2932].val = 0x690
avd.M3_RAM[2933].val = 0x70c
avd.M3_RAM[2934].val = 0x0
avd.M3_RAM[2935].val = 0x0
avd.M3_RAM[2936].val = 0x0
avd.M3_RAM[2937].val = 0x0
avd.M3_RAM[2938].val = 0x0
assert avd.MAILBOX_50.val == 0x22201
avd.MAILBOX_A2I_SEND.val = 0x1092d8c
assert avd.MAILBOX_48.val == 0x9
avd.MAILBOX_48.val = 0x8

# import time
# while True:
#     print(hex(avd.MAILBOX_5C.val))
#     time.sleep(0.1)
assert avd.MAILBOX_5C.val == 0x2301
assert avd.MAILBOX_I2A_RECV.val == 0x1091154
avd.MAILBOX_4C.val = 0x8
assert avd.M3_RAM[1109].val == 0x421
assert avd.M3_RAM[1110].val == 0x0
assert avd.M3_RAM[1111].val == 0x0
assert avd.M3_RAM[1112].val == 0x1
assert avd.M3_RAM[1113].val == 0xc0003
assert avd.M3_RAM[1114].val == 0xc
assert avd.M3_RAM[1115].val == 0x0
assert avd.M3_RAM[1116].val == 0x1093094
assert avd.M3_RAM[1117].val == 0x2c8
assert avd.M3_RAM[1118].val == 0x10930a0
assert avd.M3_RAM[1119].val == 0x4ac
assert avd.M3_RAM[1120].val == 0x724
assert avd.M3_RAM[1121].val == 0x8b504
assert avd.M3_RAM[1122].val == 0x0
assert avd.M3_RAM[1123].val == 0x10930c8
assert avd.M3_RAM[1124].val == 0x10932d0
assert avd.M3_RAM[1125].val == 0x109332c
assert avd.M3_RAM[1126].val == 0x690
assert avd.M3_RAM[1127].val == 0x70c
assert avd.M3_RAM[1128].val == 0x0


assert avd.MAILBOX_5C.val == 0x3401
assert avd.MAILBOX_I2A_RECV.val == 0x10911b4
avd.MAILBOX_4C.val = 0x8
assert avd.M3_RAM[1133].val == 0x4
assert avd.M3_RAM[1134].val == 0x1
assert avd.M3_RAM[1135].val == 0x16771
assert avd.M3_RAM[1136].val == 0x0
assert avd.M3_RAM[1137].val == 0x0
assert avd.M3_RAM[1138].val == 0x0
assert avd.M3_RAM[1139].val == 0x0
assert avd.M3_RAM[1140].val == 0x0
assert avd.M3_RAM[1141].val == 0x0
assert avd.M3_RAM[1142].val == 0x0
assert avd.M3_RAM[1143].val == 0x0
assert avd.M3_RAM[1144].val == 0x0
assert avd.M3_RAM[1145].val == 0x0
assert avd.M3_RAM[1146].val == 0x0
assert avd.M3_RAM[1147].val == 0x0
assert avd.M3_RAM[1148].val == 0x0
assert avd.M3_RAM[1149].val == 0x0
assert avd.M3_RAM[1150].val == 0x0
assert avd.M3_RAM[1151].val == 0x0
assert avd.M3_RAM[1152].val == 0x0
