
// ===== AudioPlayer 实现 =====
package com.nekkotavern.tts;

import javax.sound.sampled.*;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 音频播放器
 */
public class AudioPlayer {
    private static final Logger logger = LoggerFactory.getLogger(AudioPlayer.class);

    private BlockingQueue<byte[]> audioQueue;
    private ExecutorService executorService;
    private volatile boolean isRunning = false;
    private SourceDataLine sourceDataLine;

    public AudioPlayer() {
        this.audioQueue = new LinkedBlockingQueue<>();
        this.executorService = Executors.newSingleThreadExecutor();
    }

    /**
     * 启动播放器
     */
    public void start() {
        if (!isRunning) {
            isRunning = true;
            executorService.submit(this::playbackLoop);
            logger.info("音频播放器启动");
        }
    }

    /**
     * 停止播放器
     */
    public void stop() {
        if (isRunning) {
            isRunning = false;
            audioQueue.clear();

            if (sourceDataLine != null && sourceDataLine.isOpen()) {
                sourceDataLine.stop();
                sourceDataLine.close();
            }

            logger.info("音频播放器停止");
        }
    }

    /**
     * 添加音频到播放队列
     */
    public void playAudio(byte[] audioData) {
        if (audioData != null && audioData.length > 0) {
            try {
                audioQueue.offer(audioData);
            } catch (Exception e) {
                logger.error("添加音频到队列失败: {}", e.getMessage());
            }
        }
    }

    /**
     * 清空播放队列
     */
    public void clearQueue() {
        audioQueue.clear();
        logger.info("播放队列已清空");
    }

    /**
     * 播放循环
     */
    private void playbackLoop() {
        while (isRunning) {
            try {
                byte[] audioData = audioQueue.poll(100, java.util.concurrent.TimeUnit.MILLISECONDS);
                if (audioData != null) {
                    playAudioData(audioData);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    /**
     * 播放音频数据
     */
    private void playAudioData(byte[] audioData) {
        try (ByteArrayInputStream bais = new ByteArrayInputStream(audioData);
             AudioInputStream ais = AudioSystem.getAudioInputStream(bais)) {

            AudioFormat format = ais.getFormat();
            DataLine.Info info = new DataLine.Info(SourceDataLine.class, format);

            if (!AudioSystem.isLineSupported(info)) {
                logger.error("不支持的音频格式");
                return;
            }

            sourceDataLine = (SourceDataLine) AudioSystem.getLine(info);
            sourceDataLine.open(format);
            sourceDataLine.start();

            byte[] buffer = new byte[4096];
            int bytesRead;

            while ((bytesRead = ais.read(buffer)) != -1) {
                sourceDataLine.write(buffer, 0, bytesRead);
            }

            sourceDataLine.drain();
            sourceDataLine.stop();
            sourceDataLine.close();

        } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e) {
            logger.error("播放音频失败: {}", e.getMessage());
        }
    }

    public boolean isRunning() {
        return isRunning;
    }
}