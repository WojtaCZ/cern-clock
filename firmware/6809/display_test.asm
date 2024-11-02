; Base adresses for all peripherals

ROM_BASE equ $F000
RESET_VECTOR equ $0FFE
DISP2_BASE equ $E000
DISP1_BASE equ $D000
DISCRIM_BASE equ $C000
REG_BASE equ $B000
FIFO_BASE equ $A000
RAM_BASE equ $9000
ZZZ_BASE equ $8000

; Test character of "0" is used
TESTCHAR equ $30
	
	org ROM_BASE
init:
	; Load the test char into register A
	clra
	lda #TESTCHAR

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

	ldx #0000

loop:
	jmp loop
	
	org RESET_VECTOR
	fdb init
