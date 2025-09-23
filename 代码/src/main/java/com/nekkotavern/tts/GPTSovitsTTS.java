package com.nekkotavern.tts;

import com.nekkotavern.model.Character;
import okhttp3.*;
import java.io.IOException;
import java.util.concurrent.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GPT-SoVITS 语音合成实现
 */
public class GPTSovitsTTS {
    private static final Logger logger = LoggerFactory.getLogger(GPTSovitsTTS.class);
    private static final String TTS_API_URL = "http://127.0.0.1:9880/tts";

    private final OkHttpClient httpClient;
    private final BlockingQueue<String> textQueue;
    private final AudioPlayer audioPlayer;
    private final ExecutorService executorService;
    private volatile boolean isRunning;
    private Character character;

    public GPTSovitsTTS(Character character) {
        this.character = character;
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
        this.textQueue = new LinkedBlockingQueue<>();
        this.audioPlayer = new AudioPlayer();
        this.executorService = Executors.newSingleThreadExecutor();
    }

    /**
     * 启动TTS服务
     */
    public void start() {
        if (!isRunning) {
            isRunning = true;
            executorService.submit(this::ttsProcessLoop);
            audioPlayer.start();
            logger.info("TTS服务已启动");
        }
    }

    /**
     * 停止TTS服务
     */
    public void stop() {
        if (isRunning) {
            isRunning = false;
            textQueue.clear();
            audioPlayer.stop();
            executorService.shutdown();
            logger.info("TTS服务已停止");
        }
    }

    /**
     * 添加文本到合成队列
     */
    public void addTextToQueue(String text) {
        if (text != null && !text.trim().isEmpty() && text.length() <= 1024) {
            try {
                textQueue.offer(text);
                logger.debug("已添加文本到TTS队列: {}", text);
            } catch (Exception e) {
                logger.error("添加文本到队列失败: {}", e.getMessage());
            }
        }
    }

    /**
     * 清空TTS队列
     */
    public void clearQueue() {
        textQueue.clear();
        audioPlayer.clearQueue();
        logger.info("TTS队列已清空");
    }

    /**
     * TTS处理循环
     */
    private void ttsProcessLoop() {
        while (isRunning) {
            try {
                String text = textQueue.poll(100, TimeUnit.MILLISECONDS);
                if (text != null) {
                    byte[] audioData = synthesizeAudio(text);
                    if (audioData != null && audioData.length > 0) {
                        audioPlayer.playAudio(audioData);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                logger.error("TTS处理错误: {}", e.getMessage());
            }
        }
    }

    /**
     * 调用GPT-SoVITS API合成语音
     */
    private byte[] synthesizeAudio(String text) {
        try {
            HttpUrl.Builder urlBuilder = HttpUrl.parse(TTS_API_URL).newBuilder()
                    .addQueryParameter("text", text)
                    .addQueryParameter("text_lang", "auto");

            // 添加角色相关参数（如果存在）
            if (character != null) {
                if (character.getRefAudioPath() != null) {
                    urlBuilder.addQueryParameter("ref_audio_path", character.getRefAudioPath());
                }
                if (character.getPromptLang() != null) {
                    urlBuilder.addQueryParameter("prompt_lang", character.getPromptLang());
                }
                if (character.getPromptText() != null && !character.getPromptText().isEmpty()) {
                    urlBuilder.addQueryParameter("prompt_text", character.getPromptText());
                }
                urlBuilder.addQueryParameter("speed_factor", String.valueOf(character.getSpeedFactor()));
            }

            urlBuilder.addQueryParameter("text_split_method", "cut5")
                    .addQueryParameter("media_type", "wav");

            Request request = new Request.Builder()
                    .url(urlBuilder.build())
                    .get()
                    .build();

            try (Response response = httpClient.newCall(request).execute()) {
                if (response.isSuccessful() && response.body() != null) {
                    byte[] audioData = response.body().bytes();
                    logger.debug("音频合成成功，大小: {} bytes", audioData.length);
                    return audioData;
                } else {
                    logger.error("TTS API返回错误: {}", response.code());
                }
            }
        } catch (IOException e) {
            logger.error("音频合成失败: {}", e.getMessage());
        }

        return null;
    }
}
