import argparse
import threading
import queue
import sys
#import termios
#import tty
import random
import tkinter as tk
from PIL import Image
import io
from multiprocessing import Queue

class Peripheral:
    def __init__(self, base_address):
        self.base_address = base_address

    def read(self, address):
        raise NotImplementedError("Read method not implemented")

    def write(self, address, value):
        raise NotImplementedError("Write method not implemented")
    
class Storage:
    def __init__(self, base_address, size):
        self.base_address = base_address
        self.storage = [0] * size
    

    def preload_image_from_file(self, file_path):
        with open(file_path, 'r') as file:
            image = Image.open(io.BytesIO(file.read()))
            self.storage = image

    def read(self, offset):
        return self.storage[offset]

    def write(self, offset, value):
        self.storage[offset] = value

class RandomNumberGenerator(Peripheral):
    def __init__(self, base_address):
        self.base_address = base_address

    def read(self, offset):
        return random.randint(0, 0xFFFF)  # Generate a random 16-bit number

    def write(self, offset, value):
        pass  # Write operation is not applicable for RNG

class Display:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("CPU Display")
        self.display = tk.Text(self.window, width=40, height=20)
        self.display.pack()

    def update_display(self, data):
        self.display.insert(tk.END, str(data) + "\n")

    def run(self):
        self.window.mainloop()


class Terminal(Peripheral):
    TEXT_MODE = 0
    GRAPHICS_MODE = 1

    def __init__(self, base_address, width=80, height=25):
        super().__init__(base_address)
        self.width = width
        self.height = height
        self.mode = Terminal.TEXT_MODE
        self.text_buffer = [' '] * (width * height)
        self.graphics_buffer = [(0, 0, 0)] * (width * height)  # 24-bit color (RGB)
        self.keyboard_buffer = queue.Queue()
        self.current_address = 0

        self.command_queue = Queue()
        self.response_queue = Queue()

    def read(self, address):
        if address == 0:  # Mode register
            return self.mode
        elif address == 1:  # Keyboard buffer
            try:
                return self.keyboard_buffer.get_nowait()
            except queue.Empty:
                return 0
        elif 2 <= address < 2 + self.width * self.height:
            if self.mode == Terminal.TEXT_MODE:
                return ord(self.text_buffer[address - 2])
            else:
                r, g, b = self.graphics_buffer[address - 2]
                return (r << 16) | (g << 8) | b  # Pack RGB into a single integer
        else:
            raise IndexError("Terminal address out of range")

    def write(self, address, value):
        if address == 0:  # Mode register
            self.mode = value
        elif address == 1:  # Current address register
            self.current_address = value
        elif 2 <= address < 2 + self.width * self.height:
            if self.mode == Terminal.TEXT_MODE:
                self.text_buffer[address - 2] = chr(value)
            else:
                r = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                b = value & 0xFF
                self.graphics_buffer[address - 2] = (r, g, b)
        else:
            raise IndexError("Terminal address out of range")

    def render(self):
        if self.mode == Terminal.TEXT_MODE:
            for y in range(self.height):
                line = self.text_buffer[y * self.width:(y + 1) * self.width]
                print(''.join(line))
        else:
            for y in range(self.height):
                line = self.graphics_buffer[y * self.width:(y + 1) * self.width]
                print(' '.join(f"({r},{g},{b})" for r, g, b in line))

    def handle_keypress(self, key):
        self.keyboard_buffer.put(ord(key))