import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChartData {
  String datetime = "";
  double value = 0;
}

class SingleLineChart extends ConsumerStatefulWidget {
  final List<ChartData> dataSource;
  const SingleLineChart(this.dataSource, {super.key});

  @override
  SingleLineChartState createState() => SingleLineChartState();
}

class SingleLineChartState extends ConsumerState<SingleLineChart> {
  
  @override
  Widget build(BuildContext context) {
    return Container();
  }

}