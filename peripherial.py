import argparse
import threading
import queue
import sys
import os

#import termios
#import tty
import random
import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import io
from multiprocessing import Queue
import multiprocessing
import numpy as np

def video_buffer_process(queue, buffer_queue):
    # Create a video buffer
    buffer = np.zeros((1024, 1024, 3), dtype=np.int32)
    image = Image.fromarray((buffer * 255).astype(np.uint8))

    # Create a separate window
    window = tk.Tk()
    window.title("Video Buffer Window")
    window.geometry("1024x1024")

    # Create a label to display the video buffer
    label = tk.Label(window, text="Video Buffer")
    label.pack()

    mode = None

    while True:
        if not buffer_queue.empty():
            buffer_data = buffer_queue.get()
            if isinstance(buffer_data, str):  # TEXT MODE
                mode = Display.TEXT_MODE
                text_buffer = buffer_data
                text_image = Image.new('RGB', (1024, 1024), color = (73, 109, 137))
                fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
                d = ImageDraw.Draw(text_image)
                for i, line in enumerate(text_buffer.split('\n')):
                    d.text((10, 10 + i * 12), line, font=fnt, fill=(255, 255, 0))
                photo = ImageTk.PhotoImage(text_image)
                label.config(image=photo)
                label.image = photo
            else:  # GRAPHICS MODE
                mode = Display.GRAPHICS_MODE
                buffer = buffer_data
                image = Image.fromarray((buffer * 255).astype(np.uint8))
                photo = ImageTk.PhotoImage(image)
                label.config(image=photo)
                label.image = photo
        # Run the window event loop
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
            self.write(message[0], message[1])  # Write the value to the specified port number

    def output_process(self, queue):
        while True:
            message = self.read()  # Read the value from the peripheral device
            queue.put(message)  # Put the value and port number in the queue

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

class Display(Peripheral):
    TEXT_MODE = 0
    GRAPHICS_MODE = 1

    def __init__(self, base_address, width=80, height=25):
        super().__init__(base_address)
        self.width = width
        self.height = height
        self.registers = [0] * 10  # 10 registers, including mode register and 9 additional registers
        self.mode = Display.TEXT_MODE
        self.text_buffer = [' '] * (width * height)
        self.graphics_buffer = np.zeros((height, width, 3), dtype=np.int32)
        self.queue = multiprocessing.Queue()
        self.buffer_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=video_buffer_process, args=(self.queue, self.buffer_queue))
        self.process.start()

    def __del__(self):
        self.process.join()

    def read(self, address):
        if 0 <= address <= 9:  # Unified registers
            return self.registers[address]
        elif self.mode == Display.TEXT_MODE:
            return ord(self.text_buffer[address - 10])
        else:
            return self.graphics_buffer.flat[address - 10]

    def write(self, address, value):
        if address == 0:  # Mode register
            if value == Display.TEXT_MODE:
                self.mode = Display.TEXT_MODE
            elif value == Display.GRAPHICS_MODE:
                self.mode = Display.GRAPHICS_MODE
            else:
                raise ValueError("Invalid mode")
        elif 1 <= address <= 9:  # Additional registers
            self.registers[address] = value
        elif self.mode == Display.TEXT_MODE:
            self.text_buffer[address - 10] = chr(value)
            self.update_text_buffer()
        else:
            self.graphics_buffer.flat[address - 10] = value
            self.buffer_queue.put(self.graphics_buffer)

    def update_text_buffer(self):
        text = ''.join(self.text_buffer)
        self.buffer_queue.put(text)

    def input_process(self, queue):
        pid = os.getpid()
        print(f"Process ID: {pid}")
        while True:
            message = queue.get()
            self.write(message[0], message[1])  # Write the value to the specified port number

    def output_process(self, queue):
        pid = os.getpid()
        print(f"Process ID: {pid}")
        while True:
            message = self.read()  # Read the value from the peripheral device
            queue.put(message)  # Put the value and port number in the queue


class Keyboard(Peripheral):
    def __init__(self, base_address):
        super().__init__(base_address)
        self.buffer = ""

    def read(self, address):
        # Implement the read method for the keyboard device
        if address == self.base_address:
            if self.buffer:
                return self.buffer[0]
            else:
                return None
        else:
            raise IndexError("Address out of range")
    
    def write(self, address, value):
        # Implement the write method for the keyboard device
        if address == self.base_address:
            self.buffer += chr(value)
        else:
            raise IndexError("Address out of range")
        
    def input_process(self, queue):
        while True:
            message = queue.get()
            self.write(message[0], message[1])  # Write the value to the specified port number

    def output_process(self, queue):
        while True:
            message = self.read()  # Read the value from the peripheral device
            queue.put(message)  # Put the value and port number in the queue

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


