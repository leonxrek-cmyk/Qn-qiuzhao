try:
    import aifc
    print("aifc模块导入成功")
except ImportError:
    print("aifc模块导入失败")
    
# 也测试speech_recognition库是否使用aifc
import speech_recognition as sr
print("speech_recognition库导入成功")