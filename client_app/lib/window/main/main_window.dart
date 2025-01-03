import 'package:client_app/global.dart';

class MainWindow extends StatelessWidget {
  const MainWindow({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: Container(color: Colors.green),
    );
  }
}