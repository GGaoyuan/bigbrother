import 'package:big_brother/general/app_config.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class TestPage extends ConsumerStatefulWidget {
  const TestPage({super.key});
  @override
  TestPageState createState() => TestPageState();
}

class _HeatMapData {
  final String percentage;
  final double nancy;
  final double andrew;
  final double janet;
  final double margaret;
  final double steven;
  final double michael;
  final double robert;
  final double laura;
  final double anne;
  final double paul;
  final double mario;

  _HeatMapData(
      this.percentage,
      this.nancy,
      this.andrew,
      this.janet,
      this.margaret,
      this.steven,
      this.michael,
      this.robert,
      this.laura,
      this.anne,
      this.paul,
      this.mario);
}

class TestPageState extends ConsumerState<TestPage> {

  List<_HeatMapData>? _heatMapData;
  TooltipBehavior? _tooltipBehavior;

  @override
  void initState() {
    _heatMapData = <_HeatMapData>[
      _HeatMapData('Mon', 0.694, 27, 0.285, 0.76, 0.375, 10, 3, 4, 2, 5, 30),
      _HeatMapData('Tue', 15, 1.68, 50, 1.61, 1.75, 1.61, 60, 40, 150, 40, 0.1),
      _HeatMapData('Wed', 0.5, 0.15, 90, 0.6, 0.25, 7, 2, 3, 1, 4, 20),
      _HeatMapData('Thu', 0.3, 80, 0.1, 0.4, 112, 4, 1, 50, 0, 2, 40),
      _HeatMapData('Fri', 0.5, 0.15, 90, 0.6, 0.25, 7, 2, 3, 1, 4, 20),
      _HeatMapData('Sat', 6.9, 43.2, 40.8, 69.5, 49.5, 5.7, 80, 20, 12, 40, 9),
    ];
    _tooltipBehavior = TooltipBehavior(
      enable: true,
      header: 'Person',
      animationDuration: 0,
      tooltipPosition: TooltipPosition.pointer,
      format: 'point.x : point.y',
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

  List<NumericMultiLevelLabel> _buildNumericLabels() {
    return [
      NumericMultiLevelLabel(start: 0, end: 8, text: 'Nancy'),
      NumericMultiLevelLabel(start: 8, end: 19, text: 'Andrew'),
      NumericMultiLevelLabel(start: 19, end: 26, text: 'Janet'),
      NumericMultiLevelLabel(start: 26, end: 38, text: 'Margaret'),
      NumericMultiLevelLabel(start: 38, end: 43, text: 'Steven'),
      NumericMultiLevelLabel(start: 43, end: 56, text: 'Michael'),
      NumericMultiLevelLabel(start: 56, end: 62, text: 'Robert'),
      NumericMultiLevelLabel(start: 62, end: 75, text: 'Laura'),
      NumericMultiLevelLabel(start: 75, end: 80, text: 'Anne'),
      NumericMultiLevelLabel(start: 80, end: 92, text: 'Paul'),
      NumericMultiLevelLabel(start: 92, end: 98, text: 'Mario'),
    ];
  }

  ChartAxisLabel _formatLabel(MultiLevelLabelRenderDetails details) {
    return ChartAxisLabel(details.text,
        const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: AppConfig.backgroundColor,
        // appBar: AppBar(
        //   title: Text('Sentiment Analysis'),
        //   backgroundColor: Colors.white,
        //   foregroundColor: Colors.black87,
        //   elevation: 1,
        // ),
        body: SfCartesianChart(
          plotAreaBorderWidth: 0,
          primaryXAxis: CategoryAxis(
            axisLine: const AxisLine(width: 0),
            majorGridLines: const MajorGridLines(width: 0),
            majorTickLines: const MajorTickLines(width: 0),
            labelStyle:
            const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0),
          ),
          primaryYAxis: NumericAxis(
            opposedPosition: true,
            axisLine: const AxisLine(width: 0),
            majorGridLines: const MajorGridLines(width: 0),
            majorTickLines: const MajorTickLines(width: 0),
            labelStyle: const TextStyle(fontSize: 0),
            multiLevelLabelStyle:
            MultiLevelLabelStyle(borderColor: Colors.transparent),
            multiLevelLabels: _buildNumericLabels(),
            multiLevelLabelFormatter: _formatLabel,
          ),
          legend: Legend(
            isVisible: true,
            position: LegendPosition.top,
            toggleSeriesVisibility: false,
            legendItemBuilder: (legendText, series, point, seriesIndex) {
              return Row(
                children: [
                  const Text('Zero '),
                  const SizedBox(width: 5),
                  SizedBox(
                      width: 400,
                      height: 20,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Colors.lightBlue.withValues(alpha: 0.1),
                              Colors.lightBlue.withValues(alpha: 0.4),
                              Colors.lightBlue.withValues(alpha: 0.9),
                            ],
                            begin: Alignment.centerLeft,
                            end: Alignment.centerRight,
                          ),
                        ),
                      )),
                  const SizedBox(width: 5),
                  const Text('150'),
                ],
              );
            },
          ),
          tooltipBehavior: _tooltipBehavior,
          series: _buildHeatmapSeries(),
        )
    );
  }

  List<CartesianSeries<_HeatMapData, String>> _buildHeatmapSeries() {
    return List.generate(11, (index) {
      return StackedBar100Series<_HeatMapData, String>(
        dataSource: _heatMapData,
        xValueMapper: (_HeatMapData data, int _) => data.percentage,
        yValueMapper: (_HeatMapData data, int _) =>
            _findValueByIndex(data, index),
        pointColorMapper: (_HeatMapData data, int _) =>
            _buildColor(_findValueByIndex(data, index)),
        isVisibleInLegend: index == 0,
        animationDuration: 0,
        width: 1,
        borderWidth: 1,
        borderColor: Colors.lightBlue.shade600,
        dataLabelSettings: DataLabelSettings(
          isVisible: true,
          labelAlignment: ChartDataLabelAlignment.middle,
          textStyle: const TextStyle(
            fontSize: 15,
            color: Colors.black,
            fontWeight: FontWeight.bold,
          ),
        ),
        onCreateRenderer: (ChartSeries<_HeatMapData, String> series) {
          return _HeatmapSeriesRenderer();
        },
      );
    });
  }

  double _findValueByIndex(_HeatMapData data, int index) {
    switch (index) {
      case 0:
        return data.nancy;
      case 1:
        return data.andrew;
      case 2:
        return data.janet;
      case 3:
        return data.margaret;
      case 4:
        return data.steven;
      case 5:
        return data.michael;
      case 6:
        return data.robert;
      case 7:
        return data.laura;
      case 8:
        return data.anne;
      case 9:
        return data.paul;
      case 10:
        return data.mario;
      default:
        return 0;
    }
  }
}


