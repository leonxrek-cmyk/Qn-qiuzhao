import logging
import os
import time
import datetime
from logging.handlers import RotatingFileHandler
import json

class LogService:
    _instance = None
    _loggers = {}
    _log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # 确保日志目录存在
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        
        # 配置根日志
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        if root_logger.handlers:
            root_logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器（使用轮转文件）
        log_file = os.path.join(self._log_dir, "app.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 创建错误日志处理器
        error_log_file = os.path.join(self._log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 应用格式到处理器
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # 添加处理器到根日志记录器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name):
        """获取指定名称的日志记录器"""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def info(self, name, message):
        """记录信息级别日志"""
        logger = self.get_logger(name)
        logger.info(message)
    
    def debug(self, name, message):
        """记录调试级别日志"""
        logger = self.get_logger(name)
        logger.debug(message)
    
    def warning(self, name, message):
        """记录警告级别日志"""
        logger = self.get_logger(name)
        logger.warning(message)
    
    def error(self, name, message, exc_info=False):
        """记录错误级别日志"""
        logger = self.get_logger(name)
        logger.error(message, exc_info=exc_info)
    
    def critical(self, name, message, exc_info=False):
        """记录严重错误级别日志"""
        logger = self.get_logger(name)
        logger.critical(message, exc_info=exc_info)
    
    def log_api_request(self, endpoint, method, status_code, response_time, request_data=None):
        """记录API请求日志"""
        logger = self.get_logger("api")
        log_message = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": f"{response_time:.3f}s"
        }
        
        if request_data:
            try:
                # 尝试序列化请求数据
                log_message["request_data"] = json.dumps(request_data, ensure_ascii=False)
            except:
                log_message["request_data"] = str(request_data)
        
        logger.info(json.dumps(log_message, ensure_ascii=False))
    
    def log_chat_message(self, character_id, user_id, message_type, content):
        """记录聊天消息日志"""
        logger = self.get_logger("chat")
        log_message = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "character_id": character_id,
            "user_id": user_id,
            "type": message_type,  # 'user' 或 'ai'
            "content": content
        }
        
        logger.info(json.dumps(log_message, ensure_ascii=False))
    
    def log_tts_request(self, character_id, text_length):
        """记录文字转语音请求日志"""
        logger = self.get_logger("tts")
        log_message = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "character_id": character_id,
            "text_length": text_length
        }
        
        logger.info(json.dumps(log_message, ensure_ascii=False))
    
    # 保留原有静态方法以保持向后兼容
    @staticmethod
    def log(current_time=None, model_name='Unknown', function_name='Unknown', log_level='Info', message=''):
        """统一的日志输出方法（向后兼容）"""
        if current_time is None:
            current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        
        print(f"[{current_time}--{model_name}-{function_name}-[{log_level}]: {message}")
    
    @staticmethod
    def get_current_time():
        """获取当前格式化的时间（向后兼容）"""
        return datetime.datetime.now().strftime('%Y%m%d/%H:%M')

# 创建全局日志服务实例
log_service = LogService()

# 导出常用的日志方法
def get_logger(name):
    return log_service.get_logger(name)

def info(name, message):
    log_service.info(name, message)

def debug(name, message):
    log_service.debug(name, message)

def warning(name, message):
    log_service.warning(name, message)

def error(name, message, exc_info=False):
    log_service.error(name, message, exc_info)

def critical(name, message, exc_info=False):
    log_service.critical(name, message, exc_info)

def log_api_request(endpoint, method, status_code, response_time, request_data=None):
    log_service.log_api_request(endpoint, method, status_code, response_time, request_data)

def log_chat_message(character_id, user_id, message_type, content):
    log_service.log_chat_message(character_id, user_id, message_type, content)

def log_tts_request(character_id, text_length):
    log_service.log_tts_request(character_id, text_length)