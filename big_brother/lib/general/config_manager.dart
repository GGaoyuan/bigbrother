

class ConfigManager {
  static final ConfigManager _instance = ConfigManager._internal();
  factory ConfigManager() => _instance;
  static ConfigManager get instance => _instance;
  ConfigManager._internal() {

  }
}


