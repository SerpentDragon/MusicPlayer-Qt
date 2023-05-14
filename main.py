import sys
import os
from window import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWinExtras import QtWin
from pygame import mixer
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

mixer.init()


class MyPlayer(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Плеер")
        self.ui.pushButton.clicked.connect(self.choose_path)
        self.ui.listWidget.itemClicked.connect(self.start_music)
        self.ui.pushButton_3.clicked.connect(self.play_music)

        self.play = QPixmap("Images\\Interface\\start.png")
        self.pause = QPixmap("Images\\Interface\\pause.png")
        self.prev = QPixmap("Images\\Interface\\prev.png")
        self.next = QPixmap("Images\\Interface\\next.png")

        self.path = ""
        self.index = -1

        self.ui.pushButton_2.setIcon(QIcon(self.prev))
        self.ui.pushButton_2.setIconSize(QtCore.QSize(61, 61))
        self.ui.pushButton_2.clicked.connect(self.prev_music)

        self.ui.pushButton_3.setIcon(QIcon(self.play))
        self.ui.pushButton_3.setIconSize(QtCore.QSize(61, 61))

        self.ui.pushButton_4.setIcon(QIcon(self.next))
        self.ui.pushButton_4.setIconSize(QtCore.QSize(61, 61))
        self.ui.pushButton_4.clicked.connect(self.next_music)

        self.mode = "mp3"
        self.counter = 0
        self.music = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.movement)
        self.timer.start(1000)
        self.moved = 0

        self.ui.horizontalSlider.setMinimum(0)
        self.ui.horizontalSlider.sliderReleased.connect(self.play_position)
        self.ui.horizontalSlider.valueChanged.connect(self.play_position)

        default_picture = QPixmap("Images\\Icons\\default.png").scaled(331, 331)
        self.ui.label.setPixmap(default_picture)

        high_volume = QPixmap("Images\\Interface\\high_volume.png").scaled(21, 21)
        low_volume = QPixmap("Images\\Interface\\low_volume.png").scaled(21, 21)

        self.ui.label_4.setPixmap(high_volume)
        self.ui.label_5.setPixmap(low_volume)
        self.setWindowIcon(QtGui.QIcon("Images\\Icons\\icon.png"))

        QtWin.setCurrentProcessExplicitAppUserModelID("player")

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(189, 189, 242))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.ui.verticalSlider.setMinimum(0)
        self.ui.verticalSlider.setMaximum(100)
        self.ui.verticalSlider.setValue(int(mixer.music.get_volume()*100))
        self.ui.label_6.setText(str(int(mixer.music.get_volume()*100)))
        self.ui.verticalSlider.sliderReleased.connect(self.change_volume)
        self.ui.verticalSlider.valueChanged.connect(self.change_volume)

    def keyPressEvent(self, event):
        key = event.key()
        if key == 16777347:
            self.next_music()
        elif key == 16777346:
            self.prev_music()
        elif key == 16777344:
            self.play_music()
        elif key == 16777328:
            self.volume_decrement()
        elif key == 16777330:
            self.volume_increment()
        elif key == 16777329:
            self.no_volume()
        elif key == 16777236:
            self.move_10_forward()
        elif key == 16777234:
            self.move_10_back()
        elif key == 16777220:
            if self.counter:
                self.start_music(self.ui.listWidget.selectedItems()[0])

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выбор папки", "..",
                                                QFileDialog.ShowDirsOnly)
        if path == "":
            return
        else:
            self.path = path

        self.ui.listWidget.clear()
        for file in os.listdir(self.path):
            if not os.path.isdir(self.path + "\\" + file) and file.split('.')[-1] == "mp3":
                self.ui.listWidget.addItem(file)

    def start_music(self, item):
        self.index = self.ui.listWidget.currentRow()
        mixer.music.stop()

        self.music = self.path + "\\" + item.text()
        self.ui.label_7.setText(item.text())

        mixer.music.load(self.music)
        mixer.music.play()

        self.ui.pushButton_3.setIcon(QIcon(self.pause))
        self.ui.pushButton_3.setIconSize(QtCore.QSize(71, 71))
        self.counter = 1

        try:
            path = self.path + "\\" + item.text()
            music = ID3(path)

            tmp = open("image.jpg", "wb")
            tmp.write(music.getall("APIC")[0].data)

            picture = QPixmap(os.getcwd() + "\\" + "image.jpg")
            picture = QPixmap.scaled(picture, 331, 331)

            self.ui.label.setPixmap(picture)
            tmp.close()

            os.remove("image.jpg")
        except FileNotFoundError:
            default_picture = QPixmap("Images\\Icons\\default.png").scaled(331, 331)
            self.ui.label.setPixmap(default_picture)

        self.ui.label_3.setText(self.convert_into_minutes(int(MP3(self.music).info.length)))

        self.ui.horizontalSlider.setValue(0)
        self.ui.horizontalSlider.setMaximum(int(MP3(self.music).info.length))

    def play_music(self):
        if not self.counter:
            return
        if self.counter % 2 == 0:
            mixer.music.unpause()
            self.ui.pushButton_3.setIcon(QIcon(self.pause))
            self.ui.pushButton_3.setIconSize(QtCore.QSize(71, 71))
        else:
            mixer.music.pause()
            self.ui.pushButton_3.setIcon(QIcon(self.play))
            self.ui.pushButton_3.setIconSize(QtCore.QSize(71, 71))
        self.counter += 1

    def movement(self):
        if self.counter % 2:
            self.ui.horizontalSlider.setValue(self.ui.horizontalSlider.value() + 1)
            self.ui.label_2.setText(self.convert_into_minutes(self.ui.horizontalSlider.value()))
            if self.ui.horizontalSlider.value() == int(MP3(self.music).info.length):
                self.next_music()

    def play_position(self):
        if not self.ui.horizontalSlider.isSliderDown() and self.counter:
            mixer.music.set_pos(int(self.ui.horizontalSlider.value()))
            self.ui.label_2.setText(self.convert_into_minutes(self.ui.horizontalSlider.value()))

    @staticmethod
    def convert_into_minutes(time):
        res = ''
        if time < 60:
            res += '0:'
        else:
            res = str(time // 60) + ':'
        ost = time % 60
        if ost < 10:
            res += '0' + str(ost)
        else:
            res += str(ost)
        return res

    def change_volume(self):
        if not self.ui.horizontalSlider.isSliderDown():
            mixer.music.set_volume(self.ui.verticalSlider.value()/100)
            self.ui.label_6.setText(str(self.ui.verticalSlider.value()))

    def prev_music(self):
        if not self.counter:
            return
        self.index -= 1
        if self.index == -1:
            self.index = self.ui.listWidget.count() - 1
        self.ui.listWidget.setCurrentRow(self.index)
        self.start_music(self.ui.listWidget.item(self.ui.listWidget.currentRow()))

    def next_music(self):
        if not self.counter:
            return
        self.index += 1
        if self.index == self.ui.listWidget.count():
            self.index = 0
        self.ui.listWidget.setCurrentRow(self.index)
        self.start_music(self.ui.listWidget.item(self.ui.listWidget.currentRow()))

    def volume_decrement(self):
        self.ui.verticalSlider.setValue(self.ui.verticalSlider.value()-1)
        mixer.music.set_volume(self.ui.verticalSlider.value() / 100)
        self.ui.label_6.setText(str(self.ui.verticalSlider.value()))

    def volume_increment(self):
        self.ui.verticalSlider.setValue(self.ui.verticalSlider.value() + 1)
        mixer.music.set_volume(self.ui.verticalSlider.value() / 100)
        self.ui.label_6.setText(str(self.ui.verticalSlider.value()))

    def no_volume(self):
        self.ui.verticalSlider.setValue(0)
        mixer.music.set_volume(0)
        self.ui.label_6.setText(str(0))

    def move_10_forward(self):
        self.ui.horizontalSlider.setValue(self.ui.horizontalSlider.value() + 10)
        self.ui.label_2.setText(self.convert_into_minutes(self.ui.horizontalSlider.value()))
        mixer.music.set_pos(int(self.ui.horizontalSlider.value()))

    def move_10_back(self):
        self.ui.horizontalSlider.setValue(self.ui.horizontalSlider.value() - 10)
        self.ui.label_2.setText(self.convert_into_minutes(self.ui.horizontalSlider.value()))
        mixer.music.set_pos(int(self.ui.horizontalSlider.value()))


app = QtWidgets.QApplication(sys.argv)
myapp = MyPlayer()
myapp.show()
sys.exit(app.exec_())
