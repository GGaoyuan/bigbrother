import 'package:flutter/material.dart';
import 'package:bitsdojo_window/bitsdojo_window.dart';
import 'package:tabbed_view/tabbed_view.dart';

void main() {
  runApp(const MyApp());

  doWhenWindowReady(() {
    const initialSize = Size(900, 600);
    appWindow.minSize = const Size(600, 400);
    appWindow.size = initialSize;
    appWindow.alignment = Alignment.center;
    appWindow.show();
  });
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: true,
      home: DesktopApp(),
    );
  }
}

class TabbedDemo extends StatefulWidget {
  const TabbedDemo({super.key});
  @override
  State<TabbedDemo> createState() => _TabbedDemoState();
}

class _TabbedDemoState extends State<TabbedDemo> {
  final controller = TabbedViewController(
    [TabData(text: '首页', content: Center(child: Text('首页内容')))],);

  void _addTab() {
    controller.addTab(TabData(text: 'New Tab', content: Center(child: Text('新页面'))));

  }

  @override
  void initState() {
    super.initState();
    // var tabs = [
    //   TabData(text: 'Tab 1'),
    //   TabData(text: 'Tab 2'),
    //   TabData(text: 'Tab 3')
    // ];
    //
    // final a = TabbedViewController(tabs);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('tabbed_view 示例'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _addTab,
          )
        ],
      ),
      body: TabbedView(
          controller: controller,
          contentBuilder: (BuildContext context, int tabIndex) {
            int i = tabIndex + 1;
            return Center(child: Text('Content $i'));
          }),
    );
  }
}




class DesktopApp extends StatelessWidget {
  const DesktopApp({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = TabbedViewController(
      [TabData(text: '首页', content: Center(child: Text('首页内容')))],);

    return Scaffold(
      backgroundColor: Colors.white,
      body: MoveWindow(
          child: Column(
            children: [
              WindowTitleBarBox(),
              Expanded(child: TabbedView(
                  controller: controller,
                  contentBuilder: (BuildContext context, int tabIndex) {
                    int i = tabIndex + 1;
                    return Center(child: Text('Content $i'));
                  }))
            ],
          )

      ),
    );
  }
}

// 自定义窗口按钮区域
class WindowButtons extends StatelessWidget {
  const WindowButtons({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        MinimizeWindowButton(),
        MaximizeWindowButton(),
        CloseWindowButton(),
      ],
    );
  }
}
