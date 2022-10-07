.section .text, "ax" @progbits

.cpu cortex-m3
.syntax unified
.thumb

.global _start
_start:
    movw r0, #0x0ff0
    movt r0, #0x1000
    mov r1, #0x69696969
    str r1, [r0]
    mov r0, ORIGINIT             // real start
    bx r0
