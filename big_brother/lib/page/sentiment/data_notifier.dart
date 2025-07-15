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
  final List<SingleLineChartData> rtn = [
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
    SingleLineChartData('Jan', 35),
    SingleLineChartData('Feb', 28),
    SingleLineChartData('Mar', 42),
    SingleLineChartData('Apr', 60),
    SingleLineChartData('May', 75),
    SingleLineChartData('Jun', 90),
  ];

  return rtn;
});

/*
* 获取各个概念板块上涨家数和总家数的比值
* */


/*
* 获取各个概念板块资金的净流入
* */




