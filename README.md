# CPU emulator

python cpu.py <memory_dump_file> --image_file <File_with_fat16_image> --start_address <start_address>  --interrupt_file <File_with_interrupt_handlers>

# Custom Assembler for a Hypothetical CPU
This is a custom assembler for a hypothetical CPU. It supports a wide range of instructions, data directives, and preprocessor directives. The assembler takes one or more assembly files as input and produces a hex file as output.

## Features:
    Instructions:               Supports various arithmetic, logic, data transfer, and control flow instructions.
    Data Directives:            Supports defining bytes (db), words (dw), double words (dd), and floats (df).
    Preprocessor Directives:    Supports #define, #include, #ifdef, #ifndef, and #endif.
    Labels:                     Supports labels for defining and referencing addresses in the code.

## Usage

Command Line
To use the assembler, run the following command:

python assembler.py <input_files> <output_file>

<input_files>: One or more assembly files to be assembled.
<output_file>: The output file to store the hex representation of the assembled code.

## Assembly Language Syntax
### Instructions
The assembler supports the following instructions:

-   ADD, SUB, MUL, DIV, LOAD, STORE, CMP, JUMP, JZ, JNZ, HALT
-   FADD, FSUB, FMUL, FDIV, LOADF, STORE, CALL, RET
-   PIM_ADD, PIM_SUB, PIM_MUL, PIM_DIV, PIM_FADD, PIM_FSUB, PIM_FMUL, PIM_FDIV
-   INT, IRET, IN, OUT
### Data Directives
-   db: Define bytes.
-   dw: Define words (2 bytes).
-   dd: Define double words (4 bytes).
-   df: Define floats (4 bytes).
### Preprocessor Directives
-   #define: Define a constant.
-   #include: Include another assembly file.
-   #ifdef: Compile the following lines if the macro is defined.
-   #ifndef: Compile the following lines if the macro is not defined.
-   #endif: End of #ifdef or #ifndef.
### Labels
Labels are used to define and reference addresses in the code.

start:
    LOAD R0, count
    JUMP end

end:
    HALT
    
# FAT16 Image Creator

This Python program creates a FAT16 image containing specified input files and an optional bootloader written to the first sector.

## Requirements

- Python 3.x
- `pyfatfs` library

## Installation

1. Install Python 3.x if not already installed.
2. Install the `pyfatfs` library using pip:

    ```sh
    pip install pyfatfs
    ```

## Usage

Run the script from the command line, providing the files to include in the FAT16 image and the output image file. Optionally, specify a bootloader file to be written to the first sector.

```sh
python image_create.py <input_files> -o <output_image> [-b <bootloader>]


