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
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt, QEvent
global gps
global timeout,timeoutflag,t,count,q
q = 0
count = 0
timeout = 0
t = time.time()
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
from math import radians, sin, cos, sqrt, atan2
def find_nearest(lat, lon):
    """Tìm địa điểm gần nhất với tọa độ đầu vào."""
    places = [
        {"name": "Bách hóa Thanh Xuân", "coords": [21.01260, 105.80138]},
        {"name": "Chợ Thượng Đình", "coords": [20.99880, 105.81184]},
        {"name": "Tổng Công ty Đường sắt Việt Nam", "coords": [21.02575, 105.84145]},
        {"name": "Đại học Khoa học - Tự nhiên", "coords": [20.99600, 105.80915]},
        {"name": "Bệnh viện Phụ sản Trung ương", "coords": [21.02672, 105.84756]},
        {"name": "Bệnh viện Bạch Mai", "coords": [21.00102, 105.84150]},
        {"name": "Cung Thiếu Nhi Hà Nội", "coords": [21.02822, 105.85562]},
        {"name": "KCN Biên Giang, Hà Đông, Hà Nội", "coords": [20.93092, 105.71587]},
        {"name": "Học viện Bưu Chính Viễn Thông", "coords": [20.93721, 105.75749]},
        {"name": "Văn miếu Quốc Tử Giám", "coords": [21.02754, 105.83520]},
        {"name": "Trường Đại Học Kỹ Thuật - Hậu Cần CAND", "coords": [21.041000463711462, 106.09933048084626]}
    ]
    
    R = 6371  # Bán kính Trái Đất (km)
    min_distance, nearest_place = float('inf'), None
    
    for place in places:
        lat1, lon1, lat2, lon2 = map(radians, [lat, lon, *place['coords']])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        distance = R * 2 * atan2(sqrt(a), sqrt(1 - a))
        
        if distance < min_distance:
            min_distance, nearest_place = distance, place['name']
    
    return nearest_place

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
            if timeoutflag == False:
                t = time.time()
                # print(t)
            if timeoutflag == True:
                try:
                    if time.time() - t > timeout:
                        # print("timeout")
                        self.mySocket.so_cccd.setText("")
                        self.mySocket.ngay_cap.setText("")
                        self.mySocket.ngay_het_han.setText("")
                        self.mySocket.ho_ten.setText("")
                        self.mySocket.ngay_sinh.setText("")
                        self.mySocket.gioi_tinh.setText("")
                        self.mySocket.que_quan.setText("")
                        self.mySocket.quoc_tich.setText("")
                        self.mySocket.log.setText("🚍 Xe buýt Hà Nội xin chào quý khách! 🚍")  # Thêm icon xe buýt nếu cần
                        self.mySocket.avt.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/cccd.jpg"))
                        # print("Đã xóa toàn bộ dữ liệu hiển thị")
                        global q
                        q = 0
                        timeoutflag = False
                        t = time.time()
                except Exception as e:
                        # print("timeout")
                        self.mySocket.so_cccd.setText("")
                        self.mySocket.ngay_cap.setText("")
                        self.mySocket.ngay_het_han.setText("")
                        self.mySocket.ho_ten.setText("")
                        self.mySocket.ngay_sinh.setText("")
                        self.mySocket.gioi_tinh.setText("")
                        self.mySocket.que_quan.setText("")
                        self.mySocket.quoc_tich.setText("")
                        self.mySocket.log.setText("🚍 Xe buýt Hà Nội xin chào quý khách! 🚍")  # Thêm icon xe buýt nếu cần
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
                                self.mySocket.tram_xe.setText(find_nearest(msg.latitude, msg.longitude))
                                global count
                                count = count +1
                                if count > 6:
                                    # update_map(self.mySocket, msg.latitude, msg.longitude)
                                    try:
                                        self.mySocket.on_load_finished(msg.latitude, msg.longitude)
                                        count = 0
                                    except Exception as e: 
                                        count = count - 1

                    
                                #
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
                self.mySocket.tram_xe.setText("N/A")
                self.ser.is_open = False
                self.mySocket.toa_do.setText("Không thể kết nối với module GPS!")
            time.sleep(0.01)

    def stop(self):
        self.running = False

