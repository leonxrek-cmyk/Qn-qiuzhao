// ========== 模型类 ==========
package com.nekkotavern.model;

import com.google.gson.annotations.SerializedName;
import java.util.Map;

/**
 * 角色配置模型
 */
public class Character {
    private String name;                    // 角色名称
    @SerializedName("ref_audio")
    private String refAudioPath;            // 参考音频路径
    @SerializedName("ref_audio_lang")
    private String promptLang;              // 参考音频语言
    @SerializedName("speed_factor")
    private float speedFactor;              // 语速因子
    @SerializedName("from_model")
    private String baseModel;               // 基础模型
    private ModelParameters parameters;     // 模型参数
    private String description;             // 角色描述
    private String template;                // 模板
    private String message;                 // 消息

    // Getters and Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getRefAudioPath() { return refAudioPath; }
    public void setRefAudioPath(String path) { this.refAudioPath = path; }

    public String getPromptLang() { return promptLang; }
    public void setPromptLang(String lang) { this.promptLang = lang; }

    public String getPromptText() {
        // 从音频文件名提取提示文本
        if (refAudioPath != null) {
            String fileName = refAudioPath.substring(refAudioPath.lastIndexOf('/') + 1);
            return fileName.substring(0, fileName.lastIndexOf('.'));
        }
        return "";
    }

    public float getSpeedFactor() { return speedFactor; }
    public void setSpeedFactor(float factor) { this.speedFactor = factor; }

    public String getMemoryPath() {
        // 返回记忆存储路径
        return "memory/" + name;
    }
}