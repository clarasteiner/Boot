import tkinter
import paramiko
from tkinter import *
from tkinter.ttk import *
from tkinter.ttk import Progressbar
from RaspberryPi import SensorModule
import FTPDownload
from PIL import Image, ImageTk
import os
import time
from functools import partial
import FTPUpload
import json
import customtkinter
from tkintermapview import TkinterMapView

master = customtkinter.CTk()
cwd = os.getcwd()

connected = False


def start():
    global ride_window, btn2, btns, lbls, frms, sensors, l, btn_v, btn_m, frm_s, frm1

    with open("raspi_ssh.txt", "r") as myfile:
        data = myfile.read()
        ip, username, password = "", "", ""
        if len(data) != 0:
            ip, username, password = data.splitlines()

    master.destroy()
    ride_window = customtkinter.CTk()
    ride_window.title("Fahrt starten")

    lbl1 = customtkinter.CTkLabel(ride_window, font=("Arial", 20), text="Sensoren", height=50)
    lbl1.grid(padx=(10, 50))

    btn = customtkinter.CTkButton(ride_window, text="+", command=addSensor, width=30)
    btn.grid(row=0, column=1, padx=(0, 20), sticky="e")

    btn2 = customtkinter.CTkButton(ride_window, text="★", command=saveFav, width=30)
    btn2.grid(row=0, column=2, sticky="e")

    with open("fav_sensors.txt", "r") as myfile:
        sensors = myfile.read().splitlines()
        sensors = [sensor.split(",") for sensor in sensors]
        l = len(sensors)

    frm_s = customtkinter.CTkFrame(ride_window)
    frm_s.grid(row=1)

    frms = [customtkinter.CTkFrame(frm_s) for _ in range(l)]
    btns = [customtkinter.CTkButton(frms[i], text=":", width=2, command=partial(configureSensor, i), anchor="w") for i
            in range(l)]
    lbls = [customtkinter.CTkLabel(frms[i], text=sensors[i][0]) for i in range(l)]

    for i in range(l):
        frms[i].grid()
        btns[i].grid(row=0, column=0)
        lbls[i].grid(row=0, column=1)

    frm1 = customtkinter.CTkFrame(ride_window, fg_color="#242424")
    frm1.grid(row=2)

    btn_v = customtkinter.CTkButton(frm1, text="Verbinden", command=connectSensors)
    btn_v.grid(padx=(10,0))

    map_widget = TkinterMapView(ride_window, width=400, height=400, corner_radius=0)
    map_widget.grid(column=7, row=0, rowspan=5, padx=(50, 10), pady=(10, 10))

    # google normal tile server
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    map_widget.set_position(50.771143, 8.756525)

    ride_window.mainloop()


def configureSensor(sensor):
    global parameter, parameter2, id, calibration, btn_a, sensor_window, availableSensors

    name, code, calibration, sensor_name = sensors[sensor]

    sensor_window = customtkinter.CTkToplevel(ride_window)
    sensor_window.title("Sensor hinzufuegen")

    with open("AvailableSensors.json", "r") as myfile:
        availableSensors = json.load(myfile)

    customtkinter.CTkLabel(sensor_window, text="Sensor").grid(row=0)

    options = list(availableSensors.keys())
    parameter = customtkinter.StringVar(value=sensor_name)
    drop = tkinter.OptionMenu(sensor_window, parameter, *options, command=select)

    id = customtkinter.CTkEntry(sensor_window)
    id.insert(END, code)
    id.grid(row=1, column=1)

    combobox = customtkinter.CTkOptionMenu(master=sensor_window,
                                           values=options,
                                           variable=parameter)
    combobox.grid(row=0, column=1)

    options2 = availableSensors[sensor_name]
    customtkinter.CTkLabel(sensor_window, text="Messparameter").grid(row=2)

    parameter2 = customtkinter.StringVar(value=name)
    combobox = customtkinter.CTkOptionMenu(master=sensor_window,
                                           values=options2,
                                           variable=parameter2)
    combobox.grid(row=2, column=1)

    customtkinter.CTkLabel(sensor_window, text="Kalibrierungskurve").grid(row=3)
    calibration = customtkinter.CTkEntry(sensor_window)
    calibration.insert(END, "x")
    calibration.grid(row=3, column=1)

    customtkinter.CTkButton(sensor_window, text="Abbrechen", command=test).grid(row=5, column=0)
    customtkinter.CTkButton(sensor_window, text="Speichern", command=partial(saveSensor2, sensor)).grid(row=5, column=1)
    customtkinter.CTkButton(sensor_window, text="Sensor Löschen",
                           command=partial(deleteSensor, sensor, sensor_window)).grid(row=4, columnspan=2)


