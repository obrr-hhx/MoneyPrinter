# -*- coding: utf-8 -*-

import time
import sys
import threading
from datetime import datetime
import json
import math

sys.path.append("/Users/huanghx/code/MoneyPrinter")
from tencentcloud_speech_sdk_python import asr, common

class TencentAsr:
    def __init__(self, appid: str="", secret_id: str="", secret_key: str="", engine_type: str="16k_zh") -> None:
        self.appid = appid
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.engine_type = engine_type
        self.credential = common.credential.Credential(secret_id, secret_key)
        self.recongnizer = asr.flash_recognizer.FlashRecognizer(self.appid, self.credential)
    
    def recognize(self, audio_path: str) -> str:
        request = asr.flash_recognizer.FlashRecognitionRequest(self.engine_type)
        request.set_filter_dirty(1)
        request.set_filter_modal(1)
        request.set_filter_punc(1)
        request.set_convert_num_mode(1)
        request.set_word_info(3)
        request.set_voice_format("mp3")
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
            result = self.recongnizer.recognize(request, audio_data)
        
        self.result = json.loads(result)
        request_id = self.result["request_id"]
        code = self.result["code"]
        if code != 0:
            raise Exception(f"recognize failed, request_id: {request_id}, code: {code}, message: {self.result['message']}")
        return result

    def export_srt_data(self) -> str:
        if not hasattr(self, "result"):
            raise Exception("No result to export")
        
        def convert_to_srt_time_format(millisecond: float) -> str:
            """
            Convert seconds to the SRT time format.
            """
            second = math.floor(millisecond) // 1000
            hour = math.floor(second) // 3600000
            minute = (math.floor(second) - hour * 3600) // 60
            sec = math.floor(second) - hour * 3600 - minute * 60
            minisec = int(math.modf(second)[0] * 100)  # 处理开始时间
            return str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(sec).zfill(2) + ',' + str(minisec).zfill(2)  # 将数字填充0并按照格式写入

        srt_data = ""
        i=1
        for channl_result in self.result["flash_result"]:
            for sentence in channl_result["sentence_list"]:
                # make the start time in the format of HH:MM:SS,mmm
                start_time = convert_to_srt_time_format(sentence["start_time"])
                # make the end time in the format of HH:MM:SS,mmm
                end_time = convert_to_srt_time_format(sentence["end_time"])
                content = sentence["text"]
                new_content = ""
                # if the content is more than 15 characters, split it into multiple lines
                if len(content) > 11:
                    for i in range(0, len(content), 11):
                        new_content += content[i:i+11] + "\n"
                srt_data += f"{i}\n"
                srt_data += f"{start_time}"
                srt_data += " --> "
                srt_data += f"{end_time}\n"
                srt_data += f"{new_content}\n\n"
                i += 1
        return srt_data