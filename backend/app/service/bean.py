import json
from typing import Any, Iterable, List

from app.base.datasource_from import DatasourceFrom


def sanitize_json(data: Any) -> Any:
    return json.loads(json.dumps(data, ensure_ascii=False, default=str))


def tag_datasource(items: Iterable[Any], source: DatasourceFrom = DatasourceFrom.EAST_MONEY) -> List[dict]:
    rows: List[dict] = []
    for item in items:
        if hasattr(item, "model_dump"):
            rows.append({**item.model_dump(), "datasource": source.name})
        elif isinstance(item, dict):
            rows.append({**item, "datasource": source.name})
    return rows
