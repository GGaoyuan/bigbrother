import ast
from importlib.util import resolve_name
from pathlib import Path
from unittest import TestCase


APP = Path(__file__).resolve().parents[1] / "app"


class ArchitectureTests(TestCase):
    def test_backwards_dependencies_and_akshare_imports_are_rejected(self):
        allowed = {
            "api": {"api", "core", "models", "services"},
            "services": {"core", "models", "services"},
            "data": {"core", "models", "data"},
            "models": {"models"},
            "core": {"core"},
        }
        for path in APP.rglob("*.py"):
            if path == APP / "__init__.py":
                continue
            layer = path.relative_to(APP).parts[0]
            self.assertIn(layer, allowed, str(path))
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        package = ".".join(("app", *path.relative_to(APP).parts[:-1]))
                        module = resolve_name("." * node.level + (node.module or ""), package)
                    else:
                        module = node.module
                    imports = [f"app.{alias.name}" for alias in node.names] if module == "app" else [module]
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
                        self.assertTrue(
                            any(module == f"app.{dep}" or module.startswith(f"app.{dep}.")
                                for dep in allowed[layer]),
                            f"{path.relative_to(APP)} imports {module}",
                        )
