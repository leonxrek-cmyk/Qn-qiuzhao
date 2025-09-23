import speech_recognition as sr
import tempfile
import os
import pyaudio
import wave
import speech_recognition as sr

class VoiceService:
    def __init__(self):
        # 初始化语音识别器
        self.recognizer = sr.Recognizer()
        
    def recognize_speech(self, audio_data=None, language='zh-CN'):
        """将语音转换为文字
        audio_data: 可选的音频数据，如果不提供则从麦克风录制
        language: 语言，默认为中文
        """
        try:
            if audio_data is None:
                # 从麦克风录制
                with sr.Microphone() as source:
                    print("请说话...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio_data = self.recognizer.listen(source, timeout=10)
                    print("录音结束，正在识别...")
            
            # 使用Google语音识别将音频转换为文字
            text = self.recognizer.recognize_google(audio_data, language=language)
            return text
        except sr.UnknownValueError:
            return "无法识别您的语音"
        except sr.RequestError:
            return "语音识别服务不可用"
        except sr.WaitTimeoutError:
            return "录音超时，请重试"
        except Exception as e:
            print(f"语音识别失败: {e}")
            return f"识别错误: {str(e)}"
    
    def record_audio(self, duration=5, sample_rate=16000, channels=1, chunk=1024):
        """录制音频并返回音频数据和临时文件路径"""
        try:
            audio = pyaudio.PyAudio()
            
            # 开始录音
            stream = audio.open(format=pyaudio.paInt16,
                               channels=channels,
                               rate=sample_rate,
                               input=True,
                               frames_per_buffer=chunk)
            
            print(f"开始录音，持续{duration}秒...")
            frames = []
            
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            print("录音结束")
            
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
            
            # 读取音频数据用于识别
            with sr.AudioFile(temp_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            return audio_data, temp_file_path
        except Exception as e:
            print(f"录音失败: {e}")
            return None, None
    
    def text_to_speech(self, text, output_file=None, language='zh-CN'):
        """将文字转换为语音（这里简化实现，实际项目中可能需要使用更专业的TTS服务）"""
        # 注意：这里只是一个简化的实现，实际项目中可以使用如百度AI、讯飞等专业的TTS服务
        print(f"生成语音: {text}")
        
        # 为了演示，我们可以返回一个简单的结果
        if output_file:
            # 这里应该是实际的TTS代码
            print(f"语音已保存到: {output_file}")
            return output_file
        
        return "语音生成成功"