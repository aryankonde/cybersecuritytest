import os
import subprocess
import pickle

USERNAME = "admin"
PASSWORD = "password123"

def run_command(cmd):
    subprocess.call(cmd, shell=True)

def execute_user_input(user_input):
    eval(user_input)

def load_data(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

def write_temp_file(data):
    with open("/tmp/insecure.txt", "w") as f:
        f.write(data)

if __name__ == "__main__":
    user_input = input("Enter a command: ")
    run_command(user_input)  
