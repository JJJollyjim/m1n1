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
    volatile uint32_t *function0 = (uint32_t *)0xe0001028;
    volatile uint32_t *pcsr = (uint32_t *)0xe000101c;
    volatile uint32_t *logbuf = (uint32_t *)0x10000f00;

    // We're unfortunately triggered quite late :(
    // Given the following code, with a match on addr==69:
    //
    // *68 = 1; // this occurs
    // *69 = 1; // this occurs
    // *70 = 1; // this occurs
    // *71 = 1; // this hasn't yet occured, and is our return address from the isr.

    logbuf[0] = 0xdeb;
    logbuf[1] = *demcr;
    logbuf[2] = *dfsr;
    logbuf[3] = *function0;
    logbuf[4] = *function0;
    logbuf[5] = frame->r0;
    logbuf[6] = frame->r1;
    logbuf[7] = frame->r2;
    logbuf[8] = frame->r3;
    logbuf[9] = frame->r12;
    logbuf[10] = frame->lr;
    logbuf[11] = frame->return_address;
    logbuf[12] = frame->xpsr;
    logbuf[13] = *(uint16_t*)frame->return_address;
    logbuf[14] = *pcsr;

    *dfsr = 0;
}
