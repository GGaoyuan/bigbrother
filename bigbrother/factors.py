def test():
    print('im big brother test')

def pb_ratio() -> float:
    """
    市净率
    """
    return 0


def is_mainboard(stock_code: str) -> bool:
    """
    是否属于主板
    上交所主板：600， 601， 603， 605开头
    深交所主板：000
    深交所中小板：002
    目前中小板已经并入深交所主板了
    """
    if stock_code.startswith('600') or \
        stock_code.startswith('601') or \
        stock_code.startswith('603') or \
        stock_code.startswith('605') or \
        stock_code.startswith('000') or \
        stock_code.startswith('002'):
        return True
    else:
        return False