class _HeatmapSeriesRenderer
    extends StackedBar100SeriesRenderer<_HeatMapData, String> {
  _HeatmapSeriesRenderer();

  @override
  void populateDataSource(
      [List<ChartValueMapper<_HeatMapData, num>>? yPaths,
        List<List<num>>? chaoticYLists,
        List<List<num>>? yLists,
        List<ChartValueMapper<_HeatMapData, Object>>? fPaths,
        List<List<Object?>>? chaoticFLists,
        List<List<Object?>>? fLists]) {
    super.populateDataSource(
        yPaths, chaoticYLists, yLists, fPaths, chaoticFLists, fLists);

    // Always keep positive 0 to 101 range even set negative value.
    yMin = 0;
    yMax = 101;

    // Calculate heatmap segment top and bottom values.
    _computeHeatMapValues();
  }

  void _computeHeatMapValues() {
    if (xAxis == null || yAxis == null) {
      return;
    }

    if (yAxis!.dependents.isEmpty) {
      return;
    }

    // Get the number of series dependent on the yAxis.
    final int seriesLength = yAxis!.dependents.length;
    // Calculate the proportional height for each series
    // (as a percentage of the total height).
    final num yValue = 100 / seriesLength;
    // Loop through each dependent series to calculate top and bottom values for
    // the heatmap.
    for (int i = 0; i < seriesLength; i++) {
      // Check if the current series is a '_HeatmapSeriesRenderer'.
      if (yAxis!.dependents[i] is _HeatmapSeriesRenderer) {
        final _HeatmapSeriesRenderer current =
        yAxis!.dependents[i] as _HeatmapSeriesRenderer;

        // Skip processing if the series is not visible or has no data.
        if (!current.controller.isVisible || current.dataCount == 0) {
          continue;
        }

        // Calculate the bottom (stack) value for the current series.
        num stackValue = 0;
        stackValue = yValue * i;

        current.topValues.clear();
        current.bottomValues.clear();

        // Loop through the data points in the current series.
        final int length = current.dataCount;
        for (int j = 0; j < length; j++) {
          // Add the bottom value (stackValue) for the current data point.
          current.bottomValues.add(stackValue.toDouble());
          // Add the top value (stackValue + yValue) for the current data point.
          current.topValues.add((stackValue + yValue).toDouble());
        }
      }
    }
  }
}