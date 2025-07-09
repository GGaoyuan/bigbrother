import 'dart:io';
import 'package:big_brother/general/network/network_config.dart';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';

enum NetworkMethod {
  POST('POST'),
  GET('GET');
  final String value;
  const NetworkMethod(this.value);
}


class Network {
  static final Network _instance = Network._internal();
  factory Network() => _instance;
  static Network get instance => _instance;
  Network._internal() {
    _dio = Dio();
  }

  late Dio _dio;

  Future<dynamic> doGet(String address, {Map<String, dynamic>? headers, Map<String, dynamic>? params}) async {
    return _doRequest(NetworkMethod.GET, address, params: params);
  }

  Future<dynamic> doPost(String address, {Map<String, dynamic>? headers, Map<String, dynamic>? params}) async {
    return _doRequest(NetworkMethod.POST, address, params: params);
  }

  Future<dynamic> _doRequest(
      NetworkMethod method,
      String address, {
        Map<String, dynamic>? headers,
        Map<String, dynamic>? params
      }) async {

    final config = NetworkConfigReader.instance.getConfig();

    Options options = Options(method: method.value);
    options.sendTimeout = const Duration(seconds: 30);
    options.receiveTimeout = const Duration(seconds: 30);
    options.headers = {...config.defaultHeader, ...?headers};

    final String fullAddress = config.baseAddress + address;

    final parameters = {...config.defaultParams, ...?params};
    print("object");
    try {
      final Response response = await _dio.request(
          fullAddress,
          options: options,
          queryParameters: (method == NetworkMethod.GET ? parameters : null),
          data: (method == NetworkMethod.POST ? parameters : null));
      return response.data;
    } catch (e, stackTrace) {
      //弹一个Toast
      throw Exception("Request failed: $e, \n $stackTrace");
    }
  }
}
