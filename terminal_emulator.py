import time  # Import time module for adding delay between operations
import sys  # Import sys module for system-specific parameters and functions
from peripherial import Terminal  # Import Terminal class from peripherial module
from multiprocessing import Pipe  # Import Pipe for creating inter-process communication channels

def terminal_process(command_pipe):
    """
    This function runs the terminal process. It creates a Terminal object and continuously checks for commands
    received through the command_pipe. Based on the command, it either renders the terminal, writes to a
    specific address, or quits the process.

    :param command_pipe: A Pipe object for sending and receiving data between processes
    """
    terminal = Terminal()  # Create a Terminal object

    while True:
        # Check if there is any data in the command_pipe
        if command_pipe.poll():
            command = command_pipe.recv()  # Receive the command from the pipe
            if command == "render":
                terminal.render()  # Render the terminal
            elif command.startswith("write"):
                _, address, value = command.split()  # Split the command into parts
                terminal.write(int(address), int(value))  # Write to the specified address
            elif command == "quit":
                break  # Quit the process
        time.sleep(0.1)  # Add a delay between checks

if __name__ == "__main__":
    # Extract the pipe name from arguments
    command_pipe = Pipe(duplex=True)  # Create a Pipe object for inter-process communication

    # Run the terminal process
    terminal_process(command_pipe)
