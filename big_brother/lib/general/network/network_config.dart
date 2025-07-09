

class NetworkConfigReader {
  static final NetworkConfigReader _instance = NetworkConfigReader._internal();
  factory NetworkConfigReader() => _instance;
  static NetworkConfigReader get instance => _instance;
  NetworkConfigReader._internal() {
    _config = NetworkConfig();
  }

  late NetworkConfig _config;

  NetworkConfig getConfig() => _config;
}


class NetworkConfig {
  // final String baseAddress = "http://49.235.60.18";
  final String baseAddress = "http://127.0.0.1:5000";

  Map<String, dynamic> get defaultParams {
    return {

    };
  }

  Map<String, dynamic> get defaultHeader {
    return {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'User-Agent': 'Dart/2.18 (dart:io)',
    };
  }
}
