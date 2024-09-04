from abc import ABC, abstractmethod

class StrategyInterface(ABC):
    tradable = False
    isTrading = False
    @abstractmethod
    def prepare_trading(self):
        pass

    @abstractmethod
    def morning_market_open(self):
        pass

    @abstractmethod
    def morning_market_close(self):
        pass

    @abstractmethod
    def afternoon_market_open(self):
        pass

    @abstractmethod
    def afternoon_market_close(self):
        pass