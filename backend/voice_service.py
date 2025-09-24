import os
import pyaudio
import wave
import speech_recognition as sr
import datetime
from gtts import gTTS
from log_service import LogService
import tempfile

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
        current_time = LogService.get_current_time()
        model_name = "SpeechRecognition"
        function_name = "recognize_speech"
        
        try:
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"开始语音识别处理, 语言: {language}")
            
            if audio_data is None:
                # 从麦克风录制
                LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Debug', message="从麦克风录制音频")
                with sr.Microphone() as source:
                    LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message="请说话...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio_data = self.recognizer.listen(source, timeout=10)
                    LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message="录音结束，正在识别...")
            else:
                LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Debug', message="使用提供的音频数据进行识别")
            
            # 使用Google语音识别将音频转换为文字
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message="调用Google语音识别服务")
            text = self.recognizer.recognize_google(audio_data, language=language)
            
            # 方法成功日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"语音识别成功, 识别文本长度: {len(text)}字符")
            return text
        except sr.UnknownValueError:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message="无法识别您的语音")
            return "无法识别您的语音"
        except sr.RequestError:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message="语音识别服务不可用")
            return "语音识别服务不可用"
        except sr.WaitTimeoutError:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message="录音超时，请重试")
            return "录音超时，请重试"
        except Exception as e:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f"语音识别失败: {str(e)}")
            return f"识别错误: {str(e)}"
        finally:
            # 方法结束日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"语音识别处理结束, 耗时: {datetime.datetime.now() - start_time}")
    
    def record_audio(self, duration=5, sample_rate=16000, channels=1, chunk=1024):
        """录制音频并返回音频数据和临时文件路径"""
        start_time = datetime.datetime.now()
        current_time = LogService.get_current_time()
        model_name = "PyAudio"
        function_name = "record_audio"
        
        try:
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"开始录音, 持续时间: {duration}秒, 采样率: {sample_rate}Hz")
            
            audio = pyaudio.PyAudio()
            
            # 开始录音
            stream = audio.open(format=pyaudio.paInt16,
                               channels=channels,
                               rate=sample_rate,
                               input=True,
                               frames_per_buffer=chunk)
            
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"开始录音，持续{duration}秒...")
            frames = []
            
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message="录音结束")
            
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
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Debug', message=f"音频文件已保存至临时路径: {temp_file_path}")
            
            # 读取音频数据用于识别
            with sr.AudioFile(temp_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            # 方法成功日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"录音处理成功, 音频数据长度: {len(b''.join(frames))}字节, 耗时: {datetime.datetime.now() - start_time}")
            
            return audio_data, temp_file_path
        except Exception as e:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f"录音失败: {str(e)}")
            return None, None
    
    def text_to_speech(self, text, output_file=None, language='zh-CN', voice=None, speed=1.0):
        """将文字转换为语音，使用gTTS库实现免费的文字转语音功能"""
        start_time = datetime.datetime.now()
        current_time = LogService.get_current_time()
        model_name = "TextToSpeech"
        function_name = "text_to_speech"
        
        try:
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"开始文本转语音处理, 语言: {language}, 语音: {voice}, 语速: {speed}")
            
            # 调试日志：打印文本内容的部分预览
            text_preview = text[:50] if text else ''
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Debug', message=f"文本内容: {text_preview}...")
            
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
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"语音已保存到: {output_file}")
            
            # 方法成功日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"文本转语音成功, 已保存至文件, 文本长度: {len(text)}字符, 耗时: {datetime.datetime.now() - start_time}")
            
            return output_file
        except Exception as e:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f"文本转语音失败: {str(e)}")
            return None