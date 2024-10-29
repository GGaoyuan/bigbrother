from enum import Enum

class Node:
    def __init__(self, value):
        self.last_node: Node = None
        self.next_node: Node = None
        self.price = None
        self.datetime = None

class Peroid:
    class Grid(Enum):
        SECONDARY_RALLY = 1     # 次级回升
        NATURAL_RALLY = 2       # 自然回升
        UPWARD_TREND = 3        # 上升趋势
        DOWNWARD_TREND = 4      # 下降趋势
        NATURAL_Reaction = 5    # 自然回撤
        SECONDARY_Reaction = 6  # 次级回撤
    def __init__(self):
        self.last_peroid: Peroid = None
        self.next_peroid: Peroid = None
        




if __name__ == '__main__':
    pass