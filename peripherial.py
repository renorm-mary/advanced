import argparse
import threading
import queue
import sys
import os

#import termios
#import tty
import random
import tkinter as tk
from PIL import Image, ImageTk
import io
from multiprocessing import Queue
import multiprocessing
import numpy as np

def video_buffer_process(queue, buffer_queue):
    # Create a video buffer
    buffer = np.zeros((32, 32, 3), dtype=np.int32)
    image = Image.fromarray((buffer * 255).astype(np.uint8))

    # Create a separate window
    window = tk.Tk()
    window.title("Video Buffer Window")
    window.geometry("32x32")

    # Create a label to display the video buffer
    label = tk.Label(window, text="Video Buffer")
    label.pack()

    while True:
        if not buffer_queue.empty():
            buffer = buffer_queue.get()
            image = Image.fromarray((buffer * 255).astype(np.uint8))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
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
    def __init__(self, base_address, width=80, height=25):
        super().__init__(base_address)
        self.width = width
        self.height = height
        self.buffer = np.zeros((32, 32, 3), dtype=np.int32)
        #self.window = tk.Tk()  # Create a new tkinter window
        #self.window.title("Display Peripheral")
        #self.window.geometry(f"{width * 10}x{height * 20}")  # Set the window size
        #self.text_widget = tk.Text(self.window, height=height, width=width)  # Create a text widget
        self.queue = multiprocessing.Queue()
        self.buffer_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=video_buffer_process, args=(self.queue, self.buffer_queue))
        self.process.start()

    def __del__(self):
        #user_input = input("cpu stop ")
        self.process.join()

    def read(self, address):
        # Implement the read method for the display device
        #x = address % self.width
        #y = address // self.width
        #return ord(self.buffer[y][x])  # Return the character value at the specified address
        return self.buffer_queue.get()

    def write(self, address, value):
        print(address, value)
        self.buffer.flat[address] = value
        self.buffer_queue.put(self.buffer)
        # Implement the write method for the display device
        #x = address % self.width
        #y = address // self.width
        #self.buffer[y][x] = chr(value)  # Update the video buffer
        #self.text_widget.delete(1.0, tk.END)  # Clear the text widget
        #for row in self.buffer:
        #    self.text_widget.insert(tk.END, ''.join(row) + '\n')  # Update the text widget
        #self.window.update()  # Update the window

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


