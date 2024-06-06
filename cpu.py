import time
import argparse
import threading
import queue
import sys
import os
from multiprocessing import Process, Queue, Manager, Pipe
import multiprocessing.shared_memory as shm
import platform

if platform.system() == "Windows":
    import tkinter as tk
else:
    import Tkinter as tk

def is_windows():
    return platform.system() == "Windows"

def read_input(queue):
    for line in sys.stdin:
        queue.put(line.strip())

def execute_instruction(cpu: CPU, instruction: int):
    opcode, op_type0, op_type1, first_operand, second_operand, third_operand, immediate_value = cpu.decode(instruction)
    cpu.execute(opcode, (first_operand, second_operand, third_operand), (op_type0, op_type1), immediate_value)

def run_cpu(cpu: CPU, memory_dump_path: str, interrupt_file: str, start_address: int):
    cpu.load_interrupt_handlers(interrupt_file)
    cpu.load_memory_dump(memory_dump_path)
    cpu.run()

def main():
    parser = argparse.ArgumentParser(description="CPU Emulator with Peripheral Support")
    parser.add_argument("memory_dump_path", type=str, help="Path to the memory dump file")
    parser.add_argument("--interrupt_file", type=str, help="Path to the interrupt handlers file")
    parser.add_argument("--start_address", type=int, required=True, help="Start address for program execution in memory")
    parser.add_argument("--image_file", type=str, help="Path to the fat16 image file")
    parser.add_argument("--rom_file", type=str, help="Path to the ROM file")
    args = parser.parse_args()

    cpu = CPU()

    if not args.image_file:
        if not (args.memory_dump_path and args.interrupt_file and args.start_address):
            parser.error("Mode 1 requires --memory_dump_path, --interrupt_file, and --start_address")

        cpu.load_interrupt_handlers(args.interrupt_file)
        cpu.load_memory_dump(args.memory_dump_path)
    else:
        if not (args.memory_dump_path and args.rom_file):
            parser.error("Mode 2 requires --memory_dump_path and --rom_file")

        # Load ROM
        with open(args.rom_file, 'rb') as f:
            rom_data = f.read()
        cpu.rom.load_from_bytes(rom_data)

        # Load fat16 image
        storage = Storage(base_address=0x400, size=1024)
        storage.preload_image_from_file(args.image_file)
        cpu.add_peripheral(storage)

        cpu.load_memory_dump(args.memory_dump_path)
        cpu.pc = 0  # Start execution from the beginning of ROM

    display = Display(base_address=0x800)
    keyboard = Keyboard(base_address=0x0c00)
    rand_gen = RandomNumberGenerator(base_address=0x1000)

    cpu.add_peripheral(display)
    cpu.add_peripheral(keyboard)
    cpu.add_peripheral(rand_gen)

    if is_windows():
        input_queue = queue.Queue()
        input_thread = threading.Thread(target=read_input, args=(input_queue,))
        input_thread.start()
    else:
        input_queue = Queue()
        input_process = Process(target=read_input, args=(input_queue,))
        input_process.start()

    memory_dump_queue = queue.Queue()
    memory_dump_thread = threading.Thread(target=cpu.fetch_and_execute, args=(memory_dump_queue, input_queue))
    memory_dump_thread.start()

    run_cpu(cpu, args.memory_dump_path, args.interrupt_file, args.start_address)

    if is_windows():
        input_thread.join()
    else:
        input_process.terminate()
        input_process.join()

    memory_dump_thread.join()

if __name__ == "__main__":
    main()
