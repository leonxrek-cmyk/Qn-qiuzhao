package com.nekkotavern.model;


import com.google.gson.annotations.SerializedName;
import java.util.Map;

/**
 * 消息模型
 */
public class Message {
    private String role;      // user/assistant/system
    private String content;   // 消息内容
    private long timestamp;   // 时间戳

    public Message(String role, String content) {
        this.role = role;
        this.content = content;
        this.timestamp = System.currentTimeMillis();
    }

    // Getters and Setters
    public String getRole() { return role; }
    public String getContent() { return content; }
    public long getTimestamp() { return timestamp; }
}

