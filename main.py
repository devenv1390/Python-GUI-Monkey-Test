# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////
import csv
import ctypes
import sys
import os
import platform
import time

from PySide6 import QtGui, QtCore
from PySide6.QtCharts import QLineSeries, QChart
from PySide6.QtCore import QEventLoop, QMutexLocker

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from modules import Settings
from utils.adb import Adb
from utils.monkey import Monkey
from widgets import *

os.environ["QT_FONT_DPI"] = "200"  # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None


# 自定义的输出流，将输出重定向到某个地方
class Stream(QObject):
    """Redirects console output to text widget."""
    newText = Signal(str)

    def write(self, text):
        # 发出内容
        self.newText.emit(str(text))

    def flush(self):  # real signature unknown; restored from __doc__
        """ flush(self) """
        pass


class NewThread(QThread):
    finishSignal = Signal(str)

    def __init__(self, parent=None):
        super(NewThread, self).__init__(parent)
        self.is_paused = bool(0)  # 标记线程是否暂停
        self.mutex = QMutex()  # 互斥锁，用于线程同步
        self.cond = QWaitCondition()  # 等待条件，用于线程暂停和恢复

    def pause_thread(self):
        with QMutexLocker(self.mutex):
            self.is_paused = True  # 设置线程为暂停状态

    def resume_thread(self):
        if self.is_paused:
            with QMutexLocker(self.mutex):
                self.is_paused = False  # 设置线程为非暂停状态
                self.cond.wakeOne()  # 唤醒一个等待的线程

    def run(self):
        timer = 0
        while True:
            with QMutexLocker(self.mutex):
                while self.is_paused:
                    self.cond.wait(self.mutex)  # 当线程暂停时，等待条件满足
                timer += 1
                # print(timer)
                adb = Adb("com.example.CCAS")
                list_v = adb.sum_dic()
                cpu = list_v[3]
                mem = list_v[2]
                # print(f"list_v = {list_v}")
                with open(r"./test_data/{}".format("test.csv"), 'a', newline="") as f:
                    write = csv.writer(f)
                    write.writerow([timer, cpu, mem])
                time.sleep(2)
                self.finishSignal.emit("1")


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.dragPos = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.thread_running = False
        self.is_working = False

        # Custom output stream.
        sys.stdout = Stream(newText=self.onUpdateText)

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyDracula - Modern GUI"
        description = "PyDracula APP - Theme with colors based on Dracula for Python."
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)

        widgets.btn_monkey.clicked.connect(self.buttonClick)
        widgets.btn_save_monkey.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_dark.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    # 重定向文本
    # ///////////////////////////////////////////////////////////////

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.ui.plainTextEdit_cmd.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.ui.plainTextEdit_cmd.setTextCursor(cursor)
        self.ui.plainTextEdit_cmd.ensureCursorVisible()

    def genMastClicked(self):
        """Runs the main function."""
        print('Running...')
        # print("1")
        # self.thread1.finishSignal.connect()
        self.thread1 = NewThread()
        self.thread1.flag = True
        self.thread1.start()
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        # print('Done.')

    def display_cpu_info(self):
        with open(r'./test_data/{}'.format("test.csv"), 'r') as f:
            reader = f.readlines()
            reader_last = reader[-1].replace("\\n", "").split(",")
            # print(reader_last)
            col = int(reader_last[0])
            cpu = float(reader_last[1])

        self.series_cpu.append(col, cpu)
        self.chart_cpu = QChart()
        self.chart_cpu.setTitle("CPU占用率")
        self.chart_cpu.addSeries(self.series_cpu)
        self.chart_cpu.createDefaultAxes()
        self.ui.graphicsView_cpu.setChart(self.chart_cpu)

    def display_mem_info(self):
        with open(r'./test_data/{}'.format("test.csv"), 'r') as f:
            reader = f.readlines()
            reader_last = reader[-1].replace("\\n", "").split(",")
            # print(reader_last)
            col = int(reader_last[0])
            mem = float(reader_last[2])

        self.series_mem.append(col, mem)
        self.chart_mem = QChart()
        self.chart_mem.setTitle("内存占用(MB)")
        self.chart_mem.addSeries(self.series_mem)
        self.chart_mem.createDefaultAxes()
        self.ui.graphicsView_mem.setChart(self.chart_mem)

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)  # SET PAGE
            UIFunctions.resetStyle(self, btnName)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.series_mem = QLineSeries()
            self.series_cpu = QLineSeries()
            self.series_cpu.setName("CPU")
            self.series_mem.setName("内存")

        # 开始monkey测试
        if btnName == "btn_monkey":
            if not self.is_working:
                # self.genMastClicked()
                self.thread1 = NewThread()
                self.thread1.flag = True
                self.thread1.finishSignal.connect(self.display_cpu_info)
                self.thread1.finishSignal.connect(self.display_mem_info)
                self.thread1.start()
                self.is_working = True
            else:
                QMessageBox.warning(self, "警告", "当前已有任务在运行，请勿多次启动")

        if btnName == "btn_save_monkey":
            if self.is_working:
                if self.thread_running:
                    self.thread1.quit()  # 终止线程的事件循环
                    self.thread_running = False  # 标记线程停止
                    print("stop thread")
                    self.is_working = False
                else:
                    self.thread_running = True
                    self.thread1.pause_thread()
                    print("pause thread")
            else:
                QMessageBox.information(self, "提示", "当前没有任务在运行")

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
