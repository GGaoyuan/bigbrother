import yaml
from pathlib import Path
from typing import Optional


class Settings:
    def __init__(self):
        # 配置文件路径（项目根目录的 config.yaml）
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self._fastapi_config = config.get("fastapi", {})
        else:
            self._fastapi_config = {}

    @property
    def datasource(self) -> str:
        """获取数据源配置，默认为 akshare"""
        return self._fastapi_config.get("server", {}).get("datasource", "akshare")

    @property
    def host(self) -> str:
        return self._fastapi_config.get("server", {}).get("host", "0.0.0.0")

    @property
    def port(self) -> int:
        return self._fastapi_config.get("server", {}).get("port", 8000)

    @property
    def debug(self) -> bool:
        return self._fastapi_config.get("server", {}).get("debug", False)

    @property
    def allowed_origins(self) -> list[str]:
        return self._fastapi_config.get("cors", {}).get("allowed_origins", [])


settings = Settings()
