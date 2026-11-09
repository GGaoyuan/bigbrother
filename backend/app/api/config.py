"""Static application and workspace configuration APIs."""

from fastapi import APIRouter

from app.api.response import ApiResponse, success_response

router = APIRouter(tags=["app-config"])


@router.get("/app/config")
def get_app_config() -> ApiResponse:
    return success_response(
        {
            "workspace": [
                {
                    "id": 1,
                    "name": "数据",
                },
                {
                    "id": 2,
                    "name": "AI",
                },
                {
                    "id": 3,
                    "name": "页面",
                },
            ],
        }
    )


@router.get("/workspace/data")
def get_workspace_data() -> ApiResponse:
    return success_response(
        {
            "workspaceId": 1,
            "data": {
                "sidebar": {
                    "dataCategoriesLabel": "数据类别",
                    "marketDataLabel": "数据源",
                    "marketDataHint": "MARKET DATA",
                    "selectSeriesHint": "选择数据系列并添加到图表",
                    "searchPlaceholder": "搜索数据名称或代码",
                    "noResultsLabel": "没有匹配的数据",
                    "seriesNameLabel": "名称",
                    "seriesCodeLabel": "代码",
                    "metricsLabel": "指标",
                    "metricHint": "选择一个指标",
                    "addToChartLabel": "添加到图表",
                    "dataPageDescription": "从左侧数据分类选择数据系列，添加后在这里进行展示。",
                    "dataPageTitle": "数据工作台",
                    "dataPagePlaceholder": "数据图表容器",
                },
                "dataCategories": [
                    {
                        "id": "a-share-equities",
                        "type": "equity",
                        "label": "A股个股",
                        "icon": "◉",
                        "series": [
                            {
                                "id": "600519.SH",
                                "label": "贵州茅台",
                                "code": "600519.SH",
                                "categoryLabel": "白酒",
                            },
                            {
                                "id": "300750.SZ",
                                "label": "宁德时代",
                                "code": "300750.SZ",
                                "categoryLabel": "电池",
                            },
                            {
                                "id": "601318.SH",
                                "label": "中国平安",
                                "code": "601318.SH",
                                "categoryLabel": "保险",
                            },
                            {
                                "id": "002594.SZ",
                                "label": "比亚迪",
                                "code": "002594.SZ",
                                "categoryLabel": "汽车",
                            },
                        ],
                    },
                    {
                        "id": "a-share-indices",
                        "type": "index",
                        "label": "A股指数",
                        "icon": "▥",
                        "series": [
                            {
                                "id": "000001.SH",
                                "label": "上证指数",
                                "code": "000001.SH",
                                "categoryLabel": "上交所",
                            },
                            {
                                "id": "399001.SZ",
                                "label": "深证成指",
                                "code": "399001.SZ",
                                "categoryLabel": "深交所",
                            },
                            {
                                "id": "000300.SH",
                                "label": "沪深300",
                                "code": "000300.SH",
                                "categoryLabel": "宽基指数",
                            },
                            {
                                "id": "399006.SZ",
                                "label": "创业板指",
                                "code": "399006.SZ",
                                "categoryLabel": "深交所",
                            },
                        ],
                    },
                    {
                        "id": "a-share-index-valuations",
                        "type": "valuation",
                        "label": "A股指数估值",
                        "icon": "◷",
                        "series": [
                            {
                                "id": "300-pe-ttm",
                                "label": "沪深300 PE-TTM",
                                "code": "000300.SH",
                                "categoryLabel": "市盈率",
                            },
                            {
                                "id": "000001-pe-ttm",
                                "label": "上证指数 PE-TTM",
                                "code": "000001.SH",
                                "categoryLabel": "市盈率",
                            },
                            {
                                "id": "000905-pb",
                                "label": "中证500 PB",
                                "code": "000905.SH",
                                "categoryLabel": "市净率",
                            },
                        ],
                    },
                    {
                        "id": "margin-trading",
                        "type": "margin",
                        "label": "融资融券",
                        "icon": "↗",
                        "series": [
                            {
                                "id": "FIN.MARGIN",
                                "label": "两市融资余额",
                                "code": "FIN.MARGIN",
                                "categoryLabel": "融资余额",
                            },
                            {
                                "id": "SH.MARGIN",
                                "label": "沪市融资余额",
                                "code": "SH.MARGIN",
                                "categoryLabel": "上交所",
                            },
                            {
                                "id": "SZ.MARGIN",
                                "label": "深市融资余额",
                                "code": "SZ.MARGIN",
                                "categoryLabel": "深交所",
                            },
                        ],
                    },
                ],
                "metrics": [
                    {
                        "id": "close",
                        "label": "收盘价",
                    },
                    {
                        "id": "open",
                        "label": "开盘价",
                    },
                    {
                        "id": "high",
                        "label": "最高价",
                    },
                    {
                        "id": "low",
                        "label": "最低价",
                    },
                    {
                        "id": "volume",
                        "label": "成交量",
                    },
                    {
                        "id": "amount",
                        "label": "成交额",
                    },
                    {
                        "id": "change-percent",
                        "label": "涨跌幅",
                    },
                ],
            },
        }
    )


@router.get("/workspace/pages")
def get_workspace_pages() -> ApiResponse:
    return success_response(
        {
            "workspaceId": 3,
            "pages": [
                {
                    "id": 1,
                    "name": "行情",
                    "path": "/",
                },
                {
                    "id": 2,
                    "name": "市场情绪",
                    "path": "/market_sentiment",
                },
                {
                    "id": 3,
                    "name": "今日大盘",
                    "path": "/today",
                },
                {
                    "id": 4,
                    "name": "大盘异动",
                    "path": "/market_anomaly",
                },
                {
                    "id": 5,
                    "name": "市场面",
                    "path": "/recap",
                },
                {
                    "id": 6,
                    "name": "指标面",
                    "path": "/recap/indicators",
                },
                {
                    "id": 7,
                    "name": "宏观经济",
                    "path": "/recap/macro",
                },
                {
                    "id": 8,
                    "name": "股息率测算",
                    "path": "/recap/dividend_yield",
                },
                {
                    "id": 9,
                    "name": "热力图（复盘）",
                    "path": "/recap/heatmap",
                },
                {
                    "id": 10,
                    "name": "板块分析",
                    "path": "/recap/sector",
                },
                {
                    "id": 11,
                    "name": "题材热力图",
                    "path": "/heatmap/theme",
                },
                {
                    "id": 12,
                    "name": "行业热力图",
                    "path": "/heatmap/industry",
                },
                {
                    "id": 13,
                    "name": "涨跌热力图",
                    "path": "/heatmap/change",
                },
                {
                    "id": 14,
                    "name": "时间轴",
                    "path": "/timeline",
                },
                {
                    "id": 15,
                    "name": "题材库",
                    "path": "/theme_lib",
                },
                {
                    "id": 16,
                    "name": "订单流",
                    "path": "/order_flow",
                },
                {
                    "id": 17,
                    "name": "分时资金流",
                    "path": "/intraday_flow",
                },
                {
                    "id": 18,
                    "name": "龙虎榜统计",
                    "path": "/popularity/top-list",
                },
                {
                    "id": 19,
                    "name": "热榜",
                    "path": "/popularity/hot-rank",
                },
            ],
        }
    )
