package com.nekkotavern.stt;

import javax.sound.sampled.*;
import java.io.ByteArrayOutputStream;
import java.util.concurrent.*;

/**
 * 语音识别器接口
 */
public interface SpeechRecognizer {
    void startRecording();
    void stopRecording();
    CompletableFuture<String> recognizeAudio(byte[] audioData);
}