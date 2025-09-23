// ========== 配置管理器 ==========
package com.nekkotavern.utils;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.*;
import java.nio.file.*;

/**
 * 配置管理器 - 单例模式管理应用配置
 */
public class ConfigManager {
    private static ConfigManager instance;
    private Configuration config;
    private final Gson gson;
    private String configPath;

    private ConfigManager() {
        this.gson = new GsonBuilder()
                .setPrettyPrinting()
                .create();
    }

    /**
     * 获取单例实例
     */
    public static synchronized ConfigManager getInstance() {
        if (instance == null) {
            instance = new ConfigManager();
        }
        return instance;
    }

    /**
     * 加载配置文件
     */
    public void loadConfig(String path) {
        this.configPath = path;
        try {
            String json = Files.readString(Paths.get(path));
            config = gson.fromJson(json, Configuration.class);
            System.out.println("配置文件加载成功: " + path);
        } catch (IOException e) {
            System.err.println("配置文件加载失败，使用默认配置: " + e.getMessage());
            config = createDefaultConfig();
            saveConfig();
        }
    }

    /**
     * 保存配置文件
     */
    public void saveConfig() {
        try {
            String json = gson.toJson(config);
            Files.writeString(Paths.get(configPath), json);
            System.out.println("配置文件保存成功");
        } catch (IOException e) {
            System.err.println("配置文件保存失败: " + e.getMessage());
        }
    }

    /**
     * 创建默认配置
     */
    private Configuration createDefaultConfig() {
        Configuration config = new Configuration();
        config.setCharacter("character/Nekko/Nekko.png");
        config.setSttModelPath("model/faster-whisper-small");
        config.setKeyTTS("Ctrl+P");
        config.setKeyRecording("Ctrl+R");
        return config;
    }

    public Configuration getConfig() {
        return config;
    }
}
