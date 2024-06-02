.interrupt
.org 0x0080
dd 0x5000
.org 0x0081
dd 0x6000
.org 0x0082
dd 0x7000
.org 0x0083
dd 0x8000
.org 0x0084
dd 0x9000
.org 0x5000
dd KEYBOARD_INTERRUPT:
        ; Handle keyboard input
        IN %R0, #0x201
        STORE %R0, LAST_KEY_PRESSED
        IRET
.org 0x6000
DISPLAY_INTERRUPT:
        ; Handle display update (if any additional logic is needed)
        IRET
.org 0x7000
PRINT_STRING_INTERRUPT:
        ; Handle printing a string to the display
        ; R0 should contain the address of the string
PRINT_LOOP:
        LOAD %R1, %R0, #0      ; Load character
        CMP %R1, #0           ; Check if null terminator
        JZ PRINT_DONE        ; If null terminator, end loop
        OUT #0x202, %R1       ; Output character to display
        ADD %R0, %R0, #1       ; Move to next character
        JUMP PRINT_LOOP      ; Repeat loop

PRINT_DONE:
        IRET
.org 0x8000
FAT16_INIT:
        ; Initialize the FAT16 driver (e.g., read the boot sector)
        LOAD %R0, #0x0000  ; Address of the boot sector
        CALL READ_SECTOR  ; Read the boot sector into memory
        CALL PARSE_BOOT_SECTOR
        IRET
.org 0x9000
FAT16_READ_FILE:
        ; Handle reading a file from the FAT16 file system
        ; %R0 = address of the file name string
        ; %R1 = buffer address to load the file data into
        CALL FIND_FILE
        CALL READ_FILE_CONTENTS
        IRET

READ_SECTOR:
        ; Read a sector from the storage device
        ; %R0 = sector number
        ; %R1 = buffer address to store the sector data
        OUT #0x300, %R0      ; Write sector number to storage device
        OUT #0x301, %R1      ; Write buffer address to storage device
        IN %R2, #0x302       ; Read status (0 = success, 1 = error)
        RET

PARSE_BOOT_SECTOR:
        ; Parse the boot sector to extract FAT16 metadata
        ; Assume the boot sector is loaded at address 0x0000
        LOAD %R0, #0x0000
        ADD %R0, %R0, #11     ; Skip the first 11 bytes
        LOAD %R1, %R0, #0     ; Bytes per sector
        LOAD %R2, %R0, #2     ; Sectors per cluster
        LOAD %R3, %R0, #3     ; Reserved sectors
        LOAD %R4, %R0, #14    ; Number of FATs
        LOAD %R5, %R0, #16    ; Maximum root directory entries
        LOAD %R6, %R0, #22    ; Total sectors (16-bit)
        LOAD %R7, %R0, #24    ; Sectors per FAT
        STORE %R1, BYTES_PER_SECTOR
        STORE %R2, SECTORS_PER_CLUSTER
        STORE %R3, RESERVED_SECTORS
        STORE %R4, NUMBER_OF_FATS
        STORE %R5, MAX_ROOT_DIR_ENTRIES
        STORE %R6, TOTAL_SECTORS
        STORE %R7, SECTORS_PER_FAT
        RET

FIND_FILE:
        ; Find the file in the root directory
        ; R0 = address of the file name string
        ; Result: R2 = starting cluster number of the file
        LOAD %R1, ROOT_DIR_START_SECTOR
        LOAD %R3, MAX_ROOT_DIR_ENTRIES
FIND_FILE_LOOP:
        CMP %R3, #0
        JZ FILE_NOT_FOUND
        CALL READ_SECTOR
        LOAD %R4, %R1, #0     ; Read file name
        ; Compare file name (assuming 8.3 format)
        ; TODO: Add file name comparison logic
        ; If file found, set R2 to starting cluster number
        ADD %R1, %R1, #1
        SUB %R3, %R3, #1
        JUMP FIND_FILE_LOOP
FILE_NOT_FOUND:
        ; Handle file not found case
        RET

READ_FILE_CONTENTS:
        ; Read the contents of the file into the buffer
        ; %R2 = starting cluster number
        ; %R1 = buffer address
        ; TODO: Add logic to read the file contents
        RET

.org 0x1000
LAST_KEY_PRESSED:
        dw 0
BYTES_PER_SECTOR:
        dw 0
SECTORS_PER_CLUSTER:
        dw 0
RESERVED_SECTORS:
        dw 0
NUMBER_OF_FATS:
        dw 0
MAX_ROOT_DIR_ENTRIES:
        dw 0
TOTAL_SECTORS:
        dw 0
SECTORS_PER_FAT:
        dw 0
ROOT_DIR_START_SECTOR:
        dw 0x20  ; Example starting sector for root directory