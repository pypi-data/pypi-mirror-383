""" 
Author: Darren
Date: 11/01/2022

Obtain a Locations class, which stores directory paths 
based on the location of a specified script. 
This makes it convenient to manage and access different file and directory paths 
relative to a given script's location.

To use in your code:
script_name = "my_script"
locations = get_locations(script_name)
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Locations:
    """ Dataclass for storing various location properties """
    script_name: str # The name of this script
    script_dir: Path # The path where this script is hosted
    input_dir: Path  # A directory called "input", under the script_dir
    output_dir: Path # A directory called "output", under the script_dir
    input_file: Path # A file called input.txt, under the input_dir

def get_locations(calling_file_path: str, sub_folder="") -> Locations:
    """ Set various paths, based on the location of the calling script. """

    # Get the directory of the calling script
    script_dir = Path(calling_file_path).resolve().parent

    # If a sub_folder is provided, append it to the script_dir
    if sub_folder:
        script_dir = script_dir / sub_folder

    script_name = Path(calling_file_path).name
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"
    input_file = input_dir / "input.txt"

    return Locations(script_name, script_dir,
                     input_dir,
                     output_dir,
                     input_file)
