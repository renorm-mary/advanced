import argparse
from pyfatfs.FAT import FAT_OEM_NAME, FAT_TYPE, FAT

def create_fat16_image(file_paths, output_image_path, bootloader_path=None):
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

def initialize_fat16():
    # Initialize FAT16 structure with necessary metadata and empty file system
    fat16 = FAT(type=FAT_TYPE.FAT16, oem_name=FAT_OEM_NAME.MSDOS5_0)
    fat16.init_filesystem(volume_size=1048576)  # Initialize the file system with a 1MB volume size for example
    return fat16

def read_file(file_path):
    # Read file content
    with open(file_path, 'rb') as f:
        return f.read()

def write_bootloader(fat16, bootloader_data):
    # Write bootloader to the first sector of the FAT16 image
    sector_size = fat16.get_sector_size()  # Get the sector size
    boot_sector = bootloader_data[:sector_size]  # Extract the boot sector data
    fat16.write_bootsector(boot_sector)  # Write the boot sector data

def add_file_to_fat16(fat16, file_path, file_data):
    # Add a file to the FAT16 image
    fat16.create_file(file_path)  # Create a new file in the FAT16 image
    fat16.write_file(file_path, file_data)  # Write the file data to the newly created file

def write_fat16_image_to_file(fat16, output_image_path):
    # Write the FAT16 image to an output file
    with open(output_image_path, 'wb') as f:
        f.write(fat16.get_filesystem_image())  # Write the FAT16 image data to the output file

def main():
    parser = argparse.ArgumentParser(description="Create a FAT16 image containing the specified input files and an optional bootloader.")
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='input files to include in the FAT16 image')
    parser.add_argument('-o', '--output', type=str, required=True, help='output FAT16 image file')
    parser.add_argument('-b', '--bootloader', type=str, help='bootloader file to write to the first sector')
    args = parser.parse_args()

    create_fat16_image(args.files, args.output, args.bootloader)

if __name__ == "__main__":
    main()
