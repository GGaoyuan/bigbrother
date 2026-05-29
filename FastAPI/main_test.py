import asyncio
from app.service.industry import get_sw_industry

if __name__ == '__main__':
    result = asyncio.run(get_sw_industry())
    print(result)
