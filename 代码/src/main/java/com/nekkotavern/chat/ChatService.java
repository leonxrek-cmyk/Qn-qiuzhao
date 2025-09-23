// ========== 聊天服务 ==========
package com.nekkotavern.chat;

import com.google.gson.*;
import okhttp3.*;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/**
 * 聊天服务 - 处理与Ollama模型的交互
 */
public class ChatService {
    private static final String OLLAMA_API_URL = "http://localhost:11434/api";

    private final OkHttpClient httpClient;
    private final PromptBuilder promptBuilder;
    private final List<Message> conversationHistory;
    private String currentModel;

    public ChatService(String modelName) {
        this.httpClient = new OkHttpClient();
        this.promptBuilder = new PromptBuilder();
        this.conversationHistory = new ArrayList<>();
        this.currentModel = modelName;
    }

    /**
     * 发送消息并流式接收响应
     */
    public void streamChat(String userMessage, MessageCallback callback) {
        // 构建提示词
        String prompt = promptBuilder.buildPrompt(userMessage, conversationHistory);

        // 保存用户消息到历史
        conversationHistory.add(new Message("user", userMessage));

        // 构建请求体
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("model", currentModel);
        requestBody.addProperty("prompt", prompt);
        requestBody.addProperty("stream", true);

        Request request = new Request.Builder()
                .url(OLLAMA_API_URL + "/generate")
                .post(RequestBody.create(requestBody.toString(),
                        MediaType.parse("application/json")))
                .build();

        httpClient.newCall(request).enqueue(new Callback() {
            private StringBuilder responseBuilder = new StringBuilder();

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    callback.onError("请求失败: " + response.code());
                    return;
                }

                try (ResponseBody body = response.body()) {
                    String line;
                    while ((line = body.source().readUtf8Line()) != null) {
                        JsonObject chunk = JsonParser.parseString(line).getAsJsonObject();

                        if (chunk.has("response")) {
                            String text = chunk.get("response").getAsString();
                            responseBuilder.append(text);
                            callback.onChunk(text);

                            // 检查是否完成
                            if (chunk.has("done") && chunk.get("done").getAsBoolean()) {
                                conversationHistory.add(
                                        new Message("assistant", responseBuilder.toString())
                                );
                                callback.onComplete(responseBuilder.toString());
                                break;
                            }
                        }
                    }
                }
            }

            @Override
            public void onFailure(Call call, IOException e) {
                callback.onError("网络错误: " + e.getMessage());
            }
        });
    }

    /**
     * 生成摘要
     */
    public CompletableFuture<String> generateSummary(String content) {
        String prompt = promptBuilder.buildSummaryPrompt(content);
        return sendRequest(prompt);
    }

    /**
     * 带记忆的上下文对话
     */
    public CompletableFuture<String> contextualChat(String userInput,
                                                    List<Document> relevantDocs) {
        String prompt = promptBuilder.buildContextualPrompt(
                userInput, conversationHistory, relevantDocs
        );
        return sendRequest(prompt);
    }

    private CompletableFuture<String> sendRequest(String prompt) {
        // 实现同步请求逻辑
        return CompletableFuture.supplyAsync(() -> {
            // 发送请求并返回结果
            return "响应内容";
        });
    }

    /**
     * 消息回调接口
     */
    public interface MessageCallback {
        void onChunk(String text);      // 收到文本片段
        void onComplete(String fullText); // 完成接收
        void onError(String error);      // 错误处理
    }
}

