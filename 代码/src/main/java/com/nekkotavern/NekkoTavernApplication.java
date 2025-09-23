package com.nekkotavern;

import com.nekkotavern.ui.MainWindow;
import com.nekkotavern.utils.ConfigManager;
import javafx.application.Application;
import javafx.stage.Stage;

public class NekkoTavernApplication extends Application {

    @Override
    public void start(Stage primaryStage) {
        try {
            // 加载配置文件
            ConfigManager.getInstance().loadConfig("config.json");

            // 初始化主窗口
            MainWindow mainWindow = new MainWindow();
            mainWindow.show(primaryStage);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
