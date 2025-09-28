"""
百度语音识别服务模块
"""
import requests
import json
import base64
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ASRService:
    """百度语音识别服务类"""
    
    def __init__(self):
        # 百度语音识别API配置
        self.API_KEY = "whM6EREF7zF8yrd1eBhULQ1U"
        self.SECRET_KEY = "hOcgzrqnAvWp6TW1qtxMFj7Rtns1sivM"
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.asr_url = "https://vop.baidu.com/server_api"
        self._access_token = None
    
    def get_access_token(self) -> Optional[str]:
        """
        获取百度API访问令牌
        :return: access_token 或 None
        """
        try:
            params = {
                "grant_type": "client_credentials",
                "client_id": self.API_KEY,
                "client_secret": self.SECRET_KEY
            }
            
            response = requests.post(self.token_url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            access_token = result.get("access_token")
            
            if access_token:
                self._access_token = access_token
                logger.info("成功获取百度API访问令牌")
                return access_token
            else:
                logger.error(f"获取访问令牌失败: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求访问令牌时发生网络错误: {e}")
            return None
        except Exception as e:
            logger.error(f"获取访问令牌时发生未知错误: {e}")
            return None
    
    def audio_to_base64(self, audio_data: bytes) -> str:
        """
        将音频数据转换为base64编码
        :param audio_data: 音频二进制数据
        :return: base64编码的字符串
        """
        return base64.b64encode(audio_data).decode('utf-8')
    
    def speech_to_text(self, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        语音转文字 - 按照百度API官方规范
        :param audio_data: 音频二进制数据
        :param audio_format: 音频格式 (wav, mp3, pcm等)
        :return: 识别结果字典
        """
        try:
            logger.info(f"开始语音识别，音频大小: {len(audio_data)} bytes, 格式: {audio_format}")
            
            # 获取访问令牌
            if not self._access_token:
                token = self.get_access_token()
                if not token:
                    logger.error("无法获取API访问令牌")
                    return {
                        "success": False,
                        "error": "无法获取API访问令牌"
                    }
            
            # 按照百度API官方规范处理音频数据
            if audio_format.lower() == 'wav':
                # 对于WAV文件，提取PCM数据
                pcm_data, actual_sample_rate = self._extract_pcm_data(audio_data, audio_format)
                if pcm_data is None:
                    return {
                        "success": False,
                        "error": "WAV文件PCM数据提取失败"
                    }
                
                # 使用PCM数据
                speech_base64 = self.audio_to_base64(pcm_data)
                speech_length = len(pcm_data)  # PCM原始数据的字节长度
                format_type = "pcm"
                
                logger.info(f"WAV->PCM提取完成，PCM大小: {speech_length} bytes, 采样率: {actual_sample_rate}Hz")
                
            else:
                # 对于其他格式，直接使用原始音频数据
                speech_base64 = self.audio_to_base64(audio_data)
                speech_length = len(audio_data)  # 原始音频文件的字节长度
                actual_sample_rate = 16000  # 默认采样率
                format_type = audio_format.lower()
                
                logger.info(f"直接使用原始音频，格式: {format_type}, 大小: {speech_length} bytes")
            
            logger.info(f"Base64编码长度: {len(speech_base64)} (原始数据: {speech_length} bytes)")
            
            # 按照百度API官方规范构建请求参数
            payload = {
                "format": format_type,  # pcm/wav/amr/m4a
                "rate": actual_sample_rate,  # 采样率
                "channel": 1,   # 单声道
                "cuid": "baidu_workshop",  # 用户唯一标识
                "speech": speech_base64,  # 音频文件二进制内容的base64编码
                "len": speech_length,  # 原始音频文件的字节数（不是base64后的长度）
                "token": self._access_token,
                "dev_pid": 1537  # 普通话输入法模型
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            logger.info(f"发送识别请求到百度API")
            logger.info(f"请求参数: format={format_type}, rate={actual_sample_rate}, channel=1, len={speech_length}")
            logger.info(f"Token: {self._access_token[:20] if self._access_token else 'None'}...")
            logger.info(f"Base64数据长度: {len(speech_base64)}")
            
            # 检查音频数据的前几个字节（解码后）
            if len(audio_data) >= 12:
                header_hex = audio_data[:12].hex()
                logger.info(f"音频文件头: {header_hex}")
                
                # 检测实际格式
                if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                    logger.info("检测到WAV格式")
                    # 检查WAV文件的详细信息
                    if len(audio_data) >= 44:
                        # 解析WAV文件头
                        import struct
                        try:
                            # 读取fmt chunk信息
                            fmt_data = audio_data[20:36]
                            audio_format, channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_data)
                            logger.info(f"WAV详情: 格式={audio_format}, 声道={channels}, 采样率={sample_rate}, 位深={bits_per_sample}")
                            
                            # 检查是否符合百度API要求
                            if sample_rate != 16000:
                                logger.warning(f"采样率不符合要求: {sample_rate} (期望16000)")
                            if channels != 1:
                                logger.warning(f"声道数不符合要求: {channels} (期望1)")
                            if bits_per_sample != 16:
                                logger.warning(f"位深不符合要求: {bits_per_sample} (期望16)")
                        except Exception as e:
                            logger.error(f"解析WAV文件头失败: {e}")
                elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                    logger.info("检测到WebM格式")
                    logger.warning("WebM格式可能不被百度API正确支持")
                else:
                    logger.warning(f"未识别的格式，使用原格式: {audio_format} -> {format_type}")
                    logger.info(f"文件头详细: {header_hex}")
            
            # 检查音频数据大小是否合理
            if len(audio_data) < 1000:
                logger.warning(f"音频数据过小: {len(audio_data)} bytes，可能导致识别失败")
            elif len(audio_data) > 10 * 1024 * 1024:
                logger.warning(f"音频数据过大: {len(audio_data)} bytes")
            else:
                logger.info(f"音频数据大小正常: {len(audio_data)} bytes")
            
            # 发送识别请求
            response = requests.post(
                self.asr_url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"百度API响应: {result}")
            
            # 解析结果
            if result.get("err_no") == 0:
                # 识别成功
                recognized_text = result.get("result", [""])[0] if result.get("result") else ""
                logger.info(f"语音识别成功: {recognized_text}")
                return {
                    "success": True,
                    "text": recognized_text,
                    "confidence": result.get("confidence", 0),
                    "raw_result": result
                }
            else:
                # 识别失败
                error_code = result.get("err_no", -1)
                error_msg = self._get_error_message(error_code)
                logger.error(f"语音识别失败: {error_msg}, 错误码: {error_code}, 完整响应: {result}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_code": error_code,
                    "raw_result": result
                }
                
        except requests.exceptions.Timeout:
            logger.error("语音识别请求超时")
            return {
                "success": False,
                "error": "请求超时，请重试"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"语音识别网络请求错误: {e}")
            return {
                "success": False,
                "error": "网络请求失败，请检查网络连接"
            }
        except Exception as e:
            logger.error(f"语音识别发生未知错误: {e}")
            return {
                "success": False,
                "error": "语音识别服务异常，请稍后重试"
            }
    
    def _extract_pcm_data(self, audio_data: bytes, audio_format: str) -> tuple:
        """
        从音频数据中提取PCM原始数据
        :param audio_data: 音频二进制数据
        :param audio_format: 音频格式
        :return: (pcm_data, sample_rate) 或 (None, None)
        """
        try:
            if audio_format.lower() == 'wav':
                return self._extract_pcm_from_wav(audio_data)
            elif audio_format.lower() in ['webm', 'ogg', 'mp3', 'm4a']:
                # 对于这些格式，尝试使用ffmpeg或返回错误提示
                logger.error(f"收到未转换的 {audio_format} 格式")
                logger.error("前端音频转换可能失败，请检查转换逻辑")
                return None, None
            else:
                logger.error(f"不支持的音频格式: {audio_format}")
                return None, None
        except Exception as e:
            logger.error(f"提取PCM数据失败: {e}")
            return None, None
    
    def _extract_pcm_from_wav(self, wav_data: bytes) -> tuple:
        """
        从WAV文件中提取PCM数据
        :param wav_data: WAV文件的二进制数据
        :return: (pcm_data, sample_rate) 或 (None, None)
        """
        try:
            import struct
            
            # 检查WAV文件头
            if not wav_data.startswith(b'RIFF') or b'WAVE' not in wav_data[:20]:
                logger.error("不是有效的WAV文件")
                return None, None
            
            # 解析WAV文件头
            if len(wav_data) < 44:
                logger.error("WAV文件头不完整")
                return None, None
            
            # 读取fmt chunk信息 (偏移20-35)
            fmt_data = wav_data[20:36]
            audio_format, channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', fmt_data)
            
            logger.info(f"WAV文件信息: 格式={audio_format}, 声道={channels}, 采样率={sample_rate}, 位深={bits_per_sample}")
            
            # 检查是否为PCM格式
            if audio_format != 1:
                logger.error(f"不支持的音频格式: {audio_format} (需要PCM格式)")
                return None, None
            
            # 查找data chunk
            data_offset = 36
            while data_offset < len(wav_data) - 8:
                chunk_id = wav_data[data_offset:data_offset+4]
                chunk_size = struct.unpack('<I', wav_data[data_offset+4:data_offset+8])[0]
                
                if chunk_id == b'data':
                    # 找到data chunk，提取PCM数据
                    pcm_start = data_offset + 8
                    pcm_end = pcm_start + chunk_size
                    pcm_data = wav_data[pcm_start:pcm_end]
                    
                    logger.info(f"提取PCM数据: {len(pcm_data)} bytes")
                    
                    # 如果是立体声，转换为单声道
                    if channels == 2:
                        pcm_data = self._convert_stereo_to_mono(pcm_data, bits_per_sample)
                        logger.info("已转换立体声为单声道")
                    
                    return pcm_data, sample_rate
                
                # 移动到下一个chunk
                data_offset += 8 + chunk_size
            
            logger.error("未找到data chunk")
            return None, None
            
        except Exception as e:
            logger.error(f"解析WAV文件失败: {e}")
            return None, None
    
    def _convert_stereo_to_mono(self, stereo_data: bytes, bits_per_sample: int) -> bytes:
        """
        将立体声PCM数据转换为单声道
        :param stereo_data: 立体声PCM数据
        :param bits_per_sample: 位深度
        :return: 单声道PCM数据
        """
        try:
            import struct
            
            if bits_per_sample == 16:
                # 16位立体声转单声道
                samples = struct.unpack(f'<{len(stereo_data)//2}h', stereo_data)
                mono_samples = []
                
                # 每两个样本（左右声道）混合为一个样本
                for i in range(0, len(samples), 2):
                    if i + 1 < len(samples):
                        # 混合左右声道
                        mixed = (samples[i] + samples[i+1]) // 2
                        mono_samples.append(mixed)
                    else:
                        mono_samples.append(samples[i])
                
                return struct.pack(f'<{len(mono_samples)}h', *mono_samples)
            else:
                logger.warning(f"不支持的位深度: {bits_per_sample}")
                return stereo_data
                
        except Exception as e:
            logger.error(f"立体声转单声道失败: {e}")
            return stereo_data
    
    def _get_baidu_format(self, audio_format: str) -> str:
        """
        将通用音频格式转换为百度API支持的格式
        :param audio_format: 通用格式
        :return: 百度API格式
        """
        # 百度API支持的格式：pcm, wav, mp3, silk, amr, m4a
        format_mapping = {
            "wav": "wav",
            "mp3": "mp3", 
            "m4a": "m4a",
            "amr": "amr",
            "pcm": "pcm",
            # 对于浏览器常见的格式，映射到百度支持的格式
            # 注意：WebM/Opus应该在前端转换为WAV，不应该直接映射
            "webm": "wav",  # 应该已经在前端转换为WAV
            "ogg": "wav",   # OGG转换为wav处理
            "opus": "wav",  # Opus编码转换为wav处理
            "aac": "m4a",   # AAC当作m4a处理
            "mp4": "m4a",   # MP4音频当作m4a处理
        }
        
        # 从文件扩展名中提取格式
        if '.' in audio_format:
            audio_format = audio_format.split('.')[-1]
        
        # 从MIME类型中提取格式
        if '/' in audio_format:
            audio_format = audio_format.split('/')[-1]
        
        # 处理带编码器的格式
        if ';' in audio_format:
            audio_format = audio_format.split(';')[0]
        
        mapped_format = format_mapping.get(audio_format.lower(), "wav")
        logger.info(f"音频格式映射: {audio_format} -> {mapped_format}")
        return mapped_format
    
    def _get_error_message(self, error_code: int) -> str:
        """
        根据错误码获取错误信息
        :param error_code: 百度API错误码
        :return: 错误信息
        """
        error_messages = {
            3300: "输入参数不正确",
            3301: "音频质量过差",
            3302: "鉴权失败",
            3303: "语音服务器后端问题",
            3304: "用户的请求QPS超限",
            3305: "用户的日pv（日请求量）超限",
            3307: "语音过长",
            3308: "音频无效",
            3309: "音频文件过大",
            3310: "音频文件下载失败",
            3311: "音频时长过长",
            3312: "音频格式不支持",
        }
        return error_messages.get(error_code, f"未知错误 (错误码: {error_code})")

# 创建全局ASR服务实例
asr_service = ASRService()