def convert_date_format(date_str):
    # Chuyển từ d/m/y sang m/d/y
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%m/%d/%Y")
    except ValueError:
        return "Invalid date format"

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
# from PyQt5.QtCore import QMetaObject, Qt
# def update_map(ui, lat, lon):
#     js_code = f"window.changeMarkerCoordinates({lat}, {lon});"
#     QMetaObject.invokeMethod(ui.webEngineView.page(), "runJavaScript",Qt.QueuedConnection, js_code)
from pynput.mouse import Controller
class mySocketClass(guiHandle):
    def __init__(self,mygui,so_cccd,ngay_cap,ngay_het_han,ho_ten,ngay_sinh,gioi_tinh,que_quan,quoc_tich):
        # print('inited mySocket instance inherit from ',super().nameClass)
        guiHandle.__init__(self,mygui)
        self.webEngineView.loadFinished.connect(self.on_load_finished)
   
    def on_load_finished(self,lat= None,lon = None):
        # Thay đổi tọa độ
        if lat is None or lon is None:
            new_lat, new_lon = 21.041000463711462, 106.09933048084626  # Giá trị mặc định hoặc lấy từ config
        else:
            new_lat = lat
            new_lon = lon

        # Mã JavaScript để thay đổi tọa độ marker
        js_code = f"""
            window.changeMarkerCoordinates({new_lat}, {new_lon});
        """

        # Chạy JavaScript trên trang web nhúng
        self.webEngineView.page().runJavaScript(js_code)

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
            global g_so_cccd, g_ngay_cap, g_ngay_het_han, g_ho_ten, g_ngay_sinh, g_gioi_tinh, g_que_quan,q
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
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data = f"time:{current_time}\nid:{g_so_cccd}\nname:{self.mySocket.ho_ten.text()}\nbirth:{convert_date_format(self.mySocket.ngay_sinh.text())}\ngender:{self.mySocket.gioi_tinh.text()}\nnationality:{self.mySocket.quoc_tich.text()}\ntram:{self.mySocket.tram_xe.text()}\ntuyen:{get_route_code(self.mySocket.tuyen.text())}\nbien:{self.mySocket.bien_so.text()}"
                    # print(data)
                    target_url = "http://nguyengiang2603-1.infinityfreeapp.com/project/receive_his.php"
                    query_params = {
                        "text":{data},
                    }
                    # print (query_params)
                    try:
                        status, content = server.bypass_infinityfree(target_url, query_params)
                        if status == 200 and content[0] != '1':
                            q = q +1
                            self.mySocket.log.setText(f"Xin mời quý khách lên xe !\n Lượt : {q}")
                            playsound("/home/admin1/Documents/test_qt5/ok.mp3")
                        elif status == 200 and content[0] == '1':
                            q = q +1
                            # print(content)
                            self.mySocket.log.setText(f"Quý khách vui lòng thanh toán 10.000đ !\n Lượt : {q}")
                            playsound("/home/admin1/Documents/test_qt5/no.mp3")
                        else:
                            self.mySocket.log.setText("Vui lòng kiểm tra lại Wifi !")
                            # self.mySocket.log.setText(content)
                            # self.mySocket.que_quan.setText(status)
                        # print(f"Status: {status}")
                    except Exception as e:
                        # print(f"Lỗi khi gửi dữ liệu: {e}")
                        self.mySocket.log.setText(f"{e}")
                        # self.mySocket.que_quan.setText(content)
                        # self.mySocket.gioi_tinh.setText(status)

                    # Đảm bảo luôn reset biến sau cùng:
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
    mySocket.avt_2.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/xe_buyt_hn.png"))
    mySocket.avt_3.setPixmap(QtGui.QPixmap("/home/admin1/Documents/test_qt5/info.png"))
    font = QtGui.QFont("Arial",30, QtGui.QFont.Bold)  # Chọn font Arial, cỡ 14, in đậm
    mySocket.log.setFont(font)
    mySocket.log.setStyleSheet("color: blue;")  # Đổi màu chữ thành xanh

    mySocket.log.setText("🚍 Xe buýt Hà Nội xin chào quý khách! 🚍")  # Thêm icon xe buýt nếu cần
    # mySocket.log.setText("Xe buýt Hà Nội xin chào quý khách !")
    # new_lat, new_lon = 12.0285, 105.852

    #     # Mã JavaScript để thay đổi tọa độ marker
    # js_code = f"""
    #         window.changeMarkerCoordinates({new_lat}, {new_lon});
    #     """
        
    #     # Chạy mã JavaScript trên trang web nhúng
    # mySocket.webEngineView.page().runJavaScript(js_code)
    ui.showFullScreen()
    # ui.show()
    # ui.setStyleSheet(design.app_style)
    app.setOverrideCursor(QCursor(Qt.BlankCursor))
    # event = QEvent(QEvent.MouseMove)
    # app.sendEvent(ui, event)  # Gửi sự kiện đến cửa sổ chính
    # move_mouse_once()
    
    app.exec_()
    # wifi_thread = threading.Thread(target=monitor_wifi, daemon=True)
    # wifi_thread.start()
    # print('window close')
    uart_receive_thread.stop()
    uart_receive_thread.join()
    sio.disconnect()  # Ngắt kết nối trước khi kết thúc chương trình
    # socketThread.stop()  # Đợi thread hoàn thành
    # sys.exit(0)  # Thoát chương trình bình thường

    socketThread.join()  # Đợi thread hoàn thành
    # print('done')
#  # Hàm theo dõi sự kiện WiFi
# def move_mouse_once():
#         # Di chuyển chuột đến vị trí (200, 150)
#         mouse_controller = Controller()
#         mouse_controller.position = (0, 0)
        # print("fuck")
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
    interface = "enu1"  # Thay bằng tên giao diện mạng của bạn
    password = "1"

    # # Tắt mạng
    # time.sleep(5)
    # os.system(f"echo {password} | sudo -S nmcli device disconnect {interface}")
    # time.sleep(5)

    # # # Bật mạng
    # os.system(f"echo {password} | sudo -S nmcli device connect {interface}")
    # time.sleep(5)
   
    # # Khởi động luồng theo dõi WiFi
    
    runTest()      