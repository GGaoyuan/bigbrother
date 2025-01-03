import 'package:client_app/pages/home/home_page.dart';
import 'package:go_router/go_router.dart';
import 'router_path.dart';


final routerManager = GoRouter(
  initialLocation: RouterPath.home.home,
  routes: [
    GoRoute(
      path: RouterPath.home.home,
      builder: (context, state) => HomePage(),
    )
  ],
);