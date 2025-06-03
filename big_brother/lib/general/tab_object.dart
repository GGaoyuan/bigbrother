import 'package:big_brother/page/overview/overview_page.dart';
import 'package:big_brother/page/seesaw/seesaw_page.dart';
import 'package:tabbed_view/tabbed_view.dart';

class TabObject {
  static final overview = TabData(text: "Overview", closable: false, content: const OverviewPage());
  static final seesaw = TabData(text: "Seesaw", closable: false, content: const SeesawPage());

}


