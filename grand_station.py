import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from threading import Thread
import base64
import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import folium
import webview
from PIL import Image, ImageTk
import io
from datetime import datetime
import pandas as pd

comand="コマンド一覧\ndestination: サンプル採取地点または\nゴール地点の緯度、経度の変更\nfall:機体の落下開始判定\nlanding:機体の着地判定\nmanual:手動制御\n***以降manualで使用***\npicture:写真撮影\nsoil_moisture:土壌水分測定\nsample:サンプル採取\nw:前進\na:左旋回\nd:右旋回\ns:後退" 


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Serial Communication")
        #self.geometry("1000x600")

        #通信ボタン
        self.button = tk.Button(self, text="Start Communication", command=self.toggle_communication)
        self.button.pack(anchor='ne',padx=10, pady=10)
        self.serial_port = None
        self.is_serial_connected = False
        self.after(100, self.read_serial_data)  # シリアルデータの読み込みを開始


        #tab
        self.notebook = ttk.Notebook(self)
        tab1 = Frame(self)  #main用
        tab2 = Frame(self)  #graph用
        self.notebook.add(tab1,text="main")
        self.notebook.add(tab2,text="graph")
        self.notebook.pack(expand=True,fill="both")
        

        #右側コマンド系frame
        self.right = tk.Canvas(tab1, width=280, height=200, borderwidth=0, highlightthickness=0)
        self.command_frame = tk.Frame(self.right)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.right.create_window((0, 0), window=self.command_frame, anchor=tk.NW)


        #左側データ表示用frame
        self.canvasleft = tk.Canvas(tab1, width=250, height=200, borderwidth=0, highlightthickness=0)
        self.scrollable_lframe = tk.Frame(self.canvasleft)

        self.vsb = tk.Scrollbar(self.scrollable_lframe, orient=tk.VERTICAL, command=self.canvasleft.yview)
        self.canvasleft.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.canvasleft.pack(side=tk.LEFT, fill=tk.BOTH)
        self.canvasleft.create_window((0, 0), window=self.scrollable_lframe, anchor=tk.NW)

        self.scrollable_lframe.bind("<Configure>", self.on_frame_configure)


        #データ表示用
        self.time_label = tk.Label(self.scrollable_lframe, text="Time:", font=("Arial", 11))
        self.time_label.pack(anchor='nw',pady=10)

        self.latitude_label = tk.Label(self.scrollable_lframe, text="Latitude:", font=("Arial", 11))
        self.latitude_label.pack(anchor='nw',pady=10)

        self.longitude_label = tk.Label(self.scrollable_lframe, text="Longitude:", font=("Arial", 11))
        self.longitude_label.pack(anchor='nw',pady=10)

        self.altitude_label = tk.Label(self.scrollable_lframe, text="Altitude:", font=("Arial", 11))
        self.altitude_label.pack(anchor='nw',pady=10)

        self.sample_distance_label = tk.Label(self.scrollable_lframe, text="Sample Distance:", font=("Arial", 11))
        self.sample_distance_label.pack(anchor='nw',pady=10)

        self.sample_azimuth_label = tk.Label(self.scrollable_lframe, text="Sample Azimuth:", font=("Arial", 11))
        self.sample_azimuth_label.pack(anchor='nw',pady=10)

        self.goal_distance_label = tk.Label(self.scrollable_lframe, text="Goal Distance:", font=("Arial", 11))
        self.goal_distance_label.pack(anchor='nw',pady=10)

        self.goal_azimuth_label = tk.Label(self.scrollable_lframe, text="Goal Azimuth:", font=("Arial", 11))
        self.goal_azimuth_label.pack(anchor='nw',pady=10)

        self.acceleration_x_label = tk.Label(self.scrollable_lframe, text="Acceleration X:", font=("Arial", 11))
        self.acceleration_x_label.pack(anchor='nw',pady=10)

        self.acceleration_y_label = tk.Label(self.scrollable_lframe, text="Acceleration Y:", font=("Arial", 11))
        self.acceleration_y_label.pack(anchor='nw',pady=10)

        self.acceleration_z_label = tk.Label(self.scrollable_lframe, text="Acceleration Z:", font=("Arial", 11))
        self.acceleration_z_label.pack(anchor='nw',pady=10)

        self.angular_velocity_x_label = tk.Label(self.scrollable_lframe, text="Angular Velocity X:", font=("Arial", 11))
        self.angular_velocity_x_label.pack(anchor='nw',pady=10)

        self.angular_velocity_y_label = tk.Label(self.scrollable_lframe, text="Angular Velocity Y:", font=("Arial", 11))
        self.angular_velocity_y_label.pack(anchor='nw',pady=10)

        self.angular_velocity_z_label = tk.Label(self.scrollable_lframe, text="Angular Velocity Z:", font=("Arial", 11))
        self.angular_velocity_z_label.pack(anchor='nw',pady=10)

        self.temperature_label = tk.Label(self.scrollable_lframe, text="Temperature:", font=("Arial", 11))
        self.temperature_label.pack(anchor='nw',pady=10)

        self.humidity_label = tk.Label(self.scrollable_lframe, text="Humidity:", font=("Arial", 11))
        self.humidity_label.pack(anchor='nw',pady=10)

        self.pressure_label = tk.Label(self.scrollable_lframe, text="Pressure:", font=("Arial", 11))
        self.pressure_label.pack(anchor='nw',pady=10)

        self.pressure_temperature_label = tk.Label(self.scrollable_lframe, text="Pressure Temperature:", font=("Arial", 11))
        self.pressure_temperature_label.pack(anchor='nw',pady=10)

        self.pressure_altitude_label = tk.Label(self.scrollable_lframe, text="Pressure Altitude:", font=("Arial", 11))
        self.pressure_altitude_label.pack(anchor='nw',pady=10)

        self.battery_label = tk.Label(self.scrollable_lframe, text="Battery:", font=("Arial", 11))
        self.battery_label.pack(anchor='nw',pady=10)

        self.distance_label = tk.Label(self.scrollable_lframe, text="Distance:", font=("Arial", 11))
        self.distance_label.pack(anchor='nw',pady=10)


        #command送信用
        self.sendframe = tk.Frame(self.command_frame)
        self.sendframe.pack(anchor='ne')

        self.send_button = tk.Button(self.sendframe, text="Send Data", command=self.send_data)
        self.send_button.pack(side='right',pady=10,expand=True)
        self.entry= tk.Entry(self.sendframe)
        self.entry.pack(side='right',pady=10,expand=True)

        self.comand_label = tk.Label(self.command_frame, text=comand, font=("Arial", 10))
        self.comand_label.pack(pady=10)

        self.data_text = tk.Text(self.command_frame, width=35, height=2)
        self.data_text.pack(pady=10,expand=True)
        

        #グラフ
        self.graphframe= tk.Frame(tab2)
        fig =Figure()
        self.acx=fig.add_subplot(6,2,1)
        self.acx.set_xlabel("Time")
        self.acx.set_ylabel("Acc X")
        self.acy=fig.add_subplot(6,2,2)
        self.acy.set_xlabel("Time")
        self.acy.set_ylabel("Acc Y")
        self.acz=fig.add_subplot(6,2,3)
        self.acz.set_xlabel("Time")
        self.acz.set_ylabel("Acc Z")
        self.avx=fig.add_subplot(6,2,4)
        self.avx.set_xlabel("Time")
        self.avx.set_ylabel("ang X")
        self.avy=fig.add_subplot(6,2,5)
        self.avy.set_xlabel("Time")
        self.avy.set_ylabel("ang Y")
        self.avz=fig.add_subplot(6,2,6)
        self.avz.set_xlabel("Time")
        self.avz.set_ylabel("ang Z")
        self.tem=fig.add_subplot(6,2,7)
        self.tem.set_xlabel("Time")
        self.tem.set_ylabel("Temperature")
        self.hum=fig.add_subplot(6,2,8)
        self.hum.set_xlabel("Time")
        self.hum.set_ylabel("Humidity")
        self.pre=fig.add_subplot(6,2,9)
        self.pre.set_xlabel("Time")
        self.pre.set_ylabel("Pressure")
        self.bat=fig.add_subplot(6,2,10)
        self.bat.set_xlabel("Time")
        self.bat.set_ylabel("Battery")
        self.dis=fig.add_subplot(6,2,11)
        self.dis.set_xlabel("Time")
        self.dis.set_ylabel("Distance")

        self.fig_canvas=FigureCanvasTkAgg(fig, self.graphframe)
        self.fig_canvas.get_tk_widget().pack(anchor='center',fill=tk.BOTH, expand=True)
        self.graphframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.graphframe.bind("<Configure>", self.on_frame_configure)
        fig.tight_layout()

        #姿勢制御用


        #地図写真用frame
        self.center=tk.Frame(tab1)
        self.center.pack(fill=tk.BOTH, expand=True)

        #写真用キャンバス
        self.cvs = tk.Canvas(self.center,width=300, height=300)
        self.cvs.pack(expand=True)

        # 地図表示用のフレーム
        self.map_frame = tk.Frame(self.center)
        self.map_frame.pack(expand=True)



        self.protocol("WM_DELETE_WINDOW", self.close)

        # データ
        self.time_data = []
        self.acceleration_x_data = []
        self.acceleration_y_data = []
        self.acceleration_z_data = []
        self.angularvelocity_x_data = []
        self.angularvelocity_y_data = []
        self.angularvelocity_z_data = []
        self.Temperature_data = []
        self.Humidity_data = []
        self.Pressure_data = []
        self.coordinates = []
        self.battery_data = []
        self.distance_data = []
    
    
    def on_frame_configure(self, event):
        self.canvasleft.configure(scrollregion=self.canvasleft.bbox("all"))
        #self.canvasright.configure(scrollregion=self.canvasright.bbox("all"))
        #self.graphframe.configure(scrollregion=self.canvasright.bbox("all"))
    
    def toggle_communication(self):
        if not self.is_serial_connected:
            try:
                self.serial_port = serial.Serial("COM7", 9600)
                self.is_serial_connected = True
                self.button.configure(text="Stop Communication")
                self.read_serial_data()
            except serial.SerialException as e:
                messagebox.showerror("Error", str(e))
        else:
            self.is_serial_connected = False
            self.serial_port.close()
            self.button.configure(text="Start Communication")



    def read_serial_data(self):
        def read_data():
            while self.is_serial_connected:
                try:
                    data = self.serial_port.readline().decode("utf-8").strip()
                    decoded_data = base64.b64decode(data).decode("utf-8")
                    json_data = json.loads(decoded_data)
                    if "時間" in data and "GPS" in data:
                        self.update_data(json_data)
                        self.save_to_excel(json_data)
                    elif "時間" in data and "title" in data:
                        self.text_data(json_data)
                    else:
                        self.photo_data(decoded_data)
                except Exception as e:
                    print(str(e))


        Thread(target=read_data, daemon=True).start()

    def send_data(self):
        if self.is_serial_connected:
            try:
                data = self.entry.get().strip()
                data= data + '\n'
                encoded_data=data.encode('utf-8')
                self.serial_port.write(encoded_data)
                #messagebox.showinfo("Success", "Data sent successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Serial connection is not established.")

    def update_data(self, data):
        time = data.get("時間")
        gps = data.get("GPS")
        sample = gps.get("サンプル")
        goal = gps.get("ゴール")
        nine_axis = data.get("9軸")
        temperature_pressure = data.get("温湿度気圧")
        pressure = data.get("気圧")
        battery = data.get("電池")
        distance = data.get("距離")
        picture = data.get("写真")

        #データ表示
        self.time_label.configure(text=f"Time: {time}")
        self.latitude_label.configure(text=f"Latitude: {gps['緯度']}")
        self.longitude_label.configure(text=f"Longitude: {gps['経度']}")
        self.altitude_label.configure(text=f"Altitude: {gps['海抜']}")
        self.sample_distance_label.configure(text=f"Sample Distance: {sample['直線距離']}")
        self.sample_azimuth_label.configure(text=f"Sample Azimuth: {sample['方位角']}")
        self.goal_distance_label.configure(text=f"Goal Distance: {goal['直線距離']}")
        self.goal_azimuth_label.configure(text=f"Goal Azimuth: {goal['方位角']}")
        self.acceleration_x_label.configure(text=f"Acceleration X: {nine_axis['加速度']['X']}")
        self.acceleration_y_label.configure(text=f"Acceleration Y: {nine_axis['加速度']['Y']}")
        self.acceleration_z_label.configure(text=f"Acceleration Z: {nine_axis['加速度']['Z']}")
        self.angular_velocity_x_label.configure(text=f"Angular Velocity X: {nine_axis['角速度']['X']}")
        self.angular_velocity_y_label.configure(text=f"Angular Velocity Y: {nine_axis['角速度']['Y']}")
        self.angular_velocity_z_label.configure(text=f"Angular Velocity Z: {nine_axis['角速度']['Z']}")
        self.temperature_label.configure(text=f"Temperature: {temperature_pressure['温度']}")
        self.humidity_label.configure(text=f"Humidity: {temperature_pressure['湿度']}")
        self.pressure_label.configure(text=f"Pressure: {temperature_pressure['気圧']}")
        self.pressure_temperature_label.configure(text=f"Pressure Temperature: {pressure['温度']}")
        self.pressure_altitude_label.configure(text=f"Pressure Altitude: {pressure['高度']}")
        self.battery_label.configure(text=f"Battery: {battery}")
        self.distance_label.configure(text=f"Distance: {distance}")


        # データを取得、追加
        self.time_data.append(time)
        acceleration_x = nine_axis['加速度']['X']
        self.acceleration_x_data.append(acceleration_x)
        acceleration_y = nine_axis['加速度']['Y']
        self.acceleration_y_data.append(acceleration_y)
        acceleration_z = nine_axis['加速度']['Z']
        self.acceleration_z_data.append(acceleration_z)
        angularvelocity_x = nine_axis['角速度']['X']
        self.angularvelocity_x_data.append(angularvelocity_x)
        angularvelocity_y = nine_axis['角速度']['Y']
        self.angularvelocity_y_data.append(angularvelocity_y)
        angularvelocity_z = nine_axis['角速度']['Z']
        self.angularvelocity_z_data.append(angularvelocity_z)
        Temperature = temperature_pressure['温度']
        self.Temperature_data.append(Temperature)
        Humidity = temperature_pressure['湿度']
        self.Humidity_data.append(Humidity)
        Pressure = temperature_pressure['気圧']
        self.Pressure_data.append(Pressure)
        Latitude = gps['緯度']
        Longitude = gps['経度']
        self.coordinates.append((Latitude, Longitude))
        battery = gps['電池']
        self.battery_data.append((battery))
        distance = ['距離']
        self.distance_data.append((distance))


        # フレームをクリア
        for widget in self.map_frame.winfo_children():
            widget.destroy()

        # 地図を作成
        m = folium.Map(location=[40.1438927, 139.9869409], zoom_start=20)

        # 座標にピンを立てる
        for coord in self.coordinates:
            folium.Marker(coord).add_to(m)

        # 座標を線で結ぶ
        folium.PolyLine(self.coordinates, color='blue').add_to(m)

        # 地図をHTMLファイルに保存
        map_file = "map.html"
        m.save(map_file)

        # WebViewを表示
        self.map_frame = webview.create_window("Map", url=map_file)
        webview.start()


        #写真を表示
        img_stream = io.BytesIO(picture)
        img = Image.open(img_stream)
        img = img.resize((200, 150))
        photo = ImageTk.PhotoImage(img)
        self.cvs.create_image(100,100,image=photo,tag="mytest")
        self.cvs.image = photo


        # グラフにデータをプロット
        self.acx.clear()
        self.acx.plot(self.time_data, self.acceleration_x_data)
        
        self.acy.clear()
        self.acy.plot(self.time_data, self.acceleration_y_data)
        
        self.acz.clear()
        self.acz.plot(self.time_data, self.acceleration_z_data)
        
        self.avx.clear()
        self.avx.plot(self.time_data, self.angularvelocity_x_data)
        
        self.avy.clear()
        self.avy.plot(self.time_data, self.angularvelocity_y_data)

        self.avz.clear()
        self.avz.plot(self.time_data, self.angularvelocity_z_data)

        self.tem.clear()
        self.tem.plot(self.time_data, self.Temperature_data)

        self.hum.clear()
        self.hum.plot(self.time_data, self.Humidity_data)

        self.pre.clear()
        self.pre.plot(self.time_data, self.Pressure_data)

        self.bat.clear()
        self.bat.plot(self.time_data, self.battery_data)

        self.dis.clear()
        self.dis.plot(self.time_data, self.distance_data)

        self.fig_canvas.draw()


    def text_data(self,data):
        time = data.get("時間")
        title = data.get("title")
        message = data.get("message")
        self.data_text.config(text=f"時間: {time}")
        self.data_text.config(text=f"タイトル: {title}")
        self.data_text.config(text=f"メッセージ: {message}")


    #datasave
    def save_to_excel(self, data):
        df = pd.DataFrame(data)
        # Excelファイル名を生成
        now = datetime.now()
        excel_file_name = now.strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx"
        df.to_excel(excel_file_name, index=False)


    def photo_data(self,data):
        img_stream = io.BytesIO(data)
        img = Image.open(img_stream)
        img = img.resize((200, 150))
        photo = ImageTk.PhotoImage(img)
        self.cvs.create_image(200,150,image=photo,tag="mytest")
        self.cvs.image = photo

    
    def close(self):
        self.is_serial_connected = False
        if self.serial_port:
            self.serial_port.close()
        self.destroy()
    

    #スクロールバー
    class ScrollableFrame(tk.Frame):
        def __init__(self, parent, *args, **kwargs):
            super().__init__(parent, *args, **kwargs)

            self.canvas = tk.Canvas(self, width=300, height=0, borderwidth=0, highlightthickness=0)
            self.scrollable_frame = tk.Frame(self.canvas)

            self.vsb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vsb.set)

            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

            self.scrollable_frame.bind("<Configure>", self.on_frame_configure)



app = App()
app.mainloop()
