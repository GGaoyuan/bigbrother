import 'package:go_router/go_router.dart';
import 'router_path.dart';


final RouterManager = GoRouter(
  initialLocation: RouterPath.home.home,
  routes: [
    // GoRoute(
      // path: RouterPath.SpiritualHome,
      // builder: (context, state) => const SpiritualHomePage(data: "123"),
    // )
  ],
);