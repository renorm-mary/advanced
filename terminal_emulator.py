import time
import sys
from peripherial import Terminal
from multiprocessing import Pipe

def terminal_process(command_pipe):
    terminal = Terminal()

    while True:
        if command_pipe.poll():
            command = command_pipe.recv()
            if command == "render":
                terminal.render()
            elif command.startswith("write"):
                _, address, value = command.split()
                terminal.write(int(address), int(value))
            elif command == "quit":
                break
        time.sleep(0.1)

if __name__ == "__main__":
    # Extract the pipe name from arguments
    command_pipe = Pipe(duplex=True)

    # Run the terminal process
    terminal_process(command_pipe)