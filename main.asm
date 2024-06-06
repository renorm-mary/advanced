.text
.org 0x100

START:  
        FMOV %F0, #1.0        ; Initialize %F0
        FMOV %F1, #2.0        ; Initialize %F1

        ; Print greeting message
        LOAD %R0, STRING_ADDR
        INT 0x1

        ; Calculate %F2 = %F0 * %F1
        FMUL %F2, %F0, %F1

        ; Load word data
        LOAD %R2, WORD_DATA_ADDR, 0x0       ; Load first word
        LOAD %R3, WORD_DATA_ADDR, 0x2       ; Load second word

        ; Load double word data
        LOAD %R5, DOUBLE_WORD_DATA_ADDR, 0x0 ; Load double word

        HALT

.org 0x400
GREETING_MSG:
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

.org 0x410
WORD_DATA_ADDR:
        dw 0x1234
        dw 0x5678

.org 0x510
DOUBLE_WORD_DATA_ADDR:
        dd 0x12345678

