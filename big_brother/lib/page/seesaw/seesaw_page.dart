import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';


class SeesawPage extends ConsumerStatefulWidget {

  const SeesawPage({super.key});

  @override
  SeesawPageState createState() => SeesawPageState();
}

class SeesawPageState extends ConsumerState<SeesawPage> {

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
      body: ListView(

        children: [
          Text("data"),
        ],
      ),
    );
  }

}