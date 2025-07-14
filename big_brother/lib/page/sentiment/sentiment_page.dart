import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'package:intl/intl.dart';

// 数据模型
class SentimentData {
  final DateTime date;
  final double value;

  SentimentData(this.date, this.value);
}

class SentimentPage extends ConsumerStatefulWidget {
  const SentimentPage({super.key});

  @override
  SentimentPageState createState() => SentimentPageState();
}

class SentimentPageState extends ConsumerState<SentimentPage> {
  late ZoomPanBehavior _zoomPanBehavior;
  late CrosshairBehavior _crosshairBehavior;
  late TooltipBehavior _tooltipBehavior;
  
  // 当前选中的日期，用于联动
  DateTime? _selectedDate;
  
  // 模拟数据 - 每个图表独立的数据列表
  final List<SentimentData> _positiveData = [];
  final List<SentimentData> _negativeData = [];
  final List<SentimentData> _neutralData = [];
  final List<SentimentData> _overallData = [];

  @override
  void initState() {
    super.initState();
    _initializeBehaviors();
    _generateSampleData();
  }

  void _initializeBehaviors() {
    // 缩放和平移行为
    _zoomPanBehavior = ZoomPanBehavior(
      enablePinching: true,
      enableDoubleTapZooming: true,
      enablePanning: true,
      zoomMode: ZoomMode.x,
    );

    // 十字线行为
    _crosshairBehavior = CrosshairBehavior(
      enable: true,
      lineType: CrosshairLineType.both,
      lineColor: Colors.grey,
      lineWidth: 1,
      lineDashArray: [5, 5],
    );

    // 工具提示行为
    _tooltipBehavior = TooltipBehavior(
      enable: true,
      duration: 2000,
      canShowMarker: false,
      header: '',
      format: 'point.x : point.y',
      builder: (dynamic data, dynamic point, dynamic series, 
                int pointIndex, int seriesIndex) {
        return _buildTooltip(data, point, series, pointIndex, seriesIndex);
      },
    );
  }

  void _generateSampleData() {
    final DateTime startDate = DateTime.now().subtract(Duration(days: 30));
    
    for (int i = 0; i < 31; i++) {
      // 确保日期是当天的午夜时间，这样标签会正确对齐
      final DateTime date = DateTime(
        startDate.year,
        startDate.month,
        startDate.day + i,
        0, // 午夜0点
        0,
        0,
      );
      
      _positiveData.add(SentimentData(
        date,
        60 + (i * 0.5) + (i % 7 == 0 ? 10 : 0) + (i % 3 == 0 ? -5 : 0),
      ));
      
      _negativeData.add(SentimentData(
        date,
        30 + (i * 0.3) + (i % 5 == 0 ? 8 : 0) + (i % 4 == 0 ? -3 : 0),
      ));
      
      _neutralData.add(SentimentData(
        date,
        40 + (i * 0.2) + (i % 6 == 0 ? 6 : 0) + (i % 2 == 0 ? -4 : 0),
      ));
      
      _overallData.add(SentimentData(
        date,
        50 + (i * 0.4) + (i % 8 == 0 ? 12 : 0) + (i % 3 == 0 ? -6 : 0),
      ));
    }
  }

