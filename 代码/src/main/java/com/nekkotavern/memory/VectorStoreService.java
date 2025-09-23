package com.nekkotavern.memory;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 向量存储服务 - 简化实现
 * 在生产环境中应该使用实际的向量数据库如Qdrant, Pinecone等
 */
public class VectorStoreService {
    private static final Logger logger = LoggerFactory.getLogger(VectorStoreService.class);
    private static final int CHUNK_SIZE = 1024;
    private static final int CHUNK_OVERLAP = 64;
    private static final int DEFAULT_K = 4;

    private final RecursiveCharacterTextSplitter textSplitter;
    private final Map<String, StoredDocument> documentStore;
    private final String storePath;

    public VectorStoreService(String storePath) {
        this.storePath = storePath;
        this.textSplitter = new RecursiveCharacterTextSplitter(CHUNK_SIZE, CHUNK_OVERLAP);
        this.documentStore = new ConcurrentHashMap<>();
        loadDocuments();
    }

    /**
     * 插入文本到向量存储
     */
    public void insertText(String text) {
        if (text == null || text.trim().isEmpty()) {
            return;
        }

        // 分割文本
        List<String> chunks = textSplitter.split(text);

        for (String chunk : chunks) {
            String docId = UUID.randomUUID().toString();
            StoredDocument doc = new StoredDocument(docId, chunk, System.currentTimeMillis());
            documentStore.put(docId, doc);
        }

        logger.info("已插入 {} 个文本块到向量存储", chunks.size());
        saveDocuments();
    }

    /**
     * 查询相关文档
     * 简化实现：使用文本相似度而不是真实的向量嵌入
     */
    public List<RelevantDocument> query(String query, int k) {
        if (query == null || query.trim().isEmpty()) {
            return new ArrayList<>();
        }

        String queryLower = query.toLowerCase();
        String[] queryWords = queryLower.split("\\s+");

        // 计算每个文档的相关性分数
        List<RelevantDocument> results = documentStore.values().stream()
                .map(doc -> {
                    double score = calculateSimilarity(queryWords, doc.getContent().toLowerCase());
                    return new RelevantDocument(doc.getContent(), score, doc.getId());
                })
                .filter(doc -> doc.getScore() > 0.1) // 过滤低相关性
                .sorted((a, b) -> Double.compare(b.getScore(), a.getScore())) // 按分数降序
                .limit(k)
                .collect(Collectors.toList());

        logger.debug("查询 '{}' 返回 {} 个相关文档", query, results.size());
        return results;
    }

    /**
     * 删除指定文档
     */
    public void deleteDocuments(List<String> documentIds) {
        if (documentIds == null || documentIds.isEmpty()) {
            return;
        }

        for (String id : documentIds) {
            documentStore.remove(id);
        }

        logger.info("已删除 {} 个文档", documentIds.size());
        saveDocuments();
    }

    /**
     * 获取所有文档
     */
    public List<StoredDocument> getAllDocuments() {
        return new ArrayList<>(documentStore.values());
    }

    /**
     * 清空所有文档
     */
    public void clearAll() {
        documentStore.clear();
        saveDocuments();
        logger.info("已清空所有文档");
    }

    /**
     * 简单的文本相似度计算
     */
    private double calculateSimilarity(String[] queryWords, String content) {
        if (queryWords.length == 0) {
            return 0.0;
        }

        int matches = 0;
        for (String word : queryWords) {
            if (content.contains(word)) {
                matches++;
            }
        }

        // 计算Jaccard相似度的简化版本
        return (double) matches / queryWords.length;
    }

    /**
     * 保存文档到磁盘
     */
    private void saveDocuments() {
        // TODO: 实现持久化存储
        // 可以使用JSON序列化保存到文件
    }

    /**
     * 从磁盘加载文档
     */
    private void loadDocuments() {
        // TODO: 实现从持久化存储加载
        // 可以从JSON文件读取
    }

    /**
     * 存储的文档
     */
    public static class StoredDocument {
        private final String id;
        private final String content;
        private final long timestamp;

        public StoredDocument(String id, String content, long timestamp) {
            this.id = id;
            this.content = content;
            this.timestamp = timestamp;
        }

        public String getId() { return id; }
        public String getContent() { return content; }
        public long getTimestamp() { return timestamp; }
    }
}