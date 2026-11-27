import ast
from importlib.util import resolve_name
from pathlib import Path
from unittest import TestCase


APP = Path(__file__).resolve().parents[1] / "app"


def layer_of(parts: tuple[str, ...]) -> str:
    if parts[:2] in (("models", "provider.py"), ("models", "provider")):
        return "provider"
    return parts[0]


class ArchitectureTests(TestCase):
    def test_backwards_dependencies_and_akshare_imports_are_rejected(self):
        allowed = {
            "api": {"api", "core", "models", "services"},
            "services": {"core", "models", "provider", "services"},
            "provider": {"core", "models", "provider"},
            "models": {"models"},
            "core": {"core"},
        }
        for path in APP.rglob("*.py"):
            if path == APP / "__init__.py":
                continue
            parts = path.relative_to(APP).parts
            self.assertIn(parts[0], {"api", "core", "models", "services"}, str(path))
            if parts[0] in {"api", "services", "models"}:
                self.assertEqual(len(parts), 2, str(path))
            if parts[0] == "models":
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
