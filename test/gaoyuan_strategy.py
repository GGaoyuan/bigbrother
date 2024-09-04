from abc import ABC
from test.strategy_interface import StrategyInterface
from datetime import time
import time
class GaoyuanStrategy(StrategyInterface, ABC):
    def __init__(self):
        self.tradable = False
        self.tradabling = False

    def prepare_trading(self):
        self.tradable = True
        print('GaoyuanStrategy prepare_trading')

    def morning_market_open(self):
        while self.tradable and self.tradabling:
            print('morning_market_open whiling')
            time.sleep(1)

        print('GaoyuanStrategy morning_market_open')

    def morning_market_close(self):
        print('GaoyuanStrategy morning_market_close')

    def afternoon_market_open(self):
        print('GaoyuanStrategy after_market_open')

    def afternoon_market_close(self):
        self.tradable = False
        print('GaoyuanStrategy after_market_close')