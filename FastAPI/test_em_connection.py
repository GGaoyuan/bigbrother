"""
测试东方财富接口连接状态
"""
import time
import requests

def test_eastmoney_connection():
    """测试东方财富接口是否可访问"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'http://quote.eastmoney.com/',
    }

    # 东方财富行业板块接口
    url = 'http://80.push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': '1',
        'pz': '10',  # 只请求 10 条数据
        'po': '1',
        'np': '1',
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': '2',
        'invt': '2',
        'fid': 'f3',
        'fs': 'm:90 t:2 f:!50',
        'fields': 'f12,f14',  # 只请求代码和名称
    }

    print("正在测试东方财富接口...")
    print(f"URL: {url}")

    for i in range(3):
        try:
            print(f"\n第 {i+1} 次尝试...")
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"✓ 成功！状态码: {resp.status_code}")
            data = resp.json()
            if 'data' in data and data['data']:
                print(f"✓ 返回数据正常，共 {data['data'].get('total', 0)} 条记录")
                return True
            else:
                print("✗ 返回数据为空")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ 连接错误: {type(e).__name__}")
            print("   → 你的 IP 可能被东方财富临时封禁")
        except Exception as e:
            print(f"✗ 其他错误: {type(e).__name__} - {str(e)}")

        if i < 2:
            print("等待 5 秒后重试...")
            time.sleep(5)

    print("\n" + "="*50)
    print("结论：东方财富接口当前无法访问")
    print("建议：")
    print("1. 等待 30-60 分钟后再试")
    print("2. 切换网络环境（如手机热点）")
    print("3. 使用同花顺接口替代（ak.stock_board_industry_name_ths）")
    return False

if __name__ == '__main__':
    test_eastmoney_connection()
