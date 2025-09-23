package com.nekkotavern.stt;

import javax.sound.sampled.*;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 音频录制器
 */
public class AudioRecorder {
    private static final Logger logger = LoggerFactory.getLogger(AudioRecorder.class);
    private static final int SAMPLE_RATE = 16000;
    private static final int SAMPLE_SIZE_IN_BITS = 16;
    private static final int CHANNELS = 1;
    private static final boolean SIGNED = true;
    private static final boolean BIG_ENDIAN = false;

    private TargetDataLine targetDataLine;
    private AudioFormat audioFormat;
    private AtomicBoolean isRecording = new AtomicBoolean(false);
    private ByteArrayOutputStream audioStream;

    public AudioRecorder() {
        this.audioFormat = new AudioFormat(
                SAMPLE_RATE,
                SAMPLE_SIZE_IN_BITS,
                CHANNELS,
                SIGNED,
                BIG_ENDIAN
        );
    }

    /**
     * 开始录音
     */
    public void start() throws LineUnavailableException {
        if (isRecording.get()) {
            return;
        }

        DataLine.Info info = new DataLine.Info(TargetDataLine.class, audioFormat);

        if (!AudioSystem.isLineSupported(info)) {
            throw new LineUnavailableException("不支持的音频格式");
        }

        targetDataLine = (TargetDataLine) AudioSystem.getLine(info);
        targetDataLine.open(audioFormat);
        targetDataLine.start();

        audioStream = new ByteArrayOutputStream();
        isRecording.set(true);

        logger.info("开始录音");
    }

    /**
     * 停止录音
     */
    public void stop() {
        if (!isRecording.get()) {
            return;
        }

        isRecording.set(false);

        if (targetDataLine != null) {
            targetDataLine.stop();
            targetDataLine.close();
            targetDataLine = null;
        }

        logger.info("停止录音");
    }

    /**
     * 读取音频数据
     */
    public byte[] readAudioData(int size) {
        if (!isRecording.get() || targetDataLine == null) {
            return new byte[0];
        }

        byte[] buffer = new byte[size];
        int bytesRead = targetDataLine.read(buffer, 0, buffer.length);

        if (bytesRead > 0 && audioStream != null) {
            audioStream.write(buffer, 0, bytesRead);
        }

        return buffer;
    }

    /**
     * 获取录制的音频数据
     */
    public byte[] getAudioData() {
        if (audioStream != null) {
            return audioStream.toByteArray();
        }
        return new byte[0];
    }

    /**
     * 清空音频缓冲
     */
    public void clearBuffer() {
        if (audioStream != null) {
            audioStream.reset();
        }
    }

    public boolean isRecording() {
        return isRecording.get();
    }
}