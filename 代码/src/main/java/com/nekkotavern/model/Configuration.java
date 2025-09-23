package com.nekkotavern.model;
import com.google.gson.annotations.SerializedName;
import java.util.Map;

/**
 * 配置模型
 */
public class Configuration {
    private String character;           // 角色文件路径
    @SerializedName("stt_model_path")
    private String sttModelPath;       // STT模型路径
    @SerializedName("key_tts")
    private String keyTTS;              // TTS快捷键
    @SerializedName("key_recording")
    private String keyRecording;        // 录音快捷键

    public String getCharacterPath() { return character; }
    public String getSttModelPath() { return sttModelPath; }
    public String getKeyTTS() { return keyTTS; }
    public String getKeyRecording() { return keyRecording;

    }

    public String getCharacter() {
        return character;
    }

    public void setCharacter(String character) {
        this.character = character;
    }

    public void setKeyRecording(String keyRecording) {
        this.keyRecording = keyRecording;
    }

    public void setKeyTTS(String keyTTS) {
        this.keyTTS = keyTTS;
    }

    public void setSttModelPath(String sttModelPath) {
        this.sttModelPath = sttModelPath;
    }

    @Override
    public String toString() {
        return "Configuration{" +
                "character='" + character + '\'' +
                ", sttModelPath='" + sttModelPath + '\'' +
                ", keyTTS='" + keyTTS + '\'' +
                ", keyRecording='" + keyRecording + '\'' +
                '}';
    }
}