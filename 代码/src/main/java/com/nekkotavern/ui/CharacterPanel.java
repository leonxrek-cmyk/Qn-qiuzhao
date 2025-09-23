package com.nekkotavern.ui;

import com.nekkotavern.model.Character;
import com.nekkotavern.utils.CharacterCardManager;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import java.io.File;

/**
 * 角色设置面板
 */
public class CharacterPanel extends VBox {
    private Character character;

    private TextField nameField;
    private TextArea descriptionArea;
    private TextField audioPathField;
    private ComboBox<String> languageCombo;
    private Slider speedSlider;
    private TextField modelField;

    private Button loadButton;
    private Button saveButton;
    private Button browseAudioButton;

    public CharacterPanel(Character character) {
        this.character = character;
        initializeUI();
        loadCharacterData();
    }

    private void initializeUI() {
        setPadding(new Insets(15));
        setSpacing(10);

        // 角色名称
        Label nameLabel = new Label("角色名称:");
        nameField = new TextField();
        nameField.setPromptText("输入角色名称");

        // 角色描述
        Label descLabel = new Label("角色描述:");
        descriptionArea = new TextArea();
        descriptionArea.setPrefRowCount(4);
        descriptionArea.setWrapText(true);
        descriptionArea.setPromptText("输入角色描述...");

        // 参考音频
        Label audioLabel = new Label("参考音频:");
        audioPathField = new TextField();
        audioPathField.setPromptText("选择参考音频文件");
        audioPathField.setEditable(false);
        browseAudioButton = new Button("浏览...");
        browseAudioButton.setOnAction(e -> browseAudioFile());

        HBox audioBox = new HBox(5);
        audioBox.getChildren().addAll(audioPathField, browseAudioButton);
        HBox.setHgrow(audioPathField, Priority.ALWAYS);

        // 语言选择
        Label langLabel = new Label("语言:");
        languageCombo = new ComboBox<>();
        languageCombo.getItems().addAll("zh", "en", "ja", "auto");
        languageCombo.setValue("zh");

        // 语速调节
        Label speedLabel = new Label("语速:");
        speedSlider = new Slider(0.5, 2.0, 1.0);
        speedSlider.setShowTickLabels(true);
        speedSlider.setShowTickMarks(true);
        speedSlider.setMajorTickUnit(0.5);
        speedSlider.setBlockIncrement(0.1);

        Label speedValue = new Label("1.0");
        speedSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            speedValue.setText(String.format("%.1f", newVal.doubleValue()));
        });

        HBox speedBox = new HBox(10);
        speedBox.getChildren().addAll(speedSlider, speedValue);
        HBox.setHgrow(speedSlider, Priority.ALWAYS);

        // 基础模型
        Label modelLabel = new Label("基础模型:");
        modelField = new TextField();
        modelField.setPromptText("例如: llama2, qwen2");

        // 按钮栏
        HBox buttonBox = new HBox(10);
        loadButton = new Button("加载角色");
        saveButton = new Button("保存角色");

        loadButton.setOnAction(e -> loadCharacter());
        saveButton.setOnAction(e -> saveCharacter());

        buttonBox.getChildren().addAll(loadButton, saveButton);

        // 添加分隔符
        Separator separator = new Separator();
        separator.setPadding(new Insets(10, 0, 10, 0));

        // 添加所有组件
        getChildren().addAll(
                nameLabel, nameField,
                descLabel, descriptionArea,
                audioLabel, audioBox,
                langLabel, languageCombo,
                speedLabel, speedBox,
                modelLabel, modelField,
                separator,
                buttonBox
        );
    }

    private void loadCharacterData() {
        if (character != null) {
            nameField.setText(character.getName());
            descriptionArea.setText(character.getDescription());
            audioPathField.setText(character.getRefAudioPath());
            languageCombo.setValue(character.getPromptLang());
            speedSlider.setValue(character.getSpeedFactor());
            modelField.setText(character.getBaseModel());
        }
    }

    private void browseAudioFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("选择参考音频文件");
        fileChooser.getExtensionFilters().addAll(
                new FileChooser.ExtensionFilter("音频文件", "*.wav", "*.mp3", "*.m4a"),
                new FileChooser.ExtensionFilter("所有文件", "*.*")
        );

        File selectedFile = fileChooser.showOpenDialog(getScene().getWindow());
        if (selectedFile != null) {
            audioPathField.setText(selectedFile.getAbsolutePath());
        }
    }

    private void loadCharacter() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("加载角色配置");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("JSON文件", "*.json")
        );

        File selectedFile = fileChooser.showOpenDialog(getScene().getWindow());
        if (selectedFile != null) {
            character = CharacterCardManager.loadCharacter(selectedFile.getAbsolutePath());
            loadCharacterData();
            showInfo("角色加载成功");
        }
    }

    private void saveCharacter() {
        // 更新角色数据
        character.setName(nameField.getText());
        character.setDescription(descriptionArea.getText());
        character.setRefAudioPath(audioPathField.getText());
        character.setPromptLang(languageCombo.getValue());
        character.setSpeedFactor((float) speedSlider.getValue());
        character.setBaseModel(modelField.getText());

        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("保存角色配置");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("JSON文件", "*.json")
        );
        fileChooser.setInitialFileName(character.getName() + ".json");

        File selectedFile = fileChooser.showSaveDialog(getScene().getWindow());
        if (selectedFile != null) {
            CharacterCardManager.saveCharacter(character, selectedFile.getAbsolutePath());
            showInfo("角色保存成功");
        }
    }

    private void showInfo(String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("信息");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    public Character getCharacter() {
        return character;
    }
}
