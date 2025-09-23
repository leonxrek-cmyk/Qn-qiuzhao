package com.nekkotavern.ui;

import com.nekkotavern.chat.ChatService;
import com.nekkotavern.memory.VectorStoreService;
import com.nekkotavern.memory.RelevantDocument;
import com.nekkotavern.stt.WhisperSTT;
import com.nekkotavern.stt.STTCallback;
import com.nekkotavern.tts.GPTSovitsTTS;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.input.KeyCode;
import javafx.scene.layout.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * 聊天面板 - 处理聊天界面和交互
 */
public class ChatPanel extends VBox {
    private TextArea historyArea;        // 历史消息显示区
    private TextField inputField;        // 输入框
    private Button sendButton;          // 发送按钮
    private ToggleButton recordButton;   // 录音开关
    private ToggleButton dialingButton;  // 自动发送开关
    private ToggleButton memoryButton;   // 记忆查询开关

    private ChatService chatService;
    private WhisperSTT sttService;
    private GPTSovitsTTS ttsService;
    private VectorStoreService memoryService;

    private boolean isRecording = false;
    private boolean autoSend = false;
    private boolean useMemory = false;

    public ChatPanel(ChatService chatService, WhisperSTT sttService,
                     GPTSovitsTTS ttsService, VectorStoreService memoryService) {
        this.chatService = chatService;
        this.sttService = sttService;
        this.ttsService = ttsService;
        this.memoryService = memoryService;

        initializeUI();
        setupEventHandlers();
    }

    /**
     * 初始化UI组件
     */
    private void initializeUI() {
        setPadding(new Insets(10));
        setSpacing(10);

        // 历史消息区域
        historyArea = new TextArea();
        historyArea.setEditable(false);
        historyArea.setWrapText(true);
        historyArea.setPrefRowCount(20);
        historyArea.setStyle("-fx-font-family: 'Consolas', 'Monaco', monospace; -fx-font-size: 14px;");
        VBox.setVgrow(historyArea, Priority.ALWAYS);

        // 添加欢迎消息
        appendToHistory("系统", "欢迎使用NekkoTavern AI聊天系统！");

        // 输入区域
        inputField = new TextField();
        inputField.setPromptText("输入消息或按录音按钮说话...");
        inputField.setStyle("-fx-font-size: 14px;");
        HBox.setHgrow(inputField, Priority.ALWAYS);

        // 按钮栏
        HBox buttonBar = new HBox(10);

        memoryButton = new ToggleButton("记忆");
        memoryButton.setPrefWidth(60);
        memoryButton.setTooltip(new Tooltip("启用记忆查询"));

        recordButton = new ToggleButton("录音");
        recordButton.setPrefWidth(60);
        recordButton.setStyle("-fx-base: #4CAF50;");
        recordButton.setTooltip(new Tooltip("开始/停止录音"));

        dialingButton = new ToggleButton("自动");
        dialingButton.setPrefWidth(60);
        dialingButton.setTooltip(new Tooltip("自动发送识别结果"));

        sendButton = new Button("发送");
        sendButton.setPrefWidth(80);
        sendButton.setDefaultButton(true);
        sendButton.setStyle("-fx-base: #2196F3;");

        buttonBar.getChildren().addAll(memoryButton, recordButton, dialingButton, sendButton);

        // 输入栏
        HBox inputBar = new HBox(10);
        inputBar.getChildren().addAll(inputField, buttonBar);

        // 状态栏
        Label statusLabel = new Label("就绪");
        statusLabel.setStyle("-fx-text-fill: #666;");

        getChildren().addAll(historyArea, inputBar, statusLabel);
    }

    /**
     * 设置事件处理器
     */
    private void setupEventHandlers() {
        // 发送按钮点击事件
        sendButton.setOnAction(e -> sendMessage());

        // 回车键发送
        inputField.setOnKeyPressed(e -> {
            if (e.getCode() == KeyCode.ENTER) {
                sendMessage();
            }
        });

        // 录音开关
        recordButton.setOnAction(e -> toggleRecording());

        // 自动发送开关
        dialingButton.setOnAction(e -> toggleAutoSend());

        // 记忆查询开关
        memoryButton.setOnAction(e -> toggleMemory());

        // 设置STT回调
        setupSTTCallback();
    }

