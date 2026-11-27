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
    def test_business_routes_live_in_api_without_service_dependencies(self):
        from fastapi.routing import APIRoute

        from main import app

        routes = [route for route in app.routes if isinstance(route, APIRoute)]
        self.assertFalse((APP / "services").exists())
        modules = {route.endpoint.__module__ for route in routes}
        self.assertEqual(len(routes), len(modules))
        for route in routes:
            with self.subTest(path=route.path):
                self.assertTrue(route.endpoint.__module__.startswith("app.api."))
                self.assertFalse(route.dependant.dependencies)

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
            "api": {"api", "core", "models", "provider"},
            "provider": {"core", "models"},
            "models": {"models"},
            "core": {"core"},
        }
        for path in APP.rglob("*.py"):
            if path == APP / "__init__.py":
                continue
            parts = path.relative_to(APP).parts
            self.assertIn(parts[0], {"api", "core", "models"}, str(path))
            if parts[0] == "api":
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
                    if layer != "provider":
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