def test():
    sensor_window.destroy()


def saveSensor2(i):
    with open('sensor_data.txt', 'r') as f:
        file = f.readlines()
    with open('sensor_data.txt', 'w') as f:
        file[i] = f"{parameter2.get()},{id.get()},{calibration.get()},{parameter.get()}\n"
        f.write("".join(file))

    updateSensor()


def deleteSensor(i, win):
    global lbls
    global frms
    global btns

    with open("sensor_data.txt", 'w') as myfile:
        for number, line in enumerate(sensors):
            if number != i:
                myfile.write(f"{line[0]},{line[1]},{line[2]},{line[3]}\n")

    if connected:
        btn_m.grid_forget()

    frms[i].grid_forget()

    updateSensor()

    win.destroy()


def updateSensor():
    global btn_m
    global btn2
    global btns
    global lbls
    global frms
    global btn_v
    global sensors
    global l

    # children_widgets = frm_s.winfo_children()
    # for child_widget in children_widgets:
    # child_widget.grid_forget()

    btn2.configure(text="☆")

    with open("sensor_data.txt", "r") as myfile:
        sensors = myfile.read().splitlines()
        sensors = [sensor.split(",") for sensor in sensors]

    l = len(sensors)

    frm_s = customtkinter.CTkFrame(ride_window)
    frm_s.grid(row=1)

    frms = [customtkinter.CTkFrame(frm_s) for i in range(l)]
    btns = [customtkinter.CTkButton(frms[n], text=":", width=2, command=partial(configureSensor, n), anchor="w") for n
            in
            range(l)]
    lbls = [customtkinter.CTkLabel(frms[i], text=sensors[i][0]) for i in range(l)]

    for i in range(l):
        frms[i].grid(row=i)
        btns[i].grid(row=0, column=0, sticky=W)
        lbls[i].grid(row=0, column=1)

    if connected:
        btn_m = customtkinter.CTkButton(frm1, text="Messung", command=bar)
        btn_m.grid(row=0, column=1, padx=10)


def connectSensors():
    global progress
    connected = True

    #connected_sensors = SensorModule.connect()

    btn_m = customtkinter.CTkButton(frm1, text="Messung", command=bar)
    btn_m.grid(row=0, column=1, padx=10)

    progress = Progressbar(ride_window, orient=HORIZONTAL, length=200, mode='determinate')


def upload():
    filename = tkinter.filedialog.askopenfilename(initialdir=f"{cwd}\\Measurements")
    print(filename)
    #FTPUpload.saveValue(filename)


def bar():
    progress.grid(row=4)
    #SensorModule.measure()

    for i in range(10):
        progress['value'] = 10 * (i + 1)
        ride_window.update_idletasks()
        time.sleep(1)

    progress.grid_forget()

    customtkinter.CTkButton(ride_window, text="Datei auswählen", command=upload).grid(row=3)


def select(selection):
    global parameter2, calibration

    btn_a.grid_forget()
    customtkinter.CTkLabel(sensor_window, text="Kalibrierungskurve").grid(row=3)

    calibration = customtkinter.CTkEntry(sensor_window)
    calibration.insert(END, "x")
    calibration.grid(row=3, column=1)

    customtkinter.CTkLabel(sensor_window, text="Messparameter").grid(row=2)

    options2 = availableSensors[selection]
    parameter2 = customtkinter.StringVar(value="")

    combobox = customtkinter.CTkOptionMenu(master=sensor_window,
                                           values=options2,
                                           command=select2,
                                           variable=parameter2)
    combobox.grid(row=2, column=1)

    btn_a.grid(row=4, column=0)


def optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


def select2(selection2):
    customtkinter.CTkButton(sensor_window, text="Hinzufügen", command=partial(saveSensor, sensor_window)).grid(row=4,
                                                                                                               column=1)


