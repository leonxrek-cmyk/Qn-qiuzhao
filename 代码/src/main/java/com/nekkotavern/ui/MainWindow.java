// ========== UI主窗口 ==========
package com.nekkotavern.ui;

import com.nekkotavern.chat.ChatService;
import com.nekkotavern.memory.VectorStoreService;
import com.nekkotavern.model.Configuration;
import com.nekkotavern.stt.WhisperSTT;
import com.nekkotavern.tts.GPTSovitsTTS;
import com.nekkotavern.utils.CharacterCardManager;
import com.nekkotavern.utils.ConfigManager;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import java.util.concurrent.CompletableFuture;

/**
 * 主窗口 - 包含聊天、角色设置和记忆管理三个标签页
 */
public class MainWindow {
    private Stage primaryStage;
    private TabPane tabPane;
    private ChatPanel chatPanel;
    private CharacterPanel characterPanel;
    private MemoryPanel memoryPanel;

    // 服务实例
    private ChatService chatService;
    private WhisperSTT sttService;
    private GPTSovitsTTS ttsService;
    private VectorStoreService memoryService;

    public MainWindow() {
        initialize();
    }

    /**
     * 初始化窗口和服务
     */
    private void initialize() {
        // 初始化服务
        Configuration config = ConfigManager.getInstance().getConfig();
        String modelPath = config.getSttModelPath();
        sttService = new WhisperSTT(modelPath);

        // 加载默认角色
        Character character = CharacterCardManager.loadCharacter(config.getCharacterPath());
        ttsService = new GPTSovitsTTS(character);
        chatService = new ChatService(character.getName());
        memoryService = new VectorStoreService(character.getMemoryPath());

        // 创建UI面板
        chatPanel = new ChatPanel(chatService, sttService, ttsService, memoryService);
        characterPanel = new CharacterPanel(character);
        memoryPanel = new MemoryPanel(memoryService);

        // 创建标签页
        tabPane = new TabPane();

        Tab chatTab = new Tab("聊天", chatPanel);
        chatTab.setClosable(false);

        Tab characterTab = new Tab("角色", characterPanel);
        characterTab.setClosable(false);

        Tab memoryTab = new Tab("记忆", memoryPanel);
        memoryTab.setClosable(false);

        tabPane.getTabs().addAll(chatTab, characterTab, memoryTab);
    }

    /**
     * 显示窗口
     */
    public void show(Stage stage) {
        this.primaryStage = stage;

        Scene scene = new Scene(tabPane, 800, 600);
        scene.getStylesheets().add(getClass().getResource("/styles/main.css").toExternalForm());

        primaryStage.setTitle("NekkoTavern - AI角色聊天");
        primaryStage.setScene(scene);
        primaryStage.show();

        // 启动服务
        ttsService.start();

        // 窗口关闭时清理资源
        primaryStage.setOnCloseRequest(event -> {
            cleanup();
        });
    }

    /**
     * 清理资源
     */
    private void cleanup() {
        if (sttService != null) sttService.stopRecording();
        if (ttsService != null) ttsService.stop();
        // 保存配置等
        ConfigManager.getInstance().saveConfig();
    }
}