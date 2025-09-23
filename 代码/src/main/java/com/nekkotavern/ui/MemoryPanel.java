
// ===== MemoryPanel 实现 =====
package com.nekkotavern.ui;

import com.nekkotavern.memory.VectorStoreService;
import com.nekkotavern.memory.RelevantDocument;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import java.io.File;
import java.nio.file.Files;
import java.util.List;

/**
 * 记忆管理面板
 */
public class MemoryPanel extends VBox {
    private VectorStoreService memoryService;

    private TextArea contentArea;
    private TextField queryField;
    private ListView<String> resultsList;
    private Label statusLabel;

    private Button addMemoryButton;
    private Button searchButton;
    private Button clearButton;
    private Button importButton;

    public MemoryPanel(VectorStoreService memoryService) {
        this.memoryService = memoryService;
        initializeUI();
    }

    private void initializeUI() {
        setPadding(new Insets(15));
        setSpacing(10);

        // 标题
        Label titleLabel = new Label("记忆管理");
        titleLabel.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");

        // 添加记忆区域
        Label addLabel = new Label("添加新记忆:");
        contentArea = new TextArea();
        contentArea.setPrefRowCount(5);
        contentArea.setWrapText(true);
        contentArea.setPromptText("输入要添加到记忆库的内容...");

        HBox addButtonBox = new HBox(10);
        addMemoryButton = new Button("添加到记忆");
        importButton = new Button("从文件导入");
        addButtonBox.getChildren().addAll(addMemoryButton, importButton);

        // 分隔符
        Separator separator1 = new Separator();
        separator1.setPadding(new Insets(10, 0, 10, 0));

        // 查询区域
        Label queryLabel = new Label("查询记忆:");
        queryField = new TextField();
        queryField.setPromptText("输入查询关键词...");
        searchButton = new Button("搜索");

        HBox queryBox = new HBox(10);
        queryBox.getChildren().addAll(queryField, searchButton);
        HBox.setHgrow(queryField, Priority.ALWAYS);

        // 结果显示区域
        Label resultsLabel = new Label("查询结果:");
        resultsList = new ListView<>();
        resultsList.setPrefHeight(200);

        // 状态栏
        statusLabel = new Label("就绪");
        statusLabel.setStyle("-fx-text-fill: #666;");

        // 清空按钮
        clearButton = new Button("清空所有记忆");
        clearButton.setStyle("-fx-background-color: #ff4444; -fx-text-fill: white;");

        // 设置事件处理器
        setupEventHandlers();

        // 添加所有组件
        getChildren().addAll(
                titleLabel,
                addLabel,
                contentArea,
                addButtonBox,
                separator1,
                queryLabel,
                queryBox,
                resultsLabel,
                resultsList,
                new Separator(),
                statusLabel,
                clearButton
        );
    }

    private void setupEventHandlers() {
        // 添加记忆
        addMemoryButton.setOnAction(e -> {
            String content = contentArea.getText().trim();
            if (!content.isEmpty()) {
                memoryService.insertText(content);
                contentArea.clear();
                updateStatus("记忆已添加");
            }
        });

        // 从文件导入
        importButton.setOnAction(e -> importFromFile());

        // 搜索记忆
        searchButton.setOnAction(e -> searchMemory());
        queryField.setOnAction(e -> searchMemory());

        // 清空记忆
        clearButton.setOnAction(e -> {
            Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
            confirm.setTitle("确认");
            confirm.setHeaderText("清空所有记忆");
            confirm.setContentText("此操作将删除所有存储的记忆，是否继续？");

            confirm.showAndWait().ifPresent(response -> {
                if (response == ButtonType.OK) {
                    memoryService.clearAll();
                    resultsList.getItems().clear();
                    updateStatus("所有记忆已清空");
                }
            });
        });
    }

    private void searchMemory() {
        String query = queryField.getText().trim();
        if (query.isEmpty()) {
            return;
        }

        updateStatus("搜索中...");

        // 异步执行搜索
        Platform.runLater(() -> {
            List<RelevantDocument> results = memoryService.query(query, 5);

            resultsList.getItems().clear();
            if (results.isEmpty()) {
                resultsList.getItems().add("未找到相关记忆");
            } else {
                for (RelevantDocument doc : results) {
                    String item = String.format("[%.2f] %s",
                            doc.getScore(),
                            doc.getContent().length() > 100 ?
                                    doc.getContent().substring(0, 100) + "..." :
                                    doc.getContent()
                    );
                    resultsList.getItems().add(item);
                }
            }

            updateStatus("找到 " + results.size() + " 条相关记忆");
        });
    }

    private void importFromFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("选择要导入的文件");
        fileChooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("文本文件", "*.txt", "*.md"),
                new FileChooser.ExtensionFilter("所有文件", "*.*")
        );

        File selectedFile = fileChooser.showOpenDialog(getScene().getWindow());
        if (selectedFile != null) {
            try {
                String content = new String(Files.readAllBytes(selectedFile.toPath()));
                memoryService.insertText(content);
                updateStatus("文件已导入: " + selectedFile.getName());
            } catch (Exception ex) {
                showError("导入失败: " + ex.getMessage());
            }
        }
    }

    private void updateStatus(String message) {
        Platform.runLater(() -> statusLabel.setText(message));
    }

    private void showError(String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle("错误");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
}