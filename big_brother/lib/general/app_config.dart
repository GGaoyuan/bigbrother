

import 'package:flutter/material.dart';

class AppConfig {


  static final themeColor = Colors.white;

  // 全局主题配置
  static final globalTheme = ThemeData(
    textTheme: TextTheme(
      bodyLarge: TextStyle(decoration: TextDecoration.none),
      bodyMedium: TextStyle(decoration: TextDecoration.none),
      bodySmall: TextStyle(decoration: TextDecoration.none),
      labelLarge: TextStyle(decoration: TextDecoration.none),
      labelMedium: TextStyle(decoration: TextDecoration.none),
      labelSmall: TextStyle(decoration: TextDecoration.none),
    ),
  );

  // 全局文本样式
  static final defaultTextStyle = TextStyle(
    decoration: TextDecoration.none,
    fontSize: 14,
  );

  // 顶部栏文本样式 - 已注释
  // static final titleBarTextStyle = TextStyle(
  //   decoration: TextDecoration.none,
  //   fontSize: 16,
  //   fontWeight: FontWeight.bold,
  // );

  // 按钮文本样式 - 已注释
  // static final buttonTextStyle = TextStyle(
  //   decoration: TextDecoration.none,
  //   fontSize: 10,
  // );

  // 顶部栏高度 - 已注释
  // static const double titleBarHeight = 260.0;
}


