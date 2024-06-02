.text
.org 0x100

START:  
        FMOV %F0, #1.0        ; Initialize %F0
        FMOV %F1, #2.0        ; Initialize %F1

        ; Set terminal to text mode
        OUT 0x400, 0x0       ; Set mode to text mode

        ; Load the starting address of the string into %R0
        LOAD %R0, STRING_ADDR

        ; Trigger display interrupt to print the string
        INT 0x1

        ; Continue main program
        FMUL %F2, %F0, %F1      ; %F2 = %F0 * %F1

        ; Load address of word data into %R1
        LOAD %R1, WORD_ADDR

        ; Load word data into R2
        LOAD %R2, %R5, 0x0       ; Load first word
        LOAD %R3, %R9, 0x0       ; Load second word

        ; Load address of double word data into %R4
        LOAD %R4, DWORD_ADDR

        ; Load double word data into R5
        LOAD %R5, %R9, 0x0       ; Load double word

        HALT

.static
.org 0x400
STRING_ADDR:
        db 72                ; 'H'
        db 101               ; 'e'
        db 108               ; 'l'
        db 108               ; 'l'
        db 111               ; 'o'
        db 44                ; ','
        db 32                ; (space)
        db 87                ; 'W'
        db 111               ; 'o'
        db 114               ; 'r'
        db 108               ; 'l'
        db 100               ; 'd'
        db 33                ; '!'
        db 0                 ; Null terminator

.org 0x401
WORD_ADDR:
        dw 0x1234
        dw 0x5678

.org 0x501
DWORD_ADDR:
        dd 0x12345678
