import 'package:big_brother/general/app_config.dart';
import 'package:big_brother/page/rotation/heatmap_series.dart';
import 'package:big_brother/page/rotation/rotation_notifier.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class HeatmapWidget extends ConsumerStatefulWidget {
  final List<HeatmapSeries> dataSeries;

  const HeatmapWidget(this.dataSeries, {super.key});
  @override
  HeatmapWidgetState createState() => HeatmapWidgetState();
}

class HeatmapWidgetState extends ConsumerState<HeatmapWidget> {
  TooltipBehavior? _tooltipBehavior;

  @override
  void initState() {
    _tooltipBehavior = TooltipBehavior(
      enable: true,
      header: 'Heatmap Cell',
      animationDuration: 0,
      tooltipPosition: TooltipPosition.pointer,
      format: 'Row: point.x, Col: point.y, Value: point.size',
    );

    super.initState();
  }

  Color _buildColor(num value) {
    if (value >= 100.0) {
      return Colors.red.shade900;
    } else if (value >= 90.0) {
      return Colors.red.shade800;
    } else if (value >= 80.0) {
      return Colors.red.shade700;
    } else if (value >= 70.0) {
      return Colors.red.shade600;
    } else if (value >= 60.0) {
      return Colors.red.shade500;
    } else if (value >= 50.0) {
      return Colors.red.shade400;
    } else if (value >= 40.0) {
      return Colors.red.shade300;
    } else if (value >= 30.0) {
      return Colors.red.shade200;
    } else if (value >= 20.0) {
      return Colors.red.shade100;
    } else if (value >= 10.0) {
      return Colors.red.shade50;
    } else if (value > 0.0) {
      return Colors.white;
    } else if (value == 0.0) {
      return Colors.white;
    } else if (value >= -10.0) {
      return Colors.blue.shade50;
    } else if (value >= -20.0) {
      return Colors.blue.shade100;
    } else if (value >= -30.0) {
      return Colors.blue.shade200;
    } else if (value >= -40.0) {
      return Colors.blue.shade300;
    } else if (value >= -50.0) {
      return Colors.blue.shade400;
    } else if (value >= -60.0) {
      return Colors.blue.shade500;
    } else if (value >= -70.0) {
      return Colors.blue.shade600;
    } else if (value >= -80.0) {
      return Colors.blue.shade700;
    } else if (value >= -90.0) {
      return Colors.blue.shade800;
    } else if (value >= -100.0) {
      return Colors.blue.shade900;
    }
    return Colors.black;
  }

  // Generate heatmap data for 50x30 grid
  List<HeatmapDataPoint> _generateHeatmapData() {
    List<HeatmapDataPoint> data = [];
    for (int row = 0; row < 50; row++) {
      for (int col = 0; col < 100; col++) {
        // Generate demo value (you can replace with real data)
        double value = (row * 30 + col) % 100.0;
        data.add(HeatmapDataPoint(row, col, value));
      }
    }
    return data;
  }

  @override
  Widget build(BuildContext context) {
    const double markerLength = 50;
    final heatmapData = _generateHeatmapData();

    return Scaffold(
      backgroundColor: AppConfig.backgroundColor,
      body: Column(
        children: [
          const Center(
            child: Text("Heatmap Chart", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.vertical,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Container(
                  width: 30 * 50.0, // 30 columns * 50 pixels each
                  height: 50 * 50.0, // 50 rows * 50 pixels each
                  child: SfCartesianChart(
                    plotAreaBorderWidth: 0,
                    primaryXAxis: NumericAxis(
                      minimum: -0.5,
                      maximum: 29.5,
                      interval: 1,
                      axisLine: const AxisLine(width: 0),
                      majorGridLines: const MajorGridLines(width: 0),
                      majorTickLines: const MajorTickLines(width: 0),
                      labelStyle: const TextStyle(fontSize: 0),
                    ),
                    primaryYAxis: NumericAxis(
                      minimum: -0.5,
                      maximum: 49.5,
                      interval: 1,
                      axisLine: const AxisLine(width: 0),
                      majorGridLines: const MajorGridLines(width: 0),
                      majorTickLines: const MajorTickLines(width: 0),
                      labelStyle: const TextStyle(fontSize: 0),
                    ),
                    tooltipBehavior: _tooltipBehavior,
                    series: [
                      ScatterSeries<HeatmapDataPoint, int>(
                        dataSource: heatmapData,
                        xValueMapper: (HeatmapDataPoint data, int _) => data.column,
                        yValueMapper: (HeatmapDataPoint data, int _) => data.row,
                        pointColorMapper: (HeatmapDataPoint data, int _) => _buildColor(data.value),
                        dataLabelSettings: DataLabelSettings(
                          isVisible: true,
                          labelAlignment: ChartDataLabelAlignment.middle,
                          textStyle: const TextStyle(
                            fontSize: 8,
                            color: Colors.black,
                            fontWeight: FontWeight.bold,
                          ),
                          builder: (dynamic data, dynamic point, dynamic series, int pointIndex, int seriesIndex) {
                            return Text(
                              data.value.toStringAsFixed(0),
                              style: TextStyle(
                                fontSize: 8,
                                color: data.value > 50 ? Colors.white : Colors.black,
                                fontWeight: FontWeight.bold,
                              ),
                            );
                          },
                        ),
                        markerSettings: const MarkerSettings(
                          isVisible: true,
                          width: markerLength,
                          height: markerLength,
                          borderWidth: 0.1,
                          shape: DataMarkerType.rectangle,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Data class for heatmap points
class HeatmapDataPoint {
  final int row;
  final int column;
  final double value;

  HeatmapDataPoint(this.row, this.column, this.value);
}