from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_MainWindow

class guiHandle(Ui_MainWindow):
    nameClass = "guiHandle"
    def __init__(self,gui):
        self.setupUi(gui)
        # viet code xu ly su kien o day


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = guiHandle()
#     MainWindow.showFullScreen()
#     sys.exit(app.exec_())
