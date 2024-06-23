; Base adresses for all peripherals
ROM_BASE equ $F000
DISP2_BASE equ $E000
DISP1_BASE equ $D000
DISCRIM_BASE equ $C000
REG_BASE equ $B000
FIFO_BASE equ $A000
RAM_BASE equ $9000
ZZZ_BASE equ $8000

; Test character of "0" is used
TESTCHAR equ $30

; Place the init function at the base of the ROM memor
org ROM_BASE
init:
 ; No need to init anything

main:

; Load the DISP1 base into index register X
ldx #DISP1_BASE
; Load the test char into register A
lda #TESTCHAR
; Load the test characters into the first display
sta ,X+
sta ,X+
sta ,X+
sta ,X+

; Load the DISP2 base into index register X
ldx #DISP2_BASE
; Load the test characters into the second display
sta ,X+
sta ,X+
sta ,X+
sta ,X+

loop:
; Just loop endlessly and do nothing
nop
jmp loop



; Place the init function address at the origin of reset vector
RESET_VECTOR equ $FFFE
org RESET_VECTOR
fdb init
