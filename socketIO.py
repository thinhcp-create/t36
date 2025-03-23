import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from guiHandle import guiHandle
import serial
import serial.tools.list_ports
import serial.serialutil
import threading
import queue
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
import socketio
import json
import os
import subprocess
import sys
import base64
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QImage
import serial
import pynmea2
from datetime import datetime, timedelta
import subprocess
import time
import locale
import server
from datetime import datetime
import design
import re
import socketio
import json
import os
import time
import threading
import subprocess
from playsound import playsound
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
import serial.tools.list_ports
global gps
global timeout,timeoutflag,t
timeout = 0
t = 0
timeoutflag = False
gps = False
def find_usb_serial_port(baudrate=9600, timeout=0.1):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device.startswith('/dev/ttyUSB'):
            try:
                ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
                print(f"Kết nối thành công với {port.device}")
                return ser
            except serial.SerialException as e:
                print(f"Không thể mở {port.device}: {e}")
    print("Không tìm thấy cổng /dev/ttyUSB nào hoạt động.")

def decimal_to_dms(decimal):
    degrees = int(decimal)
    minutes_float = (decimal - degrees) * 60
    minutes = int(minutes_float)
    seconds = float((minutes_float - minutes) * 60)
    return f"{degrees}°{minutes}'{seconds:.1f}\""
def get_route_code(route_str):
    """
    Hàm lấy mã tuyến (số) từ chuỗi dạng '01 : BX Gia Lâm - BX Yên Nghĩa'.
    Nếu không tìm thấy mã, trả về None.
    """
    match = re.match(r"^\s*(\d+)\s*:", route_str)
    return match.group(1) if match else None
def get_station(lat, lon):
    stations = {
        "A": {"lat_min": 20.95, "lat_max": 20.99, "lon_min": 105.82, "lon_max": 105.85},
        "B": {"lat_min": 20.90, "lat_max": 20.94, "lon_min": 105.84, "lon_max": 105.87},
        "C": {"lat_min": 20.95, "lat_max": 21.00, "lon_min": 105.87, "lon_max": 105.90},
        "D": {"lat_min": 20.97, "lat_max": 21.01, "lon_min": 105.88, "lon_max": 105.92},
    }
    for station, bounds in stations.items():
        if bounds["lat_min"] <= lat <= bounds["lat_max"] and bounds["lon_min"] <= lon <= bounds["lon_max"]:
            return station
    return "N/A"

class UARTReceiveThread(threading.Thread):
    def __init__(self,mySocket, ser, queue_uart):
        super().__init__()
        self.ser = ser
        self.queue_uart = queue_uart
        self.running = True
        self.mySocket = mySocket
        if self.ser is not None and self.ser.is_open == True:
            self.mySocket.toa_do.setText("Đang chờ dữ liệu GPS...")
            self.mySocket.tram_xe.setText("N/A")
        
        # print("Đang chờ dữ liệu GPS...")
    def run(self):
        global timeout,timeoutflag,t
        while self.running:
            if self.ser is None or self.ser.is_open == False:
                time.sleep(1)
                try:
                    self.ser = find_usb_serial_port()
                    if self.ser is not None and self.ser.is_open == True:
                        self.mySocket.toa_do.setStyleSheet("color: black")
                        self.mySocket.toa_do.setText("Đang chờ dữ liệu GPS...")
                        self.mySocket.tram_xe.setText("N/A")
                    else:
                        self.mySocket.toa_do.setStyleSheet("color: red")
                        self.mySocket.toa_do.setText("Không thể kết nối với module GPS!")
                except serial.SerialException:
                    print("Không thể kết nối với module GPS! Kiểm tra cổng COM.")
                continue
            # if timeoutflag == False:
            #     t = time.time()
                # print(t)
            if timeoutflag == True:
                if time.time() - t > timeout:
                    self.mySocket.so_cccd.setText("")
                    self.mySocket.ngay_cap.setText("")
                    self.mySocket.ngay_het_han.setText("")
                    self.mySocket.ho_ten.setText("")
                    self.mySocket.ngay_sinh.setText("")
                    self.mySocket.gioi_tinh.setText("")
                    self.mySocket.que_quan.setText("")
                    self.mySocket.quoc_tich.setText("")
                    self.mySocket.avt.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/cccd.jpg"))
                    # print("Đã xóa toàn bộ dữ liệu hiển thị")
                    timeoutflag = False
                    t = time.time()
            try:
                if self.ser.is_open and self.ser.in_waiting > 0:
                    try:
                        data = self.ser.readline().decode(errors='ignore').strip()
                        if data.startswith("$GPGGA") or data.startswith("$GNGGA"):
                            try:
                                msg = pynmea2.parse(data)
                                # Kiểm tra độ tin cậy
                                if float(msg.gps_qual) < 1 or int(msg.num_sats) < 2 or float(msg.horizontal_dil) > 4.0:
                                    locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
                                    system_time = time.strftime("%A, %H:%M:%S - %d/%m/%Y ", time.localtime())  
                                    self.mySocket.time.setText(system_time)
                                    # print(f"Thời gian: {system_time}")
                                    continue
                                # print(msg.latitude)
                                # print(msg.longitude)
                                self.mySocket.tram_xe.setText(get_station(msg.latitude, msg.longitude))
                                lat_dms = decimal_to_dms(msg.latitude) + msg.lat_dir
                                lon_dms = decimal_to_dms(msg.longitude) + msg.lon_dir
                                locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
                                system_time = time.strftime("%A, %H:%M:%S - %d/%m/%Y ", time.localtime())  
                                self.mySocket.time.setText(system_time)
                                self.mySocket.toa_do.setText(f"{lat_dms} {lon_dms}")
                                # print(f"Vĩ độ: {lat_dms}")
                                # print(f"Kinh độ: {lon_dms:}")
                                # print("-" * 40)

                            except pynmea2.ParseError:
                                continue
                    except (serial.SerialException, OSError) as e:
                        # self.mySocket.log.setText(f"UART Receive Error: {e}")
                        print(f"UART Receive Error: {e}")
            except (serial.SerialException, OSError) as e:
                self.mySocket.toa_do.setStyleSheet("color: red")
                self.mySocket.tram_xe.setText("")
                self.ser.is_open = False
                self.mySocket.toa_do.setText("Không thể kết nối với module GPS!")
            time.sleep(0.01)

    def stop(self):
        self.running = False


