import 'package:big_brother/page/sentiment/single_line_chart.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/*
* 获取各个概念板块涨停家数和总家数的比值
* */
final testProvider = FutureProvider.autoDispose<List<SingleLineChartData>>((ref) async {
  ref.onDispose(() {
    debugPrint("testProvider dispose");
  });
  await Future.delayed(const Duration(seconds: 1));
  final List<SingleLineChartData> rtn = List.generate(50, (index) {
    // 生成4位字符串作为日期
    String dateStr = 'Date${(index + 1).toString().padLeft(3, '0')}';
    
    // 生成5-99的随机数字
    int randomValue = 5 + (index * 2) % 95; // 使用简单的算法生成5-99的数字
    
    return SingleLineChartData(dateStr, randomValue.toDouble());
  });

  return rtn;
});

/*
* 获取各个概念板块上涨家数和总家数的比值
* */


/*
* 获取各个概念板块资金的净流入
* */




