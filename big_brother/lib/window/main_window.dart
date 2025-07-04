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

  final _tabList = [
    TabObject.seesaw,
    TabObject.overview,
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
    return WindowBorder(color: AppConfig.instance.themeColor, child: Column(
      children: [
        // 自定义顶部栏
        WindowTitleBarBox(
          child: Row(
            children: [
              // 窗口控制按钮
              SizedBox(
                width: 100,
                child: MoveWindow(child: Row(
                  children: [
                    MinimizeWindowButton(),
                    MaximizeWindowButton(),
                    CloseWindowButton(),
                  ],
                )),
              ),
              // 应用名
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 12),
                child: Text("bigbrother (Git)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ),
              Spacer(),
              // 操作按钮
              _TopBarButton(icon: Icons.add, label: "提交"),
              _TopBarButton(icon: Icons.download, label: "拉取"),
              _TopBarButton(icon: Icons.upload, label: "推送"),
              _TopBarButton(icon: Icons.access_time, label: "抓取"),
              _TopBarButton(icon: Icons.device_hub, label: "分支"),
              _TopBarButton(icon: Icons.merge_type, label: "合并"),
              _TopBarButton(icon: Icons.cloud, label: "显示远程服务器"),
              _TopBarButton(icon: Icons.folder_open, label: "在Finder中显示"),
              _TopBarButton(icon: Icons.terminal, label: "终端"),
              _TopBarButton(icon: Icons.settings, label: "设置"),
              SizedBox(width: 12),
            ],
          ),
        ),
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

// 自定义顶部栏按钮组件
class _TopBarButton extends StatelessWidget {
  final IconData icon;
  final String label;
  const _TopBarButton({required this.icon, required this.label});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 6),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Icon(icon, size: 18),
          Text(label, style: TextStyle(fontSize: 10, )),
        ],
      ),
    );
  }
}




