#!/usr/bin/env python3
from m1n1.trace import Tracer
from m1n1.trace.dart8110 import DART8110Tracer
from m1n1.hw.avd import *
from m1n1.utils import *
import struct
import array

p.pmgr_adt_clocks_enable('/arm-io/dart-avd0')

dart0_tracer = DART8110Tracer(hv, "/arm-io/dart-avd0", verbose=3)
dart0_tracer.start()
print(dart0_tracer)

MESSAGE_TYPES = { 0: "Start Session", 1: "Decode Frame", 2: "Stop Session", 5: "Abort Decode", 6: "Set Property" } # perhaps 4 in reply is finished decoding?

class AvdTracer(Tracer):
    def __init__(self, hv, dev, dart_tracer):
        super().__init__(hv)
        self.dev = hv.adt[dev]
        self.base = self.dev.get_reg(0)[0]
        self.dart = dart_tracer.dart
        self.message_counter = 0

    def dump_region(self, name, stream, assumed_maximum):
        f = open(name,  "wb")
        f.truncate(assumed_maximum)

        for addr in range(0, assumed_maximum, 0x4000):
            try:
                data = self.dart.ioread(stream, addr, 0x4000)
                f.seek(addr)
                f.write(data)
            except Exception:
                pass

    def dump_everything(self):
        self.dump_region("dump_%04d_cool_zone" % self.message_counter, 1, 0xbc_0000)
        self.dump_region("dump_%04d_data" % self.message_counter, 0, 0x400_0000)

    def dump_16b8s(self):
        f=open("dump_%04d_16dbs" % self.message_counter, "wb")
        d = array.array("L")
        for i in range(0x109_3000, 0x109_3094 + (0x16b8*8) + 0x94, 4): # todo actual start and end??
            d.append(p.read32(self.base + i))
        f.write(d.tobytes())

    def evt_rw(self, evt):
        if evt.flags.WRITE and evt.addr == self.base + 0x10a0054:
            self.log(f"send msg@{hex(evt.data)} id={self.message_counter}")

            first_word = p.read32(evt.data + self.base)
            self.log("    -> MESSAGE TYPE: {}".format(MESSAGE_TYPES[first_word & 0b11111]))

            for i in range(24):
                self.log("    -> msg[{}]: {}".format(hex(i*4), hex(p.read32(evt.data + i*4 + self.base))))

            self.dump_everything()
            self.dump_16b8s()

            self.log("")

        elif not evt.flags.WRITE and evt.addr == self.base + 0x10a0064:
            self.log(f"recv msg@{hex(evt.data)} id={self.message_counter}")

            for i in range(20):
                self.log("    <- msg[{}]: {}".format(hex(i*4), hex(p.read32(evt.data + i*4 + self.base))))

            self.dump_everything()
            self.dump_16b8s()

            self.log("")
        else:
            self.log(f"weird event {evt}")

        self.message_counter += 1

    def start(self):
        self.hv.clear_tracers(self.ident)

        self.trace(self.base + 0x10a0054, 0x4, TraceMode.SYNC)
        self.trace(self.base + 0x10a0064, 0x4, TraceMode.SYNC)

AvdTracer = AvdTracer._reloadcls() # shrug, copied from prores, necessary?

p.pmgr_adt_clocks_enable('/arm-io/avd0')

tracer = AvdTracer(hv, '/arm-io/avd0', dart0_tracer)
tracer.start()
print(tracer)
