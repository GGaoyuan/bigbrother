import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';



class SentimentPage extends ConsumerStatefulWidget {

  const SentimentPage({super.key});

  @override
  SentimentPageState createState() => SentimentPageState();
}

class SentimentPageState extends ConsumerState<SentimentPage> {

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
    return Container(
      color: Colors.white,
      child: Center(
        child: Text("Emotion Page"),
      ),
    );
  }
}