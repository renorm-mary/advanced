import argparse
from typing import List, Union
from pyfatfs.FAT import FAT_OEM_NAME, FAT_TYPE, FAT

def create_fat16_image(file_paths: List[str], output_image_path: str, bootloader_path: Union[str, None] = None) -> None:
    # Initialize FAT16 file system
    fat16 = initialize_fat16()

    # If a bootloader path is provided, read and write it to the first sector
    if bootloader_path:
        bootloader_data = read_file(bootloader_path)  # Read the bootloader file
        write_bootloader(fat16, bootloader_data)  # Write the bootloader data to the first sector

    # Add input files to FAT16 image
    for file_path in file_paths:
        file_data = read_file(file_path)  # Read the file content
        add_file_to_fat16(fat16, file_path, file_data)  # Add the file to the FAT16 image

    # Write FAT16 image to file
    write_fat16_image_to_file(fat16, output_image_path)  # Write the FAT16 image to the output file