  Widget _buildTooltip(dynamic data, dynamic point, dynamic series, 
                      int pointIndex, int seriesIndex) {
    final SentimentData sentimentData = data as SentimentData;
    final String seriesName = series.name;
    final String description = _getDescription(seriesName, sentimentData.value);
    
    return Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${seriesName} Sentiment',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          SizedBox(height: 4),
          Text(
            'Date: ${_formatDate(sentimentData.date)}',
            style: TextStyle(color: Colors.white70, fontSize: 12),
          ),
          Text(
            'Value: ${sentimentData.value.toStringAsFixed(1)}%',
            style: TextStyle(color: Colors.white70, fontSize: 12),
          ),
          SizedBox(height: 4),
          Text(
            description,
            style: TextStyle(color: Colors.white70, fontSize: 11),
          ),
        ],
      ),
    );
  }

  String _getDescription(String category, double value) {
    if (category == 'Positive') {
      if (value > 70) return 'Very positive sentiment';
      if (value > 50) return 'Positive sentiment';
      return 'Slightly positive';
    } else if (category == 'Negative') {
      if (value > 50) return 'Very negative sentiment';
      if (value > 30) return 'Negative sentiment';
      return 'Slightly negative';
    } else if (category == 'Neutral') {
      if (value > 60) return 'High neutral sentiment';
      if (value > 40) return 'Neutral sentiment';
      return 'Low neutral sentiment';
    } else {
      if (value > 70) return 'Excellent overall sentiment';
      if (value > 50) return 'Good overall sentiment';
      return 'Fair overall sentiment';
    }
  }

  String _formatDate(DateTime date) {
    return '${date.month.toString().padLeft(2, '0')}/${date.day.toString().padLeft(2, '0')}/${date.year}';
  }

  String _formatDateWithMonth(DateTime date) {
    final List<String> months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[date.month - 1]} ${date.day}';
  }

  Color _getSeriesColor(String category) {
    switch (category) {
      case 'Positive':
        return Colors.green;
      case 'Negative':
        return Colors.red;
      case 'Neutral':
        return Colors.blue;
      case 'Overall':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  Widget _buildChart(String title, List<SentimentData> data, String category) {
    return Container(
      height: 200,
      width: 31 * 100.0, // 31个数据点，每个100像素宽度
      margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 8),
          Expanded(
            child: SfCartesianChart(
              primaryXAxis: CategoryAxis(
                majorGridLines: MajorGridLines(width: 0),
                labelStyle: TextStyle(fontSize: 9), // 调整标签字体大小
                labelRotation: 45, // 旋转标签以避免重叠
                // 确保标签与数据点对齐
                labelIntersectAction: AxisLabelIntersectAction.hide,
              ),
              primaryYAxis: NumericAxis(
                majorGridLines: MajorGridLines(width: 0.5, color: Colors.grey),
                labelFormat: '{value}%',
                minimum: 0,
                maximum: 100,
              ),
              zoomPanBehavior: _zoomPanBehavior,
              crosshairBehavior: _crosshairBehavior,
              tooltipBehavior: _tooltipBehavior,
              series: <CartesianSeries>[
                LineSeries<SentimentData, String>(
                  name: category,
                  dataSource: data,
                  xValueMapper: (SentimentData data, _) => _formatDateWithMonth(data.date),
                  yValueMapper: (SentimentData data, _) => data.value,
                  color: _getSeriesColor(category),
                  width: 2,
                  markerSettings: MarkerSettings(
                    isVisible: true,
                    height: 6,
                    width: 6,
                    color: _getSeriesColor(category),
                    borderColor: Colors.white,
                    borderWidth: 2,
                  ),
                  onPointTap: (ChartPointDetails details) {
                    _onPointTap(details, data);
                  },
                  // 确保数据点正确对齐
                  emptyPointSettings: EmptyPointSettings(mode: EmptyPointMode.drop),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _onPointTap(ChartPointDetails details, List<SentimentData> dataList) {
    if (details.pointIndex != null) {
      final SentimentData data = dataList[details.pointIndex!];
      setState(() {
        _selectedDate = data.date;
      });
      
      // 显示详情对话框
      _showDetailDialog(data);
    }
  }

  void _showDetailDialog(SentimentData data) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Sentiment Details - ${_formatDate(data.date)}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Date: ${_formatDate(data.date)}'),
              Text('Value: ${data.value.toStringAsFixed(1)}%'),
              SizedBox(height: 8),
              Text('Description: ${_getDescription('Overall', data.value)}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('Close'),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: Text('Sentiment Analysis'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 1,
      ),
      body: SingleChildScrollView(
        scrollDirection: Axis.horizontal, // 允许水平滚动
        child: SingleChildScrollView(
          child: Column(
            children: [
              _buildChart('Positive Sentiment', _positiveData, 'Positive'),
              _buildChart('Negative Sentiment', _negativeData, 'Negative'),
              _buildChart('Neutral Sentiment', _neutralData, 'Neutral'),
              _buildChart('Overall Sentiment', _overallData, 'Overall'),
            ],
          ),
        ),
      ),
    );
  }
}