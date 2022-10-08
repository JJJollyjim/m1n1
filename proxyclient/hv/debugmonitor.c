#include <stdint.h>

typedef struct __attribute__((packed)) ContextStateFrame {
  uint32_t r0;
  uint32_t r1;
  uint32_t r2;
  uint32_t r3;
  uint32_t r12;
  uint32_t lr;
  uint32_t return_address;
  uint32_t xpsr;
} sContextStateFrame;


__attribute__((naked))
void _start(void) {
  __asm volatile(
      "tst lr, #4 \n"
      "ite eq \n"
      "mrseq r0, msp \n"
      "mrsne r0, psp \n"
      "b debug_monitor_handler_c \n");
}


void debug_monitor_handler_c(sContextStateFrame *frame) {
    volatile uint32_t *demcr = (uint32_t *)0xE000EDFC;

    volatile uint32_t *dfsr = (uint32_t *)0xE000ED30;

    /* volatile uint32_t *function0 = (uint32_t *)0xe0001028; */
    /* volatile uint32_t *pcsr = (uint32_t *)0xe000101c; */
    volatile uint32_t *logbuf = (uint32_t *)0x10000f00;

    /* // We're unfortunately triggered quite late :( */
    /* // Given the following code, with a match on addr==69: */
    /* // */
    /* // *68 = 1; // this occurs */
    /* // *69 = 1; // this occurs */
    /* // *70 = 1; // this occurs */
    /* // *71 = 1; // this hasn't yet occured, and is our return address from the isr. */


    /* logbuf[0] = 0xdeb; */
    /* logbuf[1] = frame->return_address; */

    uint16_t hw1 = *(uint16_t*)frame->return_address;


    if (frame->return_address == 0x3788) {
        if ((hw1 & 0b1111100000000000) == 0b1110000000000000) {
            // 16-bit unconditional branch
        } else if ((hw1 & 0b1110000000000000) == 0b1110000000000000) {
            // 32-bit instruction

            uint16_t hw2 = *(uint16_t*)frame->return_address;

            uint16_t L = (hw1 >> 4) & 1;

            if (hw1 >> (16-7) == 0b1111100) {
                logbuf[0] = 0x1515;
                // Load and store single data item, memory hints
                // 00003788  41f82900   str     r0, [r1, r9, lsl #2]
                //          hw1 f841 hw2 0029
                uint16_t Rn = hw1 & 0xf;
                uint16_t Rt = (hw2 >> 12) & 0xf;

                logbuf[0] = 0xdeb;
                logbuf[1] = *(uint32_t*)frame->return_address;
                logbuf[2] = Rn;
                logbuf[3] = Rt;
            }
        } else {
            // 16-bit instruction

        }
    }

    /* uint16_t hw2 = *(uint16_t*)(frame->return_address+2); */



    /* if (frame->return_address > 0x63b8 && frame->return_address < 0x778c) { */
    /* logbuf[0] = 0xdeb; */
    /* logbuf[1] = frame->return_address; */
    /* } */
    /* logbuf[1] = *demcr; */
    /* logbuf[2] = *dfsr; */
    /* /\* logbuf[3] = *function0; *\/ */
    /* /\* logbuf[4] = *function0; *\/ */
    /* logbuf[5] = frame->r0; */
    /* logbuf[6] = frame->r1; */
    /* logbuf[7] = frame->r2; */
    /* logbuf[8] = frame->r3; */
    /* logbuf[9] = frame->r12; */
    /* logbuf[10] = frame->lr; */
    /* logbuf[11] = frame->return_address; */
    /* logbuf[12] = frame->xpsr; */
    /* logbuf[13] = *(uint16_t*)frame->return_address; */
    /* logbuf[14] = *pcsr; */

    const uint32_t demcr_single_step_mask = (1 << 18);

    const uint32_t dfsr_bkpt_evt_bitmask = (1 << 1);
    const uint32_t dfsr_halt_evt_bitmask = (1 << 0);
    const uint8_t is_bkpt_dbg_evt = (*dfsr & dfsr_bkpt_evt_bitmask);
    const uint8_t is_halt_dbg_evt = (*dfsr & dfsr_halt_evt_bitmask);

    if (is_bkpt_dbg_evt) {
        // advance past breakpoint instruction
        frame->return_address += 2;
        // single-step to the next instruction
        // This will cause a DebugMonitor interrupt to fire
        // once we return from the exception and a single
        // instruction has been executed. The HALTED bit
        // will be set in the DFSR when this happens.
        *demcr |= (demcr_single_step_mask);

        // We have serviced the breakpoint event so clear mask
        *dfsr = dfsr_bkpt_evt_bitmask;
    } else if (is_halt_dbg_evt) {
        /* if (s_debug_state != kDebugState_SingleStep) { */
        /*     *demcr &= ~(demcr_single_step_mask); */
        /* } */

        // We have serviced the single step event so clear mask
        *dfsr = dfsr_halt_evt_bitmask;
    }
}
