package com.nekkotavern.model;

import com.google.gson.annotations.SerializedName;

import java.util.HashMap;
import java.util.Map;
/**
 * 模型参数
 */
public class ModelParameters {
    private int numCtx = 2048;           // 上下文窗口大小
    private float repeatPenalty = 1.5f;  // 重复惩罚
    private float temperature = 0.95f;   // 温度
    private int topK = 40;              // Top-K采样
    private float topP = 0.95f;         // Top-P采样
    private int numPredict = 256;       // 预测token数

    // Getters and Setters
    public int getNumCtx() { return numCtx; }
    public void setNumCtx(int numCtx) { this.numCtx = numCtx; }

    public float getTemperature() { return temperature; }
    public void setTemperature(float temp) { this.temperature = temp; }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("num_ctx", numCtx);
        map.put("repeat_penalty", repeatPenalty);
        map.put("temperature", temperature);
        map.put("top_k", topK);
        map.put("top_p", topP);
        map.put("num_predict", numPredict);
        return map;
    }
}
