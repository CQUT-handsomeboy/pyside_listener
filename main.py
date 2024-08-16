from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QObject, Signal

from threading import Thread, Event
from time import sleep

from utils import *

import numpy as np
import cv2

from icecream import ic


class MySignals(QObject):
    frame_update = Signal(QImage)


uiLoader = QUiLoader()


class Main:
    def __init__(self):
        self.configs = ConfigLoader()
        self.ui = uiLoader.load(self.configs.main_ui_path)
        self.ms = MySignals()
        self.ms.frame_update.connect(self.test)
        self.running = Event()
        get_frame_thread = Thread(target=self.get_frame)
        get_frame_thread.start()

    def test(self, q_img: QImage):
        self.ui.video_frame.setPixmap(QPixmap.fromImage(q_img))

    def _np2qimg(self, np_img: np.array) -> QImage:
        q_img = QImage(
            np_img.data,
            np_img.shape[1],
            np_img.shape[0],
            np_img.shape[1] * 3,
            QImage.Format_RGB888,
        ).rgbSwapped()
        return q_img

    def get_frame(self):

        self.cap = cv2.VideoCapture(self.configs.sample_video_path)

        while self.cap.isOpened() and (not self.running.is_set()):
            ret, frame = self.cap.read()
            if not ret:
                break
            q_img = self._np2qimg(frame)
            self.ms.frame_update.emit(q_img)
            sleep(0.01)

    def on_window_close(self):
        self.running.set()


app = QApplication([])
main = Main()
app.aboutToQuit.connect(main.on_window_close)
main.ui.show()
app.exec()
