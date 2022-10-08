from m1n1.trace import Tracer
from m1n1.trace.dart8110 import DART8110Tracer
from m1n1.hw.avd import *
from m1n1.utils import *
import subprocess
import pathlib
import struct

def read_by_32(addr, len_):
    data = b''
    for i in range(0, len_, 4):
        data += struct.pack("<I", p.read32(addr + i))
    return data

class AVDFirmwareDumper(Tracer):
    DEFAULT_MODE = TraceMode.SYNC
    def __init__(self, hv, devpath, verbose=False):
        super().__init__(hv, verbose=verbose, ident=type(self).__name__ + "@" + devpath)
        self.dev = hv.adt[devpath]
        self.firmware_buffer = bytearray(0x10000)
    def start(self):
        avd_base, _ = self.dev.get_reg(0)
        self.avd_base = avd_base
        self.trace(avd_base + 0x108_0000, 0x10000, mode=self.DEFAULT_MODE, prefix="CM3CODE")
    def evt_rw(self, evt, regmap=None, prefix=None):
        if evt.flags.WRITE:
            off_start = evt.addr - (self.avd_base + 0x108_0000)
            self.firmware_buffer[off_start:off_start+4] = evt.data.to_bytes(4, "little")
            if off_start == 0x1_0000 - 4:
                print("reached the end, writing buffer")
                open("firmware_dump.bin", "wb").write(self.firmware_buffer)
                self.stop()

class AVDFirmwareSaboteur(Tracer):
    DEFAULT_MODE = TraceMode.HOOK
    def __init__(self, hv, devpath, verbose=False):
        super().__init__(hv, verbose=verbose, ident=type(self).__name__ + "@" + devpath)
        self.dev = hv.adt[devpath]
        self.firmware_buffer = open("patched_firmware.bin", "rb").read()
    def start(self):
        avd_base, _ = self.dev.get_reg(0)
        self.avd_base = avd_base
        self.trace(avd_base + 0x108_0000, 0x100, mode=self.DEFAULT_MODE, prefix="CM3CODE")
        self.trace(avd_base + 0x108_9900, 0x2000, mode=self.DEFAULT_MODE, prefix="CM3CODE")
    def hook_w(self, addr, val, width, **kwargs):
        off_start = addr - (self.avd_base + 0x108_0000)

        if off_start == 0:
            self.firmware_buffer = open("patched_firmware.bin", "rb").read()

        assert width == 32
        patched_val = int.from_bytes(self.firmware_buffer[off_start:(off_start+4)], "little")
        if val != patched_val:
            print(f"Firmware difference at {hex(off_start)}: {hex(val), hex(patched_val)}")
        super().hook_w(addr, patched_val, width, **kwargs)

class AVDTracer(Tracer):
    DEFAULT_MODE = TraceMode.SYNC

    def __init__(self, hv, devpath, dart_tracer, verbose=False):
        super().__init__(hv, verbose=verbose, ident=type(self).__name__ + "@" + devpath)
        self.dev = hv.adt[devpath]
        self.dart_tracer = dart_tracer

    def start(self):
        avd_base, _ = self.dev.get_reg(0)
        self.avd_base = avd_base
        self.trace_regmap(avd_base + 0x000_0000, 0x4000, AVDThing0_0000Regs, name="Thing_0x000_0000", prefix="Thing_0x000_0000")
        self.trace_regmap(avd_base + 0x000_8000, 0x4000, AVDThing0_8000Regs, name="Thing_0x000_8000", prefix="Thing_0x000_8000")
        self.trace_regmap(avd_base + 0x100_0000, 0x4000, AVDThing100Regs, name="Thing_0x100_0000", prefix="Thing_0x100_0000")
        self.trace_regmap(avd_base + 0x102_0000, 0x4000, AVDThing102Regs, name="Thing_0x102_0000", prefix="Thing_0x102_0000")
        self.trace_regmap(avd_base + 0x107_0000, 0x4000, AVDPIODMARegs, name="PIODMA", prefix="PIODMA")
        # self.trace(avd_base + 0x108_0000, 0x10000, mode=self.DEFAULT_MODE, prefix="CM3CODE")
        # self.trace(avd_base + 0x109_0000, 0x10000, mode=self.DEFAULT_MODE, prefix="CM3DATA")
        self.trace_regmap(avd_base + 0x10a_0000, 0x4000, AVDCM3CtrlRegs, name="CM3Ctrl", prefix="CM3Ctrl")
        self.trace_regmap(avd_base + 0x110_0000, 0x8000, AVDConfigRegs, name="CTRL", prefix="CTRL")
        self.trace_regmap(avd_base + 0x110_c000, 0x4000, AVDDMAThingyRegs, name="DMA_THINGY", prefix="DMA_THINGY")
        self.trace_regmap(avd_base + 0x140_0000, 0x4000, AVDWrapCtrlRegs, name="WRAP_CTRL", prefix="WRAP_CTRL")
        self.dart_tracer.start()

    # def w_CM3Ctrl_START_RELATED_THING(self, val):
    #     print(val)
    #     self.dart_tracer.dart.dump_all()

    def evt_rw(self, *args, **kwargs):
        print(f"~~~ DebugMonitor says: {hex(p.read32(self.avd_base+0x109_0000+0xff0))} {hex(p.read32(self.avd_base+0x109_0000+0xf00))} {hex(p.read32(self.avd_base+0x109_0000+0xf04))} {hex(p.read32(self.avd_base+0x109_0000+0xf08))} {hex(p.read32(self.avd_base+0x109_0000+0xf0c))} ~~~")

        super().evt_rw(*args, **kwargs)


    def w_CM3Ctrl_MAILBOX0_SUBMIT(self, val):
        # print("w", val)
        val = int(val)
        print("~~~~~ SUBMIT COMMAND @ {val:08X} ~~~~~")
        if val >= 0x109_0000 and val < 0x10a_0000:
            data = read_by_32(self.avd_base + val, 0x60)
            chexdump(data)

    def r_CM3Ctrl_MAILBOX1_RETRIEVE(self, val):
        # print("r", val)
        val = int(val)
        print("~~~~~ READ REPLY @ {val:08X} ~~~~~")
        if val >= 0x109_0000 and val < 0x10a_0000:
            data = read_by_32(self.avd_base + val, 0x60)
            chexdump(data)

AVDTracer = AVDTracer._reloadcls()

p.pmgr_adt_clocks_enable('/arm-io/dart-avd0')
p.pmgr_adt_clocks_enable('/arm-io/avd0')

dart_tracer = DART8110Tracer(hv, "/arm-io/dart-avd0", verbose=1)
print(dart_tracer)
tracer = AVDTracer(hv, '/arm-io/avd0', dart_tracer, verbose=3)
tracer.start()
print(tracer)

# fwdump = AVDFirmwareDumper(hv, '/arm-io/avd0')
# fwdump.start()
# print(fwdump)

fwsab = AVDFirmwareSaboteur(hv, '/arm-io/avd0')
fwsab.start()
print(fwsab)
