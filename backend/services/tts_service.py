"""
七牛云TTS语音合成服务模块
"""
import requests
import json
import logging
import re
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class TTSService:
    """七牛云TTS语音合成服务类"""
    
    def __init__(self):
        # 七牛云TTS API配置
        self.api_key = Config.QINIU_AI_API_KEY
        self.base_url = Config.QINIU_AI_BASE_URL
        self.tts_url = f"{self.base_url}/voice/tts"
        
        # 角色音色映射 - 根据AI角色特征精心匹配音色
        self.character_voices = {
            # 科学家/学者 - 使用沉稳、知性的音色
            'albert-einstein': 'qiniu_zh_male_ybxknjs',  # 优秀学科男教师 - 符合物理学家的学者气质
            'marie-curie': 'qiniu_zh_female_wwxkjx',  # 温文学科教学 - 符合女科学家的知性形象
            'leonardo-da-vinci': 'qiniu_zh_male_whxkxg',  # 文化学者小刚 - 符合文艺复兴大师的博学
            'nikola-tesla': 'qiniu_zh_male_cxkjns',  # 创新科技男士 - 完美匹配发明家特质
            'ada-lovelace': 'qiniu_zh_female_cxjxgw',  # 创新教学顾问 - 符合计算机先驱的创新精神
            
            # 哲学家/思想家 - 使用深沉、智慧的音色
            'confucius': 'qiniu_zh_male_tyygjs',  # 通用语言讲师 - 符合教育家的威严
            'socrates': 'qiniu_zh_male_wncwxz',  # 温暖成稳学者 - 符合哲学家的睿智
            
            # 文学家/艺术家 - 使用优雅、富有表现力的音色
            'shakespeare': 'qiniu_zh_male_ljfdxz',  # 邻家风度学者 - 符合文学大师的优雅
            'jane-austen': 'qiniu_zh_female_zxjxnjs',  # 知性教学女教师 - 符合女作家的知性优雅
            'frida-kahlo': 'qiniu_zh_female_sqjyay',  # 深情教育阿姨 - 符合艺术家的情感丰富
            
            # 历史人物/领袖 - 使用威严、有力的音色
            'napoleon': 'qiniu_zh_male_hllzmz',  # 活力理智男子 - 符合军事领袖的果断
            'cleopatra': 'qiniu_zh_female_dmytwz',  # 动漫御姐王者 - 符合女王的威严气质
            'sun-tzu': 'qiniu_zh_male_mzjsxg',  # 魅力绅士小哥 - 符合兵法家的智慧魅力
            
            # 现代企业家/科技领袖 - 使用现代、商务的音色
            'steve-jobs': 'qiniu_zh_male_tcsnsf',  # 特色商务男士 - 完美匹配商业领袖
            'bill-gates': 'qiniu_zh_male_gzjjxb',  # 高质精进学霸 - 符合技术天才的特质
            'elon-musk': 'qiniu_zh_male_qslymb',  # 青春励志男孩 - 符合创新企业家的活力
            'jack-ma': 'qiniu_zh_male_hlsnkk',  # 活力少年开朗 - 符合马云的亲和力和活力
            'mark-zuckerberg': 'qiniu_zh_male_szxyxd',  # 深圳校园学弟 - 符合年轻CEO的形象
            
            # 技术专家 - 使用专业、理性的音色
            'linus-torvalds': 'qiniu_zh_male_whxkxg',  # 文化学者小刚 - 符合技术大师的学者气质
            'tim-berners-lee': 'qiniu_zh_male_ybxknjs',  # 优秀学科男教师 - 符合万维网之父的教育者形象
            
            # 娱乐/创意人物 - 使用温暖、有趣的音色
            'miyazaki-hayao': 'qiniu_zh_male_wncwxz',  # 温暖成稳学者 - 符合动画大师的温暖气质
            'bruce-lee': 'qiniu_zh_male_etgsxe',  # 儿童故事小二 - 虽然是功夫巨星，但内心纯真
            
            # 虚构角色 - 使用年轻、有活力的音色
            'harry-potter': 'qiniu_zh_male_etgsxe',  # 儿童故事小二 - 完美匹配少年巫师
            'sherlock-holmes': 'qiniu_zh_male_ljfdxz',  # 邻家风度学者 - 符合绅士侦探的优雅
            
            # 默认音色
            'default': 'qiniu_zh_female_wwxkjx',
        }
        
        # 默认音色
        self.default_voice = 'qiniu_zh_female_wwxkjx'
    
    def get_voice_for_character(self, character_id: str) -> str:
        """
        根据角色ID获取对应的音色
        :param character_id: 角色ID
        :return: 音色ID
        """
        return self.character_voices.get(character_id, self.default_voice)
    
    def clean_text_for_tts(self, text: str) -> str:
        """
        清理文本，去除语气助词和修饰词
        :param text: 原始文本
        :return: 清理后的文本
        """
        # 去除常见的语气助词和修饰词
        patterns_to_remove = [
            # 括号内容（包括各种括号类型）
            r'（[^）]*）',  # 中文圆括号
            r'\([^)]*\)',  # 英文圆括号
            r'【[^】]*】',  # 中文方括号
            r'\[[^\]]*\]',  # 英文方括号
            r'《[^》]*》',  # 书名号
            r'<[^>]*>',    # 尖括号
            r'「[^」]*」',  # 日式引号
            r'『[^』]*』',  # 日式双引号
            
            # 星号包围的内容（动作描述等）
            r'\*[^*]*\*',   # 单星号包围
            r'\*\*[^*]*\*\*', # 双星号包围
            r'＊[^＊]*＊',   # 全角星号包围
            
            # 语气助词
            r'[嗯呢啊哦呀嘛吧呗哈哟咦唉嘿嘻]',  # 常见语气助词
            r'额+',        # 额（一个或多个）
            r'那个+',      # 那个（一个或多个）
            r'这个+',      # 这个（一个或多个）
            r'就是说+',    # 就是说（一个或多个）
            r'然后+',      # 然后（一个或多个）
            r'所以说+',    # 所以说（一个或多个）
            
            # 特殊符号
            r'[～~]+',     # 波浪号
            r'[…\.]{3,}',  # 多个省略号
            r'[！!]{2,}',  # 多个感叹号
            r'[？?]{2,}',  # 多个问号
            r'[，,]{2,}',  # 多个逗号
            
            # 网络用语和表情符号
            r'[哈哈哈]{3,}', # 多个哈
            r'[呵呵呵]{3,}', # 多个呵
            r'[嘿嘿嘿]{3,}', # 多个嘿
            r'[嘻嘻嘻]{3,}', # 多个嘻
        ]
        
        cleaned_text = text
        
        # 按顺序应用清理规则
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 清理多余的空格和换行
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # 去除连续的标点符号
        cleaned_text = re.sub(r'[，。！？]{2,}', '。', cleaned_text)
        
        # 去除过短的句子（可能是剩余的语气词）
        sentences = []
        for sentence in cleaned_text.split('。'):
            sentence = sentence.strip()
            # 只保留长度大于2且不全是标点符号的句子
            if len(sentence) > 2 and not re.match(r'^[，。！？、；：""''（）【】《》<>]*$', sentence):
                sentences.append(sentence)
        
        cleaned_text = '。'.join(sentences)
        
        # 确保以句号结尾
        if cleaned_text and not cleaned_text.endswith(('。', '！', '？', '.')):
            cleaned_text += '。'
        
        # 如果清理后文本为空或过短，返回原文本的简化版本
        if not cleaned_text or len(cleaned_text.strip()) < 3:
            # 至少保留基本内容，只去除括号和星号内容
            fallback_text = re.sub(r'（[^）]*）|\([^)]*\)|\*[^*]*\*', '', text).strip()
            if fallback_text and len(fallback_text) > 2:
                cleaned_text = fallback_text
                if not cleaned_text.endswith(('。', '！', '？', '.')):
                    cleaned_text += '。'
            else:
                cleaned_text = text  # 最后的保险，返回原文本
        
        logger.info(f"文本清理: '{text}' -> '{cleaned_text}'")
        return cleaned_text
    
    def calculate_speed_ratio(self, text: str) -> float:
        """
        根据文本长度计算语速比例
        :param text: 文本内容
        :return: 语速比例 (0.5-2.0)
        """
        text_length = len(text)
        
        if text_length <= 20:
            # 短文本，稍慢一些
            speed_ratio = 0.9
        elif text_length <= 50:
            # 中等文本，正常语速
            speed_ratio = 1.0
        elif text_length <= 100:
            # 较长文本，稍快一些
            speed_ratio = 1.1
        else:
            # 很长文本，更快一些
            speed_ratio = 1.2
        
        # 确保在合理范围内
        speed_ratio = max(0.8, min(1.5, speed_ratio))
        
        logger.info(f"文本长度: {text_length}, 语速比例: {speed_ratio}")
        return speed_ratio
    
    def text_to_speech(self, text: str, character_id: str = None, encoding: str = "mp3") -> Dict[str, Any]:
        """
        文字转语音
        :param text: 要转换的文本
        :param character_id: 角色ID
        :param encoding: 音频编码格式
        :return: 转换结果
        """
        try:
            # 清理文本
            cleaned_text = self.clean_text_for_tts(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 2:
                return {
                    "success": False,
                    "error": "文本内容为空或过短"
                }
            
            # 获取角色对应的音色
            voice_type = self.get_voice_for_character(character_id)
            
            # 计算语速
            speed_ratio = self.calculate_speed_ratio(cleaned_text)
            
            logger.info(f"TTS请求: 角色={character_id}, 音色={voice_type}, 语速={speed_ratio}, 文本长度={len(cleaned_text)}")
            
            # 构建请求参数 - 根据七牛云文档格式
            payload = {
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                    "speed_ratio": speed_ratio
                },
                "request": {
                    "text": cleaned_text
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # 发送请求
            logger.info(f"发送TTS请求到: {self.tts_url}")
            logger.info(f"请求头: {headers}")
            logger.info(f"请求体: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                self.tts_url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=30
            )
            
            logger.info(f"TTS API响应状态码: {response.status_code}")
            logger.info(f"TTS API响应头: {response.headers}")
            
            if response.status_code != 200:
                logger.error(f"TTS API错误响应: {response.text}")
                return {
                    "success": False,
                    "error": f"TTS API返回错误状态码: {response.status_code}"
                }
            
            result = response.json()
            logger.info(f"TTS API响应: {result}")
            
            # 检查响应
            if result.get("data"):
                return {
                    "success": True,
                    "audio_data": result["data"],  # base64编码的音频数据
                    "duration": result.get("addition", {}).get("duration", "0"),
                    "voice_type": voice_type,
                    "speed_ratio": speed_ratio,
                    "original_text": text,
                    "cleaned_text": cleaned_text
                }
            else:
                logger.error(f"TTS响应无音频数据: {result}")
                return {
                    "success": False,
                    "error": "语音合成失败，无音频数据返回"
                }
                
        except requests.exceptions.Timeout:
            logger.error("TTS请求超时")
            return {
                "success": False,
                "error": "语音合成请求超时"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS网络请求错误: {e}")
            return {
                "success": False,
                "error": "网络请求失败，请检查网络连接"
            }
        except Exception as e:
            logger.error(f"TTS发生未知错误: {e}")
            return {
                "success": False,
                "error": "语音合成服务异常，请稍后重试"
            }

# 创建全局TTS服务实例
tts_service = TTSService()
