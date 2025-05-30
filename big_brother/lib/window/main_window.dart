import 'package:big_brother/general/app_config.dart';
import 'package:big_brother/general/tab_object.dart';
import 'package:big_brother/page/overview/overview_page.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:bitsdojo_window/bitsdojo_window.dart';
import 'package:tabbed_view/tabbed_view.dart';

class MainWindow extends ConsumerStatefulWidget {

  const MainWindow({super.key});

  @override
  MainWindowState createState() => MainWindowState();
}

class MainWindowState extends ConsumerState<MainWindow> {

  final _tabList = [TabObject.overview];

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
    return WindowBorder(color: AppConfig.instance.themeColor, child: MoveWindow(
      child: Column(
        children: [
          WindowTitleBarBox(child: Container(color: AppConfig.instance.themeColor)),
          Expanded(child: TabbedView(
              controller: TabbedViewController(_tabList),
              contentBuilder: (BuildContext context, int tabIndex) {
                final widget = _tabList[tabIndex].content;
                if (widget != null) {
                  return widget;
                } else {
                  return Container();
                }
              }
          ))
        ],
      ),
    ));
  }

}




