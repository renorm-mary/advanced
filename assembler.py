import sys
import argparse
import struct
import os

def demonstrate_functionality(file_path):
    """
    This function demonstrates the use of the imported libraries.

    :param file_path: The path of the file to read.
    """
    if not os.path.isfile(file_path):
        print(f"{file_path} does not exist.")
        return

    with open(file_path, "rb") as file:
        file_content = file.read()

    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")

    struct_format = "I"
    struct_size = struct.calcsize(struct_format)
    struct_unpack = struct.unpack_from(struct_format, file_content, 0)
    first_integer = struct_unpack[0]
    print(f"First integer: {first_integer}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstrate the use of imported libraries.")
    parser.add_argument("file_path", help="The path of the file to read.")
    args = parser.parse_args()

    demonstrate_functionality(args.file_path)
