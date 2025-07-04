import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class ChartData {
  final String category;
  final double value1;
  final double value2;
  final double barValue;

  ChartData(this.category, this.value1, this.value2, this.barValue);
}


class OverviewPage extends ConsumerStatefulWidget {

  const OverviewPage({super.key});

  @override
  OverviewPageState createState() => OverviewPageState();
}

class OverviewPageState extends ConsumerState<OverviewPage> {

  @override
  void initState() {
    super.initState();


  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final List<ChartData> data = [
      ChartData('Mon', 10, 12, 30),
      ChartData('Tue', 15, 14, 28),
      ChartData('Wed', 13, 16, 35),
      ChartData('Thu', 20, 18, 32),
      ChartData('Fri', 17, 20, 40),
      ChartData('Mon1', 10, 12, 30),
      ChartData('Tue1', 15, 14, 28),
      ChartData('Wed1', 13, 16, 35),
      ChartData('Thu1', 20, 18, 32),
      ChartData('Fri1', 17, 20, 40),

      ChartData('Mon2', 10, 12, 30),
      ChartData('Tue3', 15, 14, 28),
      ChartData('Wed4', 13, 16, 35),
      ChartData('Thu5', 20, 18, 32),
      ChartData('Fri6', 17, 20, 40),

      ChartData('Mon7', 10, 12, 30),
      ChartData('Tue8', 15, 14, 28),
      ChartData('Wed9', 13, 16, 35),
      ChartData('Thu10', 20, 18, 32),
      ChartData('Fri11', 17, 20, 40),
    ];
    return ListView(
      children: [
        Text("data"),
        SfCartesianChart(
          legend: Legend(isVisible: true),
          primaryXAxis: CategoryAxis(),
          primaryYAxis: NumericAxis(),
          series: <CartesianSeries>[
            LineSeries<ChartData, String>(
              name: '折线1',
              dataSource: data,
              xValueMapper: (ChartData d, _) => d.category,
              yValueMapper: (ChartData d, _) => d.value1,
              markerSettings: const MarkerSettings(isVisible: true),
            ),
            // 第二条折线
            LineSeries<ChartData, String>(
              name: '折线2',
              dataSource: data,
              xValueMapper: (ChartData d, _) => d.category,
              yValueMapper: (ChartData d, _) => d.value2,
              markerSettings: const MarkerSettings(isVisible: true),
            ),
            ColumnSeries<ChartData, String>(
              color: Colors.red,
              name: '柱状图',
              dataSource: data,
              xValueMapper: (ChartData d, _) => d.category,
              yValueMapper: (ChartData d, _) => d.barValue,
            ),
          ],
        )
      ],
    );
  }

}