import speech_recognition as sr

import tempfile
import os
import pyaudio
import wave
import speech_recognition as sr
import datetime
from gtts import gTTS
from log_service import LogService

class VoiceService:
    def __init__(self):
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        
    def recognize_speech(self, audio_data=None, language='zh-CN'):
        """将语音转换为文字
        audio_data: 可选的音频数据，如果不提供则从麦克风录制
        language: 语言，默认为中文
        """
        start_time = datetime.datetime.now()
        log_service = LogService()
        
        try:
            # 方法开始日志
            log_service.info(f"开始语音识别处理, 语言: {language}", module="SpeechRecognition", function="recognize_speech")
            
            if audio_data is None:
                # 从麦克风录制
                log_service.debug("从麦克风录制音频", module="SpeechRecognition", function="recognize_speech")
                with sr.Microphone() as source:
                    log_service.info("请说话...", module="SpeechRecognition", function="recognize_speech")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio_data = self.recognizer.listen(source, timeout=10)
                    log_service.info("录音结束，正在识别...", module="SpeechRecognition", function="recognize_speech")
            else:
                log_service.debug("使用提供的音频数据进行识别", module="SpeechRecognition", function="recognize_speech")
            
            # 使用Google语音识别将音频转换为文字
            log_service.info("调用Google语音识别服务", module="SpeechRecognition", function="recognize_speech")
            text = self.recognizer.recognize_google(audio_data, language=language)
            
            # 方法成功日志
            log_service.info(f"语音识别成功, 识别文本长度: {len(text)}字符", module="SpeechRecognition", function="recognize_speech")
            return text
        except sr.UnknownValueError:
            log_service.error("无法识别您的语音", module="SpeechRecognition", function="recognize_speech")
            return "无法识别您的语音"
        except sr.RequestError:
            log_service.error("语音识别服务不可用", module="SpeechRecognition", function="recognize_speech")
            return "语音识别服务不可用"
        except sr.WaitTimeoutError:
            log_service.error("录音超时，请重试", module="SpeechRecognition", function="recognize_speech")
            return "录音超时，请重试"
        except Exception as e:
            log_service.error(f"语音识别失败: {str(e)}", module="SpeechRecognition", function="recognize_speech")
            return f"识别错误: {str(e)}"
        finally:
            # 方法结束日志
            log_service.info(f"语音识别处理结束, 耗时: {datetime.datetime.now() - start_time}", module="SpeechRecognition", function="recognize_speech")
    
    def record_audio(self, duration=5, sample_rate=16000, channels=1, chunk=1024):
        """录制音频并返回音频数据和临时文件路径"""
        start_time = datetime.datetime.now()
        log_service = LogService()
        
        try:
            # 方法开始日志
            log_service.info(f"开始录音, 持续时间: {duration}秒, 采样率: {sample_rate}Hz", module="PyAudio", function="record_audio")
            
            audio = pyaudio.PyAudio()
            
            # 开始录音
            stream = audio.open(format=pyaudio.paInt16,
                               channels=channels,
                               rate=sample_rate,
                               input=True,
                               frames_per_buffer=chunk)
            
            log_service.info(f"开始录音，持续{duration}秒...", module="PyAudio", function="record_audio")
            frames = []
            
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            log_service.info("录音结束", module="PyAudio", function="record_audio")
            
            # 停止录音
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # 创建临时文件保存录音
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wf = wave.open(temp_file.name, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                temp_file_path = temp_file.name
            
            # 调试日志：打印临时文件路径
            log_service.debug(f"音频文件已保存至临时路径: {temp_file_path}", module="PyAudio", function="record_audio")
            
            # 读取音频数据用于识别
            with sr.AudioFile(temp_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            # 方法成功日志
            log_service.info(f"录音处理成功, 音频数据长度: {len(b''.join(frames))}字节, 耗时: {datetime.datetime.now() - start_time}", module="PyAudio", function="record_audio")
            
            return audio_data, temp_file_path
        except Exception as e:
            log_service.error(f"录音失败: {str(e)}", module="PyAudio", function="record_audio")
            return None, None
    
    def text_to_speech(self, text, output_file=None, language='zh-CN', voice=None, speed=1.0):
        """将文字转换为语音，使用gTTS库实现免费的文字转语音功能"""
        start_time = datetime.datetime.now()
        log_service = LogService()
        
        try:
            # 方法开始日志
            log_service.info(f"开始文本转语音处理, 语言: {language}, 语音: {voice}, 语速: {speed}", module="TextToSpeech", function="text_to_speech")
            
            # 调试日志：打印文本内容的部分预览
            text_preview = text[:50] if text else ''
            log_service.debug(f"文本内容: {text_preview}...", module="TextToSpeech", function="text_to_speech")
            
            # 创建gTTS对象
            # gTTS不直接支持voice参数，但我们可以根据voice参数选择不同的语言变体或调整语速
            slow_mode = speed < 1.0  # 如果语速较慢，使用slow模式
            tts = gTTS(text=text, lang=language, slow=slow_mode)
            
            # 如果没有提供输出文件，创建临时文件
            if not output_file:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    output_file = temp_file.name
            
            # 保存语音文件
            tts.save(output_file)
            log_service.info(f"语音已保存到: {output_file}", module="TextToSpeech", function="text_to_speech")
            
            # 方法成功日志
            log_service.info(f"文本转语音成功, 已保存至文件, 文本长度: {len(text)}字符, 耗时: {datetime.datetime.now() - start_time}", module="TextToSpeech", function="text_to_speech")
            
            return output_file
        except Exception as e:
            log_service.error(f"文本转语音失败: {str(e)}", module="TextToSpeech", function="text_to_speech")
            return None