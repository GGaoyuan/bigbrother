import baostock as bs
from typing import Any
from .base import StockProvider


class BaoStockProvider(StockProvider):
    async def get_daily(self, code: str, start: str, end: str) -> list[dict[str, Any]]:
        lg = bs.login()
        if lg.error_code != "0":
            raise Exception(f"BaoStock 登录失败: {lg.error_msg}")
        try:
            rs = bs.query_history_k_data_plus(
                code,
                "date,open,high,low,close,volume",
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag="3",
            )
            result = []
            while rs.error_code == "0" and rs.next():
                row = rs.get_row_data()
                result.append({
                    "date": row[0],
                    "open": float(row[1]) if row[1] else 0,
                    "high": float(row[2]) if row[2] else 0,
                    "low": float(row[3]) if row[3] else 0,
                    "close": float(row[4]) if row[4] else 0,
                    "volume": float(row[5]) if row[5] else 0,
                    "code": code,
                    "provider": "baostock",
                })
            return result
        finally:
            bs.logout()

    async def get_realtime(self, code: str) -> dict[str, Any]:
        raise NotImplementedError("BaoStock 不支持实时行情")

    async def get_market_stats(self, date: str) -> dict[str, Any]:
        """获取市场统计数据"""
        lg = bs.login()
        if lg.error_code != "0":
            raise Exception(f"BaoStock 登录失败: {lg.error_msg}")

        try:
            # 获取所有A股列表
            rs = bs.query_all_stock(date)
            if rs.error_code != "0":
                raise Exception(f"获取股票列表失败: {rs.error_msg}")

            stock_list = []
            while rs.error_code == "0" and rs.next():
                row = rs.get_row_data()
                # 只统计沪深A股 (sh/sz开头)
                if row[0].startswith(('sh.6', 'sz.0', 'sz.3')):
                    stock_list.append(row[0])

            if not stock_list:
                raise Exception("未获取到股票列表")

            # 统计数据
            up_count = 0
            down_count = 0
            limit_up_count = 0
            limit_down_count = 0
            total_change = 0.0
            max_change = 0.0
            total_volume = 0.0
            valid_count = 0

            # 批量获取每只股票的数据
            for code in stock_list[:500]:  # 限制数量避免超时
                try:
                    rs = bs.query_history_k_data_plus(
                        code,
                        "date,pctChg,amount",
                        start_date=date,
                        end_date=date,
                        frequency="d",
                        adjustflag="3",
                    )

                    if rs.error_code == "0" and rs.next():
                        row = rs.get_row_data()
                        if row[1]:  # pctChg
                            pct_chg = float(row[1])
                            amount = float(row[2]) if row[2] else 0

                            if pct_chg > 0:
                                up_count += 1
                            elif pct_chg < 0:
                                down_count += 1

                            if pct_chg >= 9.9:
                                limit_up_count += 1
                            elif pct_chg <= -9.9:
                                limit_down_count += 1

                            total_change += pct_chg
                            max_change = max(max_change, pct_chg)
                            total_volume += amount
                            valid_count += 1
                except:
                    continue

            if valid_count == 0:
                raise Exception("未获取到有效市场数据")

            return {
                "up_count": up_count,
                "down_count": down_count,
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "avg_change_pct": total_change / valid_count,
                "total_volume": total_volume,
                "max_change_pct": max_change,
                "provider": "baostock",
            }
        finally:
            bs.logout()
