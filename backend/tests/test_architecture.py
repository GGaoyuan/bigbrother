import ast
from importlib.util import resolve_name
from pathlib import Path
from unittest import TestCase


APP = Path(__file__).resolve().parents[1] / "app"


def layer_of(parts: tuple[str, ...]) -> str:
    if len(parts) >= 3 and parts[0] == "models" and parts[2] in {"provider", "provider.py"}:
        return "provider"
    return parts[0]


class ArchitectureTests(TestCase):
    def test_each_business_route_has_its_own_service(self):
        from fastapi.routing import APIRoute

        from main import app

        routes = [route for route in app.routes if isinstance(route, APIRoute)]
        services = {path.stem for path in (APP / "services").glob("*_service.py")}
        self.assertEqual(len(routes), len(services))
        for route in routes:
            with self.subTest(path=route.path):
                api_module = route.endpoint.__module__
                service_module = f"{api_module.rsplit('.', 1)[-1]}_service"
                self.assertIn(service_module, services)
                services.remove(service_module)
                dependency, = route.dependant.dependencies
                self.assertEqual(dependency.call.__module__, api_module)
                self.assertEqual(
                    dependency.call.__annotations__["return"].__module__,
                    f"app.services.{service_module}",
                )

    def test_models_group_fields_and_provider_by_data_type(self):
        models = APP / "models"
        self.assertEqual({path.name for path in models.glob("*.py")}, {"__init__.py"})
        for category in ("kline", "stock", "calendar", "volume_profile"):
            expected = {"__init__.py", "model.py"}
            if category != "volume_profile":
                expected.add("provider.py")
            with self.subTest(category=category):
                self.assertEqual({path.name for path in (models / category).glob("*.py")}, expected)

    def test_backwards_dependencies_and_akshare_imports_are_rejected(self):
        allowed = {
            "api": {"api", "core", "models", "services"},
            "services": {"core", "models", "provider", "services"},
            "provider": {"core", "models"},
            "models": {"models"},
            "core": {"core"},
        }
        for path in APP.rglob("*.py"):
            if path == APP / "__init__.py":
                continue
            parts = path.relative_to(APP).parts
            self.assertIn(parts[0], {"api", "core", "models", "services"}, str(path))
            if parts[0] in {"api", "services"}:
                self.assertEqual(len(parts), 2, str(path))
            if parts[0] == "models":
                if path != APP / "models" / "__init__.py":
                    self.assertEqual(len(parts), 3, str(path))
                self.assertIn(parts[-1], {"__init__.py", "model.py", "provider.py"}, str(path))
            layer = layer_of(parts)
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        package = ".".join(("app", *path.relative_to(APP).parts[:-1]))
                        module = resolve_name("." * node.level + (node.module or ""), package)
                    else:
                        module = node.module
                    imports = (
                        [f"{module}.{alias.name}" for alias in node.names]
                        if module == "app" or module.startswith("app.")
                        else [module]
                    )
                else:
                    continue
                for module in imports:
                    root_module = module.split(".")[0]
                    self.assertNotEqual(root_module, "akshare", str(path))
                    if layer in {"api", "services", "models", "core"}:
                        self.assertNotIn(
                            root_module,
                            {"mootdx", "tdxpy", "easy_tdx", "exchange_calendars", "pandas", "requests"},
                            str(path),
                        )
                    if module.startswith("app."):
                        self.assertIn(
                            layer_of(tuple(module.split(".")[1:])),
                            allowed[layer],
                            f"{path.relative_to(APP)} imports {module}",
                        )
