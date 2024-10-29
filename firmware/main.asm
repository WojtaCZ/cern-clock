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

loop:

; Write the index of the display to be written to FIFO byte 0
lda #1
sta FIFO_BASE

; Now, wait for it to be zeroed out by the RPI - this serves as a confirmation that the index has been read
zerowait_disp1:
    lda FIFO_BASE
    bne zerowait_disp1

; Wait for the RPI to fill the fifo with data
nonzerowait_disp1:
    lda FIFO_BASE
    beq zerowait_disp1

; Copy the contents of the FIFO to the first display
lda FIFO_BASE+3
sta DISP1_BASE+3

lda FIFO_BASE+2
sta DISP1_BASE+2

lda FIFO_BASE+1
sta DISP1_BASE+1

lda FIFO_BASE
sta DISP1_BASE

; Write the index of the display to be written to FIFO byte 0
lda #2
sta FIFO_BASE

; Now, wait for it to be zeroed out
zerowait_disp2:
    lda FIFO_BASE
    bne zerowait_disp2

; Wait for the RPI to fill the fifo with data
nonzerowait_disp2:
    lda FIFO_BASE
    beq zerowait_disp2

; Copy the contents of the FIFO to the second display
lda FIFO_BASE+3
sta DISP2_BASE+3

lda FIFO_BASE+2
sta DISP2_BASE+2

lda FIFO_BASE+1
sta DISP2_BASE+1

lda FIFO_BASE
sta DISP2_BASE

; Jump back to the beginning
jmp loop



; Place the init function address at the origin of reset vector
RESET_VECTOR equ $FFFE
org RESET_VECTOR
fdb init
