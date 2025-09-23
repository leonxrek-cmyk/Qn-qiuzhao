// ========== 文本分割器 ==========
package com.nekkotavern.memory;

import java.util.*;
import java.util.regex.*;

/**
 * 递归字符文本分割器
 * 将长文本分割成指定大小的块，支持重叠
 */
public class RecursiveCharacterTextSplitter {
    private final int chunkSize;      // 块大小
    private final int chunkOverlap;   // 块之间的重叠
    private final List<String> separators; // 分隔符列表

    public RecursiveCharacterTextSplitter(int chunkSize, int chunkOverlap) {
        this.chunkSize = chunkSize;
        this.chunkOverlap = chunkOverlap;

        // 默认分隔符（中文、日文、英文）
        this.separators = Arrays.asList(
                "\n\n", "\n", "。", "！", "？", ".",
                "!", "?", "；", ";", "，", ","
        );
    }

    /**
     * 分割文本
     */
    public List<String> split(String text) {
        List<String> chunks = new ArrayList<>();

        // 首先尝试按段落分割
        String[] paragraphs = text.split("\n\n");

        for (String paragraph : paragraphs) {
            if (paragraph.length() <= chunkSize) {
                // 段落小于块大小，直接添加
                chunks.add(paragraph);
            } else {
                // 段落过大，需要进一步分割
                chunks.addAll(splitLargeParagraph(paragraph));
            }
        }

        // 合并过短的块
        return mergeSmallChunks(chunks);
    }

    /**
     * 分割大段落
     */
    private List<String> splitLargeParagraph(String paragraph) {
        List<String> chunks = new ArrayList<>();

        // 按句子分隔符分割
        for (String separator : separators) {
            if (paragraph.contains(separator)) {
                String[] sentences = paragraph.split(Pattern.quote(separator));

                StringBuilder currentChunk = new StringBuilder();
                for (String sentence : sentences) {
                    if (currentChunk.length() + sentence.length() + separator.length() <= chunkSize) {
                        currentChunk.append(sentence).append(separator);
                    } else {
                        if (currentChunk.length() > 0) {
                            chunks.add(currentChunk.toString());

                            // 添加重叠部分到下一个块
                            if (chunkOverlap > 0 && currentChunk.length() > chunkOverlap) {
                                String overlap = currentChunk.substring(
                                        currentChunk.length() - chunkOverlap
                                );
                                currentChunk = new StringBuilder(overlap);
                            } else {
                                currentChunk = new StringBuilder();
                            }
                        }
                        currentChunk.append(sentence).append(separator);
                    }
                }

                if (currentChunk.length() > 0) {
                    chunks.add(currentChunk.toString());
                }

                return chunks;
            }
        }

        // 如果没有找到分隔符，按固定长度分割
        return splitByLength(paragraph);
    }

    /**
     * 按固定长度分割
     */
    private List<String> splitByLength(String text) {
        List<String> chunks = new ArrayList<>();

        for (int i = 0; i < text.length(); i += chunkSize - chunkOverlap) {
            int end = Math.min(i + chunkSize, text.length());
            chunks.add(text.substring(i, end));
        }

        return chunks;
    }

    /**
     * 合并过短的块
     */
    private List<String> mergeSmallChunks(List<String> chunks) {
        List<String> merged = new ArrayList<>();
        StringBuilder buffer = new StringBuilder();

        for (String chunk : chunks) {
            if (buffer.length() + chunk.length() <= chunkSize) {
                buffer.append(chunk).append("\n");
            } else {
                if (buffer.length() > 0) {
                    merged.add(buffer.toString());
                }
                buffer = new StringBuilder(chunk);
            }
        }

        if (buffer.length() > 0) {
            merged.add(buffer.toString());
        }

        return merged;
    }
}