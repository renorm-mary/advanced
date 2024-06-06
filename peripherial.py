import argparse
import threading
import queue
import sys
import os
import random
import tkinter as tk
from PIL import Image, ImageTk
import io
import numpy as np

def video_buffer_process(buffer_queue):
    buffer = np.zeros((32, 32, 3), dtype=np.int32)
    image = Image.fromarray((buffer * 255).astype(np.uint8))
    window = tk.Tk()
    window.title("Video Buffer Window")
    window.geometry("32x32")
    label = tk.Label(window, text="Video Buffer")
    label.pack()

    while True:
        if not buffer_queue.empty():
            buffer = buffer_queue.get()
            image = Image.fromarray((buffer * 255).astype(np.uint8))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
        window.update()

class Peripheral:
    def __init__(self, base_address):
        self.base_address = base_address

    def read(self, address):
        raise NotImplementedError("Read method not implemented")

    def write(self, address, value):
        raise NotImplementedError("Write method not implemented")

    def input_process(self, queue):
        while True:
            message = queue.get()
            self.write(message[0], message[1])

    def output_process(self, queue):
        while True:
            message = self.read()
            queue.put(message)

class Storage(Peripheral):
    def __init__(self, base_address, size):
        super().__init__(base_address)
        self.storage = [0] * size

    def read(self, address):
        return self.storage[address]

    def write(self, address, value):
        self.storage[address] = value

class RandomNumberGenerator(Peripheral):
    def __init__(self, base_address):
        super().__init__(base_address)

    def read(self, offset):
        return random.randint(0, 0xFFFF)

    def write(self, offset, value):
        pass

class Display(Peripheral):
    def __init__(self, base_address, width=80, height=25):
        super().__init__(base_address)
        self.width = width
        self.height = height
        self.buffer = np.zeros((height, width, 3), dtype=np.int32)
        self.buffer_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=video_buffer_process, args=(self.buffer_queue,))
        self.process.start()

    def __del__(self):
        self.process.join()

    def read(self, address):
        x = address % self.width
        y = address // self.width
        return self.buffer[y][x]

    def write(self, address, value):
        x = address % self.width
        y = address // self.width
        self.buffer[y][x] = value
        self.buffer_queue.put(self.buffer)

class Keyboard(Peripheral):
    def __init__(self, base_address):
        super().__init__(base_address)
        self.buffer = ""

    def read(self, address):
        if address == self.base_address:
            if self.buffer:
                return self.buffer[0]
            else:
                return None
        else:
            raise IndexError("Address out of range")

    def write(self, address, value):
        if address == self.base_address:
            self.buffer += chr(value)
        else:
            raise IndexError("Address out of range")

class Terminal(Peripheral):
    TEXT_MODE = 0
    GRAPHICS_MODE = 1

    def __init__(self, base_address, width=80, height=25):
        super().__init__(base_address)
        self.width = width
        self.height = height
        self.mode = Terminal.TEXT_MODE
        self.text_buffer = [' '] * (width * height)
        self.graphics_buffer = [(0, 0, 0)] * (width * height)
        self.keyboard_buffer = queue.Queue()
        self.current_address = 0

    def read(self, address):
        if address == 0:
            return self.mode
        elif address == 1:
            try:
                return self.keyboard_buffer.get_nowait()
            except queue.Empty:
                return 0
        elif 2 <= address < 2 + self.width * self.height:
            if self.mode == Terminal.TEXT_MODE:
                return ord(self.text_buffer[address - 2])
            else:
                r, g, b = self.graphics_buffer[address - 2]
                return (r << 16) | (g << 8) | b
        else:
            raise IndexError("Terminal address out of range")

    def write(self, address, value):
        if address == 0:
            self.mode = value
        elif address == 1:
            self.current_address = value
        elif 2 <= address < 2 + self.width * self.height:
            if self.mode == Terminal.TEXT_MODE:
                self.text_buffer[address - 2] = chr(value)
            else:
                r = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                b = value & 0xFF
                self.graphics_buffer[address - 2] = (r, g, b)

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

