from objectives.conditions._objective_condition import *
from constants.objectives.condition_bits import quest_bit

class Condition(ObjectiveCondition):
    NAME = "Quest"
    def __init__(self, quest):
        self.quest = quest
        self.value = self.quest
        super().__init__(ConditionType.EventBit, self.bit())

    def __str__(self):
        return super().__str__(self.quest)

    def bit(self):
        return quest_bit[self.quest].bit

    def name(self):
        return quest_bit[self.quest].name

