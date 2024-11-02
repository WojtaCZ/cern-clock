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

loop:

    ; Write the index of the display to be written to FIFO byte 0
    clra
    lda #1
    ldx #FIFO_BASE
    sta ,X

; Now, wait for it to be zeroed out by the RPI - this serves as a confirmation that the index has been read
    ldx #FIFO_BASE
zerowait_disp1:
    lda ,X
    bne zerowait_disp1

; Wait for the RPI to fill the fifo with data
    ldx #FIFO_BASE
nonzerowait_disp1:
    lda ,X
    beq nonzerowait_disp1

    ; Copy the contents of the FIFO to the first display
    ldx #FIFO_BASE
    ldy #DISP1_BASE

    lda 3,X
    sta 3,Y

    lda 2,X
    sta 2,Y

    lda 1,X
    sta 1,Y

    lda ,X
    sta ,Y

    ; Write the index of the display to be written to FIFO byte 0
    clra
    lda #2
    ldx #FIFO_BASE
    sta ,X

; Now, wait for it to be zeroed out
    ldx #FIFO_BASE
zerowait_disp2:
    lda ,X
    bne zerowait_disp2

; Wait for the RPI to fill the fifo with data
    ldx #FIFO_BASE
nonzerowait_disp2:
    lda ,X
    beq nonzerowait_disp2

    ; Copy the contents of the FIFO to the second display
    ldx #FIFO_BASE
    ldy #DISP2_BASE

    lda 3,X
    sta 3,Y

    lda 2,X
    sta 2,Y

    lda 1,X
    sta 1,Y

    lda ,X
    sta ,Y

    ; Jump back to the beginning
    jmp loop



; Place the init function address at the origin of reset vector
    org RESET_VECTOR
    fdb init
