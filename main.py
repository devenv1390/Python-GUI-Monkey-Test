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
import threading
import time

from PySide6 import QtGui, QtCore
from PySide6.QtCharts import QLineSeries, QChart
from PySide6.QtCore import QEventLoop, QMutexLocker
from PySide6.scripts.metaobjectdump import Signal

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from modules import Settings
from utils.get_system_info import GetSystemInfo
from utils.monkey import Monkey, get_info
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


# 开启新线程
class NewThread(QThread):
    finishSignal = Signal(str)

    def __init__(self, parent=None, package=None):
        super(NewThread, self).__init__(parent)
        self.is_paused = bool(0)  # 标记线程是否暂停
        self.mutex = QMutex()  # 互斥锁，用于线程同步
        self.cond = QWaitCondition()  # 等待条件，用于线程暂停和恢复
        self.package = package

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
                adb = GetSystemInfo(self.package)
                list_v = adb.sum_dic()
                cpu = list_v[3]
                system_cpu = list_v[4]
                mem = list_v[2]
                # print(f"list_v = {list_v}")
                with open(r"./test_data/{}".format("test.csv"), 'a', newline="") as f:
                    write = csv.writer(f)
                    write.writerow([timer, cpu, system_cpu, mem])
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
        self.set_event = {
            "touch": 0,
            "motion": 0,
            "trackball": 0,
            "nav": 0,
            "majornav": 0,
            "syskeys": 0,
            "appswitch": 0,
            "pinchzoom": 0,
            "rotation": 0,
            "flip": 0,
            "anyevent": 0,
        }
        self.set_ignore = {
            "--ignore-crashes": False,
            "--ignore-timeouts": False,
            "--ignore-security-exceptions": False,
            "--ignore-native-crashes": False,
            "--monitor-native-crashes": False,
        }

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
        widgets.btn_home.clicked.connect(self.button_click)
        widgets.btn_widgets.clicked.connect(self.button_click)
        widgets.btn_new.clicked.connect(self.button_click)
        widgets.btn_save1.clicked.connect(self.button_click)

        # 功能按钮
        widgets.btn_start_monkey.clicked.connect(self.button_click)
        widgets.btn_pause.clicked.connect(self.button_click)
        widgets.btn_generateTest.clicked.connect(self.generate_test_data)
        widgets.btn_save_cmd.clicked.connect(self.button_click)

        # CHECK BOX
        widgets.checkBox_security.clicked.connect(self.checkbox_click)
        widgets.checkBox_crash.clicked.connect(self.checkbox_click)
        widgets.checkBox_timeout.clicked.connect(self.checkbox_click)
        widgets.checkBox_monitor_native_crash.clicked.connect(self.checkbox_click)
        widgets.checkBox_native_crash.clicked.connect(self.checkbox_click)

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

    # 主要功能UI逻辑
    # ///////////////////////////////////////////////////////////////

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = widgets.plainTextEdit_cmd.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        widgets.plainTextEdit_cmd.setTextCursor(cursor)
        widgets.plainTextEdit_cmd.ensureCursorVisible()

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

    def check_sum(self):
        sum_event = 0
        for key in self.set_event:
            if int(self.set_event[key]) < 0:
                return False
            sum_event += int(self.set_event[key])
        if sum_event > 100:
            return False
        else:
            return True

    def check_safe(self):
        self.save_event()
        self.save_ignore()
        if not self.ui.lineEdit_package.text() or self.ui.lineEdit_package.text() == "null":
            QMessageBox.warning(self, "警告", "包名为空")
            return False
        if not self.ui.lineEdit_epoch.text():
            QMessageBox.warning(self, "警告", "测试次数为空")
            return False
        if not self.check_sum():
            QMessageBox.warning(self, "警告", "事件概率总和超过100%或存在负数")
            return False
        return True

    def save_cmd(self):

        QMessageBox.information(self, "提示", "参数已保存")

    def save_event(self):
        self.set_event['touch'] = int(self.ui.lineEdit_touch.text())
        self.set_event['motion'] = int(self.ui.lineEdit_motion.text())
        self.set_event['trackball'] = int(self.ui.lineEdit_trackball.text())
        self.set_event['nav'] = int(self.ui.lineEdit_nav.text())
        self.set_event['majornav'] = int(self.ui.lineEdit_majorNav.text())
        self.set_event['syskeys'] = int(self.ui.lineEdit_syskeys.text())
        self.set_event['appswitch'] = int(self.ui.lineEdit_appSwitch.text())
        self.set_event['pinchzoom'] = int(self.ui.lineEdit_zoom.text())
        self.set_event['rotation'] = int(self.ui.lineEdit_rotation.text())
        self.set_event['flip'] = int(self.ui.lineEdit_keyboard.text())
        self.set_event['anyevent'] = int(self.ui.lineEdit_anything.text())

    def save_ignore(self):
        self.set_ignore["--ignore-crashes"] = self.ui.checkBox_crash.isChecked()
        self.set_ignore["--ignore-security-exceptions"] = self.ui.checkBox_security.isChecked()
        self.set_ignore["--ignore-timeouts"] = self.ui.checkBox_timeout.isChecked()
        self.set_ignore["--ignore-native-crashes"] = self.ui.checkBox_native_crash.isChecked()
        self.set_ignore["--motion-native-crashes"] = self.ui.checkBox_monitor_native_crash.isChecked()

    def get_monkey(self):
        cmd = Monkey(package=self.ui.lineEdit_package.text(), epoch=self.ui.lineEdit_epoch.text(),
                     seed=self.ui.lineEdit_seed.text(), throttle=self.ui.lineEdit_throttle.text(),
                     level=int(self.ui.lineEdit_level.text()), event=self.set_event,
                     ignore=self.set_ignore)
        return cmd

    def generate_base_data(self):
        info = get_info()
        if info["device"] == "null":
            QMessageBox.warning(self, "警告", "未检测到设备，请检查设备连接")
        if info["package"] == "null":
            QMessageBox.warning(self, "警告", "未检测到正在运行的应用，请将需要测试的应用置于前台")
        self.ui.lineEdit_package.setText(info["package"])
        self.ui.lineEdit_epoch.setText("10000")
        self.ui.lineEdit_seed.setText("11")
        self.ui.lineEdit_throttle.setText("300")
        self.ui.lineEdit_level.setText("3")

    def generate_event_data(self):
        self.ui.lineEdit_touch.setText("50")
        self.ui.lineEdit_motion.setText("50")
        self.ui.lineEdit_anything.setText("0")
        self.ui.lineEdit_zoom.setText("0")
        self.ui.lineEdit_appSwitch.setText("0")
        self.ui.lineEdit_keyboard.setText("0")
        self.ui.lineEdit_majorNav.setText("0")
        self.ui.lineEdit_nav.setText("0")
        self.ui.lineEdit_rotation.setText("0")
        self.ui.lineEdit_trackball.setText("0")
        self.ui.lineEdit_syskeys.setText("0")
        self.save_event()

    def generate_ignore_data(self):
        self.ui.checkBox_crash.setChecked(True)
        self.ui.checkBox_timeout.setChecked(True)
        self.ui.checkBox_security.setChecked(True)
        self.ui.checkBox_native_crash.setChecked(True)
        self.save_ignore()

    def generate_test_data(self):
        self.generate_base_data()
        self.generate_event_data()
        self.generate_ignore_data()
        cmd = self.get_monkey().combine_cmd()
        self.ui.lineEdit_cmd.setText(cmd)

    def display_cpu_info(self):
        with open(r'./test_data/{}'.format("test.csv"), 'r') as f:
            reader = f.readlines()
            reader_last = reader[-1].replace("\\n", "").split(",")
            # print(reader_last)
            col = int(reader_last[0])
            cpu = float(reader_last[1])
            system_cpu = float(reader_last[2])

        self.series_cpu.append(col, cpu)
        self.series_system_cpu.append(col, system_cpu)
        self.chart_cpu = QChart()
        self.chart_cpu.setTitle("CPU占用率")
        self.chart_cpu.addSeries(self.series_cpu)
        self.chart_cpu.addSeries(self.series_system_cpu)
        self.chart_cpu.createDefaultAxes()
        widgets.graphicsView_cpu.setChart(self.chart_cpu)

    def display_mem_info(self):
        with open(r'./test_data/{}'.format("test.csv"), 'r') as f:
            reader = f.readlines()
            reader_last = reader[-1].replace("\\n", "").split(",")
            # print(reader_last)
            col = int(reader_last[0])
            mem = float(reader_last[3])

        self.series_mem.append(col, mem)
        self.chart_mem = QChart()
        self.chart_mem.setTitle("内存占用(MB)")
        self.chart_mem.addSeries(self.series_mem)
        self.chart_mem.createDefaultAxes()
        widgets.graphicsView_mem.setChart(self.chart_mem)

    # CHECKBOX CLICK
    # Post here your functions for clicked check_boxs
    # ///////////////////////////////////////////////////////////////
    def checkbox_click(self):
        check_box = self.sender()
        check_box_name = check_box.objectName()

        if check_box_name == "checkBox_crash":
            self.set_ignore["--ignore-crashes"] = not self.set_ignore["--ignore-crashes"]

        if check_box_name == "checkBox_security":
            self.set_ignore["--ignore-security-exceptions"] = not self.set_ignore["--ignore-security-exceptions"]

        if check_box_name == "checkBox_timeout":
            self.set_ignore["--ignore-timeouts"] = not self.set_ignore["--ignore-timeouts"]

        if check_box_name == "checkBox_native_crash":
            self.set_ignore["--ignore-native-crashes"] = not self.set_ignore["--ignore-native-crashes"]

        if check_box_name == "checkBox_monitor_native_crash":
            self.set_ignore["--monitor-native-crashes"] = not self.set_ignore["--monitor-native-crashes"]

        print(f'CheckBox "{check_box_name}" pressed!')

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def button_click(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btn_name = btn.objectName()

        # SHOW HOME PAGE
        if btn_name == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btn_name)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btn_name == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btn_name)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btn_name == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)  # SET PAGE
            UIFunctions.resetStyle(self, btn_name)  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU

            self.series_mem = QLineSeries()
            self.series_cpu = QLineSeries()
            self.series_system_cpu = QLineSeries()
            self.series_cpu.setName("CPU占用率")
            self.series_system_cpu.setName("系统CPU占用率")
            self.series_mem.setName("内存占用")

        # 开始monkey测试
        if btn_name == "btn_start_monkey":
            if not self.is_working:
                if self.check_safe():
                    # self.genMastClicked()
                    package = self.ui.lineEdit_package.text()
                    self.thread1 = NewThread(package=package)
                    self.thread1.flag = True
                    self.thread1.finishSignal.connect(self.display_cpu_info)
                    self.thread1.finishSignal.connect(self.display_mem_info)
                    self.thread1.start()
                    monkey = self.get_monkey()
                    monkey.run_monkey_test()
                    self.is_working = True
            else:
                QMessageBox.warning(self, "警告", "当前已有任务在运行，请勿多次启动")

        if btn_name == "btn_pause":
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

        if btn_name == "btn_save1":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btn_name}" pressed!')

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
