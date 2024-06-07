.text
.org 0x100

START:  
        ; Initialize stack pointer
        MOV %R14, 0x100
        ; Set display mode to text mode
        MOV %R7, 0x800
        MOV %R8, 0x0

        OUT %R7, %R8



        ; Load the starting address of the string into %R0
        MOV %R4, STRING_ADDR

        ; Trigger display interrupt to print the string
        INT 0x2

        OUT 0x840, 'H'
        OUT 0x841, 'E'
        OUT 0x842, 'R'
        OUT 0x843, 'O'
        OUT 0x844, 'I'
        OUT 0x845, 'N'
        OUT 0x846, 'R'
        OUT 0x847, 'S'
        OUT 0x848, 'U'
        OUT 0x849, 'S'
        OUT 0x84a, 'Y'
        OUT 0x84b, 'M'
        OUT 0x84c, '='
        OUT 0x84d, 'L'
        OUT 0x84e, 'O'
        OUT 0x84f, 'V'
        OUT 0x850, 'E'


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

.org 0x601
WORD_ADDR:
        dw 0x1234
        dw 0x5678

.org 0x501
DWORD_ADDR:
        dd 0x12345678
