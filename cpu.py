import time
import argparse
import threading
import queue
import sys
import os
from multiprocessing import Process, Queue, Manager, Pipe
import multiprocessing
import numpy as np
import platform
if platform.system() == "Windows":
    import tkinter as tk
else:
    import Tkinter as tk

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty

import subprocess
from memory import Memory
from peripherial import Peripheral, Terminal, Storage, RandomNumberGenerator, Display, Keyboard

class ROM:
    def __init__(self, size):
        self.size = size
        self.memory = [0] * size

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    value = int(parts[1], 16)
                    self.memory[address] = value

    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise IndexError("ROM address out of range")
        

class CPU:
    INTERRUPT_VECTOR_BASE = 0x80  # Fixed address for interrupt vector table

    def __init__(self):
        self.registers = [0] * 64
        self.floating_point_registers = [0.0] * 64
        self.vector_registers = [[0.0] * 4 for _ in range(4)]
        self.memory = Memory()
        self.rom = ROM(0x10)  # 64KB ROM
        self.pc = 0
        self.flags = {
            'Z': 0,  # Zero flag
            'N': 0,  # Negative flag
            'C': 0,  # Carry flag
            'V': 0   # Overflow flag
        }
        self.interrupt_flag = 0
        self.peripherals = {}
        self.storage = {}
        print("mem size = ", self.memory.size)
    def load_memory_dump(self, dump_path):
        with open(dump_path, 'r') as file:
            for line in file:
                print("instr = ", line)
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    handler_code = int(parts[1], 16)
                    print(handler_code)
                    self.memory.load(address, handler_code)


    def load_interrupt_handlers(self, interrupt_file):
        with open(interrupt_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    handler_code = int(parts[1], 16)
                    print("address = ", address)
                    self.memory.load(address, handler_code)

    def handle_interrupt(self):
        if self.interrupt_flag:
            vector_address = self.INTERRUPT_VECTOR_BASE + self.interrupt_flag #* 4
            isr_address = self.memory.read(vector_address)# >> 40
            self.push_stack(self.pc)
            self.pc = isr_address
            self.interrupt_flag = 0

    def fetch(self):
        #self.pc 
        print("pc = ", self.pc)
        if 0 <= self.pc < len(self.rom.memory):
            instruction = self.rom.read(self.pc)
        else:
            instruction = self.memory.read(self.pc)
            #instruction_high = self.memory.read(self.pc)
            #instruction_low = self.memory.read(self.pc + 1)
            #print(f"{instruction_high:014X}\n")
            #print(f"{instruction_low:014X}\n")
            #instruction = (instruction_high << 32) | instruction_low
        self.pc += 1
        return instruction

    def decode(self, instruction):
        opcode = (instruction >> 56) & 0xFF  # Highest 8 bits for the opcode
        op_type0 = (instruction >> 52) & 0xF  # Type of first operand (1 - reg, 2 - imm)
        op_type1 = (instruction >> 48) & 0xF  # Type of second operand (1 - reg, 2 - imm)
        first_operand = (instruction >> 36) & 0xFFF  # Next 12 bits for the first operand
        second_operand = (instruction >> 24) & 0xFFF  # Next 12 bits for the second operand
        third_operand = (instruction >> 12) & 0xFFF  # Next 8 bits for the third operand
        immediate_value = instruction & 0xFFFFFFFFFF  # Lowest 40 bits for the immediate value
        print("operand type (decode)= ", op_type0, op_type1)
        return opcode, op_type0, op_type1, first_operand, second_operand, third_operand, immediate_value

    def set_flags(self, result):
        self.flags['Z'] = int(result == 0)
        self.flags['N'] = int(result != 0)

    def push_stack(self, value):
        sp = self.registers[14]
        if 0 <= sp < len(self.rom.memory):
            self.rom.load(sp, value)
        else:
            self.memory.load(sp, value)
        self.registers[14] -= 1

    def pop_stack(self):
        self.registers[14] += 1
        sp = self.registers[14]
        return self.memory.read(sp)

    def allocate_heap(self, size):
        heap_ptr = self.registers[15]
        addr = heap_ptr
        self.registers[15] += size
        return addr

    def execute(self, opcode, operands, operands_type):
        try:
            if opcode == 1:  # ADD
                result = self.registers[operands[1]] + self.registers[operands[2]]
                self.registers[operands[0]] = result
                self.set_flags(result)
            
            elif opcode == 38:  # ADDI
                print("ADDI")
                print("operands: ", operands)
                result = self.registers[operands[1]] + operands[2]
                print(result)
                #user_input = input("next instr: ")
                self.registers[operands[0]] = result
                self.set_flags(result)

            elif opcode == 2:  # SUB
                result = self.registers[operands[1]] - self.registers[operands[2]]
                self.registers[operands[0]] = result
                self.set_flags(result)
            elif opcode == 3:  # FADD
                result = self.floating_point_registers[operands[1]] + self.floating_point_registers[operands[2]]
                self.floating_point_registers[operands[0]] = result
            elif opcode == 4:  # FSUB
                result = self.floating_point_registers[operands[1]] - self.floating_point_registers[operands[2]]
                self.floating_point_registers[operands[0]] = result
            elif opcode == 5:  # VADD
                for i in range(4):
                    self.vector_registers[operands[0]][i] = self.vector_registers[operands[1]][i] + self.vector_registers[operands[2]][i] 
            elif opcode == 6:  # VSUB
                for i in range(4):
                    self.vector_registers[operands[0]][i] = self.vector_registers[operands[1]][i] - self.vector_registers[operands[2]][i]
            elif opcode == 7:  # MUL
                result = self.registers[operands[1]] * self.registers[operands[2]]
                self.registers[operands[0]] = result
                self.set_flags(result)
            elif opcode == 8:  # DIV
                if self.registers[operands[2]] != 0:
                    result = self.registers[operands[1]] / self.registers[operands[2]]
                    self.registers[operands[0]] = result
                    self.set_flags(result)
                else:
                    raise ZeroDivisionError("Division by zero")
            elif opcode == 9:  # FMUL
                result = self.floating_point_registers[operands[1]] * self.floating_point_registers[operands[2]]
                self.floating_point_registers[operands[0]] = result
            elif opcode == 10:  # FDIV
                if self.floating_point_registers[operands[2]] != 0.0:
                    result = self.floating_point_registers[operands[1]] / self.floating_point_registers[operands[2]]
                    self.floating_point_registers[operands[0]] = result
                else:
                    raise ZeroDivisionError("Division by zero")
            elif opcode == 11:  # VMUL
                for i in range(4):
                    self.vector_registers[operands[0]][i] = self.vector_registers[operands[1]][i] * self.vector_registers[operands[2]][i]
            elif opcode == 12:  # VDIV
                for i in range(4):
                    if self.vector_registers[operands[2]][i] != 0.0:
                        self.vector_registers[operands[0]][i] = self.vector_registers[operands[1]][i] / self.vector_registers[operands[2]][i]
                    else:
                        raise ZeroDivisionError("Division by zero")
            elif opcode == 13:  # LOAD
                print("LOAD")
                print(operands[0])
                print(operands[1])
                #print(self.registers[operands[1]])
                if(operands_type[1] == 1):
                    print(self.registers[operands[1]])
                    self.registers[operands[0]] = self.memory.read(self.registers[operands[1]] + operands[2])
                else:
                    self.registers[operands[0]] = self.memory.read(operands[1] + operands[2])
            elif opcode == 14:  # STORE
                self.memory.load(self.registers[operands[1]] + operands[2], self.registers[operands[0]])
            elif opcode == 15:  # CMP
                result = self.registers[operands[0]] - self.registers[operands[1]]
                #user_input = input("next instr: ")
                print(result)
                #user_input = input("next instr: ")
                self.set_flags(result)
            elif opcode == 16:  # FCMP
                result = self.floating_point_registers[operands[0]] - self.floating_point_registers[operands[1]]
                self.set_flags(result)
            elif opcode == 17:  # JUMP
                self.pc = operands[3]
                print("pc _ after JMP = ", self.pc)
                #user_input = input("next instr: ")
            elif opcode == 18:  # JZ (Jump if Zero)
                #user_input = input("next instr: ")
                print(self.flags)
                if self.flags['Z']:
                    self.pc = operands[3]
                #user_input = input("next instr: ")
            elif opcode == 19:  # JNZ (Jump if Not Zero)
                if not self.flags['Z']:
                    self.pc = operands[3]
            elif opcode == 20:  # FMOV
                self.floating_point_registers[operands[0]] = float(operands[1])
            elif opcode == 21:  # HALT
                #exit()
                return 1
                #raise SystemExit
            elif opcode == 22:  # PIM_ADD
                self.memory.pim_add(operands[0], operands[1], operands[2])
            elif opcode == 23:  # PIM_SUB
                self.memory.pim_sub(operands[0], operands[1], operands[2])
            elif opcode == 24:  # PIM_MUL
                self.memory.pim_mul(operands[0], operands[1], operands[2])
            elif opcode == 25:  # PIM_DIV
                self.memory.pim_div(operands[0], operands[1], operands[2])
            elif opcode == 26:  # PIM_FADD
                self.memory.pim_fadd(operands[0], operands[1], operands[2])
            elif opcode == 27:  # PIM_FSUB
                self.memory.pim_fsub(operands[0], operands[1], operands[2])
            elif opcode == 28:  # PIM_FMUL
                self.memory.pim_fmul(operands[0], operands[1], operands[2])
            elif opcode == 29:  # PIM_FDIV
                self.memory.pim_fdiv(operands[0], operands[1], operands[2])
            elif opcode == 30:  # INT
                self.push_stack(self.pc)
                self.interrupt_flag = operands[0]
            elif opcode == 31:  # IRET
                self.pc = self.pop_stack()
            elif opcode == 32:  # IN (Read from peripheral)
                self.registers[operands[0]] = self.read_from_peripheral(operands[1]) #self.queues[operands[1]].get() #
            elif opcode == 33:  # OUT (Write to peripheral)
                print("OUT ex", operands_type)
                if(operands_type == [1,1]):
                    self.write_to_peripheral(self.registers[operands[0]], self.registers[operands[1]])
                    #self.queues[self.registers[operands[0]]].put(self.registers[operands[1]])
                elif (operands_type == [1,2]):
                    self.write_to_peripheral(self.registers[operands[0]], operands[1])
                    #self.queues[self.registers[operands[0]]].put(operands[1])
                elif (operands_type == [2,2]):
                    self.write_to_peripheral(operands[0], operands[1])
                    #self.queues[operands[0]].put(operands[1])
                elif (operands_type == [2,1]):
                    self.write_to_peripheral(operands[0], self.registers[operands[1]])
                    #self.queues[operands[0]].put(self.registers[operands[1]])             
            elif opcode == 35:  # CALL
                self.push_stack(self.pc)
                self.pc = operands[0]
            elif opcode == 36:  # RET
                self.pc = self.pop_stack()
            elif opcode == 37:  # MOV
                if operands_type[1] == 1:
                    self.registers[operands[0]] = self.registers[operands[1]]
                else:
                    self.registers[operands[0]] = operands[1]
        except ZeroDivisionError as e:
            print(e)

    def add_peripheral(self, peripheral):
        self.peripherals[peripheral.base_address] = peripheral

    def read_from_peripheral(self, address):
        for base_address, peripheral in self.peripherals.items():
            if base_address <= address < base_address + 0x100:  # Assuming each peripheral uses 16 addresses
                return peripheral.read(address - base_address)
        raise IndexError("Peripheral address out of range")

    def write_to_peripheral(self, address, value):
        for base_address, peripheral in self.peripherals.items():
            if base_address <= address < base_address + 0x400:  # Assuming each peripheral uses 16 addresses
                peripheral.write(address - base_address, value)
                return
        raise IndexError("Peripheral address out of range")

    def run(self):
        while self.pc < len(self.memory.memory):
            self.handle_interrupt()
            instruction = self.fetch()
            opcode, *operands = self.decode(instruction)
            print("opcode = ", opcode)
            # Print all each from self.registers = [0] * 64
            print("self.registers = ", self.registers)
            #user_input = input("next instr: ")

            operands_type = []
            operands_type.append(operands[0])
            operands_type.append(operands[1])
            #if opcode != 0:
                #print(f"{instruction:016X}\n")
                #print(opcode)
                #print(operands)
                #print("operands type = ", operands_type)
                #print("operands = ", operands[2:])

            if (self.execute(opcode, operands[2:], operands_type) == 1):
                break
            self.render_peripherals()

    def render_peripherals(self):
        for peripheral in self.peripherals.values():
            if isinstance(peripheral, Terminal):
                peripheral.render()



def main():
    parser = argparse.ArgumentParser(description="CPU Emulator with Peripheral Support")
    parser.add_argument("input_file", type=str, help="File with memory dump (address-value pairs)")
    parser.add_argument("--image_file", type=str, help="File with fat16 image")
    parser.add_argument("--start_address", type=int, required=True, help="Start address for program execution in memory")
    parser.add_argument("--interrupt_file", type=str, help="File with interrupt handlers (address-value pairs)")
    args = parser.parse_args()

    cpu = CPU()
    # Add the storage peripheral
    storage = Storage(base_address=0x400, size=1024)  # Fix spelling and add size
    
    print(not args.input_file)
    print(not args.interrupt_file)
    print(not (args.start_address != None))
    print(not args.image_file)
    if not args.image_file:
        if not (args.input_file != None) or not (args.interrupt_file != None) or not (args.start_address != None):
            parser.error("Mode 1 requires --input_file, --interrupt_file, and --start_address")
        
        cpu.load_interrupt_handlers(args.interrupt_file)
        cpu.load_memory_dump(args.input_file)
        cpu.add_peripheral(storage)
        cpu.pc = args.start_address
    elif args.image_file:
        if not args.input_file or not args.rom_file:
            parser.error("Mode 2 requires --input_file and --rom_file")

        storage.preload_image_from_file(args.image_file)
        cpu.add_peripheral(storage)
        cpu.rom.load_from_file(args.rom_file)
        cpu.load_memory_dump(args.input_file)
        cpu.pc = 0  # Start execution from the beginning of ROM

    # Create instances of the peripheral devices
    display = Display(base_address=0x800)
    keyboard = Keyboard(base_address=0x0c00)
    rand_gen = RandomNumberGenerator(base_address=0x1000)

    cpu.add_peripheral(display)
    cpu.add_peripheral(keyboard)
    cpu.add_peripheral(rand_gen)
    #user_input = input("cpu start ")
    cpu.run()
    user_input = input("cpu stop ")
    print("Registers:", cpu.registers)
    print("Floating Point Registers:", cpu.floating_point_registers)
    print("Vector Registers:", cpu.vector_registers)
    print("Flags:", cpu.flags)

if __name__ == "__main__":
    main()