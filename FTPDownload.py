# Author -  Luis Gerloni | MINDCode
# Email:    gerloni-luis@outlook.com

from paramiko import *
import os


def connect(ip, username, password):
    client = SSHClient()
    client.load_host_keys(r'C:\Users\luisg\.ssh\known_hosts')
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())

    client.connect(ip, username=username, password=password)
    ftp = client.open_sftp()

    ftp.chdir('values')

    l = []
    for n in ftp.listdir():
        lstatout = str(ftp.lstat(n)).split()[0]
        if 'd' not in lstatout: l.append(n)
    l.sort(reverse=True)


def getValue(fileName):
    try:
        ftp.get(fr'/home/mint/values/Values {fileName}.csv',
                fr'{cwd}\Values {fileName}.csv')

    except Exception as error:
        print(f"Error occurred: ", type(error).__name__)
        print(f"Check if date is entered like this: 'Year-Month-Day.Hour-Minute'")