def addSensor():
    global parameter
    global id, btn_a
    global sensor_window, availableSensors

    sensor_window = customtkinter.CTkToplevel(ride_window)
    sensor_window.title("Sensor hinzufügen")

    customtkinter.CTkLabel(sensor_window, text="Sensor").grid(row=0)

    with open("AvailableSensors.json", "r") as myfile:
        availableSensors = json.load(myfile)

    options = list(availableSensors.keys())
    parameter = customtkinter.StringVar(value="")

    combobox = customtkinter.CTkOptionMenu(master=sensor_window,
                                           values=options,
                                           command=select,
                                           variable=parameter)
    combobox.grid(row=0, column=1)

    customtkinter.CTkLabel(sensor_window, text="ID").grid(row=1)
    id = customtkinter.CTkEntry(sensor_window)
    id.grid(row=1, column=1)

    btn_a = customtkinter.CTkButton(sensor_window, text="Abbrechen", command=sensor_window.destroy)
    btn_a.grid(row=2, column=0)


def sshRaspi():
    global e1
    global e2
    global e3
    global raspi_window

    with open("raspi_ssh.txt", "r") as myfile:
        data = myfile.read()
        ip, username, password = "", "", ""
        if len(data) != 0:
            ip, username, password = data.splitlines()

    raspi_window = customtkinter.CTkToplevel(master)
    raspi_window.title("SSH-Einstellungen")
    customtkinter.CTkLabel(raspi_window, text="IP-Adresse").grid(row=0)
    e1 = Entry(raspi_window)
    e1.insert(END, ip)
    e1.grid(row=0, column=1)
    customtkinter.CTkLabel(raspi_window, text="Nutzername").grid(row=1)
    e2 = Entry(raspi_window)
    e2.insert(END, username)
    e2.grid(row=1, column=1)
    customtkinter.CTkLabel(raspi_window, text="Passwort").grid(row=2)
    e3 = Entry(raspi_window)
    e3.insert(END, password)
    e3.grid(row=2, column=1)
    customtkinter.CTkButton(raspi_window, text="Verbinden", command=saveRaspi).grid(row=3, column=0)
    customtkinter.CTkButton(raspi_window, text="Abbrechen", command=raspi_window.destroy).grid(row=3, column=1)


def sshCloud():
    global e1
    global e2
    global e3
    global cloud_window

    with open("cloud_ssh.txt", "r") as myfile:
        data = myfile.read()
        ip, username, password = "", "", ""
        if len(data) != 0:
            ip, username, password = data.splitlines()

    cloud_window = customtkinter.CTkToplevel(master)
    cloud_window.title("SSH-Einstellungen")
    customtkinter.CTkLabel(cloud_window, text="IP-Adresse").grid(row=0)
    e1 = Entry(cloud_window)
    e1.insert(END, ip)
    e1.grid(row=0, column=1)
    customtkinter.CTkLabel(cloud_window, text="Nutzername").grid(row=1)
    e2 = Entry(cloud_window)
    e2.insert(END, username)
    e2.grid(row=1, column=1)
    customtkinter.CTkLabel(cloud_window, text="Passwort").grid(row=2)
    e3 = Entry(cloud_window)
    e3.insert(END, password)
    e3.grid(row=2, column=1)
    customtkinter.CTkButton(cloud_window, text="Verbinden", command=saveCloud).grid(row=3, column=0)
    customtkinter.CTkButton(cloud_window, text="Abbrechen", command=cloud_window.destroy).grid(row=3, column=1)


def saveRaspi():
    with open('raspi_ssh.txt', 'w') as f:
        f.write(f"{e1.get()}\n{e2.get()}\n{e3.get()}")
    raspi_window.destroy()
    start()


def saveCloud():
    with open('cloud_ssh.txt', 'w') as f:
        f.write(f"{e1.get()}\n{e2.get()}\n{e3.get()}")
    cloud_window.destroy()


def saveFav():
    global btn2
    btn2.configure(text="★")
    os.system('copy sensor_data.txt fav_sensors.txt')


def saveSensor(win):
    if (id.get() == ""):
        customtkinter.CTkLabel(win, text="Gib den Verbindungscode ein").grid(row=5, columnspan=2)
    for i in range(l):
        frms[i].grid_forget()

    with open('sensor_data.txt', 'a') as f:
        f.write(f"{parameter2.get()},{id.get()},{calibration},{parameter.get()}\n")
        f.close()

    if connected:
        btn_m.grid_forget()

    win.destroy()
    updateSensor()


