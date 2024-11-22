from pathlib import Path

# Explicit imports to satisfy Flake8
from tkinter import Tk, ttk, messagebox, Canvas, Entry, Text, Button, PhotoImage

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import socketio
import serial
import json
import threading

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets") # assets folder path

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class app:
    proportional = 0
    integral = 0
    derivative = 0
    kp = None
    ki = None
    kd = None
    flImgFile = "fl-g.png"
    frImgFile = "fr-g.png"
    blImgFile = "bl-g.png"
    brImgFile = "br-g.png"

    def __init__(self, window, ip):
        if not ip:
            print("IP Address is required")
            exit(1)
            
        self.window = window
        self.window.title("Self Balancing Robot Monitoring")
        self.window.geometry("1280x720")
        self.window.configure(bg = "#FFFFFF")
        self.window.resizable(False, False)
        self.window.option_add('*TCombobox*Listbox.font', ("Poppins SemiBold", 24 * -1))

        try:
            self.serverAddr = f"http://{ip}:5000"
            self.sio = socketio.Client()
            self.dashboard()
            self.setup_events()
            socket_thread = threading.Thread(target=self.run_socketio)
            socket_thread.daemon = True
            socket_thread.start()
        except socketio.exceptions.ConnectionError as e:
            print("Failed to connect to server:", e)
            exit(1)

    ''' Dashboard Canvas '''
    def dashboard(self):
        for i in self.window.winfo_children():
            i.destroy()

        self.canvas = Canvas(
            self.window,
            bg = "#FFFFFF",
            height = 720,
            width = 1280,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.pack()

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            0.0,
            0.0,
            1280.0,
            102.0,
            fill="#3D3669",
            outline="")

        self.imgHeader = PhotoImage(file=relative_to_assets("header.png"))
        self.canvas.create_image(
            233.0,
            65.0,
            image=self.imgHeader
        )

        self.imgToSettings = PhotoImage(
            file=relative_to_assets("btn-settings.png"))
        btnToSettings = Button(
            image=self.imgToSettings,
            borderwidth=0,
            highlightthickness=0,
            command=self.settings,
            relief="flat"
        )
        btnToSettings.place(
            x=999.0,
            y=54.0,
            width=202.0,
            height=48.0
        )

        self.canvas.create_text(
            38.0,
            113.0,
            anchor="nw",
            text="Parameter Overview",
            fill="#333333",
            font=("Poppins Medium", 14 * -1)
        )

        self.direction = self.canvas.create_text(
            1184.0,
            113.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 14 * -1)
        )

        self.yawImg = PhotoImage(file=relative_to_assets("yaw.png"))
        self.canvas.create_image(
            226.0,
            219.0,
            image=self.yawImg
        )

        self.yaw = self.canvas.create_text(
            194.0,
            195.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.pitchImg = PhotoImage(file=relative_to_assets("pitch.png"))
        self.canvas.create_image(
            502.0,
            219.0,
            image=self.pitchImg
        )

        self.pitch = self.canvas.create_text(
            470.0,
            195.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.rollImg = PhotoImage(file=relative_to_assets("roll.png"))
        self.canvas.create_image(
            778.0,
            219.0,
            image=self.rollImg
        )

        self.roll = self.canvas.create_text(
            722.0,
            195.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.speedImg = PhotoImage(file=relative_to_assets("speed.png"))
        self.canvas.create_image(
            1054.0,
            219.0,
            image=self.speedImg
        )

        self.speed = self.canvas.create_text(
            949.0,
            195.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.pidImg = PhotoImage(file=relative_to_assets("pid.png"))
        self.canvas.create_image(
            226.0,
            357.0,
            image=self.pidImg
        )

        self.pid = self.canvas.create_text(
            126.0,
            345.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.errorImg = PhotoImage(file=relative_to_assets("error.png"))
        self.canvas.create_image(
            502.0,
            357.0,
            image=self.errorImg
        )

        self.errorPid = self.canvas.create_text(
            402.0,
            345.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.distanceImg = PhotoImage(file=relative_to_assets("distance.png"))
        self.canvas.create_image(
            778.0,
            357.0,
            image=self.distanceImg
        )

        self.distance = self.canvas.create_text(
            678.0,
            345.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.tlImg = PhotoImage(file=relative_to_assets(self.flImgFile))
        self.tlImgId = self.canvas.create_image(
            992.0,
            328.0,
            image=self.tlImg
        )

        self.trImg = PhotoImage(file=relative_to_assets(self.frImgFile))
        self.trImgId = self.canvas.create_image(
            1116.0,
            328.0,
            image=self.trImg
        )

        self.blImg = PhotoImage(file=relative_to_assets(self.blImgFile))
        self.blImgId = self.canvas.create_image(
            992.0,
            387.0,
            image=self.blImg
        )

        self.brImg = PhotoImage(file=relative_to_assets(self.brImgFile))
        self.brImgId = self.canvas.create_image(
            1116.0,
            387.0,
            image=self.brImg
        )

        # Matplotlib plot
        self.fig, self.ax = plt.subplots(figsize=(12.78, 2.51))

        self.x_data = np.linspace(0, 10, 100)
        self.y_data = np.sin(self.x_data)
        self.line, = self.ax.plot(self.x_data, self.y_data)

        self.ax.set_title("Grafik PID")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("PID")

        plt.tight_layout()

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas_plot.get_tk_widget().pack()
        self.canvas_plot.get_tk_widget().place(x=0, y=430)

    ''' Settings Canvas '''
    def settings(self):
        for i in self.window.winfo_children():
            i.destroy()

        self.canvas = Canvas(
            window,
            bg = "#FFFFFF",
            height = 720,
            width = 1280,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            0.0,
            0.0,
            1280.0,
            102.0,
            fill="#3D3669",
            outline="")

        self.imgHeader = PhotoImage(file=relative_to_assets("header.png"))
        self.canvas.create_image(
            233.0,
            65.0,
            image=self.imgHeader
        )

        self.imgToDashboard = PhotoImage(
            file=relative_to_assets("btn-dashboard.png"))
        btnToDashboard = Button(
            image=self.imgToDashboard,
            borderwidth=0,
            highlightthickness=0,
            command=self.dashboard,
            relief="flat"
        )
        btnToDashboard.place(
            x=999.0,
            y=54.0,
            width=202.0,
            height=48.0
        )

        self.canvas.create_text(
            38.0,
            113.0,
            anchor="nw",
            text="Setting Parameter",
            fill="#333333",
            font=("Poppins Medium", 14 * -1)
        )

        self.kpImg = PhotoImage(file=relative_to_assets("proportional.png"))
        self.canvas.create_image(
            364.0,
            219.0,
            image=self.kpImg
        )

        self.kiImg = PhotoImage(file=relative_to_assets("integral.png"))
        self.canvas.create_image(
            640.0,
            219.0,
            image=self.kiImg
        )

        self.kdImg = PhotoImage(file=relative_to_assets("derivative.png"))
        self.canvas.create_image(
            916.0,
            219.0,
            image=self.kdImg
        )

        self.proportional = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.proportional.place(
            x=264.0,
            y=202.0,
            width=200.0,
            height=62.0
        )
        self.proportional.insert(0, str(self.kp))  # Set default KP value from serial

        self.integral = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.integral.place(
            x=540.0,
            y=202.0,
            width=200.0,
            height=62.0
        )
        self.integral.insert(0, str(self.ki))  # Set default KI value from serial

        self.derivative = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.derivative.place(
            x=816.0,
            y=202.0,
            width=200.0,
            height=62.0
        )
        self.derivative.insert(0, str(self.kd))  # Set default KD value from serial

        # self.canvas.create_text(
        #     515.0,
        #     308.0,
        #     anchor="nw",
        #     text="Mode:",
        #     fill="#333333",
        #     font=("Poppins SemiBold", 16 * -1)
        # )

        # self.mode = ttk.Combobox(
        #     values=["Manual", "Auto"],
        #     state="readonly",
        #     justify="center",
        #     font=("Poppins SemiBold", 24 * -1)
        # )

        # self.mode.set("Auto") # set default value
        # self.mode.place(
        #     x=515.0,
        #     y=339.0,
        #     width=250.0,
        #     height=54.0
        # )

        self.imgSave = PhotoImage(file=relative_to_assets("btn-apply.png"))
        btnSave = Button(
            image=self.imgSave,
            borderwidth=0,
            highlightthickness=0,
            command=self.save,
            relief="flat"
        )
        btnSave.place(
            x=518.0,
            y=339.0,
            width=244.0,
            height=57.0
        )

    ''' Save Parameter '''
    def save(self):
        # selectedMode = self.mode.get()
        kp = self.proportional.get()
        ki = self.integral.get()
        kd = self.derivative.get()

        if (not kp or not ki or not kd):
            messagebox.showerror("Invalid Value", "Semua parameter dan mode harus terisi", icon="error")
            return
            
        self.kp = kp
        self.ki = ki
        self.kd = kd

        print("Sending to server:", kp, ki, kd)
        self.sio.emit('message', json.dumps({
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            # "mode": selectedMode
        }))

    ''' Update data in main thread '''
    def update_data(self, data):
        self.window.after(0, self.update, data)

    ''' Update data from event '''
    def update(self, data):
        try:
            data_json = json.loads(data)
            if self.canvas.type(self.yaw) == 'text': self.canvas.itemconfig(self.yaw, text=f"{data_json['yaw']:.2f}")
            if self.pitch: self.canvas.itemconfig(self.pitch, text=f"{data_json['pitch']:.2f}")
            if self.roll: self.canvas.itemconfig(self.roll, text=f"{data_json['roll']:.2f}")
            if self.speed: self.canvas.itemconfig(self.speed, text=f"{data_json['speed']:.2f}")
            if self.pid: self.canvas.itemconfig(self.pid, text=f"{data_json['pid']:.2f}")
            if self.errorPid: self.canvas.itemconfig(self.errorPid, text=f"{data_json['error']:.2f}")
            if self.distance: self.canvas.itemconfig(self.distance, text=f"{data_json['distance']:.1f} m")

            self.flImgFile = "fl-r.png" if data_json['usfl'] == 1 else "fl-g.png"
            self.frImgFile = "fr-r.png" if data_json['usfr'] == 1 else "fr-g.png"
            self.blImgFile = "bl-r.png" if data_json['usbl'] == 1 else "bl-g.png"
            self.brImgFile = "br-r.png" if data_json['usbr'] == 1 else "br-g.png"
            self.tlImg = PhotoImage(file=relative_to_assets(self.flImgFile))
            self.trImg = PhotoImage(file=relative_to_assets(self.frImgFile))
            self.blImg = PhotoImage(file=relative_to_assets(self.blImgFile))
            self.brImg = PhotoImage(file=relative_to_assets(self.brImgFile))
            self.canvas.itemconfig(self.tlImgId, image=self.tlImg)
            self.canvas.itemconfig(self.trImgId, image=self.trImg)
            self.canvas.itemconfig(self.blImgId, image=self.blImg)
            self.canvas.itemconfig(self.brImgId, image=self.brImg)

            if self.kp is None: self.kp = data_json['kp']
            if self.ki is None: self.ki = data_json['ki']
            if self.kd is None: self.kd = data_json['kd']

            direction = "Forward" if data_json['speed'] >= 0 else "Backward"
            if self.canvas.type(self.direction) == 'text': self.canvas.itemconfig(self.direction, text=direction)

            # self.y_data = np.sin(self.x_data + data_json['pitch'])
            # self.line.set_ydata(self.y_data)
            # self.canvas_plot.draw()
        except json.JSONDecodeError:
            print("Error parsing JSON")

        # self.window.after(100, self.on_update)

    ''' SocketIO Connect '''
    def run_socketio(self):
        self.sio.connect(self.serverAddr)
        self.sio.wait()
    
    ''' SocketIO Event Listener '''
    def setup_events(self):
        @self.sio.event
        def connect():
            print("Connected to:", self.serverAddr)
            # self.sio.emit('message', 'Hello, Server!')

        @self.sio.event
        def message(data):
            # self.update(data)
            self.window.after(0, self.update_data, data)
            print("Received from server:", data)
        
        @self.sio.event
        def disconnect():
            print("Disconnected from server:", self.serverAddr)
            self.window.quit()

raspyAddress = input("Input Server IP Address: ") # IP Address of Raspberry Pi
window = Tk()
app(window, raspyAddress)
window.mainloop()
