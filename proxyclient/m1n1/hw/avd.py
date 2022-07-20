from ..utils import *
from collections import namedtuple
from enum import IntEnum
import struct

def dma_block(self, name, addr):
    setattr(self, "DMA_"+name+"_CONFIG",  (addr, Register32))
    setattr(self, "DMA_"+name+"_BFR_CONFIG", (addr+4, Register32))
    setattr(self, "DMA_"+name+"_08", (addr+8, Register32))
    setattr(self, "DMA_"+name+"_10", (addr+0x10, Register32))

def dma_block_array(self, name, addr, count):
    setattr(self, "DMA_"+name+"_CONFIG",  (irange(addr, count, 0x40), Register32))
    setattr(self, "DMA_"+name+"_BFR_CONFIG", (irange(addr+4, count, 0x40), Register32))
    setattr(self, "DMA_"+name+"_08", (irange(addr+8, count, 0x40), Register32))
    setattr(self, "DMA_"+name+"_10", (irange(addr+0x10, count, 0x40), Register32))

class AvdRegs(RegMap):
    # ** Totally unused: =0 - 0ff_ffff=
    # This address range has not been observed in use at all.
    # it does have some regs in it, but writing to them can kill m1n1 so i haven't investigated them:
    # 0x0 : init=0x10,
    # # writable:min=0x0,max=0x3ff0713
    # 0x4 : init=0xfff,
    # writable:min=0x0,max=0xff0fff

    # ** Unknown: =100_0000=
    # A single register is observable at this address in MMIO traces, written by macOS.
    #  0x1000000 : writable:min=0x0,max=0x1fff
    #  0x1000040 : init=0x80,
    #  0x1000084 : init=0x3,
    #  0x1001000 : writable:min=0x0,max=0x1fff
    #  0x1001040 : init=0x80,
    #  0x1001084 : init=0x1,
    #  0x1002000 : init=0x10000,
    #  0x1002004 : writable:min=0x0,max=0x7f
    #  0x1002008 : writable:min=0x0,max=0xffffffff
    #  0x100200c : writable:min=0x0,max=0xffffffff
    #  0x100201c : init=0x2,
    #  0x1002020 : writable:min=0x0,max=0x3fff
    #  0x1002024 : writable:min=0x0,max=0xff
    #  0x1002028 : init=0x2,
    #  0x1002208 : init=0xffffffff,
    #  0x1002210 : init=0xffffffff,
    #  0x1002218 : init=0xffffffff,
    #  0x1002220 : init=0xffffffff,
    #  0x1002228 : init=0xffffffff,
    #  0x1002230 : init=0xffffffff,
    #  0x1002238 : init=0xffffffff,
    #  0x1002240 : init=0xffffffff,
    #  0x1002248 : init=0xffffffff,
    #  0x1002250 : init=0xffffffff,
    #  0x1002258 : init=0xffffffff,
    #  0x1002260 : init=0xffffffff,
    #  0x1002268 : init=0xffffffff,
    #  0x1002270 : init=0xffffffff,
    #  0x1002278 : init=0xffffffff,
    #  0x1002280 : init=0xffffffff,
    #  0x1002288 : init=0xffffffff,
    #  0x1002290 : init=0xffffffff,
    #  0x1002298 : init=0xffffffff,
    #  0x10022a0 : init=0xffffffff,
    #  0x10022a8 : init=0xffffffff,
    #  0x10022b0 : init=0xffffffff,
    #  0x10022b8 : init=0xffffffff,
    #  0x10022c0 : init=0xffffffff,
    #  0x10022c8 : init=0xffffffff,
    #  0x10022d0 : init=0xffffffff,
    #  0x10022d8 : init=0xffffffff,
    #  0x10022e0 : init=0xffffffff,
    #  0x10022e8 : init=0xffffffff,
    #  0x10022f0 : init=0xffffffff,
    #  0x10022f8 : init=0xffffffff,
    #  0x1002300 : init=0xffffffff,
    #  0x1002308 : init=0xffffffff,
    #  0x1002310 : init=0xffffffff,
    #  0x1002318 : init=0xffffffff,
    #  0x1002320 : init=0xffffffff,
    #  0x1002328 : init=0xffffffff,
    #  0x1002330 : init=0xffffffff,
    #  0x1002338 : init=0xffffffff,
    #  0x1002340 : init=0xffffffff,
    #  0x1002348 : init=0xffffffff,
    #  0x1002350 : init=0xffffffff,
    #  0x1002358 : init=0xffffffff,
    #  0x1002360 : init=0xffffffff,
    #  0x1002368 : init=0xffffffff,
    #  0x1002370 : init=0xffffffff,
    #  0x1002378 : init=0xffffffff,
    #  0x1002380 : init=0xffffffff,
    #  0x1002388 : init=0xffffffff,
    #  0x1002390 : init=0xffffffff,
    #  0x1002398 : init=0xffffffff,
    #  0x10023a0 : init=0xffffffff,
    #  0x10023a8 : init=0xffffffff,
    #  0x10023b0 : init=0xffffffff,
    #  0x10023b8 : init=0xffffffff,
    #  0x10023c0 : init=0xffffffff,
    #  0x10023c8 : init=0xffffffff,
    #  0x10023d0 : init=0xffffffff,
    #  0x10023d8 : init=0xffffffff,
    #  0x10023e0 : init=0xffffffff,
    #  0x10023e8 : init=0xffffffff,
    #  0x10023f0 : init=0xffffffff,
    #  0x10023f8 : init=0xffffffff,
    UNKNOWN_INITIAL = 0x100_0000, Register32

    # ** dart-avd: =101_0000=
    # This has its own Device Tree entry. Presumably it behaves as a totally standard
    # DART, though I have not investigated this.

    # ** piodma: =107_0000= (in M3's address space, =4007_0000=)
    # Not investigated much, presumably this region is similar to the other things
    # with "piodma" mentioned in the Device Tree?
    #
    # macOS sets some tunables in this range:
    #
    # *** =+00=: =AVD_PIODMA_APIODMA_CFG=
    # *** =+10=: =AVD_PIODMA_APIODMA_DMACFGMEMSRC=
    # *** =+14=: =AVD_PIODMA_APIODMA_DMACFGMEMDAT=
    # *** =+18=: =AVD_PIODMA_APIODMA_DMACFGMEMDST=
    # *** =+1c=: =AVD_PIODMA_APIODMA_DMACFGPIORD=
    # *** =+20=: =AVD_PIODMA_APIODMA_DMACFGPIOWR=
    #
    PIODMA_PIODMA_APIODMA_CFG = 0x1070000, Register32 # writable:min=0x0,max=0x3
    PIODMA_0004 = 0x1070004, Register32 # init=0x20,
    PIODMA_0008 = 0x1070008, Register32 # writable:min=0x0,max=0x3ff
    PIODMA_000c = 0x107000c, Register32 # init=0x8000000f,
    PIODMA_PIODMA_APIODMA_DMACFGMEMSRC = 0x1070010, Register32 # writable:min=0x0,max=0x7ffffff
    PIODMA_PIODMA_APIODMA_DMACFGMEMDAT = 0x1070014, Register32 # writable:min=0x0,max=0x7ffffff
    PIODMA_PIODMA_APIODMA_DMACFGMEMDST = 0x1070018, Register32 # writable:min=0x0,max=0x7ffffff
    PIODMA_PIODMA_APIODMA_DMACFGMEMRD = 0x107001c, Register32 # writable:min=0x0,max=0x1ffff
    PIODMA_PIODMA_APIODMA_DMACFGMEMWR = 0x1070020, Register32 # writable:min=0x0,max=0x1ffff
    PIODMA_0024 = 0x1070024, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0028 = 0x1070028, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_002c = 0x107002c, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0030 = 0x1070030, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0034 = 0x1070034, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0038 = 0x1070038, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_003c = 0x107003c, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0040 = 0x1070040, Register32 # writable:min=0x0,max=0xfffffffc
    PIODMA_0044 = 0x1070044, Register32 # writable:min=0x0,max=0xffffffff
    PIODMA_0048 = 0x1070048, Register32 # writable:min=0x0,max=0x3ff
    PIODMA_004c = 0x107004c, Register32 # writable:min=0x0,max=0xffffffff
    PIODMA_0050 = 0x1070050, Register32 # writable:min=0x0,max=0x800003ff
    PIODMA_0054 = 0x1070054, Register32 # writable:min=0x0,max=0xffffff7e
    PIODMA_0058 = 0x1070058, Register32 # init=0xbe86c7d, writable:min=0xbeb505b,max=0xbe9dcd2
    PIODMA_005c = 0x107005c, Register32 # init=0xffffff7f,
    PIODMA_006c = 0x107006c, Register32 # init=0x10000,
    PIODMA_0070 = 0x1070070, Register32 # init=0xffffff7f,
    PIODMA_0090 = 0x1070090, Register32 # init=0x180,
    PIODMA_00b4 = 0x10700b4, Register32 # init=0x30000,
    PIODMA_00c4 = 0x10700c4, Register32 # init=0x10000000,
    PIODMA_00c8 = 0x10700c8, Register32 # init=0x1000000,
    PIODMA_00cc = 0x10700cc, Register32 # init=0x1,
    PIODMA_00d0 = 0x10700d0, Register32 # writable:min=0x0,max=0xc0000002
    PIODMA_00d4 = 0x10700d4, Register32 # writable:min=0x0,max=0xffffffff
    PIODMA_00d8 = 0x10700d8, Register32 # writable:min=0x0,max=0xffffff
    PIODMA_00dc = 0x10700dc, Register32 # writable:min=0x0,max=0xffffffff
    PIODMA_00e0 = 0x10700e0, Register32 # writable:min=0x0,max=0xff
    PIODMA_00e4 = 0x10700e4, Register32 # init=0x800000, writable:min=0x800000,max=0x80ffff
    PIODMA_00f0 = 0x10700f0, Register32 # writable:min=0x0,max=0x3f
    PIODMA_00f4 = 0x10700f4, Register32 # writable:min=0x0,max=0x3f
    PIODMA_00f8 = 0x10700f8, Register32 # writable:min=0x0,max=0x3f
    PIODMA_00fc = 0x10700fc, Register32 # writable:min=0x0,max=0x3f
    PIODMA_0100 = 0x1070100, Register32 # writable:min=0x0,max=0x3f
    PIODMA_0104 = 0x1070104, Register32 # writable:min=0x0,max=0x3f
    PIODMA_0108 = 0x1070108, Register32 # writable:min=0x0,max=0x3f
    PIODMA_010c = 0x107010c, Register32 # writable:min=0x0,max=0x3f


    # ** firmware: =108_0000 - 108_ffff== (in M3's address space, =0000 - ffff=)
    # The firmware image is written to (and executed from) here.
    #
    # Contains random data at startup.

    M3_FW = irange(0x108_0000, 0x4000, 4), Register32

    # ** ram: =109_0000 - 109_ffff= (in M3's address space, =1000_0000 - 1000_ffff=)
    # Contains random data at startup.
    #
    # This is where the M3 keeps its non-magic-peripheral-register state.
    #
    # Parts are also used as shared memory with the application processor, notably:
    #
    # *** =+0000 - +0fff=: Log
    # A ring buffer of 32-bit log entries. Hope you enjoy trying to discern a whole sentence worth of meaning from jibberish four-letter words!
    #
    # Frequently contains =FwVn= followed by =0xaa8d2eda=, which is presumably a firmware version code.

    # *** =+1094 - +2834=: I2A (M3->host) command buffers
    # There are 64 buffers, each 0x60 (96) bytes. The M3 writes a command into one of
    # these, then writes its address in the mailbox. The address is of the form
    # =109_xxxx=, i.e. it is an offset from the =adt= peripheral on the host.
    #
    # *** =+2ccc - +2fcc=: A2I (host->M3) command buffers
    # There are 8 buffers, each 0x60 (96) bytes. As above, but in the reverse direction (written by the host).
    #
    # *** =+dae8=: Log message counter
    # Incremented whenever a log message is written. Note that this is an index into an array of 32-bit ints, rather than a byte-level pointer. Also note that it does not wrap around, it keeps incrementing when the ring buffer cycles back to zero.
    #
    # *** =+? - +ffff=: Stack

    M3_RAM = irange(0x109_0000, 0x4000, 4), Register32

    # ** mailbox: =10a_0000= (in M3's addess space, =5001_0000=)
    # This appears similar to the thunderbolt M3 mailbox described in Linux's =drivers/mailbox/apple-mailbox.c=, but in an older form, with 32-bit messages.
    #
    # *** =+1c= and =20=:
    # bitfield with the following layout (actual contents unknown):
    #
    # #+BEGIN_EXAMPLE
    # 0x1c:
    #     +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # bit |31 30 29 28 27|26 25 24 23 22|21 20 19 18 17|16 15 14 13 12|11 10  9  8  7| 6  5  4  3  2| 1  0|
    #     |    H.264 1   |    H.264 0   |    HEVC 3    |    HEVC 2    |    HEVC 1    |    HEVC 0    | ??? |
    #     +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # 0x20:
    #     +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # bit |31 30 29 28 27|26 25 24 23 22|21 20 19 18 17 16 15|14 13 12 11 10| 9  8  7  6  5| 4  3  2  1  0|
    #     |                                                  |      VP9     |    H.264 3   |    H.264 2   |
    #     +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    # #+END_EXAMPLE
    #
    # *** =+48=: IRQ_ENABLE
    # Seemingly as in =apple-mailbox.c=.
    #
    # *** =+4c=: IRQ_ACK
    # Seemingly as in =apple-mailbox.c=, e.g. the host writes =BIT(3)= here to clear the incoming interrupt.
    #
    # *** =+54=: A2I_SEND
    # M3 writes
    #
    # *** =+58=: I2A_RECV
    # Host reads
    #
    # *** =+60=: A2I_SEND
    # Host writes
    #
    # *** =+64=: I2A_RECV
    # M3 reads
    #
    # *** =+90=: Ready
    # Set to 1 when M3 firmware has finished initializing and it is ready to accept mailbox requests
    #

    MAILBOX_00 = 0x10a0000, Register32 # init=0x400,
    MAILBOX_04 = 0x10a0004, Register32 # init=0x16,
    MAILBOX_08 = 0x10a0008, Register32 # writable:min=0x0,max=0xf
    MAILBOX_10 = 0x10a0010, Register32 # writable:min=0x0,max=0x3fff
    MAILBOX_14 = 0x10a0014, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_18 = 0x10a0018, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_1C = 0x10a001c, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_20 = 0x10a0020, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_24 = 0x10a0024, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_28 = 0x10a0028, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_2C = 0x10a002c, Register32 # init=0x3355,
    MAILBOX_48 = 0x10a0048, Register32 # writable:min=0x0,max=0x3ff
    MAILBOX_4C = 0x10a004c, Register32 # init=0x355,
    MAILBOX_50 = 0x10a0050, Register32 # init=0x20000, writable:min=0x20000,max=0x20001
    MAILBOX_A2I_SEND = 0x10a0054, Register32 # init=0xd84a554b,
    MAILBOX_58 = 0x10a0058, Register32 # init=0xd84a554b,
    MAILBOX_5C = 0x10a005c, Register32 # init=0x20000, writable:min=0x20000,max=0x20001
    MAILBOX_60 = 0x10a0060, Register32 # init=0xf35ee748,
    MAILBOX_I2A_RECV = 0x10a0064, Register32 # init=0xf35ee748,
    MAILBOX_68 = 0x10a0068, Register32 # init=0x20000, writable:min=0x20000,max=0x20001
    MAILBOX_6C = 0x10a006c, Register32 # init=0xdcf8ecf9,
    MAILBOX_70 = 0x10a0070, Register32 # init=0xdcf8ecf9,
    MAILBOX_74 = 0x10a0074, Register32 # init=0x20000, writable:min=0x20000,max=0x20001
    MAILBOX_78 = 0x10a0078, Register32 # init=0xfef8d789,
    MAILBOX_7C = 0x10a007c, Register32 # init=0xfef8d789,
    MAILBOX_80 = 0x10a0080, Register32 # writable:min=0x0,max=0x81
    MAILBOX_84 = 0x10a0084, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_88 = 0x10a0088, Register32 # writable:min=0x0,max=0x81
    MAILBOX_8C = 0x10a008c, Register32 # writable:min=0x0,max=0xffffffff
    MAILBOX_90 = 0x10a0090, Register32 # init=0xffffffff,
    MAILBOX_98 = 0x10a0098, Register32 # init=0xffffffff,
    MAILBOX_9C = 0x10a009c, Register32 # init=0xffffffff,


    # ** avd peripherals: =110_0000= (in M3's address space, =4010_0000=)
    # macOS sets a ton of tunables in here:
    #
    # *** =+0008=: AVD_MCTLCONFIG_MODE
    # *** =+1000=: AVD_HVPCONFIG_MODE(0)
    # *** =+1100=: AVD_HVPCONFIG_MODE(1)
    # *** =+1200=: AVD_HVPCONFIG_MODE(2)
    # *** =+1300=: AVD_HVPCONFIG_MODE(3)
    # *** =+1400=: AVD_AVPCONFIG_MODE(0)
    # *** =+1500=: AVD_AVPCONFIG_MODE(1)
    # *** =+1600=: AVD_AVPCONFIG_MODE(2)
    # *** =+1700=: AVD_AVPCONFIG_MODE(3)
    # *** =+1800=: AVD_LVPCONFIG_MODE

    AVD_0000 = 0x1100000, Register32 # init=0x30001,
    AVD_0004 = 0x1100004, Register32 # init=0xf144,
    AVD_MCTLCONFIG_MODE = 0x1100008, Register32 # writable:min=0x0,max=0xe0000001
    AVD_0034 = 0x1100034, Register32 # init=0x80,
    AVD_0038 = 0x1100038, Register32 # init=0x80,
    AVD_003c = 0x110003c, Register32 # init=0x80,
    AVD_0040 = 0x1100040, Register32 # init=0x80,
    AVD_0044 = 0x1100044, Register32 # init=0x80,
    AVD_0048 = 0x1100048, Register32 # init=0x80,
    AVD_004c = 0x110004c, Register32 # init=0x80,
    AVD_0050 = 0x1100050, Register32 # init=0x80,
    AVD_0054 = 0x1100054, Register32 # init=0x80,
    AVD_0058 = 0x1100058, Register32 # init=0x80,
    AVD_0084 = 0x1100084, Register32 # writable:min=0x0,max=0xff
    AVD_0088 = 0x1100088, Register32 # writable:min=0x0,max=0xff
    AVD_008c = 0x110008c, Register32 # writable:min=0x0,max=0xff
    AVD_0090 = 0x1100090, Register32 # writable:min=0x0,max=0xff
    AVD_0094 = 0x1100094, Register32 # writable:min=0x0,max=0xff
    AVD_0098 = 0x1100098, Register32 # writable:min=0x0,max=0xff
    AVD_009c = 0x110009c, Register32 # writable:min=0x0,max=0xff
    AVD_00a0 = 0x11000a0, Register32 # writable:min=0x0,max=0xff
    AVD_00a4 = 0x11000a4, Register32 # writable:min=0x0,max=0xff
    AVD_00a8 = 0x11000a8, Register32 # writable:min=0x0,max=0xff
    AVD_00d4 = 0x11000d4, Register32 # writable:min=0x0,max=0x1
    AVD_00d8 = 0x11000d8, Register32 # writable:min=0x0,max=0x1
    AVD_00dc = 0x11000dc, Register32 # writable:min=0x0,max=0x1
    AVD_00e0 = 0x11000e0, Register32 # writable:min=0x0,max=0x1
    AVD_00e4 = 0x11000e4, Register32 # writable:min=0x0,max=0x1
    AVD_00e8 = 0x11000e8, Register32 # writable:min=0x0,max=0x1
    AVD_00ec = 0x11000ec, Register32 # writable:min=0x0,max=0x1
    AVD_00f0 = 0x11000f0, Register32 # writable:min=0x0,max=0x1
    AVD_00f4 = 0x11000f4, Register32 # writable:min=0x0,max=0x1
    AVD_00f8 = 0x11000f8, Register32 # writable:min=0x0,max=0x1
    AVD_00fc = 0x11000fc, Register32 # writable:min=0x0,max=0x1f
    AVD_0100 = 0x1100100, Register32 # writable:min=0x0,max=0x1f
    AVD_0104 = 0x1100104, Register32 # writable:min=0x0,max=0x1f
    AVD_0108 = 0x1100108, Register32 # writable:min=0x0,max=0x1f
    AVD_010c = 0x110010c, Register32 # writable:min=0x0,max=0x1f
    AVD_0110 = 0x1100110, Register32 # writable:min=0x0,max=0x1f
    AVD_0114 = 0x1100114, Register32 # writable:min=0x0,max=0x1f
    AVD_0118 = 0x1100118, Register32 # writable:min=0x0,max=0x1f
    AVD_011c = 0x110011c, Register32 # writable:min=0x0,max=0x1f
    AVD_0120 = 0x1100120, Register32 # writable:min=0x0,max=0x3f
    AVD_0124 = 0x1100124, Register32 # init=0x9,
    AVD_0128 = 0x1100128, Register32 # init=0x9,
    AVD_012c = 0x110012c, Register32 # init=0x9,
    AVD_0130 = 0x1100130, Register32 # init=0x9,
    AVD_0134 = 0x1100134, Register32 # init=0x9,
    AVD_0138 = 0x1100138, Register32 # init=0x9,
    AVD_013c = 0x110013c, Register32 # init=0x9,
    AVD_0140 = 0x1100140, Register32 # init=0x9,
    AVD_0144 = 0x1100144, Register32 # init=0x9,
    AVD_0148 = 0x1100148, Register32 # init=0x9,
    AVD_014c = 0x110014c, Register32 # writable:min=0x0,max=0x7ff
    AVD_0150 = 0x1100150, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0154 = 0x1100154, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0158 = 0x1100158, Register32 # writable:min=0x0,max=0xfffffff
    AVD_015c = 0x110015c, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0160 = 0x1100160, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0164 = 0x1100164, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0168 = 0x1100168, Register32 # writable:min=0x0,max=0xfffffff
    AVD_016c = 0x110016c, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0170 = 0x1100170, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0174 = 0x1100174, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0178 = 0x1100178, Register32 # writable:min=0x0,max=0xfffffff
    AVD_017c = 0x110017c, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0180 = 0x1100180, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0184 = 0x1100184, Register32 # writable:min=0x0,max=0xfffffff
    AVD_0188 = 0x1100188, Register32 # writable:min=0x0,max=0xfffffff
    AVD_018c = 0x110018c, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_0190 = 0x1100190, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_0194 = 0x1100194, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_0198 = 0x1100198, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_019c = 0x110019c, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01a0 = 0x11001a0, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01a4 = 0x11001a4, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01a8 = 0x11001a8, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01ac = 0x11001ac, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01b0 = 0x11001b0, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01b4 = 0x11001b4, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01b8 = 0x11001b8, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01bc = 0x11001bc, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01c0 = 0x11001c0, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01c4 = 0x11001c4, Register32 # writable:min=0x0,max=0x7ffffe00
    AVD_01c8 = 0x11001c8, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01cc = 0x11001cc, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01d0 = 0x11001d0, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01d4 = 0x11001d4, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01d8 = 0x11001d8, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01dc = 0x11001dc, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01e0 = 0x11001e0, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01e4 = 0x11001e4, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01e8 = 0x11001e8, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01ec = 0x11001ec, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01f0 = 0x11001f0, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01f4 = 0x11001f4, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01f8 = 0x11001f8, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_01fc = 0x11001fc, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0200 = 0x1100200, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0204 = 0x1100204, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0208 = 0x1100208, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_020c = 0x110020c, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0210 = 0x1100210, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0214 = 0x1100214, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0218 = 0x1100218, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_021c = 0x110021c, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0220 = 0x1100220, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0224 = 0x1100224, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0228 = 0x1100228, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_022c = 0x110022c, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0230 = 0x1100230, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0234 = 0x1100234, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0238 = 0x1100238, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_023c = 0x110023c, Register32 # writable:min=0x0,max=0xfffffffc
    AVD_0240 = 0x1100240, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0244 = 0x1100244, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0248 = 0x1100248, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_024c = 0x110024c, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0250 = 0x1100250, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0254 = 0x1100254, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0258 = 0x1100258, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_025c = 0x110025c, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0260 = 0x1100260, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0264 = 0x1100264, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0268 = 0x1100268, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_026c = 0x110026c, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0270 = 0x1100270, Register32 # init=0xf, writable:min=0x0,max=0xf
    AVD_0274 = 0x1100274, Register32 # writable:min=0x0,max=0x3
    AVD_0278 = 0x1100278, Register32 # writable:min=0x0,max=0x3
    AVD_027c = 0x110027c, Register32 # writable:min=0x0,max=0x3
    AVD_0280 = 0x1100280, Register32 # writable:min=0x0,max=0x3
    AVD_0284 = 0x1100284, Register32 # writable:min=0x0,max=0x3
    AVD_0288 = 0x1100288, Register32 # writable:min=0x0,max=0x3
    AVD_028c = 0x110028c, Register32 # writable:min=0x0,max=0x3
    AVD_0290 = 0x1100290, Register32 # writable:min=0x0,max=0x3
    AVD_0294 = 0x1100294, Register32 # writable:min=0x0,max=0x3
    AVD_0298 = 0x1100298, Register32 # writable:min=0x0,max=0x3
    AVD_029c = 0x110029c, Register32 # writable:min=0x0,max=0x3
    AVD_02a0 = 0x11002a0, Register32 # writable:min=0x0,max=0x3
    AVD_02a4 = 0x11002a4, Register32 # writable:min=0x0,max=0x3
    AVD_02a8 = 0x11002a8, Register32 # writable:min=0x0,max=0x3
    AVD_02ac = 0x11002ac, Register32 # writable:min=0x0,max=0x3
    AVD_02b0 = 0x11002b0, Register32 # init=0x1,
    AVD_02f4 = 0x11002f4, Register32 # writable:min=0x0,max=0xffffffff
    AVD_02f8 = 0x11002f8, Register32 # writable:min=0x0,max=0xffffffff
    AVD_0300 = 0x1100300, Register32 # writable:min=0x0,max=0xffffff
    AVD_0304 = 0x1100304, Register32 # writable:min=0x0,max=0x80000fff

    AVD_HVP_CONFIG_MODE = irange(0x1101000, 4, 0x100), Register32 # writable:min=0x0,max=0xc0000000
    AVD_HVP_1C = irange(0x110101c, 4, 0x100), Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_HVP_CONFIG_MODE = irange(0x1101400, 4, 0x100), Register32 # writable:min=0x0,max=0xc0000000
    AVD_HVP_20 = irange(0x1101420, 4, 0x100), Register32 # writable:min=0x0,max=0xc0000000

    AVD_LVP_CONFIG_MODE = 0x1101800, Register32 # writable:min=0x0,max=0xc0000000
    AVD_LVP_04 = 0x1101804, Register32 # init=0x3fc000,
    AVD_LVP_1C = 0x110181c, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    # *** =+4000=: AVD_QTCONFIG_MODE
    # *** =+4100=: AVD_IPMCCONFIG_MODE
    # *** =+4200=: AVD_LFCONFIG_MODE
    # *** =+4300=: AVD_MVCONFIG_MODE
    # *** =+4400=: AVD_TPCONFIG_MODE
    # *** =+4500=: AVD_PCCONFIG_MODE
    # *** =+4600=: AVD_SWRCONFIG_MODE

    AVD_QT_CONFIG_MODE = 0x1104000, Register32 # writable:min=0x0,max=0xc0000000
    AVD_QT_04 = 0x1104004, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_QT_08 = 0x1104008, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_QT_0C = 0x110400c, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_IPM_CONFIG_MODE = 0x1104100, Register32 # writable:min=0x0,max=0xc0000000
    AVD_IPM_04 = 0x1104104, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_LF_CONFIG_MODE = 0x1104200, Register32 # writable:min=0x0,max=0xc0000000
    AVD_LF_04 = 0x1104204, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_LF_08 = 0x1104208, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_LF_0C = 0x110420c, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_MV_CONFIG_MODE = 0x1104300, Register32 # writable:min=0x0,max=0xc0000000
    AVD_MV_04 = 0x1104304, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_MV_08 = 0x1104308, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_MV_0C = 0x110430c, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_TP_CONFIG_MODE = 0x1104400, Register32 # writable:min=0x0,max=0xc0000000
    AVD_TP_04 = 0x1104404, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_TP_08 = 0x1104408, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_PC_CONFIG_MODE = 0x1104500, Register32 # writable:min=0x0,max=0xc0000000
    AVD_PC_04 = 0x1104504, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff
    AVD_PC_08 = 0x1104508, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    AVD_SWR_CONFIG_MODE = 0x1104600, Register32 # writable:min=0x0,max=0xc0000000

    # *** =+c000=: AVD_DMAVPTOP_CLKGATINGEN

    DMAVPTOP_CLKGATINGEN = 0x110c000, Register32 # writable:min=0x0,max=0x1
    DMA_c004 = 0x110c004, Register32 # init=0x5df3, writable:min=0x0,max=0xffff
    DMA_c024 = 0x110c024, Register32 # writable:min=0x0,max=0x1
    DMA_c028 = 0x110c028, Register32 # init=0xffffffff, writable:min=0x0,max=0xffffffff

    # *** =+c080=: AVD_RDDMAHVPBITS_DMACONFIG(0)
    # *** =+c084=: AVD_RDDMAHVPBITS_DMABFRCONFIG(0)
    # *** =+c0c0=: AVD_RDDMAHVPBITS_DMACONFIG(1)
    # *** =+c0c4=: AVD_RDDMAHVPBITS_DMABFRCONFIG(1)
    # *** =+c100=: AVD_RDDMAHVPBITS_DMACONFIG(2)
    # *** =+c104=: AVD_RDDMAHVPBITS_DMABFRCONFIG(2)
    # *** =+c140=: AVD_RDDMAHVPBITS_DMACONFIG(3)
    # *** =+c144=: AVD_RDDMAHVPBITS_DMABFRCONFIG(3)



    # *** =+c180=: AVD_WRDMAHVPINSN_DMACONFIG(0)
    # *** =+c184=: AVD_WRDMAHVPINSN_DMABFRCONFIG(0)
    # *** =+c1c0=: AVD_WRDMAHVPINSN_DMACONFIG(1)
    # *** =+c1c4=: AVD_WRDMAHVPINSN_DMABFRCONFIG(1)
    # *** =+c200=: AVD_WRDMAHVPINSN_DMACONFIG(2)
    # *** =+c204=: AVD_WRDMAHVPINSN_DMABFRCONFIG(2)
    # *** =+c240=: AVD_WRDMAHVPINSN_DMACONFIG(3)
    # *** =+c244=: AVD_WRDMAHVPINSN_DMABFRCONFIG(3)


    # *** =+c280=: AVD_RDDMAAVPBITS_DMACONFIG(0)
    # *** =+c284=: AVD_RDDMAAVPBITS_DMABFRCONFIG(0)
    # *** =+c2c0=: AVD_RDDMAAVPBITS_DMACONFIG(1)
    # *** =+c2c4=: AVD_RDDMAAVPBITS_DMABFRCONFIG(1)
    # *** =+c300=: AVD_RDDMAAVPBITS_DMACONFIG(2)
    # *** =+c304=: AVD_RDDMAAVPBITS_DMABFRCONFIG(2)
    # *** =+c340=: AVD_RDDMAAVPBITS_DMACONFIG(3)
    # *** =+c344=: AVD_RDDMAAVPBITS_DMABFRCONFIG(3)


    # *** =+c380=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(0)
    # *** =+c384=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(0)
    # *** =+c3c0=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(1)
    # *** =+c3c4=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(1)
    # *** =+c400=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(2)
    # *** =+c404=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(2)
    # *** =+c440=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(3)
    # *** =+c444=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(3)
    # *** =+c480=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(4)
    # *** =+c484=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(4)
    # *** =+c4c0=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(5)
    # *** =+c4c4=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(5)
    # *** =+c500=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(6)
    # *** =+c504=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(6)
    # *** =+c540=: AVD_WRDMAAVPABOVEINFO_DMACONFIG(7)
    # *** =+c544=: AVD_WRDMAAVPABOVEINFO_DMABFRCONFIG(7)


    # *** =+c580=: AVD_WRDMAAVPINSN_DMACONFIG(0)
    # *** =+c584=: AVD_WRDMAAVPINSN_DMABFRCONFIG(0)
    # *** =+c5c0=: AVD_WRDMAAVPINSN_DMACONFIG(1)
    # *** =+c5c4=: AVD_WRDMAAVPINSN_DMABFRCONFIG(1)
    # *** =+c600=: AVD_WRDMAAVPINSN_DMACONFIG(2)
    # *** =+c604=: AVD_WRDMAAVPINSN_DMABFRCONFIG(2)
    # *** =+c640=: AVD_WRDMAAVPINSN_DMACONFIG(3)
    # *** =+c644=: AVD_WRDMAAVPINSN_DMABFRCONFIG(3)


    # *** =+c680=: AVD_RDDMALVPBITS_DMACONFIG
    # *** =+c684=: AVD_RDDMALVPBITS_DMABFRCONFIG






    # *** =+e000=: AVD_DMAINTRATOP_CLKGATINGEN


    DMA_INTRATOP_CLKGATINGEN = 0x110e000, Register32 # writable:min=0x0,max=0x1
    DMA_INTRATOP_04 = 0x110e004, Register32 # init=0x5df3, writable:min=0x0,max=0xffff


    # *** =+e4c0=: AVD_WRDMAZIP_DMACONFIG(0)
    # *** =+e4c8=: AVD_WRDMAZIP_CMPBFRCONFIG(0)
    # *** =+e4cc=: AVD_WRDMAZIP_HDRBFRCONFIG(0)
    #
    # *** =+e500=: AVD_WRDMAZIP_DMACONFIG(1)
    # *** =+e508=: AVD_WRDMAZIP_CMPBFRCONFIG(1)
    # *** =+e50c=: AVD_WRDMAZIP_HDRBFRCONFIG(1)
    #
    # *** =+e800=: AVD_DMAINTERTOP_CLKGATINGEN


    DMA_ZIP_WR_CONFIG_0 = 0x110e4c0, Register32 # init=0x71, writable:min=0x11,max=0xc01ffffd
    DMA_ZIP_WR_04_0 = 0x110e4c4, Register32 # init=0x1000003, writable:min=0x0,max=0xffff0007
    DMA_ZIP_WR_CMPBFR_CONFIG_0 = 0x110e4c8, Register32 # init=0xa8e0ccf, writable:min=0x0,max=0xfff0fff
    DMA_ZIP_WR_HDRBFR_CONFIG_0 = 0x110e4cc, Register32 # init=0x7df0dd8, writable:min=0x0,max=0xfff0fff
    DMA_ZIP_WR_HDRBFR_18_0 = 0x110e4d8, Register32 # writable:min=0x0,max=0x3ff01ff
    DMA_ZIP_WR_HDRBFR_28_0 = 0x110e4e8, Register32 # init=0x391d69fd, writable:min=0x0,max=0xffffffff

    DMA_ZIP_WR_CONFIG_1 = 0x110e500, Register32 # init=0x71, writable:min=0x11,max=0xc01ffffd
    DMA_ZIP_WR_14_0 = 0x110e504, Register32 # init=0x1000003, writable:min=0x0,max=0xffff0007
    DMA_ZIP_WR_CMPBFR_CONFIG_1 = 0x110e508, Register32 # init=0xa8e0ccf, writable:min=0x0,max=0xfff0fff
    DMA_ZIP_WR_HDRBFR_CONFIG_1 = 0x110e50c, Register32 # init=0x7df0dd8, writable:min=0x0,max=0xfff0fff
    DMA_ZIP_WR_HDRBFR_18_1 = 0x110e518, Register32 # writable:min=0x0,max=0x3ff01ff
    DMA_ZIP_WR_HDRBFR_28_1 = 0x110e528, Register32 # init=0x391d69fd, writable:min=0x0,max=0xffffffff

    DMA_INTERTOP_CLKGATINGEN = 0x110e800, Register32 # writable:min=0x0,max=0x1
    DMA_INTERTOP_04 = 0x110e804, Register32 # init=0x5df3, writable:min=0x0,max=0xffff



    # *** =+e980=: AVD_RDDMAZIP_DMACONFIG

    DMA_ZIP_RD_CONFIG = 0x110e980, Register32 # init=0x3, writable:min=0x0,max=0xe0ff0007
    DMA_ZIP_RD_04 = 0x110e984, Register32 # init=0x100, writable:min=0x0,max=0x1ff
    DMA_ZIP_RD_08 = 0x110e988, Register32 # init=0x30, writable:min=0x0,max=0x1ff

    DMA_E9A8 = 0x110e9a8, Register32 # init=0x196ed5ea, writable:min=0x0,max=0xffffffff