def mask_last_four_digits(original_str):
    masked_str = original_str[:-4] + "****" if len(original_str) > 4 else ""
    return masked_str
# Xử lý cho máy đọc
def base64_to_pixmap(base64_string):
    """Chuyển chuỗi base64 thành QPixmap"""
    image_data = base64.b64decode(base64_string)
    pixmap = QPixmap()
    pixmap.loadFromData(image_data)
    return pixmap
class mySocketClass(guiHandle):
    def __init__(self,mygui,so_cccd,ngay_cap,ngay_het_han,ho_ten,ngay_sinh,gioi_tinh,que_quan,quoc_tich):
        # print('inited mySocket instance inherit from ',super().nameClass)
        guiHandle.__init__(self,mygui)
    

class socketThreadClass(threading.Thread):
    def __init__(self, mySocket, sio):
        super().__init__()
        self.mySocket = mySocket
        self.sio = sio
        self.register_events()

    def register_events(self):
        @self.sio.event
        def connect():
            self.mySocket.label_status.setText('')
            # print('Đã kết nối đến máy chủ.')

        @self.sio.event
        def disconnect():
            self.mySocket.label_status.setText('Chưa kết nối thiết bị')
            # print('Đã ngắt kết nối khỏi máy chủ.')

        @self.sio.on('/event')
        def on_event(data):
            global g_so_cccd, g_ngay_cap, g_ngay_het_han, g_ho_ten, g_ngay_sinh, g_gioi_tinh, g_que_quan
            try:
                if isinstance(data, dict) and data.get('id') == 4 and "data" in data:
                    info = data["data"]  # Trích xuất dữ liệu con trong "data"
                    img = info.get("img_data", "")
                    pixmap = base64_to_pixmap(img)
                    self.mySocket.avt.setPixmap(pixmap)
                    self.mySocket.avt.setScaledContents(True)  # Căn chỉnh kích thước tự động
                # Kiểm tra nếu `data` là dictionary và có 'id' = 2
                if isinstance(data, dict) and data.get('id') == 2 and "data" in data:
                    info = data["data"]  # Trích xuất dữ liệu con trong "data"

                    # Gán giá trị vào các biến toàn cục
                    g_so_cccd = info.get("idCode", "")
                    g_ngay_cap = info.get("issueDate", "")
                    g_ngay_het_han = info.get("expiryDate", "")
                    g_ho_ten = info.get("personName", "")
                    g_ngay_sinh = info.get("dateOfBirth", "")
                    g_gioi_tinh = info.get("gender", "")
                    g_que_quan = info.get("originPlace", "")
                    g_quoc_tich = info.get("nationality", "")
                    # In ra để kiểm tra
                    
                    self.mySocket.so_cccd.setText(mask_last_four_digits(g_so_cccd))
                    self.mySocket.ngay_cap.setText(g_ngay_cap)
                    self.mySocket.ngay_het_han.setText(g_ngay_het_han)
                    self.mySocket.ho_ten.setText(g_ho_ten)
                    self.mySocket.ngay_sinh.setText(g_ngay_sinh)
                    self.mySocket.gioi_tinh.setText(g_gioi_tinh)
                    self.mySocket.que_quan.setText(g_que_quan)
                    self.mySocket.quoc_tich.setText(g_quoc_tich)
                    self.mySocket.so_cccd.text
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data = f"time:{current_time}\nid:{g_so_cccd}\nname:{self.mySocket.ho_ten.text()}\nbirth:{self.mySocket.ngay_sinh.text()}\ngender:{self.mySocket.gioi_tinh.text()}\nnationality:{self.mySocket.quoc_tich.text()}\ntram:{self.mySocket.tram_xe.text()}\ntuyen:{get_route_code(self.mySocket.tuyen.text())}\nbien:{self.mySocket.bien_so.text()}"
                    print(data)
                    target_url = "http://nguyengiang2603-1.infinityfreeapp.com/project/recieve_json.php"
                    query_params = {
                        "text":{data},
                    }
                    status, content = server.bypass_infinityfree(target_url, query_params)
                    print(f"Status: {status}")
                    print(content)
                    g_so_cccd = ""
                    g_ngay_cap = ""
                    g_ngay_het_han = ""
                    g_ho_ten = ""
                    g_ngay_sinh = ""
                    g_gioi_tinh = ""
                    g_que_quan = ""
                    g_quoc_tich = ""
                    global timeout,timeoutflag,t
                    timeout = 60
                    timeoutflag = True
                    t = time.time()
                    # print(f"CCCD: {g_so_cccd}")
                    # print(f"Ngày cấp: {g_ngay_cap}")
                    # print(f"Ngày hết hạn: {g_ngay_het_han}")
                    # print(f"Họ tên: {g_ho_ten}")
                    # print(f"Ngày sinh: {g_ngay_sinh}")
                    # print(f"Giới tính: {g_gioi_tinh}")
                    # print(f"Quê quán: {g_que_quan}")

            except Exception as e:
                print(f"Lỗi khi xử lý dữ liệu: {e}")


    def run(self):
        while True:
            try:
                self.sio.connect('http://192.168.5.1:8000')
                self.sio.wait()
            except Exception as e:
                # print(f"Socket connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(1)


        
