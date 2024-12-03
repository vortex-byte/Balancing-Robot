from pathlib import Path
from tkinter import Tk, ttk, messagebox, Canvas, Entry, Text, Button, PhotoImage
import socketio
import serial
import json
import keyboard
import threading
import time

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets") # assets folder absolute path

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class app:
    is_manual_control = False
    proportional = 0
    integral = 0
    derivative = 0
    setpoint = None
    ultrasonic = 20 # Ultrasonic Threshold
    speedfactor = None
    kp = None
    ki = None
    kd = None
    flImgFile = "fl-g.png"
    frImgFile = "fr-g.png"
    blImgFile = "bl-g.png"
    brImgFile = "br-g.png"
    switchControlImgFile = "btn-start-control.png"
    wImgFile = "w-inactive.png"
    aImgFile = "a-inactive.png"
    sImgFile = "s-inactive.png"
    dImgFile = "d-inactive.png"

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

        keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        keyboard_thread.start()

        try:
            self.serverAddr = f"http://{ip}:5000"
            self.sio = socketio.Client()
            self.dashboard()
            self.setup_events()
            socket_thread = threading.Thread(target=self.run_socketio, daemon=True)
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

        self.imgToControl = PhotoImage(
            file=relative_to_assets("btn-control.png"))
        btnToControl = Button(
            image=self.imgToControl,
            borderwidth=0,
            highlightthickness=0,
            command=self.manual_control,
            relief="flat"
        )
        btnToControl.place(
            x=777.0,
            y=54.0,
            width=202.0,
            height=48.0
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
            290.0,
            image=self.yawImg
        )

        self.yaw = self.canvas.create_text(
            126.0,
            257.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.pitchImg = PhotoImage(file=relative_to_assets("pitch.png"))
        self.canvas.create_image(
            502.0,
            290.0,
            image=self.pitchImg
        )

        self.pitch = self.canvas.create_text(
            399.0,
            257.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.rollImg = PhotoImage(file=relative_to_assets("roll.png"))
        self.canvas.create_image(
            778.0,
            290.0,
            image=self.rollImg
        )

        self.roll = self.canvas.create_text(
            675.0,
            254.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.speedImg = PhotoImage(file=relative_to_assets("speed.png"))
        self.canvas.create_image(
            1054.0,
            290.0,
            image=self.speedImg
        )

        self.speed = self.canvas.create_text(
            946.0,
            254.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Regular", 64 * -1)
        )

        self.pidImg = PhotoImage(file=relative_to_assets("pid.png"))
        self.canvas.create_image(
            226.0,
            428.0,
            image=self.pidImg
        )

        self.pid = self.canvas.create_text(
            126.0,
            406.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.errorImg = PhotoImage(file=relative_to_assets("error.png"))
        self.canvas.create_image(
            502.0,
            428.0,
            image=self.errorImg
        )

        self.errorPid = self.canvas.create_text(
            402.0,
            406.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.distanceImg = PhotoImage(file=relative_to_assets("distance.png"))
        self.canvas.create_image(
            778.0,
            428.0,
            image=self.distanceImg
        )

        self.distance = self.canvas.create_text(
            678.0,
            406.0,
            anchor="nw",
            text="",
            fill="#333333",
            font=("Poppins Medium", 48 * -1)
        )

        self.flImg = PhotoImage(file=relative_to_assets(self.flImgFile))
        self.flImgId = self.canvas.create_image(
            992.0,
            399.0,
            image=self.flImg
        )

        self.frImg = PhotoImage(file=relative_to_assets(self.frImgFile))
        self.frImgId = self.canvas.create_image(
            1116.0,
            399.0,
            image=self.frImg
        )

        self.blImg = PhotoImage(file=relative_to_assets(self.blImgFile))
        self.blImgId = self.canvas.create_image(
            992.0,
            458.0,
            image=self.blImg
        )

        self.brImg = PhotoImage(file=relative_to_assets(self.brImgFile))
        self.brImgId = self.canvas.create_image(
            1116.0,
            458.0,
            image=self.brImg
        )

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
            outline=""
        )

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
            248.0,
            image=self.kpImg
        )

        self.kiImg = PhotoImage(file=relative_to_assets("integral.png"))
        self.canvas.create_image(
            640.0,
            248.0,
            image=self.kiImg
        )

        self.kdImg = PhotoImage(file=relative_to_assets("derivative.png"))
        self.canvas.create_image(
            916.0,
            248.0,
            image=self.kdImg
        )

        self.setpointImg = PhotoImage(file=relative_to_assets("setpoint.png"))
        self.canvas.create_image(
            359.0,
            403.0,
            image=self.setpointImg
        )

        self.ultrasonicImg = PhotoImage(file=relative_to_assets("ultrasonic.png"))
        self.canvas.create_image(
            640.0,
            403.0,
            image=self.ultrasonicImg
        )

        self.speedFactorImg = PhotoImage(file=relative_to_assets("speedfactor.png"))
        self.canvas.create_image(
            916.0,
            403.0,
            image=self.speedFactorImg
        )

        self.kpInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.kpInput.place(
            x=264.0,
            y=231.0,
            width=200.0,
            height=62.0
        )
        self.kpInput.insert(0, str(self.kp))  # Set default KP value from serial

        self.kiInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.kiInput.place(
            x=540.0,
            y=231.0,
            width=200.0,
            height=62.0
        )
        self.kiInput.insert(0, str(self.ki))  # Set default KI value from serial

        self.kdInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.kdInput.place(
            x=816.0,
            y=231.0,
            width=200.0,
            height=62.0
        )
        self.kdInput.insert(0, str(self.kd))  # Set default KD value from serial

        self.setpointInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.setpointInput.place(
            x=259.0,
            y=390.0,
            width=200.0,
            height=62.0
        )
        self.setpointInput.insert(0, str(self.setpoint))  # Set default Setpoint value from serial

        self.ultrasonicInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.ultrasonicInput.place(
            x=540.0,
            y=390.0,
            width=200.0,
            height=62.0
        )
        self.ultrasonicInput.insert(0, str(self.ultrasonic))  # Set default Ultrasonic threshold value from serial

        self.speedfactorInput = Entry(
            bd=0,
            bg="#F6F7F9",
            fg="#000716",
            font=('Poppins', 48, 'bold'),
            highlightthickness=0
        )
        self.speedfactorInput.place(
            x=816.0,
            y=390.0,
            width=200.0,
            height=62.0
        )
        self.speedfactorInput.insert(0, str(self.speedfactor))  # Set default Speed Factor value from serial

        self.imgSave = PhotoImage(file=relative_to_assets("btn-apply.png"))
        btnSave = Button(
            image=self.imgSave,
            borderwidth=0,
            highlightthickness=0,
            command=self.handle_save,
            relief="flat"
        )
        btnSave.place(
            x=518.0,
            y=500.0,
            width=244.0,
            height=57.0
        )

    ''' Manual Control Canvas '''
    def manual_control(self):
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

        self.imgToDashboard = PhotoImage(file=relative_to_assets("btn-dashboard.png"))
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
            text="Manual Control",
            fill="#333333",
            font=("Poppins Medium", 14 * -1)
        )

        self.switchControlImg = PhotoImage(file=relative_to_assets(self.switchControlImgFile))
        self.switchControlImgId = Button(
            image=self.switchControlImg,
            borderwidth=0,
            highlightthickness=0,
            command=self.handle_control,
            relief="flat"
        )
        self.switchControlImgId.place(
            x=518.0,
            y=500.0,
            width=244.0,
            height=57.0
        )

        self.wImg = PhotoImage(file=relative_to_assets(self.wImgFile))
        self.wImgId = self.canvas.create_image(
            640.0,
            236.0,
            image=self.wImg
        )

        self.aImg = PhotoImage(file=relative_to_assets(self.aImgFile))
        self.aImgId = self.canvas.create_image(
            503.0,
            366.0,
            image=self.aImg
        )

        self.sImg = PhotoImage(file=relative_to_assets(self.sImgFile))
        self.sImgId = self.canvas.create_image(
            640.0,
            366.0,
            image=self.sImg
        )

        self.dImg = PhotoImage(file=relative_to_assets(self.dImgFile))
        self.dImgId = self.canvas.create_image(
            777.0,
            366.0,
            image=self.dImg
        )

    ''' Handle Save Parameter '''
    def handle_save(self):
        try:
            self.kp = float(self.kpInput.get())
            self.ki = float(self.kiInput.get())
            self.kd = float(self.kdInput.get())
            self.ultrasonic = int(self.ultrasonicInput.get())
            self.speedfactor = float(self.speedfactorInput.get())
            self.setpoint = float(self.setpointInput.get())

            # print("Sending to server:", kp, ki, kd)
            dataToSend = json.dumps({
                "kp": self.kp,
                "ki": self.ki,
                "kd": self.kd,
                "setpoint": self.setpoint,
                # "threshold": self.ultrasonic,
                # "speedfactor": self.speedfactor,
            })
            self.sio.emit('message', dataToSend)
        except ValueError:
            messagebox.showerror("Invalid Value", "Parameter harus terisi", icon="error")
            return
        except Exception as e:
            err = "Gagal mengirim pesan. Periksa kembali koneksi Websocket"
            print(err)
            messagebox.showerror("Failed send message", err, icon="error")
            self.window.quit()
            return

    ''' Handle Manual Control '''
    def handle_control(self):
        self.is_manual_control = not self.is_manual_control
        self.switchControlImgFile = "btn-stop-control.png" if self.is_manual_control else "btn-start-control.png"
        self.switchControlImg = PhotoImage(file=relative_to_assets(self.switchControlImgFile))
        self.switchControlImgId.config(image=self.switchControlImg)

    ''' Handle Keyboard Event '''
    def keyboard_listener(self):
        allowed = ["w", "a", "s", "d"]
        while True:
            if self.is_manual_control == True:
                for key in allowed:
                    # pressed = "active" if keyboard.is_pressed(key) else "inactive"
                    if keyboard.is_pressed(key):
                        img_file = f"{key}-active.png"
                        img = PhotoImage(file=relative_to_assets(img_file))
                        
                        setattr(self, f"{key}ImgFile", img_file)
                        setattr(self, f"{key}Img", img)
                        
                        img_id = getattr(self, f"{key}ImgId")
                        self.canvas.itemconfig(img_id, image=img)
                        
                        try:
                            self.sio.emit('message', json.dumps({
                                "a": "c",
                                "direction": key,
                            }))
                        except Exception as e:
                            err = "Gagal mengirim pesan. Periksa kembali koneksi Websocket"
                            print(err)
                            messagebox.showerror("Failed send message", err, icon="error")
                            self.window.quit()
                            return
                    else:
                        img_file = f"{key}-inactive.png"
                        img = PhotoImage(file=relative_to_assets(img_file))
                        
                        setattr(self, f"{key}ImgFile", img_file)
                        setattr(self, f"{key}Img", img)
                        
                        img_id = getattr(self, f"{key}ImgId")
                        self.canvas.itemconfig(img_id, image=img)

                        try:
                            self.sio.emit('message', json.dumps({
                                "a": "c",
                                "direction": "x",
                            }))
                        except Exception as e:
                            err = "Gagal mengirim pesan. Periksa kembali koneksi Websocket"
                            print(err)
                            messagebox.showerror("Failed send message", err, icon="error")
                            self.window.quit()
                            return

            time.sleep(0.1)

    ''' Forward new data to main thread '''
    def forward_data(self, data):
        self.window.after(0, self.update, data)

    ''' Update data from event '''
    def update(self, data):
        try:
            data_json = json.loads(data)
            if self.canvas.type(self.yaw) == 'text': self.canvas.itemconfig(self.yaw, text=f"{data_json['yaw']:.2f}")
            if self.canvas.type(self.pitch) == 'text': self.canvas.itemconfig(self.pitch, text=f"{data_json['pitch']:.2f}")
            if self.canvas.type(self.roll) == 'text': self.canvas.itemconfig(self.roll, text=f"{data_json['roll']:.2f}")
            if self.canvas.type(self.speed) == 'text': self.canvas.itemconfig(self.speed, text=f"{data_json['speed']:.2f}")
            if self.canvas.type(self.pid) == 'text': self.canvas.itemconfig(self.pid, text=f"{data_json['pid']:.2f}")
            if self.canvas.type(self.errorPid) == 'text': self.canvas.itemconfig(self.errorPid, text=f"{data_json['error']:.2f}")
            if self.canvas.type(self.distance) == 'text': self.canvas.itemconfig(self.distance, text=f"{data_json['distance']:.1f} m")

            self.setpoint = f"{data_json['setpoint']:.2f}"
            self.speedfactor = f"{data_json['speedfactor']:.2f}"

            self.flImgFile = "fl-r.png" if data_json['usfl'] < self.ultrasonic else "fl-g.png" # Red if there is obstacle
            self.frImgFile = "fr-r.png" if data_json['usfr'] < self.ultrasonic else "fr-g.png"
            self.blImgFile = "bl-r.png" if data_json['usbl'] < self.ultrasonic else "bl-g.png"
            self.brImgFile = "br-r.png" if data_json['usbr'] < self.ultrasonic else "br-g.png"
            self.flImg = PhotoImage(file=relative_to_assets(self.flImgFile))
            self.frImg = PhotoImage(file=relative_to_assets(self.frImgFile))
            self.blImg = PhotoImage(file=relative_to_assets(self.blImgFile))
            self.brImg = PhotoImage(file=relative_to_assets(self.brImgFile))
            self.canvas.itemconfig(self.flImgId, image=self.flImg)
            self.canvas.itemconfig(self.frImgId, image=self.frImg)
            self.canvas.itemconfig(self.blImgId, image=self.blImg)
            self.canvas.itemconfig(self.brImgId, image=self.brImg)

            if self.kp is None: self.kp = data_json['kp']
            if self.ki is None: self.ki = data_json['ki']
            if self.kd is None: self.kd = data_json['kd']

            direction = "Forward" if data_json['speed'] >= 0 else "Backward"
            if self.canvas.type(self.direction) == 'text': self.canvas.itemconfig(self.direction, text=direction)
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

        @self.sio.event
        def message(data):
            self.window.after(0, self.forward_data, data)
            print("Received from server:", data)
        
        @self.sio.event
        def disconnect():
            print("Disconnected from server:", self.serverAddr)
            messagebox.showerror("Disconnected from server", "GUI disconnected from server", icon="error")
            self.window.quit()
            return

raspyAddress = input("Input Server IP Address: ") # IP Address of Raspberry Pi
window = Tk()
app(window, raspyAddress)
window.mainloop()
