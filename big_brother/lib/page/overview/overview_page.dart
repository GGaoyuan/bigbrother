import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';



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
    return Scaffold(
        body: Container(color: Colors.blue)
    );
  }

}