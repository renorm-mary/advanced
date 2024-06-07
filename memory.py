import argparse
import threading
import queue
import sys
#import termios
#import tty

class Memory:
    def __init__(self, size=32 * 1024 * 1024):  # Increase size for HD resolution
        self.size = size
        self.memory = [0] * size
        

    def load(self, address, value):
        if 0 <= address < self.size:
            self.memory[address] = value
        else:
            raise IndexError("Memory address out of range")

    def read(self, address):
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise IndexError("Memory address out of range")

    def preload_memory_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 32)
                    value = int(parts[1], 64)
                    self.load(address, value)
        print(self.memory)

    def pim_add(self, addr1, addr2, addr3):
        self.load(addr3, self.read(addr1) + self.read(addr2))

    def pim_sub(self, addr1, addr2, addr3):
        self.load(addr3, self.read(addr1) - self.read(addr2))

    def pim_mul(self, addr1, addr2, addr3):
        self.load(addr3, self.read(addr1) * self.read(addr2))

    def pim_div(self, addr1, addr2, addr3):
        if self.read(addr2) != 0:
            self.load(addr3, self.read(addr1) / self.read(addr2))
        else:
            raise ZeroDivisionError("Division by zero")

    def pim_fadd(self, addr1, addr2, addr3):
        self.load(addr3, float(self.read(addr1)) + float(self.read(addr2)))

    def pim_fsub(self, addr1, addr2, addr3):
        self.load(addr3, float(self.read(addr1)) - float(self.read(addr2)))

    def pim_fmul(self, addr1, addr2, addr3):
        self.load(addr3, float(self.read(addr1)) * float(self.read(addr2)))

    def pim_fdiv(self, addr1, addr2, addr3):
        if float(self.read(addr2)) != 0.0:
            self.load(addr3, float(self.read(addr1)) / float(self.read(addr2)))
        else:
            raise ZeroDivisionError("Division by zero")