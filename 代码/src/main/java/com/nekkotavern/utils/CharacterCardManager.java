// ========== 角色卡管理器 ==========
package com.nekkotavern.utils;

import com.google.gson.*;
import javax.imageio.ImageIO;
import javax.imageio.metadata.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/**
 * 角色卡管理器 - 处理角色卡的导入导出
 */
public class CharacterCardManager {
    private static final Gson gson = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    /**
     * 从文件加载角色
     */
    public static Character loadCharacter(String filePath) {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new RuntimeException("角色文件不存在: " + filePath);
        }

        try {
            if (filePath.toLowerCase().endsWith(".png")) {
                return loadFromPNG(file);
            } else if (filePath.toLowerCase().endsWith(".json")) {
                return loadFromJSON(file);
            } else {
                throw new IllegalArgumentException("不支持的文件格式");
            }
        } catch (Exception e) {
            System.err.println("加载角色失败: " + e.getMessage());
            return null;
        }
    }

    /**
     * 从PNG文件加载角色（包含元数据）
     */
    private static Character loadFromPNG(File file) throws IOException {
        BufferedImage image = ImageIO.read(file);

        // 读取PNG元数据
        IIOMetadata metadata = ImageIO.getImageReaders(ImageIO.createImageInputStream(file))
                .next().getImageMetadata(0);

        String[] names = metadata.getMetadataFormatNames();
        for (String name : names) {
            IIOMetadataNode root = (IIOMetadataNode) metadata.getAsTree(name);

            // 查找包含角色数据的文本节点
            NodeList textNodes = root.getElementsByTagName("tEXt");
            for (int i = 0; i < textNodes.getLength(); i++) {
                IIOMetadataNode textNode = (IIOMetadataNode) textNodes.item(i);
                String keyword = textNode.getAttribute("keyword");

                if ("chara".equals(keyword)) {
                    String value = textNode.getAttribute("value");
                    // Base64解码
                    byte[] decodedBytes = Base64.getDecoder().decode(value);
                    String json = new String(decodedBytes, StandardCharsets.UTF_8);
                    return gson.fromJson(json, Character.class);
                }
            }
        }

        throw new IOException("PNG文件中未找到角色数据");
    }

    /**
     * 从JSON文件加载角色
     */
    private static Character loadFromJSON(File file) throws IOException {
        try (Reader reader = new FileReader(file)) {
            return gson.fromJson(reader, Character.class);
        }
    }

    /**
     * 保存角色到文件
     */
    public static void saveCharacter(Character character, String filePath) {
        try {
            if (filePath.toLowerCase().endsWith(".png")) {
                saveToPNG(character, filePath);
            } else if (filePath.toLowerCase().endsWith(".json")) {
                saveToJSON(character, filePath);
            } else {
                throw new IllegalArgumentException("不支持的文件格式");
            }
            System.out.println("角色保存成功: " + filePath);
        } catch (Exception e) {
            System.err.println("保存角色失败: " + e.getMessage());
        }
    }

    /**
     * 保存角色到JSON文件
     */
    private static void saveToJSON(Character character, String filePath) throws IOException {
        try (Writer writer = new FileWriter(filePath)) {
            gson.toJson(character, writer);
        }
    }

    /**
     * 保存角色到PNG文件（嵌入元数据）
     */
    private static void saveToPNG(Character character, String filePath) throws IOException {
        // 读取现有的PNG图片或创建新的
        File file = new File(filePath);
        BufferedImage image;
        if (file.exists()) {
            image = ImageIO.read(file);
        } else {
            // 创建默认图片
            image = new BufferedImage(256, 256, BufferedImage.TYPE_INT_ARGB);
        }

        // 将角色数据转换为JSON并Base64编码
        String json = gson.toJson(character);
        String base64 = Base64.getEncoder().encodeToString(
                json.getBytes(StandardCharsets.UTF_8)
        );

        // 创建PNG元数据
        IIOMetadata metadata = ImageIO.getImageWritersByFormatName("png")
                .next().getDefaultImageMetadata(null, null);

        // 添加文本元数据
        IIOMetadataNode textEntry = new IIOMetadataNode("tEXtEntry");
        textEntry.setAttribute("keyword", "chara");
        textEntry.setAttribute("value", base64);

        IIOMetadataNode text = new IIOMetadataNode("tEXt");
        text.appendChild(textEntry);

        IIOMetadataNode root = new IIOMetadataNode("javax_imageio_1.0");
        root.appendChild(text);

        metadata.mergeTree("javax_imageio_1.0", root);

        // 写入PNG文件
        ImageIO.write(image, "png", file);
    }
}