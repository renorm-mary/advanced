import time
import sys
from peripherial import Terminal
import multiprocessing as mp

def terminal_process(command_queue):
    """
    This function runs the terminal process. It creates a Terminal object and continuously checks for commands
    received through the command_queue. Based on the command, it either renders the terminal, writes to a
    specific address, or quits the process.

    :param command_queue: A multiprocessing.Queue object for sending and receiving data between processes
    """
    terminal = Terminal()  # Create a Terminal object

    while True:
        # Check if there is any data in the command_queue
        if not command_queue.empty():
            command = command_queue.get()  # Receive the command from the queue
            if command == "render":
                terminal.render()  # Render the terminal
            elif command.startswith("write"):
                _, address, value = command.split()  # Split the command into parts
                terminal.write(int(address), int(value))  # Write to the specified address
            elif command == "quit":
                break  # Quit the process
        time.sleep(0.1)  # Add a delay between checks

if __name__ == "__main__":
    # Create a multiprocessing.Queue object for inter-process communication
    command_queue = mp.Queue()

    # Run the terminal process as a separate process
    terminal_process_proc = mp.Process(target=terminal_process, args=(command_queue,))
    terminal_process_proc.start()

    # Send commands to the terminal process using the command_queue
    command_queue.put("render")
    command_queue.put("write 10 20")
    command_queue.put("quit")

    # Wait for the terminal process to finish
    terminal_process_proc.join()
