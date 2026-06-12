import asyncio
from app.service.industry import get_sw_industry, get_sw_stock_industry

if __name__ == '__main__':
    result = asyncio.run(get_sw_industry())
    print(result)
    result2 = asyncio.run(get_sw_stock_industry())
    print(result2)
