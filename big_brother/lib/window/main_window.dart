import 'package:big_brother/general/app_config.dart';
import 'package:big_brother/page/overview/overview_page.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:bitsdojo_window/bitsdojo_window.dart';
import 'package:tabbed_view/tabbed_view.dart';
import 'package:big_brother/page/seesaw/seesaw_page.dart';
import 'package:big_brother/page/sentiment/main_page.dart';
import 'package:big_brother/page/rotation/rotation_page.dart';

class MainWindow extends ConsumerStatefulWidget {

  const MainWindow({super.key});

  @override
  MainWindowState createState() => MainWindowState();
}

class MainWindowState extends ConsumerState<MainWindow> {

  final _tabList = [
    TabData(text: "Rotation", closable: false, content: const RotationPage()),
    TabData(text: "Overview", closable: false, content: const OverviewPage()),
    TabData(text: "Seesaw", closable: false, content: const SeesawPage()),
    TabData(text: "AAA", closable: false, content: const MainPage()),
  ];

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
    return WindowBorder(color: AppConfig.themeColor, child: Column(
      children: [
        // 自定义顶部栏 - 已注释
        // WindowTitleBarBox(
        //   child: Container(color: Colors.black, child: Row(
        // children: [
        //       // 窗口控制按钮
        //       SizedBox(
        //         width: 100,
        //         child: MoveWindow(),
        //       ),
        //       // 应用名
        //       Padding(
        //         padding: EdgeInsets.symmetric(horizontal: 12),
        //         child: Text("bigbrother (Git)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        //       ),
        //       // const Spacer(),
        //       // 操作按钮
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       Flexible(flex: 1, child: _TopBarButton(icon: Icons.add, label: "提交")),
        //       SizedBox(
        //         width: 100,
        //         child: MoveWindow(),
        //       ),
        //     ],
        //   ))
        // ),
        Expanded(child: MoveWindow(
          child: TabbedView(
              controller: TabbedViewController(_tabList),
              contentBuilder: (BuildContext context, int tabIndex) {
                final widget = _tabList[tabIndex].content;
                if (widget != null) {
                  return widget;
                } else {
                  return Container();
                }
              }
          )
          ))
        ],
    ));
  }

}

// 自定义顶部栏按钮组件 - 已注释
// class _TopBarButton extends StatelessWidget {
//   final IconData icon;
//   final String label;
//   const _TopBarButton({required this.icon, required this.label});
//   @override
//   Widget build(BuildContext context) {
//     return Padding(
//       padding: EdgeInsets.symmetric(horizontal: 6),
//       child: Column(
//         mainAxisAlignment: MainAxisAlignment.center,
//         children: [
//           // Icon(icon, size: 18),
//           Text(label, style: TextStyle(fontSize: 10, )),
//           // Container(color: randomColor())
//         ],
//       ),
//     );
//   }
// }




