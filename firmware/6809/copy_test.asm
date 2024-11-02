; Base adresses for all peripherals
RESET_VECTOR equ $FFFE
ROM_BASE equ $F000
DISP2_BASE equ $E000
DISP1_BASE equ $D000
DISCRIM_BASE equ $C000
REG_BASE equ $B000
FIFO_BASE equ $A000
RAM_BASE equ $9000
ZZZ_BASE equ $8000

; Place the init function at the base of the ROM memor
    org ROM_BASE
init:
    ; Blank out all the displays
    clra
    lda #32 

    ; Load the DISP1 base into index register X
	ldx #DISP1_BASE

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

    ldx #FIFO_BASE
    ldy #DISP1_BASE

    lda ,X
    sta ,Y
loop:
    jmp loop



; Place the init function address at the origin of reset vector
    org RESET_VECTOR
    fdb init
