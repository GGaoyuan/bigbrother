from stock.stock_gateway import StockGateway


if __name__ == '__main__':
    sg = StockGateway()
    sg.start_scheduler()

