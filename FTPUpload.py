# Author    -   Luis Gerloni    |   MIND-Codes
# Author    -   Clara Steiner   |   MIND-Codes
# Email:    -   gerloni-luis@outlook.com
# Github:   -   https://github.com/MIND-Codes

# Imports
from paramiko import *
import os


# Class for colored outputs
class c:
    INCIDENTAL = '\33[90m'
    ERROR = '\33[31m'
    SUCCESS = '\33[32m'
    WARNING = '\33[33m'
    HIGHLIGHT = '\33[34m'
    ENDC = '\033[0m'


# Setup for FTP-Server connection
def connect(ip, username, password):
    global ftp
    global cwd
    client = SSHClient()
    client.load_host_keys(r'C:\Users\clara\Desktop\Boot\known_hosts')
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())

    # Connection to FTP-Server and getting current working directory on local computer
    client.connect(ip, username=username, password=password)
    ftp = client.open_sftp()
    cwd = os.getcwd()

    return ftp


# Function to upload files to FTP-Server
def saveValue(fileName):
    name = fileName.split("/")[-1]
    print(name)
    try:
        ftp.put(fileName,
                fr'/home/mint/measurements/{name}')

        #os.remove(fileName)
    except Exception as error:
        print(f"{c.ERROR}Error occurred: ", type(error).__name__)
        print(f"{c.WARNING}Check if date is entered like this: 'Year-Month-Day.Hour-Minute'")
