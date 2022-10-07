.section .text, "ax" @progbits

.cpu cortex-m3
.syntax unified
.thumb

.global _start
_start:
    movw r0, #0x0ff0            // say hi
    movt r0, #0x1000
    mov r1, #0x69696969
    str r1, [r0]

    movw r0, #0xEDFC             // enable debugmonitor and DWT
    movt r0, #0xE000
    movw r1, #0x0000
    movt r1, #0x0101
    str r1, [r0]

    mov r0, ORIGINIT            // real start
    bx r0
