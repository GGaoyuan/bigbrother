from abc import ABC
from test.strategy_interface import StrategyInterface


class DemoStrategy(StrategyInterface, ABC):
    def __init__(self):
        pass

    def prepare_trading(self):
        print('DemoStrategy prepare_trading')
        pass

    def morning_market_open(self):
        print('DemoStrategy morning_market_open')

    def morning_market_close(self):
        print('DemoStrategy morning_market_close')

    def afternoon_market_open(self):
        print('DemoStrategy after_market_open')

    def afternoon_market_close(self):
        print('DemoStrategy after_market_close')