import os
import subprocess
import pickle  # Unsafe module, triggers Bandit warnings
import requests  # Insecure usage of requests, triggers Bandit

# Hardcoded sensitive data (triggers Bandit B105 and B106)
API_KEY = "1234567890SECRET"
DB_PASSWORD = "supersecretpassword"

# Using eval (triggers Bandit B307)
user_input = input("Enter a command: ")
eval(user_input)  # Dangerous, allows arbitrary code execution

# Unverified HTTPS request (triggers Bandit B501)
response = requests.get("https://example.com", verify=False)
print(response.text)

# Arbitrary file read/write using pickle (triggers Bandit B301)
def save_data(filename, data):
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def load_data(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

# Running system commands unsafely (triggers Bandit B605)
cmd = input("Enter a shell command: ")
subprocess.call(cmd, shell=True)  # Dangerous, allows shell injection

# Install vulnerable dependency (triggers Safety)
# Install the `requests` package but an old version with known vulnerabilities
os.system("pip install requests==2.19.1")  # Known security vulnerabilities
