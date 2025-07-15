import 'package:big_brother/general/general_import.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class SingleLineChartData {
  final String datetime;
  final double value;
  const SingleLineChartData(this.datetime, this.value);
}

class SingleLineChart extends ConsumerStatefulWidget {
  final List<SingleLineChartData> dataSource;
  const SingleLineChart(this.dataSource, {super.key});

  @override
  SingleLineChartState createState() => SingleLineChartState();
}

class SingleLineChartState extends ConsumerState<SingleLineChart> {

  @override
  Widget build(BuildContext context) {
    return Container(
      color: randomColor(),
      height: 200,
      width: widget.dataSource.length * 100.0, //每个100像素宽度
      margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      padding: EdgeInsets.all(16),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: SfCartesianChart(
          // 1. 设置X轴为字符串分类轴（CategoryAxis）
          primaryXAxis: CategoryAxis(
            title: AxisTitle(text: '月份'), // X轴标题
            labelPlacement: LabelPlacement.onTicks, // 标签位置（对齐刻度线）
            labelRotation: -45, // 标签旋转角度（避免重叠）
            majorGridLines: MajorGridLines(width: 0), // 隐藏X轴网格线
          ),
          // 2. 设置Y轴
          primaryYAxis: NumericAxis(
            title: AxisTitle(text: '销售额 (万)'), // Y轴标题
            minimum: 0, // Y轴最小值
            maximum: 100, // Y轴最大值
            interval: 20, // 刻度间隔
          ),
          series: <CartesianSeries>[
            LineSeries<SingleLineChartData, String>(
              dataSource: widget.dataSource,
              xValueMapper: (SingleLineChartData sales, _) => sales.datetime, // X轴绑定字符串
              yValueMapper: (SingleLineChartData sales, _) => sales.value, // Y轴绑定数值
              dataLabelSettings: DataLabelSettings(isVisible: true), // 显示数据标签
              markerSettings: MarkerSettings(isVisible: true), // 显示数据点标记
              color: Colors.blue, // 折线颜色
              width: 3, // 折线宽度
            ),
          ],
          // 4. 其他图表配置
          tooltipBehavior: TooltipBehavior(enable: true), // 启用悬停提示
          legend: Legend(isVisible: true), // 显示图例（如果有多个系列）
          ),
        ),
    );
  }
}