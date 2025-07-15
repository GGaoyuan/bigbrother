import 'package:flutter/cupertino.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/*
* 获取各个概念板块涨停家数和总家数的比值
* */
final clickProvider = FutureProvider.autoDispose<int>((ref) {
  ref.onDispose(() {
    debugPrint("clickProvider dispose");
  });
  return 0;
});

/*
* 获取各个概念板块上涨家数和总家数的比值
* */


/*
* 获取各个概念板块资金的净流入
* */




