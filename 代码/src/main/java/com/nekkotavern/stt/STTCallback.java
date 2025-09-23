
// ===== STT回调接口 =====
package com.nekkotavern.stt;

/**
 * 语音识别回调接口
 */
public interface STTCallback {
    /**
     * 语音开始
     */
    void onSpeechStart();

    /**
     * 语音结束
     */
    void onSpeechEnd();

    /**
     * 识别到文本
     */
    void onTextRecognized(String text);

    /**
     * 发生错误
     */
    default void onError(String error) {
        // 默认实现
    }
}