def evaluation():
    master.destroy()

    window = customtkinter.CTk()
    window.title("Messung auswerten")

    parameters = ["Temperatur", "Sauerstoff", "pH", "Nitrat", "Ammonium", "Leitfähigkeit", "Phosphat", "BSB5"]
    list = [91.5, 82.84, 90.6, 97.96, 96, 85.36, 69.13, 16.6]

    l = len(parameters)

    customtkinter.CTkButton(window, text="Datei auswählen", command=upload).grid(row=0, columnspan=3)

    for i in range(l):
        customtkinter.CTkLabel(window, text=parameters[i]).grid(row=i + 1, column=0, padx=(5, 5))
        Progressbar(window, orient=HORIZONTAL, length=100, mode='determinate', value=list[i]).grid(row=i + 1, column=1,
                                                                                                   )
        customtkinter.CTkLabel(window, text=list[i]).grid(row=i + 1, column=2, padx=(5, 5))

    customtkinter.CTkLabel(window, text="62").grid(row=l + 1, column=0, padx=(5, 5))
    customtkinter.CTkLabel(window, text="II - mäßig belastet").grid(row=l + 1, column=1, padx=(5, 5))

    frm1 = customtkinter.CTkFrame(window, fg_color="#242424")
    frm1.grid(row=0, column=3, padx=(50, 5), pady=5)
    customtkinter.CTkButton(frm1, text="1 Jahr", command=start, state="disabled", width=2, fg_color="#2b2b2b").grid(
        row=0, column=0, padx=5, pady=5)
    customtkinter.CTkButton(frm1, text="3 Monate", command=start, state="disabled", fg_color="#2b2b2b", width=2).grid(
        row=0, column=1, padx=5, pady=5)
    customtkinter.CTkButton(frm1, text="1 Monat", command=start, width=2).grid(
        row=0, column=2, padx=5, pady=5)

    map_widget = TkinterMapView(window, width=400, height=400, corner_radius=0)
    map_widget.grid(column=3, row=1, rowspan=10, columnspan=4, padx=(50, 10), pady=(10, 10))

    map_widget.set_position(50.771143, 8.756525)

    current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    print(current_path)
    plane_circle_2_image = ImageTk.PhotoImage(
        Image.open(os.path.join(current_path, "76.png")).resize((35, 35)))

    plane_circle_1_image = ImageTk.PhotoImage(
        Image.open(os.path.join(current_path, "89.png")).resize((35, 35)))

    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    map_widget.set_marker(50.7716991, 8.7569005, icon=plane_circle_2_image)
    map_widget.set_marker(50.7708105, 8.7559242, icon=plane_circle_1_image)

    window.mainloop()


def setup():
    global ftp
    # client = paramiko.SSHClient()
    # client.load_system_host_keys()
    # client.connect(ip, username=username, password=password)
    # sftp = client.open_sftp()
    # sftp.put("sensor_data.txt", "sensor_data2.txt")
    # ssh_stdin, stdout, ssh_stderr = client.exec_command("echo hallo")

    # stdout = stdout.readlines()

    #    output = ""
    #    for line in stdout:
    #        output = output + line
    #    if output != "":
    #        print(output)
    #    else:
    #        print("There was no output for this command")

    with open("cloud_ssh.txt", "r") as myfile:
        data = myfile.read()
        ip, username, password = data.splitlines()

    ftp = FTPUpload.connect(ip, username, password)


if __name__ == '__main__':
    os.system('copy fav_sensors.txt sensor_data.txt')
    master.title("Gewässeranalyse Software")
    #setup()

    btn = customtkinter.CTkButton(master, text="\n\nFahrt starten\n\n", command=start)
    btn.grid(row=1, column=0, padx=50, pady=30)
    btn = customtkinter.CTkButton(master, text="RaspberryPi Einstellungen", command=sshRaspi, fg_color="#2b2b2b")
    btn.grid(row=0, column=0, padx=50, pady=30)

    btn = customtkinter.CTkButton(master, text="\n\nMessung auswerten\n\n", command=evaluation)
    btn.grid(row=1, column=1, padx=50, pady=30)
    btn = customtkinter.CTkButton(master, text="Cloud Einstellungen", command=sshCloud, fg_color="#2b2b2b")
    btn.grid(row=0, column=1, padx=50, pady=30)

    master.mainloop()
