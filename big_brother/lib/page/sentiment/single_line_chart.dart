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
    return SingleChildScrollView(
      // shrinkWrap: true,
      // physics: const NeverScrollableScrollPhysics(),
      scrollDirection: Axis.horizontal, // 启用水平滚动
      physics: const ClampingScrollPhysics(), // 移除弹簧效果
      child: Container(
        // color: randomColor(),
        height: 400,
        width: widget.dataSource.length * 50.0, //每个节点100像素宽度
        // margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        // padding: EdgeInsets.all(16),
        child: SfCartesianChart(
          // 1. 设置X轴为字符串分类轴（CategoryAxis）
          primaryXAxis: CategoryAxis(
            // title: AxisTitle(text: '月份'), // X轴标题
            labelPlacement: LabelPlacement.onTicks, // 标签位置（对齐刻度线）
            labelRotation: -45, // 标签旋转角度（避免重叠）
            // majorGridLines: MajorGridLines(width: 0), // 隐藏X轴网格线
            // 设置节点间隔
            interval: 1, // 显示所有标签
            labelStyle: TextStyle(fontSize: 10), // 调整标签字体大小
            // 设置轴的位置和间距
            plotOffset: 50, // 减少轴与图表的间距
          ),
          // 2. 设置Y轴
          primaryYAxis: NumericAxis(
            // title: AxisTitle(text: '销售额 (万)'), // Y轴标题
            minimum: 0, // Y轴最小值
            maximum: 100, // Y轴最大值
            interval: 10, // 刻度间隔
            plotOffset: 0, // 减少轴与图表的间距
          ),
          // 3. 设置图表区域
          plotAreaBorderWidth: 0, // 移除图表区域边框
          margin: EdgeInsets.all(50), // 移除图表边距
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
          legend: Legend(isVisible: false), // 隐藏图例
        ),
      ),
    );
  }
}