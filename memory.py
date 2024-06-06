import argparse
import threading
import queue
import sys
#import termios
#import tty

class Memory:
    def __init__(self, size=16 * 16 * 1024 * 1024):  # Increase size for HD resolution
        """
        Initializes the memory with a specified size. The default size is 16 MB.
        :param size: The size of the memory in bytes.
        """
        self.size = size
        self.memory = [0] * size

    def load(self, address, value):
        """
        Loads a value into the memory at the specified address.
        :param address: The memory address where the value will be stored.
        :param value: The value to be stored in the memory.
        """
        if 0 <= address < self.size:
            self.memory[address] = value
        else:
            raise IndexError("Memory address out of range")

    def read(self, address):
        """
        Reads the value at the specified address.
        :param address: The memory address to be read.
        :return: The value stored at the specified memory address.
        """
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise IndexError("Memory address out of range")

    def preload_memory_from_file(self, file_path):
        """
        Preloads memory content from a given file containing address-value pairs.
        :param file_path: The path to the file containing memory data.
        """
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    value = int(parts[1], 16)
                    self.load(address, value)

    def pim_add(self, addr1, addr2, addr3):
        """
        Performs integer addition on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, self.read(addr1) + self.read(addr2))

    def pim_sub(self, addr1, addr2, addr3):
        """
        Performs integer subtraction on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, self.read(addr1) - self.read(addr2))

    def pim_mul(self, addr1, addr2, addr3):
        """
        Performs integer multiplication on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, self.read(addr1) * self.read(addr2))

    def pim_div(self, addr1, addr2, addr3):
        """
        Performs integer division on memory values at addr1 and addr2, and stores the result in addr3.
        Raises a ZeroDivisionError if the divisor is zero.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        if self.read(addr2) != 0:
            self.load(addr3, self.read(addr1) / self.read(addr2))
        else:
            raise ZeroDivisionError("Division by zero")

    def pim_fadd(self, addr1, addr2, addr3):
        """
        Performs floating-point addition on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, float(self.read(addr1)) + float(self.read(addr2)))

    def pim_fsub(self, addr1, addr2, addr3):
        """
        Performs floating-point subtraction on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, float(self.read(addr1)) - float(self.read(addr2)))

    def pim_fmul(self, addr1, addr2, addr3):
        """
        Performs floating-point multiplication on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self.load(addr3, float(self.read(addr1)) * float(self.read(addr2)))

    def pim_fdiv(self, addr1, addr2, addr3):
        """
        Performs floating-point division on memory values at addr1 and addr2, and stores the result in addr3.
        Raises a ZeroDivisionError if the divisor is zero.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        if float(self.read(addr2)) != 0.0:
            self.load(addr3, float(self.read(addr1)) / float(self.read(addr2)))
        else:
            raise ZeroDivisionError("Division by zero")
