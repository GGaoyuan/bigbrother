import 'package:big_brother/page/rotation/heatmap_series.dart';
import 'package:big_brother/page/sentiment/single_line_chart.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math';
import 'package:intl/intl.dart';

/*
* 获取各个概念板块涨停家数和总家数的比值
* */
final industryProvider = FutureProvider.autoDispose<List<HeatmapSeries>>((ref) async {
  ref.onDispose(() {
    debugPrint("testProvider dispose");
  });
  await Future.delayed(const Duration(milliseconds: 300));
  
  // 生成30个HeatmapSeries数据
  final List<HeatmapSeries> result = [];
  final Random random = Random();
  final DateTime today = DateTime.now();
  
  for (int i = 0; i < 30; i++) {
    final DateTime date = today.subtract(Duration(days: 29 - i));
    final String dateString = DateFormat('M/d').format(date);
    final double value = -100 + random.nextDouble() * 200;
    final series = HeatmapSeries((i + 1).toString(), SeriesPiece(dateString, value));
    result.add(series);
  }
  
  return result;
});