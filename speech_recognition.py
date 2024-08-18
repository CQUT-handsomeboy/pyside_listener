"""
模型权重文件，请自行下载，然后修改configs.json中的参数
"""

import shutil
import subprocess
import numpy as np
import sherpa_onnx

from utils import Configs
from paticipate_words import participle_words
from typing import Callable, Set


class SpeechRecognition_And_ParticipateWords:
    """
    语音识别并分词，需要向内注册一个回调函数`callback()`
    """

    def __init__(
        self,
        url: str,
        captions_callback: Callable[[str], None],
        participate_words_callback: Callable[[Set], None],
    ) -> None:

        assert (
            shutil.which("ffmpeg") is not None
        ), "!!!PLEASE INSTALL THE FUCKING FFMPEG FIRST!!!"

        self.configs = Configs()

        self.url = url
        self.captions_callback = captions_callback  # 字幕
        self.participate_words_callback = participate_words_callback  # 分词

        self.recognizer = self.create_recognizer()

    def handle_string(self, temp_string: str):
        """
        此处处理字符串，进行分词操作以后将结果传递给回调函数
        """
        self.captions_callback(temp_string)
        result = participle_words(temp_string)
        self.participate_words_callback(result)

    def create_recognizer(self):
        recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=self.configs.tokens,
            encoder=self.configs.encoder,
            decoder=self.configs.decoder,
            joiner=self.configs.joiner,
            num_threads=1,
            sample_rate=16000,
            feature_dim=80,
            decoding_method="greedy_search",
            enable_endpoint_detection=True,
            rule1_min_trailing_silence=2.4,
            rule2_min_trailing_silence=1.2,
            rule3_min_utterance_length=300,  # it essentially disables this rule
        )
        return recognizer

    def start(self,stop_flag):

        ffmpeg_cmd = [
            "ffmpeg",
            "-i",
            self.url,
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-",
        ]

        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        frames_per_read = 1600  # 0.1 second

        stream = self.recognizer.create_stream()

        last_result = ""

        from sample_const import START_STRING

        print(START_STRING)

        seg_id = 1
        temp_string = ""
        while not stop_flag.is_set():
            # *2 because int16_t has two bytes
            data = process.stdout.read(frames_per_read * 2)
            if not data:
                break

            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples.astype(np.float32) / 32768
            stream.accept_waveform(16000, samples)

            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)

            is_endpoint = self.recognizer.is_endpoint(stream)

            result = self.recognizer.get_result(stream)

            # if result and (last_result != result):

            if not result or last_result == result:
                continue

            if last_result in result:
                X = result[len(last_result) :]
            else:
                X = result

            if seg_id % self.configs.tokenization_time == 0:
                self.handle_string(temp_string)
                temp_string = ""

            temp_string += X
            seg_id += 1

            last_result = result

            if is_endpoint:
                self.recognizer.reset(stream)


if __name__ == "__main__":
    configs = Configs()

    i = 0

    def callback_test_1(result_set):
        global i
        print(f"[{i}] [result_set] ", ",".join(result_set))
        i += 1

    def callback_test_2(result_string: str):
        global i
        print(f"[{i}] [result_string] ", result_string)
        i += 1

    srpw = SpeechRecognition_And_ParticipateWords(
        configs.sample_rtmp_url,
        callback_test_2,
        callback_test_1,
    )

    srpw.start()
