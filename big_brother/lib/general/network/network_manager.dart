import 'package:big_brother/general/network/network.dart';

class NetworkManager {

  /*
  * test
  * */
  // static Future<dynamic> requestTest() async {
  //   final data = await Network.instance.doGet("/test");
  //   return data;
  // }

  //测试成功
  static Future<dynamic> requestTest11111() async {
    final data = await Network.instance.doPost("/dynamic_call", params: {
      "code": "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2021-01-01')"
    });
    return data;
  }

  static Future<dynamic> requestTest() async {
    final data = await Network.instance.doPost("/dynamic_calls", params: {
      "codes": [
        "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2021-01-01')",
        "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2022-01-01')",
        "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2023-01-01')",
        "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2024-01-01')",
        "adata.stock.market.get_market(stock_code='000001', k_type=1, start_date='2025-01-01')",
      ]
    });
    return data;
  }

}