dma_block_array(AvdRegs, "HVP_RD_BITS", 0x110_c080, 4)
dma_block_array(AvdRegs, "HVP_WR_INSN", 0x110_c180, 4)
dma_block_array(AvdRegs, "AVP_RD_BITS", 0x110_c280, 4)
dma_block_array(AvdRegs, "AVP_WR_AVP_ABOVEINFO", 0x110_c380, 8)
dma_block_array(AvdRegs, "AVP_WR_AVP_INSN", 0x110_c580, 4)
dma_block(AvdRegs, "LVP_RD_BITS", 0x110_c680)
dma_block(AvdRegs, "LVP_WR_ABOVEINFO", 0x110_c6c0)
dma_block(AvdRegs, "LVP_RD_ABOVEINFO", 0x110_c700)
dma_block(AvdRegs, "LVP_WR_SEG", 0x110_c740)
dma_block(AvdRegs, "LVP_RD_SEG", 0x110_c780)
dma_block(AvdRegs, "LVP_WR_COLO", 0x110_c7c0)
dma_block(AvdRegs, "LVP_RD_COLO", 0x110_c800)
dma_block(AvdRegs, "LVP_WR_STATE", 0x110_c840)
dma_block(AvdRegs, "LVP_RD_STATE", 0x110_c880)
dma_block(AvdRegs, "LVP_WR_INSN", 0x110_c8c0)
dma_block_array(AvdRegs, "DMAPIPEINSN_RD", 0x110_c900, 4)
dma_block(AvdRegs, "INTRA_IP_WR_ABOVEPIX", 0x110_e080)
dma_block(AvdRegs, "INTRA_IP_RD_ABOVEPIX", 0x110_e0c0)
dma_block(AvdRegs, "INTRA_LF_WR_ABOVEPIX", 0x110_e100)
dma_block(AvdRegs, "INTRA_LF_RD_ABOVEPIX", 0x110_e140)
dma_block(AvdRegs, "INTRA_LF_WR_ABOVEINFO", 0x110_e180)
dma_block(AvdRegs, "INTRA_LF_RD_ABOVEINFO", 0x110_e1c0)
dma_block(AvdRegs, "INTRA_LF_WR_LEFTPIX", 0x110_e200)
dma_block(AvdRegs, "INTRA_LF_RD_LEFTPIX", 0x110_e240)
dma_block(AvdRegs, "INTRA_LF_WR_LEFTINFO", 0x110_e280)
dma_block(AvdRegs, "INTRA_LF_RD_LEFTINFO", 0x110_e2c0)
dma_block(AvdRegs, "INTRA_SW_WR_PIX", 0x110_e300)
dma_block(AvdRegs, "INTRA_SW_WR_LEFT", 0x110_e340)
dma_block(AvdRegs, "INTRA_SW_RD_LEFT", 0x110_e380)
dma_block(AvdRegs, "INTRA_AZ_WR_ABOVEPIX", 0x110_e3c0)
dma_block(AvdRegs, "INTRA_AZ_RD_ABOVEPIX", 0x110_e400)
dma_block(AvdRegs, "INTRA_AZ_WR_LEFTPIX", 0x110_e440)
dma_block(AvdRegs, "INTRA_AZ_RD_LEFTPIX", 0x110_e480)
dma_block(AvdRegs, "INTER_MV_WR_ABOVEINFO", 0x110_e880)
dma_block(AvdRegs, "INTER_MV_RD_ABOVEINFO", 0x110_e8c0)
dma_block(AvdRegs, "INTER_MV_WR_COLO", 0x110_e900)
dma_block(AvdRegs, "INTER_MV_RD_COLO", 0x110_e940)

    # TODO
    # wrapctrl: =140_0000= (in M3's address space, =4040_0000=)
    # One tunable here:
    #
    # *** =+0018=: AVDWRAPCTRL_AVDCTRL_CLOCKGATEENABLE

def apply_avd_tunables(p, base, data):
    for addr, name, mask, val in struct.iter_unpack("<Q64sII", data):
        current = p.read32(base + addr)
        ignored = current & ~mask
        new = ignored | (val & mask)
        print("{} {} {} {}: read {} writing {}", hex(addr), name, hex(mask), hex(val), hex(current), hex(new))
        p.write32(base + addr, new)
