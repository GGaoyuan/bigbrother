import 'package:big_brother/general/general_import.dart';
import 'package:big_brother/page/sentiment/data_notifier.dart';
import 'package:big_brother/page/sentiment/single_line_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'package:intl/intl.dart';


class MainPage extends ConsumerStatefulWidget {
  const MainPage({super.key});

  @override
  MainPageState createState() => MainPageState();
}

class MainPageState extends ConsumerState<MainPage> {

  @override
  void initState() {
    super.initState();
    _generateSampleData();
  }

  void _generateSampleData() {

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
        scrollDirection: Axis.vertical, // 允许水平滚动
        child: Column(
          children: [
            Consumer(builder: (_, _, _) {
              return ref.watch(testProvider).when(data: (data) {
                return SingleLineChart(data);
              }, error: (error, _) {
                return Text("$error");
              }, loading: (){
                return const Center(child: CircularProgressIndicator());
              });
            }),
            Container(height: 300, color: randomColor()),
            Container(height: 300, color: randomColor()),
            Container(height: 300, color: randomColor()),
            Container(height: 300, color: randomColor()),
            Container(height: 300, color: randomColor()),
          ],
        ),
      ),
    );
  }
}