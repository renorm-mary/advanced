import argparse
import threading
import queue
import sys

class Memory:
    def __init__(self, size: int = 16 * 16 * 1024 * 1024):  # Increase size for HD resolution
        """
        Initializes the memory with a specified size. The default size is 16 MB.
        :param size: The size of the memory in bytes.
        """
        self.size = size
        self.memory = [0] * size

    def __getitem__(self, address: int) -> int:
        """
        Reads the value at the specified address.
        :param address: The memory address to be read.
        :return: The value stored at the specified memory address.
        """
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise IndexError("Memory address out of range")

    def __setitem__(self, address: int, value: int):
        """
        Loads a value into the memory at the specified address.
        :param address: The memory address where the value will be stored.
        :param value: The value to be stored in the memory.
        """
        if 0 <= address < self.size:
            self.memory[address] = value
        else:
            raise IndexError("Memory address out of range")

    def preload_memory_from_file(self, file_path: str):
        """
        Preloads memory content from a given file containing address-value pairs.
        :param file_path: The path to the file containing memory data.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    try:
                        parts = line.strip().split()
                        if len(parts) == 2:
                            address = int(parts[0], 16)
                            value = int(parts[1], 16)
                            self[address] = value
                    except ValueError:
                        print(f"Invalid line: {line}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")

    def pim_add(self, addr1: int, addr2: int, addr3: int):
        """
        Performs integer addition on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] + self[addr2]

    def pim_sub(self, addr1: int, addr2: int, addr3: int):
        """
        Performs integer subtraction on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] - self[addr2]

    def pim_mul(self, addr1: int, addr2: int, addr3: int):
        """
        Performs integer multiplication on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] * self[addr2]

    def pim_div(self, addr1: int, addr2: int, addr3: int):
        """
        Performs integer division on memory values at addr1 and addr2, and stores the result in addr3.
        Raises a ZeroDivisionError if the divisor is zero.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        if self[addr2] != 0:
            self[addr3] = self[addr1] // self[addr2]
        else:
            raise ZeroDivisionError("Division by zero")

    def pim_fadd(self, addr1: int, addr2: int, addr3: int):
        """
        Performs floating-point addition on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] + self[addr2]

    def pim_fsub(self, addr1: int, addr2: int, addr3: int):
        """
        Performs floating-point subtraction on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] - self[addr2]

    def pim_fmul(self, addr1: int, addr2: int, addr3: int):
        """
        Performs floating-point multiplication on memory values at addr1 and addr2, and stores the result in addr3.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        self[addr3] = self[addr1] * self[addr2]

    def pim_fdiv(self, addr1: int, addr2: int, addr3: int):
        """
        Performs floating-point division on memory values at addr1 and addr2, and stores the result in addr3.
        Raises a ZeroDivisionError if the divisor is zero.
        :param addr1: The first memory address.
        :param addr2: The second memory address.
        :param addr3: The memory address to store the result.
        """
        if self[addr2] != 0.0:
            self[addr3] = self[addr1] / self[addr2]
        else:
            raise ZeroDivisionError("Division by zero")
