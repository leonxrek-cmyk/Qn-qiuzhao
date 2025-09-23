
// ========== 文件工具类 ==========
package com.nekkotavern.utils;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

/**
 * 文件工具类 - 提供文件操作的辅助方法
 */
public class FileUtils {

    /**
     * 获取绝对路径
     */
    public static String getAbsolutePath(String path, String baseDir) {
        Path p = Paths.get(path);
        if (!p.isAbsolute()) {
            p = Paths.get(baseDir, path);
        }
        return p.normalize().toString().replace("\\", "/");
    }

    /**
     * 获取相对路径
     */
    public static String getRelativePath(String path, String baseDir) {
        if (baseDir == null) {
            baseDir = System.getProperty("user.dir");
        }

        Path pathObj = Paths.get(path).normalize();
        Path baseObj = Paths.get(baseDir).normalize();

        if (pathObj.isAbsolute() && pathObj.startsWith(baseObj)) {
            return baseObj.relativize(pathObj).toString().replace("\\", "/");
        }

        return path.replace("\\", "/");
    }

    /**
     * 读取文本文件
     */
    public static String readTextFile(String filePath) throws IOException {
        return Files.readString(Paths.get(filePath));
    }

    /**
     * 写入文本文件
     */
    public static void writeTextFile(String filePath, String content) throws IOException {
        Files.writeString(Paths.get(filePath), content);
    }

    /**
     * 从文本中提取对话
     * 匹配各种引号内的内容
     */
    public static List<String> extractDialogueFromText(String text) {
        String pattern = "(?:[""][^""]*[""]|[''][^'']*['']|"[^"]*"|'[^']*'|「[^」]*」|『[^』]*』|［[^］]*］|\\([^)]*\\)|（[^）]*）)";

        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(text);

        List<String> dialogues = new ArrayList<>();
        while (m.find()) {
            String match = m.group();
            // 去除引号
            if (match.length() > 2) {
                dialogues.add(match.substring(1, match.length() - 1));
            }
        }

        return dialogues;
    }
}