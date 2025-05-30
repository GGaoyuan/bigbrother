

import 'package:flutter/material.dart';

class AppConfig {
  static final AppConfig _instance = AppConfig._internal();
  factory AppConfig() => _instance;
  static AppConfig get instance => _instance;
  AppConfig._internal() {

  }

  Color get themeColor => Colors.white;

}


