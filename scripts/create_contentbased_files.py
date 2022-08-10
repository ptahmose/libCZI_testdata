"""
Utility used to create "content-based filenames" for use with CMake's ExternalData-mechanism
(c.f. https://cmake.org/cmake/help/book/mastering-cmake/chapter/Testing%20With%20CMake%20and%20CTest.html#managing-test-data)

What this does is:
* for all files in the "source directories" list ...
* calculate the MD5-hash of the file
* copy the file into a destination folder with the hash as filename

The synopsis is: create_contentbased_files.py [-s <source_directory>] [-d <destination_directory>] [-v]

Multiple source directories may be given, and the tool will process all of them. If no source directory is not given,
then [folder-where-this-script-resides]/../CZICheck_Testdata will be used.
If the destination directory is not given, then [folder-where-this-script-resides]/../ will be used.

The intended use case is:
* After making any change in the folder "CZICheck_Testdata" (i.e. modify a file, or adding a file)...
* run this script, and it will update the content of the "MD5"-folder
* then, then use git to check stuff in and push

"""
import argparse
import hashlib
import os
import shutil
import sys


class Parameters:
    __source_directories: []
    __destination_directory: str
    __pointersDestinationDirectory: str
    __verbose: bool

    def parse_commandline(self):
        parser = argparse.ArgumentParser(
            description='Utility for preparing test-data to be stored for CMake-test-data')
        parser.add_argument('-s', '--source', dest='source_directory', action='append',
                            help='Add a source directory to be processed.')
        parser.add_argument('-d', '--destination', dest='destination_directory',
                            help='The folder where the renamed files will be copied to.')
        parser.add_argument('-v', '--verbose', dest='verbosity', action='store_true', default=False,
                            help='Whether verbose output is requested.')
        args = parser.parse_args()

        path_of_repo = os.path.normpath(os.path.join(os.path.dirname(__file__), '../'))

        if args.source_directory:
            self.__source_directories = []
            for directory in args.source_directory:
                self.__source_directories.append(directory)
        else:
            self.__source_directories = [os.path.join(path_of_repo, 'CZICheck_Testdata')]

        if args.destination_directory:
            self.__destination_directory = args.destination_directory
        else:
            self.__destination_directory = os.path.join(path_of_repo, 'MD5')

        self.__verbose = args.verbosity

    def get_source_directories(self):
        return self.__source_directories

    def get_destination_directory(self):
        return self.__destination_directory

    def get_verbose_output(self):
        return self.__verbose


def hashfile(file_name):
    block_size = 65536
    hasher = hashlib.md5()
    with open(file_name, 'rb') as filestream:
        buf = filestream.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = filestream.read(block_size)

    return hasher.hexdigest()


def process_folder(directory_name, cmdline_parameters):
    list_of_files = os.listdir(directory_name)
    number_of_files_copied = 0
    for filename in list_of_files:
        full_filename = os.path.join(directory_name, filename)
        if os.path.isfile(full_filename):
            hash_code = hashfile(full_filename)
            destination_full_filename = os.path.join(parameters.get_destination_directory(), hash_code)
            if cmdline_parameters.get_verbose_output():
                print(f" file: '{full_filename}' hash: {hash_code} -> '{destination_full_filename}'")

            shutil.copy(full_filename, destination_full_filename)
            number_of_files_copied += 1

    return number_of_files_copied


parameters = Parameters()
parameters.parse_commandline()

# print operational parameters on stdout
print("Source Directories:")
no = 1
for source_directory in parameters.get_source_directories():
    print(f" {no}. : '{source_directory}'")
print()
print("Destination Directory:")
print(f" '{parameters.get_destination_directory()}'")
print()

total_number_of_files_copied = 0
for source_directory in parameters.get_source_directories():
    print(f"Processing directory '{source_directory}'")
    total_number_of_files_copied += process_folder(source_directory, parameters)

print()
print(f"{total_number_of_files_copied} file"
      f"{'s' if (total_number_of_files_copied>1 or total_number_of_files_copied==0) else ''}"
      f" copied in total.")