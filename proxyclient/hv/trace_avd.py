from m1n1.trace import ADTDevTracer
from m1n1.trace.dart8110 import DART8110Tracer
from m1n1.hw.avd import *
from m1n1.utils import *
import struct

p.pmgr_adt_clocks_enable('/arm-io/dart-avd0')

dart0_tracer = DART8110Tracer(hv, "/arm-io/dart-avd0", verbose=3)
dart0_tracer.start()
print(dart0_tracer)

class AvdTracer(ADTDevTracer):
    # DEFAULT_MODE = TraceMode.SYNC
    DEFAULT_MODE = TraceMode.ASYNC # TODO
    REGMAPS = [AvdRegs]
    NAMES = ['avd']

    def __init__(self, hv, devpath, dart_tracer):
        super().__init__(hv, devpath, verbose=2)
        self.dart_tracer = dart_tracer

        pass

    # BULK_PREVIOUS = {'r_M3_RAM': 0, 'w_M3_RAM': 0, 'r_M3_FW': 0, 'w_M3_FW': 0 }
    # BULK_COUNT = {'r_M3_RAM': 0, 'w_M3_RAM': 0, 'r_M3_FW': 0, 'w_M3_FW': 0 }

    # def debounce(self, name, op, value, index):
    #     if index == self.BULK_PREVIOUS[name] + 1:
    #         self.BULK_COUNT[name] += 1
    #     else:
    #         self.BULK_COUNT[name] = 0

    #     if self.BULK_COUNT[name] < 50:
    #         s = name[2:] + f"[{index}] = {value!s}"
    #         self.log(f"MMIO: " + op + "  " + s)

    #     self.BULK_PREVIOUS[name] = index

    # def r_M3_RAM(self, value, index):
    #     self.debounce('r_M3_RAM', 'R.4', value, index)

    # def w_M3_RAM(self, value, index):
    #     self.debounce('w_M3_RAM', 'W.4', value, index)

    # def r_M3_FW(self, value, index):
    #     self.debounce('r_M3_FW', 'R.4', value, index)

    # def w_M3_FW(self, value, index):
    #     self.debounce('w_M3_FW', 'W.4', value, index)

    # def w_MAILBOX_48(self, value):
    #     self.log("W.4 MAILBOX_48 = {}".format(value))
    #     self.dart_tracer.dart.dump_all()

    # def w_MAILBOX_A2I_SEND(self, value):
    #     self.log(f"mailbox send @ {value!s}")
    #     base_addr = next(iter(self.regmaps.keys()))
    #     for i in range(24):
    #         self.log("    -> msg[{}]: {}".format(hex(i*4), hex(p.read32(value.value + i*4 + base_addr))))

    #     # first_word = p.read32(value.value + 0 + base_addr)

    #     # if first_word & 7 != 1:
    #     #     self.log("    not a message with a cool zone pointer ({})".format(first_word & 7))
    #     # else:
    #     #     cool_zone_ptr = p.read32(value.value + 8 + base_addr)

    #     #     self.log("    send cool zone dump: {}".format(self.dart_tracer.dart.ioread(1, cool_zone_ptr, 0xb8000).hex()))

    # def r_MAILBOX_I2A_RECV(self, value):
    #     self.log(f"mailbox recv @ {value!s}")
    #     base_addr = next(iter(self.regmaps.keys()))
    #     for i in range(20):
    #         self.log("    <- msg[{}]: {}".format(hex(i*4), hex(p.read32(value.value + i*4 + base_addr))))

    #     # first_word = p.read32(value.value + 0 + base_addr)

    #     # if first_word & 7 != 1:
    #     #     self.log("    not a message with a cool zone pointer ({})".format(first_word & 7))
    #     # else:
    #     #     cool_zone_ptr = p.read32(value.value + 8 + base_addr)

    #     #     self.log("    recv cool zone dump: {}".format(self.dart_tracer.dart.ioread(1, cool_zone_ptr, 0xb8000).hex()))

AvdTracer = AvdTracer._reloadcls() # shrug, copied from prores, necessary?

p.pmgr_adt_clocks_enable('/arm-io/avd0')

tracer = AvdTracer(hv, '/arm-io/avd0', dart0_tracer)
tracer.start()
print(tracer)