    /**
     * 发送消息
     */
    private void sendMessage() {
        String message = inputField.getText().trim();
        if (message.isEmpty()) return;

        // 清空输入框
        inputField.clear();
        inputField.setDisable(true);
        sendButton.setDisable(true);

        // 添加用户消息到历史
        appendToHistory("你", message);

        // 准备提示词
        String finalPrompt = message;

        // 如果启用记忆查询
        if (useMemory) {
            List<RelevantDocument> relevantDocs = memoryService.query(message, 4);
            if (!relevantDocs.isEmpty()) {
                StringBuilder context = new StringBuilder();
                context.append("【相关上下文】\n");
                for (RelevantDocument doc : relevantDocs) {
                    context.append("- ").append(doc.getContent()).append("\n");
                }
                context.append("\n");

                // 使用带上下文的提示词
                finalPrompt = buildContextualPrompt(message, context.toString());
            }
        }

        // 添加AI回复占位
        appendToHistory("AI", "");

        // 发送到聊天服务
        chatService.streamChat(finalPrompt, new ChatService.MessageCallback() {
            private StringBuilder responseBuilder = new StringBuilder();
            private StringBuilder sentenceBuffer = new StringBuilder();

            @Override
            public void onChunk(String text) {
                responseBuilder.append(text);
                sentenceBuffer.append(text);

                // 实时显示
                Platform.runLater(() -> {
                    historyArea.appendText(text);
                });

                // 检测句子结束并发送到TTS
                if (text.matches(".*[。！？.!?\\n].*")) {
                    String sentence = sentenceBuffer.toString().trim();
                    if (!sentence.isEmpty()) {
                        ttsService.addTextToQueue(sentence);
                    }
                    sentenceBuffer.setLength(0);
                }
            }

            @Override
            public void onComplete(String fullText) {
                // 处理剩余文本
                if (sentenceBuffer.length() > 0) {
                    String remaining = sentenceBuffer.toString().trim();
                    if (!remaining.isEmpty()) {
                        ttsService.addTextToQueue(remaining);
                    }
                }

                Platform.runLater(() -> {
                    historyArea.appendText("\n");
                    inputField.setDisable(false);
                    sendButton.setDisable(false);
                    inputField.requestFocus();
                });

                // 将完整回复存入记忆（如果启用）
                if (useMemory && fullText.length() > 50) {
                    memoryService.insertText(fullText);
                }
            }

            @Override
            public void onError(String error) {
                Platform.runLater(() -> {
                    showError("发送消息失败: " + error);
                    inputField.setDisable(false);
                    sendButton.setDisable(false);
                });
            }
        });
    }

    /**
     * 构建带上下文的提示词
     */
    private String buildContextualPrompt(String message, String context) {
        StringBuilder prompt = new StringBuilder();

        if (context != null && !context.isEmpty()) {
            prompt.append("基于以下上下文信息回答问题：\n\n");
            prompt.append(context);
            prompt.append("\n用户问题：");
        }

        prompt.append(message);

        return prompt.toString();
    }

    /**
     * 切换录音状态
     */
    private void toggleRecording() {
        isRecording = !isRecording;

        if (isRecording) {
            sttService.startRecording();
            recordButton.setText("停止");
            recordButton.setStyle("-fx-base: #f44336;");
        } else {
            sttService.stopRecording();
            recordButton.setText("录音");
            recordButton.setStyle("-fx-base: #4CAF50;");
        }
    }

    /**
     * 切换自动发送
     */
    private void toggleAutoSend() {
        autoSend = !autoSend;

        if (autoSend) {
            dialingButton.setText("手动");
            dialingButton.setStyle("-fx-base: #FF9800;");
            if (!isRecording) {
                toggleRecording();
            }
        } else {
            dialingButton.setText("自动");
            dialingButton.setStyle("");
        }
    }

    /**
     * 切换记忆查询
     */
    private void toggleMemory() {
        useMemory = !useMemory;
        memoryButton.setSelected(useMemory);

        if (useMemory) {
            memoryButton.setStyle("-fx-base: #9C27B0;");
        } else {
            memoryButton.setStyle("");
        }
    }

    /**
     * 设置STT回调处理
     */
    private void setupSTTCallback() {
        // 监听STT识别结果
        sttService.setRecognitionCallback(new STTCallback() {
            @Override
            public void onSpeechStart() {
                if (autoSend) {
                    // 清空TTS队列，停止AI说话
                    ttsService.clearQueue();
                }

                Platform.runLater(() -> {
                    recordButton.setText("听取中...");
                });
            }

            @Override
            public void onSpeechEnd() {
                Platform.runLater(() -> {
                    recordButton.setText("处理中...");

                    if (autoSend) {
                        // 自动发送消息
                        sendMessage();
                    }
                });
            }

            @Override
            public void onTextRecognized(String text) {
                Platform.runLater(() -> {
                    inputField.setText(inputField.getText() + text + " ");
                });
            }

            @Override
            public void onError(String error) {
                Platform.runLater(() -> {
                    showError("语音识别错误: " + error);
                });
            }
        });
    }

    /**
     * 添加消息到历史记录
     */
    private void appendToHistory(String sender, String message) {
        String timestamp = LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("HH:mm:ss")
        );

        String formattedMessage;
        if (message.isEmpty()) {
            // 占位消息，不添加换行
            formattedMessage = String.format("[%s] %s: ",
                    timestamp, sender);
        } else {
            formattedMessage = String.format("[%s] %s: %s\n\n",
                    timestamp, sender, message);
        }

        Platform.runLater(() -> {
            historyArea.appendText(formattedMessage);
            // 自动滚动到底部
            historyArea.setScrollTop(Double.MAX_VALUE);
        });
    }

    /**
     * 显示错误对话框
     */
    private void showError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("错误");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    /**
     * 清空聊天历史
     */
    public void clearHistory() {
        historyArea.clear();
        appendToHistory("系统", "聊天历史已清空");
    }
}