def runTest():
    global g_so_cccd , g_ngay_cap,g_ngay_het_han,g_ho_ten,g_ngay_sinh,g_gioi_tinh,g_que_quan,g_quoc_tich,g_x,g_y
    g_so_cccd = ""
    g_ngay_cap = ""
    g_ngay_het_han = ""
    g_ho_ten = ""
    g_ngay_sinh = ""
    g_gioi_tinh = ""
    g_que_quan = ""
    g_quoc_tich = ""
    g_x = ""
    g_y = ""
    # queueSer = queue.Queue(maxsize= 1)
    # queueSend = queue.Queue(maxsize= 10)
    # queueRev = queue.Queue(maxsize= 1)
    # queueMusic = queue.Queue(maxsize= 1)
    app = QApplication([])
    ui= QMainWindow()
    # ui.setWindowIcon(QtGui.QIcon('mydata/mkp.ico'))
    gui= guiHandle(ui)
    sio = socketio.Client()
    mySocket = mySocketClass(ui,g_so_cccd, g_ngay_cap,g_ngay_het_han,g_ho_ten,g_ngay_sinh,g_gioi_tinh,g_que_quan,g_quoc_tich)
    ser = None
    try:
        ser = find_usb_serial_port()
    except serial.SerialException: 
        mySocket.toa_do.setStyleSheet("color: red")
        mySocket.toa_do.setText("Không thể kết nối với module GPS!")
        # print("Không thể kết nối với module GPS! Kiểm tra cổng COM.")
        # mySocket.log.setText("Không thể kết nối với module GPS! Kiểm tra cổng UART.")
    socketThread = socketThreadClass(mySocket,sio) #tao instance running serial task
    socketThread.start()
    uart_queue = queue.Queue()
    uart_receive_thread = UARTReceiveThread(mySocket,ser, uart_queue)
    uart_receive_thread.start()
    
    
    mySocket.label_logo.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/logo_t07.png"))
    mySocket.avt.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/cccd.jpg"))
    mySocket.avt_2.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/bus.png"))
    # ui.showFullScreen()
    ui.show()
    # ui.setStyleSheet(design.app_style)
    app.exec_()
    # wifi_thread = threading.Thread(target=monitor_wifi, daemon=True)
    # wifi_thread.start()
    print('window close')
    uart_receive_thread.stop()
    uart_receive_thread.join()
    sio.disconnect()  # Ngắt kết nối trước khi kết thúc chương trình
    socketThread.join()  # Đợi thread hoàn thành
    print('done')
#  # Hàm theo dõi sự kiện WiFi
# def monitor_wifi():
#     print("Bắt đầu theo dõi sự kiện WiFi...")
#     process = subprocess.Popen(["nmcli", "monitor"], stdout=subprocess.PIPE, text=True)

#     for line in process.stdout:
#          if "wlan0: connected" in line :
#             print("WiFi đã kết nối!")
#             os.system(f"echo {password} | sudo -S nmcli device disconnect {interface}")
#             time.sleep(2)
#             os.system(f"echo {password} | sudo -S nmcli device connect {interface}") 
if __name__ == "__main__":
    # interface = "enu1"  # Thay bằng tên giao diện mạng của bạn
    # password = "1"

    # # Tắt mạng
    # # time.sleep(5)
    # os.system(f"echo {password} | sudo -S nmcli device disconnect {interface}")
    # time.sleep(5)

    # # Bật mạng
    # os.system(f"echo {password} | sudo -S nmcli device connect {interface}")
    # time.sleep(5)
   
    # # Khởi động luồng theo dõi WiFi
    
    runTest()      