import 'package:big_brother/window/main_window.dart';
import 'package:flutter/material.dart';
import 'package:bitsdojo_window/bitsdojo_window.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:tabbed_view/tabbed_view.dart';
import 'package:big_brother/general/app_config.dart';

void main() {
  runApp(
    ProviderScope(child: MyApp()),
  );

  doWhenWindowReady(() {
    // appWindow.minSize = const Size(900, 600);
    appWindow.alignment = Alignment.center;
    appWindow.maximize();
    appWindow.show();
  });
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: true,
      theme: AppConfig.globalTheme,
      home: const MainWindow(),
    );
  }
}
