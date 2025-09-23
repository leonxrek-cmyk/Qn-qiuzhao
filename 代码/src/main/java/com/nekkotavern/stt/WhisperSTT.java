package com.nekkotavern.stt;

import javax.sound.sampled.*;
import java.io.ByteArrayOutputStream;
import java.util.concurrent.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Whisper语音识别实现
 */
public class WhisperSTT implements SpeechRecognizer {
    private static final Logger logger = LoggerFactory.getLogger(WhisperSTT.class);
    private static final int SAMPLE_RATE = 16000;
    private static final int CHUNK_SIZE = SAMPLE_RATE / 2;  // 0.5秒音频数据
    private static final float ACTIVATION_THRESHOLD = 0.4f;  // 激活阈值
    private static final int SILENCE_THRESHOLD_MS = 1000;    // 静音阈值

    private AudioRecorder audioRecorder;
    private BlockingQueue<String> textQueue;
    private ExecutorService executorService;
    private volatile boolean isRecording;
    private String modelPath;
    private STTCallback callback;

    public WhisperSTT(String modelPath) {
        this.modelPath = modelPath;
        this.textQueue = new LinkedBlockingQueue<>();
        this.executorService = Executors.newCachedThreadPool();
        this.audioRecorder = new AudioRecorder();
    }

    /**
     * 设置识别回调
     */
    public void setRecognitionCallback(STTCallback callback) {
        this.callback = callback;
    }

    @Override
    public void startRecording() {
        if (!isRecording) {
            isRecording = true;
            try {
                audioRecorder.start();
                executorService.submit(this::recordingTask);
                executorService.submit(this::recognitionTask);
                logger.info("开始语音识别...");
            } catch (LineUnavailableException e) {
                logger.error("启动录音失败: {}", e.getMessage());
                isRecording = false;
            }
        }
    }

    @Override
    public void stopRecording() {
        if (isRecording) {
            isRecording = false;
            audioRecorder.stop();
            executorService.shutdown();
            logger.info("停止语音识别...");
        }
    }

    private void recordingTask() {
        try {
            AudioFormat format = new AudioFormat(SAMPLE_RATE, 16, 1, true, false);
            DataLine.Info info = new DataLine.Info(TargetDataLine.class, format);

            if (!AudioSystem.isLineSupported(info)) {
                logger.error("不支持的音频格式");
                return;
            }

            TargetDataLine line = (TargetDataLine) AudioSystem.getLine(info);
            line.open(format);
            line.start();

            byte[] buffer = new byte[CHUNK_SIZE];
            ByteArrayOutputStream speechBuffer = new ByteArrayOutputStream();
            boolean speechDetected = false;
            int silenceCount = 0;

            while (isRecording) {
                int bytesRead = line.read(buffer, 0, buffer.length);

                if (isSpeech(buffer)) {
                    if (!speechDetected) {
                        if (callback != null) {
                            callback.onSpeechStart();
                        }
                        speechDetected = true;
                    }
                    speechBuffer.write(buffer, 0, bytesRead);
                    silenceCount = 0;
                } else if (speechDetected) {
                    silenceCount++;
                    int silenceThreshold = SILENCE_THRESHOLD_MS / (CHUNK_SIZE * 1000 / SAMPLE_RATE);

                    if (silenceCount >= silenceThreshold) {
                        // 语音结束，提交识别
                        byte[] audioData = speechBuffer.toByteArray();
                        recognizeAudioAsync(audioData);
                        speechBuffer.reset();
                        speechDetected = false;
                        silenceCount = 0;

                        if (callback != null) {
                            callback.onSpeechEnd();
                        }
                    }
                }
            }

            line.stop();
            line.close();
        } catch (Exception e) {
            logger.error("录音任务异常: {}", e.getMessage());
            if (callback != null) {
                callback.onError(e.getMessage());
            }
        }
    }

    private void recognitionTask() {
        // 处理识别结果队列
        while (isRecording || !textQueue.isEmpty()) {
            try {
                String text = textQueue.poll(100, TimeUnit.MILLISECONDS);
                if (text != null && !text.isEmpty()) {
                    logger.info("识别结果: {}", text);
                    if (callback != null) {
                        callback.onTextRecognized(text);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    /**
     * VAD语音活动检测
     */
    private boolean isSpeech(byte[] audioData) {
        // 简单的能量检测算法
        double energy = 0;
        for (int i = 0; i < audioData.length - 1; i += 2) {
            short sample = (short) ((audioData[i + 1] << 8) | (audioData[i] & 0xFF));
            energy += sample * sample;
        }
        energy = Math.sqrt(energy / (audioData.length / 2));
        double normalizedEnergy = energy / Short.MAX_VALUE;

        return normalizedEnergy > ACTIVATION_THRESHOLD;
    }

    /**
     * 异步识别音频
     */
    private void recognizeAudioAsync(byte[] audioData) {
        CompletableFuture.supplyAsync(() -> recognizeWithWhisper(audioData))
                .thenAccept(text -> {
                    if (text != null && !text.isEmpty()) {
                        textQueue.offer(text);
                    }
                })
                .exceptionally(ex -> {
                    logger.error("识别异常: {}", ex.getMessage());
                    return null;
                });
    }

    @Override
    public CompletableFuture<String> recognizeAudio(byte[] audioData) {
        return CompletableFuture.supplyAsync(() -> recognizeWithWhisper(audioData));
    }

    /**
     * 调用Whisper进行识别
     * 注意：这里需要实际的Whisper JNI绑定或API调用
     * 示例中返回模拟结果
     */
    private String recognizeWithWhisper(byte[] audioData) {
        // TODO: 实际实现需要调用Whisper API或JNI
        // 这里是模拟实现
        logger.debug("调用Whisper识别，音频大小: {} bytes", audioData.length);

        // 模拟识别延迟
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 返回模拟结果
        return "识别的文本内容";
    }
}