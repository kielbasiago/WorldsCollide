import args
from objectives.conditions._objective_condition import *
from seed import get_random_instance

class Condition(ObjectiveCondition):
    NAME = "Bosses"
    def __init__(self, min_count, max_count):
        random = get_random_instance(f"{args.subseed_check}--condition-{self.NAME}")
        self.count = random.randint(min_count, max_count)
        super().__init__(ConditionType.EventWord, event_word.BOSSES_DEFEATED, self.count)

    def __str__(self):
        return super().__str__(self.count)
