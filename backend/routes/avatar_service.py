#!/usr/bin/env python3
"""
用户头像生成服务
为用户生成基于昵称的占位符头像
"""

import os
import io
import base64
import colorsys
from PIL import Image, ImageDraw, ImageFont

def generate_color_from_name(name):
    """根据名字生成一个颜色"""
    # 使用名字的哈希值生成颜色
    hash_value = hash(name) % 360
    # 使用HSV颜色空间，固定饱和度和亮度，只改变色相
    rgb = colorsys.hsv_to_rgb(hash_value / 360.0, 0.7, 0.9)
    return tuple(int(c * 255) for c in rgb)

def get_avatar_text(name):
    """根据名字获取头像显示文本"""
    if not name:
        return "?"
    
    # 检查是否包含中文字符
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in name)
    
    if has_chinese:
        # 中文名取第一个字符
        return name[0]
    else:
        # 英文名取缩写（最多2个字符）
        words = name.strip().split()
        if len(words) >= 2:
            # 取前两个单词的首字母
            return (words[0][0] + words[1][0]).upper()
        elif len(words) == 1 and len(words[0]) >= 2:
            # 单个单词取前两个字母
            return words[0][:2].upper()
        else:
            # 单个字符
            return words[0][0].upper() if words else "?"

def create_user_avatar(name, size=(256, 256)):
    """创建用户头像并返回base64编码"""
    # 创建图片
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # 生成背景颜色
    bg_color = generate_color_from_name(name)
    
    # 绘制圆形背景
    margin = 20
    circle_bbox = [margin, margin, size[0] - margin, size[1] - margin]
    draw.ellipse(circle_bbox, fill=bg_color)
    
    # 获取显示文本
    text = get_avatar_text(name)
    
    # 尝试使用系统字体
    try:
        # Windows系统字体
        font_size = 80 if len(text) == 1 else 60
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
    except:
        try:
            # 备用字体
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # 默认字体
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - 10  # 稍微向上偏移
    
    # 绘制文字（白色）
    draw.text((x, y), text, fill='white', font=font)
    
    # 转换为base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # 生成data URL
    img_data = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_data}"

def save_user_avatar(name, user_id, output_dir="frontend/public/user-avatars"):
    """保存用户头像到文件系统"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建头像
    image = Image.new('RGB', (256, 256), 'white')
    draw = ImageDraw.Draw(image)
    
    # 生成背景颜色
    bg_color = generate_color_from_name(name)
    
    # 绘制圆形背景
    margin = 20
    circle_bbox = [margin, margin, 256 - margin, 256 - margin]
    draw.ellipse(circle_bbox, fill=bg_color)
    
    # 获取显示文本
    text = get_avatar_text(name)
    
    # 尝试使用系统字体
    try:
        font_size = 80 if len(text) == 1 else 60
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10
    
    # 绘制文字（白色）
    draw.text((x, y), text, fill='white', font=font)
    
    # 保存图片
    output_path = os.path.join(output_dir, f"user_{user_id}.png")
    image.save(output_path, 'PNG')
    
    return f"/user-avatars/user_{user_id}.png"

def create_character_avatar(character_name, character_id, output_dir="frontend/public/avatars"):
    """为角色创建头像并保存到文件系统"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建头像
    image = Image.new('RGB', (256, 256), 'white')
    draw = ImageDraw.Draw(image)
    
    # 生成背景颜色
    bg_color = generate_color_from_name(character_name)
    
    # 绘制圆形背景
    margin = 20
    circle_bbox = [margin, margin, 256 - margin, 256 - margin]
    draw.ellipse(circle_bbox, fill=bg_color)
    
    # 获取显示文本
    text = get_avatar_text(character_name)
    
    # 尝试使用系统字体
    try:
        font_size = 80 if len(text) == 1 else 60
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (256 - text_width) // 2
    y = (256 - text_height) // 2 - 10
    
    # 绘制文字（白色）
    draw.text((x, y), text, fill='white', font=font)
    
    # 保存图片
    output_path = os.path.join(output_dir, f"{character_id}.png")
    image.save(output_path, 'PNG')
    
    return f"/avatars/{character_id}.png"
