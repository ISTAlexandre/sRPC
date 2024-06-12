import argparse
import tarfile
import os
import time
import datetime

import numpy as np
import ROOT
from array import array

import subprocess
import shutil

def execute_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")

def move_root_files(source_folder, destination_folder):
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate through all files in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.root'):
            source_path = os.path.join(source_folder, file_name)
            destination_path = os.path.join(destination_folder, file_name)
            # Move the file to the destination folder
            shutil.move(source_path, destination_path)
            print(f"Moved {file_name} to {destination_folder}")


if __name__ == "__main__":
    start_time = time.time()

    
    files = os.listdir("data/")
    for file in files:
        if file.endswith('.gz'):
            command = "python3 dataConverter.py data/"+file
            execute_command(command)
            command = "rm data/"+file
            execute_command(command)
    move_root_files("data/","data_ready/")


    files = os.listdir("data_ready/")
    for file in files:
        if file.endswith('.root'):
            command = "python3 python/QB2.py data_ready/"+file
            execute_command(command)
            print("QB2 DONE!")
            
            command = "python3 python/TH2D_planes.py data_ready/"+file
            execute_command(command)
            print("N_HITS DRAWN")

            command = "python3 python/trajectories.py data_ready/"+file
            execute_command(command)
            print("efficiency drawn")

            command = "python3 python/TH1D_angle.py"
            execute_command(command)
            print("angle drawn")

            end_time = time.time()
            elapsed = -start_time + end_time
            print("This took "+str(elapsed/60)+" minutes\n")
            print("AGAIN!")
