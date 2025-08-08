import 'package:big_brother/general/app_config.dart';
import 'package:big_brother/page/rotation/heatmap_widget.dart';
import 'package:big_brother/page/rotation/rotation_notifier.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class RotationPage extends ConsumerStatefulWidget {
  const RotationPage({super.key});
  @override
  RotationPageState createState() => RotationPageState();
}


class RotationPageState extends ConsumerState<RotationPage> {

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConfig.backgroundColor,
      body: ref.watch(industryProvider).when(data: (data) {
        return Container(
          // 根据数据量计算容器大小
          width: data.isNotEmpty ? data.first.pieces.length * 50.0 : 300,
          height: data.length * 50.0,
          child: HeatmapWidget(data),
        );
      }, error: (error, _) {
        return Center(child: Text("$error"));
      }, loading: (){
        return const Center(child: CircularProgressIndicator());
      })
    );
  }
}