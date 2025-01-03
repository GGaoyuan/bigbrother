import 'global.dart';
import 'package:client_app/window/main/main_window.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MainWindow(),
    ),
  );// MainPage());
}
