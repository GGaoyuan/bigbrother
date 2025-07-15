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


//
// Widget _buildChart(String title, List<SentimentData> data, String category) {
//   return Container(
//     height: 200,
//     width: 31 * 100.0, // 31个数据点，每个100像素宽度
//     margin: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
//     padding: EdgeInsets.all(16),
//     decoration: BoxDecoration(
//       color: Colors.white,
//       borderRadius: BorderRadius.circular(12),
//       boxShadow: [
//         BoxShadow(
//           color: Colors.black12,
//           blurRadius: 4,
//           offset: Offset(0, 2),
//         ),
//       ],
//     ),
//     child: Column(
//       crossAxisAlignment: CrossAxisAlignment.start,
//       children: [
//         Text(
//           title,
//           style: TextStyle(
//             fontSize: 16,
//             fontWeight: FontWeight.bold,
//             color: Colors.black87,
//           ),
//         ),
//         SizedBox(height: 8),
//         Expanded(
//           child: SfCartesianChart(
//             primaryXAxis: CategoryAxis(
//               majorGridLines: MajorGridLines(width: 0),
//               labelStyle: TextStyle(fontSize: 9), // 调整标签字体大小
//               labelRotation: 45, // 旋转标签以避免重叠
//               // 确保标签与数据点对齐
//               labelIntersectAction: AxisLabelIntersectAction.hide,
//             ),
//             primaryYAxis: NumericAxis(
//               majorGridLines: MajorGridLines(width: 0.5, color: Colors.grey),
//               labelFormat: '{value}%',
//               minimum: 0,
//               maximum: 100,
//             ),
//             zoomPanBehavior: _zoomPanBehavior,
//             crosshairBehavior: _crosshairBehavior,
//             tooltipBehavior: _tooltipBehavior,
//             series: <CartesianSeries>[
//               LineSeries<SentimentData, String>(
//                 name: category,
//                 dataSource: data,
//                 xValueMapper: (SentimentData data, _) => _formatDateWithMonth(data.date),
//                 yValueMapper: (SentimentData data, _) => data.value,
//                 color: _getSeriesColor(category),
//                 width: 2,
//                 markerSettings: MarkerSettings(
//                   isVisible: true,
//                   height: 6,
//                   width: 6,
//                   color: _getSeriesColor(category),
//                   borderColor: Colors.white,
//                   borderWidth: 2,
//                 ),
//                 onPointTap: (ChartPointDetails details) {
//                   _onPointTap(details, data);
//                 },
//                 // 确保数据点正确对齐
//                 emptyPointSettings: EmptyPointSettings(mode: EmptyPointMode.drop),
//               ),
//             ],
//           ),
//         ),
//       ],
//     ),
//   );
// }