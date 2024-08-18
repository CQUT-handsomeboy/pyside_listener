from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QObject, Signal

from threading import Thread, Event

from utils import *
from speech_recognition import SpeechRecognition_And_ParticipateWords

import numpy as np
import cv2
import pyaudio
import subprocess

from icecream import ic


class MySignals(QObject):
    frame_update = Signal(QImage)


uiLoader = QUiLoader()


class Main:
    def __init__(self):
        self.configs = Configs()
        self.url = self.configs.sample_rtmp_url
        self.ui = uiLoader.load(self.configs.main_ui_path)

        self.ms = MySignals()
        self.ms.frame_update.connect(self.on_frame_update)
        self.stop = Event()

        get_frame_thread = Thread(target=self.get_frame)
        play_audio_thread = Thread(target=self.play_audio)

        self.srpw = SpeechRecognition_And_ParticipateWords(
            self.url, self.on_caption_update, self.on_words_update
        )

        srpw_thread = Thread(target=self.srpw.start, args=(self.stop,))

        get_frame_thread.start()
        play_audio_thread.start()
        srpw_thread.start()

        self.ui.words_table.setItem(0, 0, QTableWidgetItem("Hello"))

    def insert_words_table(self, word_name: str, word_explain: str):
        self.ui.words_table.insertRow(0)
        self.ui.words_table.setItem(0, 0, QTableWidgetItem(word_name))
        self.ui.words_table.setItem(0, 1, QTableWidgetItem(word_explain))

    def on_words_update(self, words: set):
        for word in words:
            self.insert_words_table(word, "暂时还不知道什么意思")

    def on_caption_update(self, caption_text: str):
        self.ui.caption.setText(caption_text)

    def on_frame_update(self, q_img: QImage):
        self.ui.video_frame.setPixmap(QPixmap.fromImage(q_img))

    def _np2qimg(self, np_img: np.array, shape: tuple = (640, 480)) -> QImage:
        np_img = cv2.resize(np_img, dsize=shape)
        q_img = QImage(
            np_img.data,
            np_img.shape[1],
            np_img.shape[0],
            np_img.shape[1] * 3,
            QImage.Format_RGB888,
        ).rgbSwapped()
        return q_img

    def get_frame(self):

        self.cap = cv2.VideoCapture(self.url)

        while self.cap.isOpened() and (not self.stop.is_set()):
            ret, frame = self.cap.read()
            if not ret:
                break
            q_img = self._np2qimg(frame)
            self.ms.frame_update.emit(q_img)

    def on_window_close(self):
        self.stop.set()

    def play_audio(self):
        """
        播放音频
        """
        # 设置ffmpeg命令行参数以从RTSP流中提取音频
        ff_cmd = [
            "ffmpeg",
            "-i",
            self.url,
            "-acodec",
            "pcm_s16le",  # 使用pcm_s16le编码，这是pyaudio支持的格式之一
            "-f",
            "s16le",  # 设置输出格式为s16le
            "-ar",
            "44100",  # 设置采样率为44100Hz，这是常见的音频采样率
            "-ac",
            "1",  # 单声道输出
            "-",  # 输出到标准输出
        ]

        # 初始化PyAudio
        p = pyaudio.PyAudio()

        # 打开一个音频流用于播放
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

        # 使用subprocess.Popen启动ffmpeg进程，通过管道读取音频数据
        ffmpeg_process = subprocess.Popen(
            ff_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        # 持续读取ffmpeg输出的数据并播放
        while not self.stop.is_set():
            data = ffmpeg_process.stdout.read(1024)
            if not data:
                break
            stream.write(data)

        # 清理工作
        stream.stop_stream()
        stream.close()
        p.terminate()

        # 确保ffmpeg进程也被正确终止
        ffmpeg_process.terminate()
        ffmpeg_process.wait()


app = QApplication([])
main = Main()
app.aboutToQuit.connect(main.on_window_close)
main.ui.show()
app.exec()
