import sys
import argparse
import struct
import os

class Assembler:
    def __init__(self):
        self.instructions = {
            'ADD': 1, 'SUB': 2, 'FADD': 3, 'FSUB': 4, 'VADD': 5, 'VSUB': 6,
            'MUL': 7, 'DIV': 8, 'FMUL': 9, 'FDIV': 10, 'VMUL': 11, 'VDIV': 12,
            'LOAD': 13, 'STORE': 14, 'CMP': 15, 'FCMP': 16, 'JUMP': 17, 'JZ': 18,
            'JNZ': 19, 'FMOV': 20, 'HALT': 21, 'PIM_ADD': 22, 'PIM_SUB': 23,
            'PIM_MUL': 24, 'PIM_DIV': 25, 'PIM_FADD': 26, 'PIM_FSUB': 27, 'PIM_FMUL': 28,
            'PIM_FDIV': 29, 'INT': 30, 'IRET': 31, 'IN': 32, 'OUT': 33, 'LOADF': 34,
            'CALL': 35, 'RET': 36, 'MOV': 37, 'ADDI': 38
        }
        self.labels = {}
        self.defines = {}
        self.text_segment = []
        self.static_segment = []
        self.heap_segment = []
        self.stack_segment = []
        self.interrupt_handlers = []
        self.current_segment = self.text_segment
        self.current_address = 0
        self.conditions_stack = []

    def preprocess(self, lines):
        processed_lines = []
        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments
            if not line:
                continue
            
            if line.startswith('#define'):
                parts = line.split()
                if len(parts) >= 3:
                    self.defines[parts[1]] = ' '.join(parts[2:])
                continue
            elif line.startswith('#include'):
                parts = line.split()
                if len(parts) == 2:
                    include_path = parts[1].strip('\"')
                    if os.path.exists(include_path):
                        with open(include_path, 'r') as inc_file:
                            included_lines = inc_file.readlines()
                            processed_lines.extend(self.preprocess(included_lines))
                continue
            elif line.startswith('#ifdef'):
                parts = line.split()
                if len(parts) == 2:
                    condition = parts[1] in self.defines
                    self.conditions_stack.append(condition)
                continue
            elif line.startswith('#ifndef'):
                parts = line.split()
                if len(parts) == 2:
                    condition = parts[1] not in self.defines
                    self.conditions_stack.append(condition)
                continue
            elif line.startswith('#endif'):
                if self.conditions_stack:
                    self.conditions_stack.pop()
                continue
            if not any(self.conditions_stack) or all(self.conditions_stack):
                for key, value in self.defines.items():
                    line = line.replace(key, value)
                processed_lines.append(line)

        return processed_lines

    def parse_operand(self, operand):
        #print(self.labels)
        operand = operand.strip(',')
        operand_type = 0
        
        if operand.startswith("'"):  # ASCII code
            ascii_code = ord(operand[1:-1])
            return ascii_code, 2
        elif operand.startswith('%R'):  # Register
            operand_type = 1
            return int(operand[2:]), operand_type
        elif operand.startswith('%F'):  # Floating point register
            operand_type = 1
            return int(operand[2:]), operand_type #+ 100  # Let's assume floating point registers start from 100
        elif operand.startswith('#0x'):  # Immediate value in hex
            operand_type = 2
            return int(operand[1:], 16), operand_type
        elif operand.startswith('0x'):  # Immediate value in hex
            operand_type = 2
            #print(int(operand, 16), operand_type)
            return int(operand, 16), operand_type
        elif operand.startswith('#'):  # Immediate float value
            operand_type = 2
            #print(struct.unpack('<I', struct.pack('<f', float(operand[1:])))[0], operand_type)
            return struct.unpack('<I', struct.pack('<f', float(operand[1:])))[0], operand_type
        elif operand.isdigit():  # Immediate value in decimal
            operand_type = 2
            return int(operand), operand_type
        elif operand in self.labels:  # Label
            operand_type = 9
            return self.labels[operand], operand_type
        else:
            raise ValueError(f"Invalid operand: {operand, operand_type}")

    def first_pass(self, lines):
        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments
            if not line:
                continue

            if line.startswith('.text'):
                self.current_segment = self.text_segment
            elif line.startswith('.static'):
                self.current_segment = self.static_segment
            elif line.startswith('.heap'):
                self.current_segment = self.heap_segment
            elif line.startswith('.stack'):
                self.current_segment = self.stack_segment
            elif line.startswith('.interrupt'):
                self.current_segment = self.interrupt_handlers
            elif line.startswith('.org'):
                self.current_address = int(line.split()[1], 16)
            elif ':' in line:
                label = line.split(':')[0].strip()
                self.labels[label] = self.current_address
            else:
                parts = line.split()
                if not parts:
                    continue
                instruction = parts[0]#.upper()
                if instruction in self.instructions:
                    self.current_address += 1
                elif instruction in ('db', 'dw', 'dd', 'df'):
                    if instruction == 'db':
                        self.current_address += len(parts) - 1
                    elif instruction == 'dw':
                        self.current_address += 2 * (len(parts) - 1)
                    elif instruction == 'dd':
                        self.current_address += 4 * (len(parts) - 1)
                    elif instruction == 'df':
                        self.current_address += 4 * (len(parts) - 1)

    def second_pass(self, lines):
        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments
            if not line:
                continue

            if line.startswith('.text'):
                self.current_segment = self.text_segment
            elif line.startswith('.static'):
                self.current_segment = self.static_segment
            elif line.startswith('.heap'):
                self.current_segment = self.heap_segment
            elif line.startswith('.stack'):
                self.current_segment = self.stack_segment
            elif line.startswith('.interrupt'):
                self.current_segment = self.interrupt_handlers
            elif line.startswith('.org'):
                self.current_address = int(line.split()[1], 16)
            elif ':' in line:
                continue  # Labels were processed in the first pass
            else:
                parts = line.split()
                if not parts:
                    continue
                instruction = parts[0]#.upper()
                if instruction in self.instructions:
                    print("instr = ", instruction)
                    opcode = self.instructions[instruction]
                    operands_o = [[],[]]
                    print(type([self.parse_operand(x) for x in parts[1:]] if len(parts) > 1 else []))
                    operands_o = [self.parse_operand(x) for x in parts[1:]] if len(parts) > 1 else [(0, 0),(0,0)]
                    
                    print(operands_o)
                    operands = [operands_o[n][0] for n in range(len(operands_o))]
                    print(operands)
                    
                    operands_type =  [operands_o[n][1] for n in range(len(operands_o))]
                    operands_type.append(0)
                    operands_type.append(0)
                    print("operands_type = ", operands_type[0], operands_type[1])
                    self.current_segment.append((self.current_address, opcode,operands_type[0], operands_type[1], operands))
                    self.current_address += 1
                elif instruction in ('db', 'dw', 'dd', 'df'):
                    self.handle_data_directive(instruction, parts[1:])
                else:
                    raise ValueError(f"Unknown instruction or directive: {instruction}")
    

    def parse(self, lines):
        for line in lines:
            line = line.split(';')[0].strip()  # Remove comments
            if not line:
                continue

            if line.startswith('.text'):
                self.current_segment = self.text_segment
            elif line.startswith('.static'):
                self.current_segment = self.static_segment
            elif line.startswith('.heap'):
                self.current_segment = self.heap_segment
            elif line.startswith('.stack'):
                self.current_segment = self.stack_segment
            elif line.startswith('.interrupt'):
                self.current_segment = self.interrupt_handlers
            elif line.startswith('.org'):
                self.current_address = int(line.split()[1], 16)
            elif ':' in line:
                label = line.split(':')[0].strip()
                self.labels[label] = self.current_address
            else:
                parts = line.split()
                if not parts:
                    continue
                instruction = parts[0]#.upper()
                if instruction in self.instructions:
                    opcode = self.instructions[instruction]
                    operands = [self.parse_operand(x) for x in parts[1:]] if len(parts) > 1 else []
                    self.current_segment.append((self.current_address, opcode, operands))
                    self.current_address += 1
                elif instruction in ('db', 'dw', 'dd', 'df'):
                    self.handle_data_directive(instruction, parts[1:])
                else:
                    raise ValueError(f"Unknown instruction or directive: {instruction}")

    def handle_data_directive(self, directive, operands):
        if directive == 'db':
            values = [int(x, 0) for x in operands]
            for value in values:
                self.current_segment.append((self.current_address, value & 0xFF))
                self.current_address += 1
        elif directive == 'dw':
            values = [int(x, 0) for x in operands]
            for value in values:
                self.current_segment.append((self.current_address, value & 0xFFFF))
                self.current_address += 2
        elif directive == 'dd':
            values = [int(x, 0) for x in operands]
            for value in values:
                self.current_segment.append((self.current_address, value & 0xFFFFFFFF))
                self.current_address += 4
        elif directive == 'df':
            values = [float(x) for x in operands]
            for value in values:
                packed_value = struct.unpack('<I', struct.pack('<f', value))[0]
                self.current_segment.append((self.current_address, packed_value))
                self.current_address += 4

    def write_output(self, output_file):
        with open(output_file, 'w') as file:
            for segment in [self.text_segment, self.static_segment, self.heap_segment, self.stack_segment, self.interrupt_handlers]:
                for entry in segment:
                    if len(entry) == 5:
                        address, opcode, operand0_type, operand1_type, operands = entry
                        if opcode == 17 or opcode == 18 or opcode == 19:
                            hex_code = f"{opcode:02X}"
                            hex_code += f"{operands[0]:014X}"
                            file.write(f"{address:04X} {hex_code.ljust(16, '0')}\n")
                            continue

                        hex_code = f"{opcode:02X}"
                        print("------------------------------------")
                        print("hex_code = ", hex_code)
                        print("operand_type = ", operand0_type)
                        #print("operand_type = ", operand_type)
                        hex_code += f"{operand0_type:01X}"
                        print("hex_code = ", f"{operand0_type:01X}")
                        hex_code += f"{operand1_type:01X}"
                        print("hex_code = ", f"{operand1_type:01X}")

                        for operand in operands:
                            #print(operand)
                            hex_code += f"{operand:03X}"
                            print("hex_code = ", f"{operand:03X}")
                        print("------------------------------------")
                        file.write(f"{address:04X} {hex_code.ljust(16, '0')}\n")
                    elif len(entry) == 2:
                        address, value = entry
                        #print(type(value))
                        file.write(f"{address:04X} {value:016X}\n")


def main():
    parser = argparse.ArgumentParser(description="Assembler for custom CPU")
    parser.add_argument("input_files", type=str, nargs='+', help="Input assembly files")
    parser.add_argument("output_file", type=str, help="Output hex file")
    args = parser.parse_args()

    assembler = Assembler()
    for input_file in args.input_files:
        with open(input_file, 'r') as file:
            lines = file.readlines()
            preprocessed_lines = assembler.preprocess(lines)
            assembler.first_pass(preprocessed_lines)
            assembler.second_pass(preprocessed_lines)
    assembler.write_output(args.output_file)

if __name__ == "__main__":
    main()
