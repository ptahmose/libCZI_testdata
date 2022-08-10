"""
This is a utility for preparing files in a folder for usage with CMake's ExternalData-mechanism
(c.f. https://cmake.org/cmake/help/book/mastering-cmake/chapter/Testing%20With%20CMake%20and%20CTest.html#managing-test-data).

The synopsis is: prepare_sample_data.py -s <source_directory> -d <destination_directory> -p <pointer_destination_directory>

'source_directory' is the folder where the files to be processed are found in. Only files directly in this folder
are processed (i.e. no sub-folders).

For each file md5-checksum is calculated. Then, the file is copied to a file which gets the filename of the hash-code
in the destination_directory. If the argument destination_directory is not given, this step is not done.
Next, the hash-code is written into a file with the same name as the original file with ".md5" appended, in the
directory pointer_destination_directory. Again, if the argument pointer_destination_directory is not given, this
step is not done.

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

    def get_verbosity(self):
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


def process_folder(directory_name, parameters):
    list_of_files = os.listdir(directory_name)
    for filename in list_of_files:
        full_filename = os.path.join(directory_name, filename)
        if os.path.isfile(full_filename):
            hash_code = hashfile(full_filename)
            destination_full_filename = os.path.join(parameters.get_destination_directory(), hash_code)
            print(f"file: {full_filename} hash: {hash_code}")
            shutil.copy(full_filename, destination_full_filename)


parameters = Parameters()
parameters.parse_commandline()

for source_directory in parameters.get_source_directories():
    print(f"Processing directory '{source_directory}'")
    process_folder(source_directory, parameters)
