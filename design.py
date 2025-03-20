app_style = """
QMainWindow {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #f8f9fa, stop:1 #e8ecef);
}

QLabel {
    color: #2c3e50;
    font-size: 18px;
    font-family: Arial, sans-serif;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px;
    font-size: 14px;
    color: #2c3e50;
}

QLineEdit:focus {
    border: 1px solid #2980b9;
    background-color: #ecf0f1;
}

QPushButton {
    background-color: #3498db;
    color: #ffffff;
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QGroupBox {
    border: 1px solid #dfe6e9;
    border-radius: 6px;
    margin-top: 10px;
    padding: 10px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
    color: #34495e;
    font-weight: bold;
}

QStatusBar {
    background: #ecf0f1;
    border-top: 1px solid #bdc3c7;
}
"""

# Trong code PyQt5 dùng:
# self.setStyleSheet(app_style)
