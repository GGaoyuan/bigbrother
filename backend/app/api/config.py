"""Static application and workspace configuration APIs."""

from fastapi import APIRouter

from app.api.response import ApiResponse, success_response

router = APIRouter(tags=["app-config"])


@router.post("/app/config")
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


@router.post("/workspace/data")
def get_workspace_data() -> ApiResponse:
    return success_response(
        {
            "workspaceId": 1,
            "dataCategories": [
                {
                    "id": "china-index",
                    "name": "中国指数",
                    "series": [
                        {
                            "id": "000001.SH",
                            "name": "上证指数",
                            "code": "000001.SH",
                        },
                        {
                            "id": "000300.SH",
                            "name": "沪深300",
                            "code": "000300.SH",
                        },
                        {
                            "id": "399001.SZ",
                            "name": "深证成指",
                            "code": "399001.SZ",
                        },
                        {
                            "id": "000852.SH",
                            "name": "中证1000",
                            "code": "000852.SH",
                        },
                        {
                            "id": "932000.CSI",
                            "name": "中证2000",
                            "code": "932000.CSI",
                        },
                        {
                            "id": "000905.SH",
                            "name": "中证500",
                            "code": "000905.SH",
                        },
                        {
                            "id": "399006.SZ",
                            "name": "创业板指",
                            "code": "399006.SZ",
                        },
                    ],
                    "metrics": [
                        {
                            "id": "close",
                            "name": "收盘价",
                        },
                        {
                            "id": "previous-close",
                            "name": "前收盘价",
                        },
                        {
                            "id": "change-amount",
                            "name": "涨跌额",
                        },
                        {
                            "id": "change-percent",
                            "name": "涨跌幅",
                        },
                        {
                            "id": "volume",
                            "name": "成交量",
                        },
                        {
                            "id": "amount",
                            "name": "成交额",
                        },
                    ],
                    "chartTypes": [
                        "line",
                        "bar",
                        "candlestick",
                    ],
                },
                {
                    "id": "margin-financing",
                    "name": "融资融券",
                    "metrics": [
                        {
                            "id": "margin-financing-balance",
                            "name": "融资融券余额",
                        },
                        {
                            "id": "financing-balance",
                            "name": "融资余额",
                        },
                        {
                            "id": "financing-buy-amount",
                            "name": "融资买入额",
                        },
                        {
                            "id": "financing-repayment-amount",
                            "name": "融资偿还额",
                        },
                        {
                            "id": "securities-lending-balance",
                            "name": "融券余额",
                        },
                        {
                            "id": "securities-sold-volume",
                            "name": "融券卖出量",
                        },
                        {
                            "id": "securities-lending-volume",
                            "name": "融券余量",
                        },
                    ],
                },
            ],
        }
    )


@router.post("/workspace/pages")
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
